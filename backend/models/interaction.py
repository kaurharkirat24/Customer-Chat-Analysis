from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    tier = Column(String, default="Standard") # Standard, Enterprise, VIP
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interactions = relationship("Interaction", back_populates="customer")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    channel = Column(String) # Email, Slack, etc
    is_spam = Column(Boolean, default=False, index=True)
    original_message = Column(Text, nullable=False)
    ai_intent = Column(String)
    ai_sentiment = Column(String)
    ai_summary = Column(Text)
    confidence_score = Column(Float, default=1.0)
    priority = Column(String, default="P3") # P0, P1, P2, P3
    feature_tag = Column(String, nullable=True) # Extracted feature for feedback
    status = Column(String, default="Pending") # Pending, Resolved, Escalated, Draft_Pending_Approval, Resolved_By_Human
    resolved_by = Column(String, nullable=True) # Email of internal user who resolved
    resolution_note = Column(Text, nullable=True) # Human's note when self-resolving
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="interactions")
    action_logs = relationship("ActionLog", back_populates="interaction")
    attachments = relationship("Attachment", back_populates="interaction")

class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    action_type = Column(String) # AutoReply, Escalate, Tag
    outgoing_message = Column(Text, nullable=True)
    status = Column(String) # Success, Failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interaction = relationship("Interaction", back_populates="action_logs")
