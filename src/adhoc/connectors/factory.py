from typing import Any

from adhoc.connectors.base import DatabaseConnector
from adhoc.connectors.duckdb import DuckDBConnector
from adhoc.connectors.postgres import PostgresConnector
from adhoc.core.exceptions import ConfigurationError

CONNECTORS = {
    "postgres": PostgresConnector,
    "postgresql": PostgresConnector,
    "duckdb": DuckDBConnector
}


def create_connector(database_type: str, url:str, **kwargs: Any) -> DatabaseConnector:
    """Create a dtabase connector based on its type"""
    
    connector_class = CONNECTORS.get(database_type.lower())
    
    if connector_class is None:
        supported = ", ".join(sorted(CONNECTORS.keys()))
        
        raise ConfigurationError(
            f"Unsupported database type: {databse_type}. "
            f"Supported types: {supported}"
        )
        
    return connector_class(url=url, **kwargs)
