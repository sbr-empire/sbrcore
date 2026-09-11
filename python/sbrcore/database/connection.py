# ============================================================================
# Database Connection Manager
# Connection pooling and session management
# ============================================================================

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator, Optional
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

class DatabaseConnection:
    """
    Manages database connection, pooling, and sessions
    Supports PostgreSQL, MySQL, SQLite
    """
    
    _engine = None
    _session_factory = None
    
    @classmethod
    def initialize(cls, database_url: Optional[str] = None, echo: bool = False):
        """
        Initialize database connection and engine
        
        Args:
            database_url: Database connection URL
            echo: Print SQL statements
        """
        if cls._engine is not None:
            logger.warning("Database already initialized")
            return
        
        url = database_url or Config.DATABASE_URL
        
        logger.info(f"Initializing database: {url[:50]}...")
        
        # Create engine with connection pooling
        cls._engine = create_engine(
            url,
            echo=echo or Config.DEBUG,
            poolclass=QueuePool,
            pool_size=Config.DATABASE_POOL_SIZE,
            max_overflow=10,
            pool_pre_ping=True,  # Test connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
        
        # Create session factory
        cls._session_factory = sessionmaker(
            bind=cls._engine,
            expire_on_commit=False,
            autoflush=False
        )
        
        # Test connection
        try:
            with cls._engine.connect() as conn:
                conn.execute("SELECT 1")
                logger.info("✅ Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise
    
    @classmethod
    def get_engine(cls):
        """Get database engine"""
        if cls._engine is None:
            cls.initialize()
        return cls._engine
    
    @classmethod
    def get_session_factory(cls):
        """Get session factory"""
        if cls._session_factory is None:
            cls.initialize()
        return cls._session_factory
    
    @classmethod
    def create_session(cls) -> Session:
        """
        Create a new database session
        
        Returns:
            SQLAlchemy Session
        """
        factory = cls.get_session_factory()
        return factory()
    
    @classmethod
    @contextmanager
    def session_scope(cls) -> Generator[Session, None, None]:
        """
        Context manager for database sessions
        Automatically commits or rolls back
        
        Usage:
            with DatabaseConnection.session_scope() as session:
                session.add(user)
        """
        session = cls.create_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    @classmethod
    def create_all_tables(cls):
        """
        Create all database tables
        """
        from .models import BaseModel
        engine = cls.get_engine()
        BaseModel.metadata.create_all(engine)
        logger.info("✅ All database tables created")
    
    @classmethod
    def drop_all_tables(cls):
        """
        Drop all database tables (Use with caution!)
        """
        from .models import BaseModel
        engine = cls.get_engine()
        BaseModel.metadata.drop_all(engine)
        logger.warning("⚠️ All database tables dropped")
    
    @classmethod
    def close(cls):
        """
        Close database connection
        """
        if cls._engine:
            cls._engine.dispose()
            logger.info("Database connection closed")

def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency injection function for FastAPI/Flask
    
    Usage in Flask:
        @app.route('/users')
        def get_users():
            for session in get_db_session():
                users = session.query(User).all()
    """
    session = DatabaseConnection.create_session()
    try:
        yield session
    finally:
        session.close()
