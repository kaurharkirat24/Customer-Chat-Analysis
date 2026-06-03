from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    filename = Column(String)
    file_type = Column(String)
    size = Column(Integer)
    s3_key = Column(String)
    s3_url = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    interaction = relationship("Interaction", back_populates="attachments")
