import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.settings import settings

logger = logging.getLogger(__name__)


#-------------------------------------------------------------------------------------
# Motor / engine
#-------------------------------------------------------------------------------------

engine = create_engine(
    settings.DATABASE_URL_str,
    pool_pre_ping = True,
    pool_size=settings.DB_POLL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout= settings.DB_POOL_TIMEOUT,
    pool_recycle= settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    connect_args={"connect_timeout": 10},
)


@event.listens_for(engine, "connect")
def _on_connect(dbapi_conn, _connection_record) -> None:
    logger.debug("Nova conexão aberta com o banco de dado.")


@event.listens_for(engine, "checkout")
def _on_checkout(dbapi_conn, _conecction_record, _conecction_proxy) -> None:
    logger.debug("Conexão retirada do pool.")


#-------------------------------------------------------------------------------------
# Fabrica de sessoes /  Session factory
#-------------------------------------------------------------------------------------   

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False, # evita SELECT extra após commit em contextos async-like
)

#-------------------------------------------------------------------------------------
# Base declarativa (SQLAlchemy 2.x) / Declarative basis (SQLAlchemy 2.x)
#-------------------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Base para todos os models. Use como: classe Meumodel(Base): ..."""


#-------------------------------------------------------------------------------------
#  Dependência FastAPI  →  get_db / FastAPI dependency → get_db
#-------------------------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Dependência injetável via Depends(get_db).
 
    Garante:
    - rollback automático em qualquer exceção não tratada
    - fechamento da sessão mesmo em caso de erro
    - log de erros inesperados sem suprimir a exceção original
 
    Uso:
        @router.get("/exemplo")
        def minha_rota(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Erro inesperado na sessão do banco — rollback executado.")
        raise
    finally:
        db.close()
 
 
# ---------------------------------------------------------------------------
# Context manager para uso fora do ciclo de requisição (scripts, tasks, etc.)
# ---------------------------------------------------------------------------
 
@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager para uso fora do FastAPI (scripts, workers, testes).
 
    Uso:
        with get_db_context() as db:
            db.add(obj)
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
 
 
# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
 
def check_db_connection() -> bool:
    """
    Verifica se o banco está acessível. Use em /health ou no startup.
    Retorna True se OK, False se não conseguir conectar.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Falha no health check do banco de dados.")
        return False
 