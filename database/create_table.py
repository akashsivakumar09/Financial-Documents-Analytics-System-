from sqlalchemy import text
from database.sql import get_engine, create_database


def create_tables() -> None:
    engine = get_engine()

    # T-SQL uses a different approach for IF NOT EXISTS and data types
    query = """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'financial_metrics')
    BEGIN
        CREATE TABLE financial_metrics (
            id INT IDENTITY(1,1) PRIMARY KEY,
            company NVARCHAR(100),
            year NVARCHAR(10),
            revenue NVARCHAR(MAX),
            net_income NVARCHAR(MAX),
            operating_income NVARCHAR(MAX),
            cash_flow NVARCHAR(MAX),
            total_assets NVARCHAR(MAX),
            total_liabilities NVARCHAR(MAX),
            risk_factors NVARCHAR(MAX),
            growth_drivers NVARCHAR(MAX),
            created_at DATETIME2 DEFAULT CURRENT_TIMESTAMP
        );
    END
    """

    with engine.begin() as connection:
        connection.execute(text(query))

    print("financial_metrics table created.")


if __name__ == "__main__":
    create_database()
    create_tables()