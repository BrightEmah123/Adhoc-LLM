from typing import Protocol, Any

class LLMProvider(Protocol):
    """
    Descr: Contract for all LLM providers
    """
    def generate(self, prompt: str) -> str:
        ...