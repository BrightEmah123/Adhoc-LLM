from threading import RLock

from adhoc.connectors.base import DatabaseConnector
from adhoc.core.exceptions import (
    ConfigurationError,
    DatabaseConnectionError,
 )

class ConnectorRegistry:
    """
    Descr: Manage named database connector instances.
    """
    
    def __init__(self):
        self._connectors: dict[str, DatabaseConnector] = {}
        self._lock = RLock()
        
    def register(self, name: str, connector: DatabaseConnector, connect: bool = True) -> None:
        """Register a named database connector"""
        
        with self._lock:
            if name in self._connectors:
                raise ConfigurationError(
                    f"Connection '{name}' is already registered."
                )
                
            if connect:
                connector.connect()
                
            self._connectors[name] = connector
            
    def get(self, name: str) -> DatabaseConnector:
        """Retrieve a registered connector"""
        
        with self._lock:
            connector = self._connectors.get(name)
            
            if connector is None:
                raise DatabaseConnectionError(
                    f"Connection '{name}' was not found."
                )
                
            return connector
            
    def list_connection(self) -> list[str]:
        """List registered connection names."""
        
        with self._lock:
            return list(self._connectors.keys())
            
    def remove(self, name: str) -> None:
        """Remove and close a registered connector."""
        
        with self._lock:
            connector = self._connectors.pop(name, None)
            
            if connector is None:
                raise DatabaseConnectionError(
                    f"Connection '{name}' was not found. "
                )
                
            connector.close()
            
    def close_all(self) -> None:
        """Close every registered connector."""
        
        with self._lock:
            for connector in self._connectors.values():
                connector.close()
                
            self._connectors.clear()
        
 
