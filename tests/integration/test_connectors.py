import os

import pytest
from adhoc.connectors.import (
    DuckDBConnector, 
    PostgresConnector
)
from adhoc.core.exceptions import DatabaseConnectionError



def test_duckdb_connection_and_query():
    connector = DuckDBConnector(
        url="duckdb:///:memory:",
        read_only=False,
    )
    
    try:
        connector.connect()
        
        connector.execute(
            """
            CREATE TABLE customers (
                id INTEGER,
                name VARCHAR,
                revenue DOUBLE
            )
            """
        )
        
        connector.execute(
            """
            INSERT INTO customers VALUES
            (1, 'Alice', 5000),
            (2, 'Bob', 3500)
            """
        )
        
        result = connector.execute(
            "SELECT id, name, revenue FROM customers ORDER BY id"
        )
        
        assert result.columns == ["id", "name", "revenue"]
        assert result.row_count == 2
        assert result.rows[0]["name"] == "Alice"
        
    finally:
        connector.close()
        
        
def test_duckdb_schema_discovery():
    connector = DuckDBConnector(read_only=False)
    
    try:
        connector.connect()
        
        connector.execute(
            """
            CREATE TABLE products (
                id INTEGER,
                name VARCHAR
            )
            """
        )
        
        schema = connector.get_schema()
        
        assert schema["dialect"] == "duckdb"
        
        table_names = [
            table["name"]
            for schema_item in schema["schemas"]
            for table in schema_item["tables"]
        ]
        
        assert "products" in table_names
        
    finally:
        connector.close()
        
        
def test_duckdb_row_limit():
    connector = DuckDBConnector(
        max_rows=2,
        read_only=False
    )
    
    try:
        conenctor.connect()
        
        result = connector.execute(
            "SELECT * FROM range(5) AS numbers"
        )
        
        assert result.row_count == 2
        assert result.truncated is True
        
    finally:
        connector.close()

        
@pytest.mark.skipif(
    not os.getenv("TEST_POSTGRES_URL"),
    reason="TEST_POSTGRES_URL is not configured",
)
def test_postgres_connection_and_query():
    connector = PostgresConnector(
        url=os.environ["TEST_POSTGRES_URL"]
        read_only=True,
    )
    
    try:
        connector.connect()
        
        result = connector.execute(
            "SELECT 1 AS value"
        )
        
        assert result.columns == ["value"]
        assert result.rows[0]["value"] == 1
        
    finally:
        connector.close()
    
