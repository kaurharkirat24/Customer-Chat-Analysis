from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db, Interaction, ActionLog, Customer
from pydantic import BaseModel
from typing import Optional
from services.gmail_service import send_email

router = APIRouter(prefix="/review", tags=["review"])


class ResolveRequest(BaseModel):
    decision: str  # "approve", "self_resolved", "reject"
    edited_message: Optional[str] = None
    resolution_note: Optional[str] = None
    reassign_to: Optional[str] = None  # forced intent for re-route
    resolved_by: Optional[str] = None  # email of reviewer


@router.get("/queue")
def get_review_queue(db: Session = Depends(get_db)):
    """Return all interactions needing human review, sorted by priority."""
    interactions = (
        db.query(Interaction)
        .filter(Interaction.status == "Draft_Pending_Approval")
        .order_by(
            # P0 first, then P1, P2, P3
            Interaction.priority.asc(),
            Interaction.id.desc()
        )
        .all()
    )

    results = []
    for it in interactions:
        customer = db.query(Customer).filter(Customer.id == it.customer_id).first()
        log = db.query(ActionLog).filter(ActionLog.interaction_id == it.id).first()
        results.append({
            "id": it.id,
            "customer_email": customer.email if customer else "Unknown",
            "customer_name": customer.name if customer else "Unknown",
            "original_message": it.original_message,
            "ai_intent": it.ai_intent or "Unknown",
            "ai_sentiment": it.ai_sentiment or "Unknown",
            "confidence": it.confidence_score or 0,
            "priority": it.priority or "P3",
            "feature_tag": it.feature_tag,
            "ai_draft_response": log.outgoing_message if log else None,
            "action_type": log.action_type if log else None,
            "created_at": it.created_at.isoformat() if it.created_at else None,
        })
    return results


@router.get("/{interaction_id}")
def get_review_detail(interaction_id: int, db: Session = Depends(get_db)):
    """Return full detail of a single interaction for review."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    customer = db.query(Customer).filter(Customer.id == interaction.customer_id).first()
    logs = (
        db.query(ActionLog)
        .filter(ActionLog.interaction_id == interaction.id)
        .order_by(ActionLog.id.asc())
        .all()
    )

    return {
        "id": interaction.id,
        "customer": {
            "id": customer.id if customer else None,
            "email": customer.email if customer else "Unknown",
            "name": customer.name if customer else "Unknown",
            "tier": customer.tier if customer else "Standard",
        },
        "channel": interaction.channel,
        "original_message": interaction.original_message,
        "ai_intent": interaction.ai_intent,
        "ai_sentiment": interaction.ai_sentiment,
        "confidence": interaction.confidence_score,
        "priority": interaction.priority,
        "feature_tag": interaction.feature_tag,
        "is_spam": interaction.is_spam,
        "status": interaction.status,
        "resolved_by": interaction.resolved_by,
        "resolution_note": interaction.resolution_note,
        "created_at": interaction.created_at.isoformat() if interaction.created_at else None,
        "action_history": [
            {
                "id": log.id,
                "action_type": log.action_type,
                "outgoing_message": log.outgoing_message,
                "status": log.status,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }


@router.post("/{interaction_id}/resolve")
def resolve_interaction(interaction_id: int, req: ResolveRequest, db: Session = Depends(get_db)):
    """Human resolves a pending review item."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    customer = db.query(Customer).filter(Customer.id == interaction.customer_id).first()

    if req.decision == "approve":
        # Send the (optionally edited) email and mark as resolved
        message_to_send = req.edited_message
        if not message_to_send:
            # Fall back to the AI draft
            existing_log = db.query(ActionLog).filter(ActionLog.interaction_id == interaction.id).first()
            message_to_send = existing_log.outgoing_message if existing_log else "Thank you for reaching out."

        if customer and customer.email and "@" in customer.email:
            try:
                send_email(customer.email, "Re: Your Recent Request", message_to_send)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

        interaction.status = "Resolved"
        interaction.resolved_by = req.resolved_by
        db.commit()

        action_log = ActionLog(
            interaction_id=interaction.id,
            action_type="Human_Approved_Send",
            outgoing_message=message_to_send,
            status="Success"
        )
        db.add(action_log)
        db.commit()

    elif req.decision == "self_resolved":
        # Human handled it outside the system
        interaction.status = "Resolved_By_Human"
        interaction.resolved_by = req.resolved_by
        interaction.resolution_note = req.resolution_note or "Resolved manually by agent."
        db.commit()

        action_log = ActionLog(
            interaction_id=interaction.id,
            action_type="Human_Self_Resolved",
            outgoing_message=req.resolution_note or "Resolved manually by agent.",
            status="Success"
        )
        db.add(action_log)
        db.commit()

    elif req.decision == "reject":
        # Mark as re-routed, log the rejection
        interaction.status = "Re_Routed"
        interaction.resolved_by = req.resolved_by
        interaction.resolution_note = req.resolution_note or f"Rejected and re-routed to: {req.reassign_to}"
        db.commit()

        action_log = ActionLog(
            interaction_id=interaction.id,
            action_type=f"Human_Rejected_ReRouted_To_{req.reassign_to or 'Manual'}",
            outgoing_message=req.resolution_note or "Human rejected AI classification.",
            status="Success"
        )
        db.add(action_log)
        db.commit()

    else:
        raise HTTPException(status_code=400, detail="Invalid decision. Must be: approve, self_resolved, or reject.")

    return {"success": True, "new_status": interaction.status}
