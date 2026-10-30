from sqlalchemy import text

# Import from your MSSQL connection file
from database.sql import get_engine


def get_metrics():
    engine = get_engine()

    # The standard SQL window function works exactly the same in MSSQL
    query = """
    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY company, year
                   ORDER BY created_at DESC
               ) AS rn
        FROM financial_metrics
    ) t
    WHERE rn = 1
    ORDER BY company
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = [dict(row._mapping) for row in result]

    return rows