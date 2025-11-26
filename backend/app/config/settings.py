from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = Field("RAG System")
    environment: str = Field("development")
    debug: bool = Field(False)

    database_url: str = Field(..., alias="DATABASE_URL")
    db_echo: bool = Field(False, alias="DB_ECHO")

    embedding_model_name: str = Field(..., alias="EMBEDDING_MODEL_NAME")
    embedding_dim: int = Field(..., alias="EMBEDDING_DIM")
    embedding_batch_size: int = Field(..., alias="EMBEDDING_BATCH_SIZE")
    vector_index_type: str = Field(..., alias="VECTOR_INDEX_TYPE")

    llm_endpoint: str = Field(..., alias="LLM_ENDPOINT")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    llm_timeout_seconds: int = Field(..., alias="LLM_TIMEOUT_SECONDS")

    mock_auth: bool = Field(True, alias="MOCK_AUTH")
    jwt_secret: str = Field(None, alias="JWT_SECRET")
    signing_algorithm: str = Field("HS256", alias="SIGNING_ALGORITHM")
    permissions_default: str = Field("query:read", alias="PERMISSIONS_DEFAULT")

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    enable_metrics: bool = Field(True, alias="ENABLE_METRICS")
    enable_tracing: bool = Field(False, alias="ENABLE_TRACING")

    data_path: str = Field(..., alias="DATA_PATH")
    chunk_size: int = Field(..., alias="CHUNK_SIZE")
    chunk_overlap: int = Field(..., alias="CHUNK_OVERLAP")

    orc_max_iterations: int = Field(..., alias="ORC_MAX_ITERATIONS")
    operator_timeout_seconds: int = Field(..., alias="OPERATOR_TIMEOUT_SECONDS")

    # 🔥 THIS LINE IS THE FIX 🔥
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
