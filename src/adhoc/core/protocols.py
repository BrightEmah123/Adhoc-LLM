from typing import Protocol, Any

class LLMProvider(Protocol):
    """
    Descr: Contract for all LLM providers
    """
    def generate(self, prompt: str) -> str:


class DatabaseConnector(Protocol):
    """
    Descr: Contract for all database connectors
    """
    def connect(self) -> None:

    def get_schema(self) -> dict[str, Any]:

    def execute(self, query: str) -> Any:

    def close(self) -> None: