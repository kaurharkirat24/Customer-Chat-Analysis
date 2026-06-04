import os
from sqlalchemy import create_engine
from models.database import Base
from models import interaction, attachment, action_log  # Ensure all models are loaded

# Get the URL
url = os.getenv("DATABASE_URL")
if not url:
    print("No DATABASE_URL")
    exit(1)

print(f"Connecting to {url}")
engine = create_engine(url)

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("Database recreation successful!")
