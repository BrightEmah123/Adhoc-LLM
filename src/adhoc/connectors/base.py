from dataclasses import dataclass 
from typing import Any, Protocol

@dataclass
class QueryResult:
    """
    Descr: Standardized result returned by every database connector
    """
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int 
    
class DatabaseConnector(Protocol):
    """
    Descr: Contract that all database connectors must implement
           
           Implementations can use different database drivers, but must expose the same interface 
    """
    
    @property
    def dialect(self) -> str:
        """Return the SQL dialect used by the database"""

    def connect(self) -> None:
        """Establish or initialize the database connection"""
        
    def get_schema(self) -> dict[str, Any]:
        """Discover the database schema"""
        
    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None
    ) -> QueryResult:
        """Execute SQL and return a standardized result."""
        
    def close(self) -> None:
        """Release database resources."""
    