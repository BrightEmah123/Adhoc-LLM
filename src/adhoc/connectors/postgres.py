from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine 

from adhoc.connectors.base import QueryResult 
from adhoc.core.exceptions import (
    DatabaseConnectionError,
    MetadataError,
    QueryExecutionError
)

class PostgresConnector:
    """
    Descr: PostgreSQL database connector
    """
    def __init__(
        self, 
        url: str, 
        max_rows: int = 1000, 
        read_only: bool = True 
    ):
        self.url = url
        self.max_rows = max_rows 
        self.read_only = read_only 
        self._engine: Engine | None = None
        
    @property
    def dialect(self) -> str:
        return "postgresql"
        
    def connect(self) -> None:
        """Initialize and verify the PostgreSQL connection."""
        
        if self._engine is not None:
            return 
        
        connect_args = {}
        
        if self.read_only:
            connect_args["options"] = (
                "-c default_transaction_read_only=on"
            )
            
        try:
            self._engine = create_engine(
                self.url,
                pool_pre_ping=True,
                connect_args=connect_args,
            )
            
            with self._engine.connect():
                pass 
                
        except Exception as exc:
            self.close()
            raise DatabaseConnectionError(
                f"Could not connect to PostgreSQL: {exc}"
            ) from exc 
            
    def get_schema(self) -> dict[str, Any]:
        """Discover PostgreSQL database metadata"""
        
        if self._engine is None:
            raise DatabaseConnectionError(
                "Connect to PostgreSQL before inspecting its schema."
            )
            
        try:
            inspector = inspect(self._engine)
            schemas = []
            
            for schema_name in inspector.get_schema_names():
                if schema_name.startswith("pg_") or schema_name == "information_schema":
                    continue
                    
                tables = []
                
                for table_name in inspector.get_table_names(schema=schema_name):
                    columns = inspector.get_columns(
                        table_name, 
                        schema=schema_name
                    )
                    
                    primary_key = inspector.get_pk_constraint(
                        table_name, 
                        schema=schema_name
                    )
                    
                    foreign_keys = inspector.get_foreign_keys(
                        table_name,
                        schema=schema_name
                    )
                    
                    tables.append({
                        "name": table_name,
                        "columns": [
                            {
                                "name": column["name"],
                                "type": str(column["type"]),
                                "nullable": column["nullable"],
                                "default": str(column["default"]) if column["default"] is not None else None
                            }
                            for column in columns 
                        ],
                        "primary_key": primary_key.get("constrained_columns", []),
                        "foreign_keys": foreign_keys
                    })
                    
                schemas.append({
                    "name": schema_name,
                    "tables": tables
                })
                
            return {
                "dialect": self.dialect,
                "schemas": schemas,
            }
        except Exception as exc:
            raise MetadataError(
                f"PostgreSQL schema discovery failed: {exc}"
            ) from exc
        
    def execute(
        self, 
        query: str, 
        parameters: dict[str, Any] | None = None
    ) -> QueryResult:
        """Executes SQL and return a normalized result."""
        
        if self._engine is None:
            raise DatabaseConnectionError(
                "Connect to PostgreSQL before executing query"
            )
            
        try:
            with self._engine.connect() as connection:
                result = connection.execute(
                    text(query),
                    parameters or {}
                )
                
                columns = list(result.keys())
                rows = result.mappings().fetchmany(
                    self.max_rows + 1
                )
                
                truncated = len(rows) > self.max_rows 
                rows = rows[:self.max_rows]
                
                return QueryResult(
                    columns=columns,
                    rows=[dict(row) for row in rows],
                    row_count=len(rows),
                    truncated=truncated
                )
                
        except Exception as exc:
            raise QueryExecutionError(
                f"PostgreSQL query execution failed: {exc}"
            ) from exc 
            
    def close(self) -> None:
        """Dispose of the SQLAlchemy engine."""
        
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None 
        