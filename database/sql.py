import pyodbc
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


def get_engine(database: str | None = None):
    """
    Create Azure MSSQL connection using SQLAlchemy.
    
    Args:
        database: Database name. Defaults to MSSQL_DATABASE from .env.
    """
    if database is None:
        database = os.getenv("MSSQL_DATABASE")
    
    host = os.getenv("MSSQL_HOST") # e.g., your-server.database.windows.net
    port = os.getenv("MSSQL_PORT", "1433")
    user = os.getenv("MSSQL_USER")
    password = os.getenv("MSSQL_PASSWORD")
    driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")

    # quote_plus is generally safer for ODBC connection strings in SQLAlchemy
    encoded_user = quote_plus(user)
    encoded_password = quote_plus(password)
    encoded_driver = quote_plus(driver)

    # Azure requires Encrypt=yes
    connection_string = (
        f"mssql+pyodbc://{encoded_user}:{encoded_password}@{host}:{port}/{database}"
        f"?driver={encoded_driver}&Encrypt=yes&TrustServerCertificate=no"
    )

    return create_engine(connection_string)


def create_database() -> None:
    """
    Create the target database if it does not exist.
    
    Uses pyodbc directly with autocommit to bypass SQLAlchemy transaction wrapping,
    connecting to the 'master' database as required by SQL Server.
    """
    target_db = os.getenv("MSSQL_DATABASE")
    host = os.getenv("MSSQL_HOST")
    port = os.getenv("MSSQL_PORT", "1433")
    user = os.getenv("MSSQL_USER")
    password = os.getenv("MSSQL_PASSWORD")
    driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
    
    # Build raw pyodbc connection string connecting directly to 'master'
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={host},{port};"
        f"DATABASE=master;"
        f"UID={user};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    
    try:
        # Connect with autocommit enabled to allow CREATE DATABASE execution
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        try:
            # Check if database exists in sys.databases
            cursor.execute(
                "SELECT 1 FROM sys.databases WHERE name = ?",
                (target_db,)
            )
            
            if not cursor.fetchone():
                print(f"Database '{target_db}' does not exist. Creating...")
                # CREATE DATABASE cannot take parameters, safely bracket the identifier
                cursor.execute(f"CREATE DATABASE [{target_db}]")
                print(f"Database '{target_db}' created successfully.")
            else:
                print(f"Database '{target_db}' already exists.")
        finally:
            cursor.close()
            conn.close()
    except Exception as exc:
        print(f"Failed to create database: {exc}")
        raise


