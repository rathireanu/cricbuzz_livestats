import pymysql
from sqlalchemy import create_engine
import pandas as pd

# Database configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "2024"
DB_NAME = "cricbuzz_db"

def get_connection():
    """Establish and return a PyMySQL connection."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_engine():
    """Create a SQLAlchemy engine for Pandas integration."""
    connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    return create_engine(connection_string)

def run_query(query):
    """Execute SQL query and return DataFrame."""
    engine = get_engine()
    return pd.read_sql(query, engine)