from functools import lru_cache

from pydantic import Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",           
    )

    # ------------------------------------------------------------------
    # Banco de dados
    # ------------------------------------------------------------------
    DATABASE_URL: PostgresDsn = Field(
        ...,
        description="Connection string do PostgreSQL. Ex: postgresql://user:pass@host:5432/db",
    )
    DB_POOL_SIZE: int = Field(10, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(20, ge=0, le=100)
    DB_POOL_TIMEOUT: int = Field(30, ge=5)       # segundos esperando conexão do pool
    DB_POOL_RECYCLE: int = Field(1800, ge=60)    # recicla conexões após 30 min
    DB_ECHO: bool = Field(False)                  # True → loga SQL no console

    # ------------------------------------------------------------------
    # JWT / Auth
    # ------------------------------------------------------------------
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = Field("HS256", pattern=r"^(HS256|HS384|HS512|RS256)$")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, ge=1, le=10080)  # máx 7 dias

    # ------------------------------------------------------------------
    # Ambiente
    # ------------------------------------------------------------------
    ENVIRONMENT: str = Field("development", pattern=r"^(development|staging|production)$")

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_not_be_example(cls, v: str) -> str:
        forbidden = {"changeme", "secret", "troque", "example", "test"}
        if any(word in v.lower() for word in forbidden):
            raise ValueError(
                "SECRET_KEY parece ser um valor de exemplo. "
                "Gere uma chave real com: openssl rand -hex 32"
            )
        return v

    @model_validator(mode="after")
    def warn_if_echo_in_production(self) -> "Settings":
        if self.ENVIRONMENT == "production" and self.DB_ECHO:
            raise ValueError("DB_ECHO=True não é permitido em produção (vaza dados sensíveis nos logs).")
        return self

    @property
    def DATABASE_URL_str(self) -> str:
        """Retorna a DATABASE_URL como string (SQLAlchemy não aceita Url do Pydantic diretamente)."""
        return str(self.DATABASE_URL)


@lru_cache
def get_settings() -> Settings:
    """
    Retorna a instância singleton das settings.
    O @lru_cache garante que o .env é lido uma única vez.

    Uso:
        from app.core.settings import settings
    """
    return Settings()


# Instância global 
settings: Settings = get_settings()