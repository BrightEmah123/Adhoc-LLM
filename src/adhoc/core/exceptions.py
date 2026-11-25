class AdhocError(Exception):
    """
    Descr: Base exception for all Adhoc Analytics errors.
    """
    ...

class ConfigurationError(AdhocError):
    """
    Descr: Invalid or missing application configuration
    """
    ...

class DatabaseConnectionError(AdhocError):
    """
    Descr: Database connection failure.
    """
    ...

class MetaDataError(AdhocError):
    """
    Descr: Database metadata discovery failure
    """
    ...

class LLMProviderError(AdhocError):
    """
    Descr: LLM provider communication or generation failure
    """
    ...

class SQLGenerationError(AdhocError):
    """
    Descr: SQL generation failure
    """
    ...

class SQLValidationError(AdhocError):
    """
    Descr: Generated SQL failed validation
    """
    ...

class QueryExecutionError(AdhocError):
    """
    Descr: SQL execution failure
    """
    ...