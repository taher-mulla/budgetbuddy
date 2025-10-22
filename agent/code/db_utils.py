"""
Database Utility Module

Handles all PostgreSQL database operations with connection pooling.
"""

import psycopg2
from psycopg2 import pool
import json
import os
from typing import Optional, Dict, List
from datetime import datetime
from contextlib import contextmanager
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database connection configuration"""
    host: str = Field(..., description="Database host")
    port: int = Field(default=5432, description="Database port")
    database: str = Field(..., description="Database name")
    user: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    min_conn: int = Field(default=1, description="Minimum connections in pool")
    max_conn: int = Field(default=5, description="Maximum connections in pool")
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "budgetbuddy"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD")
        )


class DatabaseManager:
    """
    Database connection manager with pooling
    
    Uses connection pooling for better performance in Lambda.
    """
    
    _pool: Optional[pool.SimpleConnectionPool] = None
    _config: Optional[DatabaseConfig] = None
    
    @classmethod
    def initialize(cls, config: DatabaseConfig):
        """Initialize connection pool"""
        cls._config = config
        cls._pool = pool.SimpleConnectionPool(
            config.min_conn,
            config.max_conn,
            host=config.host,
            port=config.port,
            database=config.database,
            user=config.user,
            password=config.password
        )
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Get database connection from pool
        
        Usage:
            with DatabaseManager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM expenses")
        """
        if cls._pool is None:
            cls.initialize(DatabaseConfig.from_env())
        
        conn = cls._pool.getconn()
        try:
            yield conn
        finally:
            cls._pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        """Close all connections in pool"""
        if cls._pool:
            cls._pool.closeall()


class Expense(BaseModel):
    """Expense model"""
    id: Optional[int] = None
    amount: float
    category: str
    note: Optional[str] = None
    date_added: Optional[datetime] = None


class SessionState(BaseModel):
    """Session state model"""
    user_id: str
    state_json: Dict
    last_updated: Optional[datetime] = None


def insert_expense(amount: float, category: str, note: Optional[str] = None) -> int:
    """
    Insert expense into database
    
    Args:
        amount: Expense amount
        category: Expense category
        note: Optional note
        
    Returns:
        ID of inserted expense
    """
    with DatabaseManager.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO expenses (amount, category, note, date_added)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (amount, category, note, datetime.now())
            )
            expense_id = cur.fetchone()[0]
            conn.commit()
            return expense_id


def get_session_state(user_id: str) -> Dict:
    """
    Retrieve user session state
    
    Args:
        user_id: User identifier
        
    Returns:
        Session state dictionary
    """
    with DatabaseManager.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT state_json FROM sessions WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            
            if row:
                return row[0] if isinstance(row[0], dict) else json.loads(row[0])
            
            # Return empty state if not found
            return {"history": [], "context": {}}


def save_session_state(user_id: str, state: Dict):
    """
    Save user session state
    
    Args:
        user_id: User identifier
        state: Session state to save
    """
    with DatabaseManager.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sessions (user_id, state_json, last_updated)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    state_json = EXCLUDED.state_json,
                    last_updated = EXCLUDED.last_updated
                """,
                (user_id, json.dumps(state), datetime.now())
            )
            conn.commit()


def get_recent_expenses(user_id: str, limit: int = 10) -> List[Expense]:
    """
    Get recent expenses (for future features)
    
    Args:
        user_id: User identifier (unused in MVP)
        limit: Number of expenses to retrieve
        
    Returns:
        List of Expense objects
    """
    with DatabaseManager.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, amount, category, note, date_added
                FROM expenses
                ORDER BY date_added DESC
                LIMIT %s
                """,
                (limit,)
            )
            rows = cur.fetchall()
            
            return [
                Expense(
                    id=row[0],
                    amount=float(row[1]),
                    category=row[2],
                    note=row[3],
                    date_added=row[4]
                )
                for row in rows
            ]
