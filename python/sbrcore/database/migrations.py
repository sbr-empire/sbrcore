# ============================================================================
# Database Migrations Manager
# Alembic integration for schema versioning
# ============================================================================

import os
from sqlalchemy import inspect
from .connection import DatabaseConnection
from .models import BaseModel
from ..logging import get_logger

logger = get_logger(__name__)

class DatabaseMigrations:
    """
    Manages database schema migrations
    """
    
    @staticmethod
    def create_tables():
        """
        Create all tables from ORM models
        Safe for development - won't recreate existing tables
        """
        engine = DatabaseConnection.get_engine()
        BaseModel.metadata.create_all(engine)
        logger.info("✅ Database tables created/verified")
    
    @staticmethod
    def get_table_names():
        """
        Get all existing table names
        """
        engine = DatabaseConnection.get_engine()
        inspector = inspect(engine)
        return inspector.get_table_names()
    
    @staticmethod
    def get_table_columns(table_name):
        """
        Get all columns for a table
        """
        engine = DatabaseConnection.get_engine()
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return {col['name']: col['type'] for col in columns}
    
    @staticmethod
    def drop_tables():
        """
        Drop all tables (WARNING: Data loss!)
        """
        engine = DatabaseConnection.get_engine()
        response = input("⚠️ WARNING: This will delete ALL data. Type 'yes' to confirm: ")
        if response.lower() == 'yes':
            BaseModel.metadata.drop_all(engine)
            logger.warning("🗑️ All database tables dropped")
        else:
            logger.info("Operation cancelled")

def run_migrations():
    """
    Run database migrations on startup
    """
    DatabaseConnection.initialize()
    DatabaseMigrations.create_tables()
    logger.info("Database migrations completed")
