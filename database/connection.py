"""
Database Connection & Engine Factory
Enterprise AI Business Decision Intelligence Platform
Supports PostgreSQL as Primary with SQLite Local Fallback
"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from config.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

Base = declarative_base()

def get_engine_and_db_type():
    """
    Attempts to connect to PostgreSQL first.
    If PostgreSQL is unreachable and USE_SQLITE_FALLBACK is enabled,
    seamlessly falls back to local SQLite.
    """
    pg_url = settings.DATABASE_URL
    if pg_url and not settings.USE_SQLITE_FALLBACK:
        engine = create_engine(pg_url, pool_pre_ping=True)
        return engine, "postgresql"
    
    # Try PostgreSQL first
    try:
        engine = create_engine(pg_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to primary PostgreSQL database.")
        return engine, "postgresql"
    except Exception as e:
        if settings.USE_SQLITE_FALLBACK:
            sqlite_path = settings.SQLITE_DB_PATH
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            sqlite_url = f"sqlite:///{sqlite_path.as_posix()}"
            logger.warning(
                f"PostgreSQL connection failed ({e}). Falling back to local SQLite at {sqlite_url}"
            )
            # SQLite connection with multi-threaded access enabled
            engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
            return engine, "sqlite"
        else:
            raise e

engine, DB_DIALECT = get_engine_and_db_type()
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    """FastAPI and service dependency for acquiring database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_raw_sql(sql_query: str, params: dict = None):
    """Executes validated raw SQL query and returns list of dictionaries"""
    with engine.connect() as conn:
        result = conn.execute(text(sql_query), params or {})
        if result.returns_rows:
            columns = list(result.keys())
            return [dict(zip(columns, row)) for row in result.fetchall()]
        return []
