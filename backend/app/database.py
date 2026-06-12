import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
database_url = os.getenv("DATABASE_URL")

# sanity check to ensure the database URL is set
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Create the SQLAlchemy engine
engine = create_engine(database_url, echo=False)

# Create a session - this will be used to interact with the database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
