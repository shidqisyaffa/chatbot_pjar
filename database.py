import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

import config
from models import Base

logger = logging.getLogger(__name__)

# Configure SQLAlchemy Engine with Connection Pool
engine = None
SessionLocal = None

if config.DATABASE_URL:
    try:
        # Standard configuration for Neon PostgreSQL (SSL mode is required, pool size limits, etc.)
        engine = create_engine(
            config.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Database engine initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database engine: {e}")
else:
    logger.error("DATABASE_URL is not configured. Database engine not initialized.")

def init_db():
    """
    Creates all tables in the database if they do not exist.
    """
    if engine is None:
        logger.error("Cannot initialize DB: Database engine is not configured.")
        return False
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        return False

@contextmanager
def get_db_session():
    """
    Context manager to yield a database session, handle commits/rollbacks,
    and close the session cleanly.
    """
    if SessionLocal is None:
        raise ValueError("Database session factory is not initialized. Check your DATABASE_URL.")
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        session.close()

def check_db_status() -> bool:
    """
    Checks if connection to the database is healthy.
    """
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            # Run a lightweight query to verify connectivity
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
