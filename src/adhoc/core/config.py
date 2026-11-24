from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Descr: Central application configuration, values can be loaded from environment variables
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "Adhoc Analytics"
    debug: bool = False

    # LLM configuration
    llm_provider: str = "ollama"
    llm_model: str = "qwen3:4b"
    llm_base_url: str = "http://localhost:11434"

    # Database configuration
    default_database: str | None = None 

    # SQL execution settings 
    query_timeout: int = 30 
    max_rows: int = 1000
    read_only: bool = True 


settings = Settings() 