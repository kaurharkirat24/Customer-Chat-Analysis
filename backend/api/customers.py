from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import get_db, Customer, Interaction

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/")
def get_all_customers(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    """Return paginated list of customers with interaction count and last interaction date.
    Args:
        page: 1‑based page number.
        page_size: Number of items per page (max 100).
    """
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    # total count for metadata
    total = db.query(func.count(Customer.id)).scalar()
    offset = (page - 1) * page_size
    customers = (
        db.query(Customer)
        .order_by(Customer.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    results = []
    for c in customers:
        interaction_count = db.query(func.count(Interaction.id)).filter(
            Interaction.customer_id == c.id
        ).scalar()
        last_interaction = (
            db.query(Interaction)
            .filter(Interaction.customer_id == c.id)
            .order_by(Interaction.id.desc())
            .first()
        )
        results.append({
            "id": c.id,
            "email": c.email,
            "name": c.name or "Unknown",
            "tier": c.tier or "Standard",
            "interaction_count": interaction_count,
            "last_interaction_date": last_interaction.created_at.isoformat() if last_interaction and last_interaction.created_at else None,
            "last_intent": last_interaction.ai_intent if last_interaction else None,
            "last_status": last_interaction.status if last_interaction else None,
        })
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "customers": results,
    }


@router.get("/{customer_id}")
def get_customer_detail(customer_id: int, db: Session = Depends(get_db)):
    """Return a single customer with all their interactions."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {"error": "Customer not found"}

    interactions = (
        db.query(Interaction)
        .filter(Interaction.customer_id == customer.id)
        .order_by(Interaction.id.desc())
        .all()
    )

    return {
        "id": customer.id,
        "email": customer.email,
        "name": customer.name or "Unknown",
        "tier": customer.tier or "Standard",
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
        "interactions": [
            {
                "id": it.id,
                "channel": it.channel,
                "original_message": it.original_message,
                "ai_intent": it.ai_intent,
                "ai_sentiment": it.ai_sentiment,
                "confidence": it.confidence_score,
                "priority": it.priority,
                "feature_tag": it.feature_tag,
                "status": it.status,
                "created_at": it.created_at.isoformat() if it.created_at else None,
            }
            for it in interactions
        ],
    }
