from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite Database configuration (no installation required)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ai_consultancy.db"  # Creates a local SQLite file
)

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite with FastAPI
        echo=False  # Set to True for SQL query logging in development
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging in development
        pool_pre_ping=True  # Verify connections before use
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: Function to create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Optional: Function to drop all tables (useful for testing)
def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)