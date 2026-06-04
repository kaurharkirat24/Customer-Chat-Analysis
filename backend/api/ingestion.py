from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models import get_db, Interaction, ActionLog, Customer
from graph.workflow import app_graph
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

class MockEmailPayload(BaseModel):
    email: str
    name: str
    message: str

@router.post("/mock")
def ingest_mock_email(payload: MockEmailPayload, db: Session = Depends(get_db)):
    # 1. Ensure customer exists
    customer = db.query(Customer).filter(Customer.email == payload.email).first()
    if not customer:
        customer = Customer(email=payload.email, name=payload.name)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    
    # 2. Save Initial Interaction
    interaction = Interaction(
        customer_id=customer.id,
        channel="Email (Mock)",
        original_message=payload.message
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    # 3. Run through LangGraph
    initial_state = {
        "interaction_id": interaction.id,
        "text": payload.message
    }
    
    final_state = app_graph.invoke(initial_state)

    # 4. Update Interaction with AI analysis
    interaction.ai_intent = final_state.get("intent")
    interaction.ai_sentiment = final_state.get("sentiment")
    interaction.status = final_state.get("status", "Processed")
    db.commit()

    # 5. Log the Action
    action_log = ActionLog(
        interaction_id=interaction.id,
        action_type=final_state.get("action_type"),
        outgoing_message=final_state.get("outgoing_message"),
        status="Success"
    )
    db.add(action_log)
    db.commit()

    return {
        "message": "Processed successfully",
        "interaction_id": interaction.id,
        "ai_analysis": {
            "intent": interaction.ai_intent,
            "sentiment": interaction.ai_sentiment
        },
        "action_taken": action_log.action_type
    }

@router.get("/interactions")
def get_recent_interactions(
    timeframe: str = Query("all", description="Timeframe filter: 1h, 1d, 15d, 30d, 1y, all"),
    search: str = Query("", description="Search by email or message content"),
    status: str = Query("", description="Filter by status"),
    intent: str = Query("", description="Filter by intent"),
    priority: str = Query("", description="Filter by priority"),
    db: Session = Depends(get_db)
):
    query = db.query(Interaction)
    
    if timeframe != "all":
        now = datetime.now(timezone.utc)
        if timeframe == "1h":
            threshold = now - timedelta(hours=1)
        elif timeframe == "1d":
            threshold = now - timedelta(days=1)
        elif timeframe == "15d":
            threshold = now - timedelta(days=15)
        elif timeframe == "30d":
            threshold = now - timedelta(days=30)
        elif timeframe == "1y":
            threshold = now - timedelta(days=365)
        else:
            threshold = None
            
        if threshold:
            query = query.filter(Interaction.created_at >= threshold)

    if status:
        query = query.filter(Interaction.status == status)
    if intent:
        query = query.filter(Interaction.ai_intent.ilike(f"%{intent}%"))
    if priority:
        query = query.filter(Interaction.priority == priority)

    # Search across customer email and original message
    if search:
        query = query.join(Customer, Interaction.customer_id == Customer.id).filter(
            (Customer.email.ilike(f"%{search}%")) | 
            (Interaction.original_message.ilike(f"%{search}%"))
        )

    interactions = query.order_by(Interaction.id.desc()).limit(100).all()
    results = []
    for it in interactions:
        customer = db.query(Customer).filter(Customer.id == it.customer_id).first()
        log = db.query(ActionLog).filter(ActionLog.interaction_id == it.id).first()
        
        # Truncate message for preview
        preview = it.original_message[:120] + "..." if it.original_message and len(it.original_message) > 120 else it.original_message

        results.append({
            "id": it.id,
            "user": customer.email if customer else "Unknown",
            "customer_name": customer.name if customer else "Unknown",
            "intent": it.ai_intent or "Unknown",
            "sentiment": it.ai_sentiment or "Pending",
            "action": log.action_type if log else "Pending",
            "priority": it.priority or "P3",
            "confidence": it.confidence_score or 1.0,
            "status": it.status or "Pending",
            "feature": it.feature_tag,
            "is_spam": it.is_spam,
            "message_preview": preview,
            "created_at": it.created_at.isoformat() if it.created_at else None,
        })
    return results

