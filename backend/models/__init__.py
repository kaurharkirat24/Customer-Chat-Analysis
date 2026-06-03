from .database import Base, engine, get_db
from .user import InternalUser
from .interaction import Customer, Interaction, ActionLog
from .attachment import Attachment
# Create all tables in the database on import for MVP
Base.metadata.create_all(bind=engine)
