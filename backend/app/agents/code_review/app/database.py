import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./code_reviews.db')

# Configure engine based on database type
if "postgresql" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CodeReview(Base):
    __tablename__ = "code_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    original_repo_url = Column(String(500), nullable=False)
    updated_repo_url = Column(String(500), nullable=False)
    scan_report = Column(Text)
    changes_summary = Column(Text)
    diff_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    logger.warning("Application will continue without database functionality")

def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(f"Database session failed: {e}")
        raise
    finally:
        if db:
            db.close()