from .database import Base, engine, get_db
from .user import InternalUser
from .interaction import Customer, Interaction, ActionLog

# Create all tables in the database on import for MVP
Base.metadata.create_all(bind=engine)
