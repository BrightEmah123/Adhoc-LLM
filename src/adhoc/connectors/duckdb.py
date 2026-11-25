from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine 

from adhoc.connectors.base import QueryResult 
from adhoc.core.exceptions import (
    DatabaseConnectionError,
    MetadataError,
    QueryExecutionError
)

class DuckDBConnector:
    """
    Descr: DuckDB database connector
    """
    def __init__(
        self,
        url: str = "duckdb://:memory:",
        max_rows: int = 1000,
        read_only: bool = False,
    ):
        self.url = url
        self.max_rows = max_rows
        self.read_only = read_only 
        self._engine: Engine | None = None

    @property
    def dialect(self) -> str:
        return "duckdb"
        
    def connect(self) -> None:
        """Initialize and verify the DuckDB connection"""
        
        if self._engine is not None:
            return 
            
        connect_args = {}
        
        # DuckDB's in-memory database cannot be opened read-only
        if self.read_only and ":memory:" not in self.url:
            connect_args["read_only"] = True
            
        try:
            self._engine = create_engine(
                self.url,
                connect_args=connect_args 
            )
            
            with self._engine.connect():
                pass
                
        except Exception as exc:
            self.close()
            raise DatabaseConnectionError(
                f"Could not connect to DuckDB: {exc}"
            ) from exc 
            
    def get_schema(self) -> dict[str, Any]:
        """Discover DuckDB database metadata"""
        
        if self._engine is None:
            raise DatabaseConnectionError(
                "Connect to DuckDB before inspecting its schema. "
            )
            
        try:
            inspector = inspect(self._engine)
            schemas = []
            
            for schema_name in inspector.get_schema_names():
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
                                "default": str(column["default"] if column["default"] is not None else None
                            }
                            for column in columns
                        ],
                        "primary_key": primary_key.get(
                            "constained_columns", []
                        ),
                        "foreign_keys": foreign_keys,
                    })
                    
                schemas.append({
                    "name": schema_name,
                    "tables": tables,
                })
                
            return {
                "dialect": self.dialect,
                "schemas": schemas,
            }
            
        except Exception as exc:
            raise MetadataError(
                f"DuckDB schema discovery failed: {exc}"
            ) from exc 
            
            
    def execute(self, query: str, paraeters: dict[str, Any] | None = None) -> QueryResult:
        """Execute SQL and return a normalized result"""
        
        if self._engine is None:
            raise DatabaseConnectionError(
                "Connect to DuckDB before executing queries
            )
            
        try:
            with self._engine.connect() as connection:
                result = connection.execute(
                    text(query),
                    parameters or {},
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
                    truncated=truncated,
                )
        
        except Exception as exc:
            raise QueryExecutionError(
                f"DuckDB query execution failed: {exc}"
            ) from exc
            
            
    def close(self) -> None:
        """Closes the transaction"""
        
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None