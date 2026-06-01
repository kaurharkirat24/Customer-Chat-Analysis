from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, Interaction, ActionLog, Customer
from graph.workflow import app_graph
from pydantic import BaseModel

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
def get_recent_interactions(db: Session = Depends(get_db)):
    # Fetch top 20 recent interactions
    interactions = db.query(Interaction).order_by(Interaction.id.desc()).limit(20).all()
    results = []
    for it in interactions:
        customer = db.query(Customer).filter(Customer.id == it.customer_id).first()
        log = db.query(ActionLog).filter(ActionLog.interaction_id == it.id).first()
        results.append({
            "id": it.id,
            "user": customer.email if customer else "Unknown",
            "intent": it.ai_intent or "Unknown",
            "sentiment": it.ai_sentiment or "Pending",
            "action": log.action_type if log else "Pending",
            "time": "Just now" # Simplification for MVP
        })
    return results
