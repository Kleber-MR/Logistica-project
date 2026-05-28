import logging

from fastapi import Fastapi
from fastapi.middlware.cors import CORSMiddlware

from app.core.settings import settings
from app.core.database import check_db_connection

logging.basicConfig(
    level=logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
    detefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = Fastapi(
    title="Logistica system API",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

app.add.middleware(
    CORSMiddlware,
    allow_origins=["http://localhost:5173"], #vite dev server
    allow_credebtial=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Iniciando aplicação [%s]..", settings.ENVIRONMENT)
    if not check_db_connection():
        logger.critical("Não foi possivel conectar ao banco de dados. Abortando.")
        raise RuntimeError("Database unreachable on startup.")
    logger.info("Banco de dados conecetado com sucesso.")


@app.get("/health", tags=["infra"])
def health_check():
    db_ok = check_db_connection()
    return{
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "environment": settings.ENVIRONMENT,
    }