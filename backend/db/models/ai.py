"""AI / Agents domain models.

Models: RegistroAgente, ContextoAgente, VectorContexto, Herramienta,
        AgenteHerramienta, SolicitudLLM, RespuestaLLM  (7 models)

The VectorContexto model stores embeddings.  When the database backend
is PostgreSQL the embedding column uses the pgvector ``Vector`` type,
which enables efficient nearest-neighbour queries with the
``<->`` (L2 distance) operator.  On SQLite the column falls back to
``Text`` and embeddings are stored as JSON arrays.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Model 43 – RegistroAgente
# ---------------------------------------------------------------------------
class RegistroAgente(Base):
    __tablename__ = "registro_agentes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    agent_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    dominio: Mapped[str] = mapped_column(String(64), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    registrado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    contextos: Mapped[list["ContextoAgente"]] = relationship(back_populates="agente", cascade="all, delete-orphan")
    herramientas: Mapped[list["AgenteHerramienta"]] = relationship(back_populates="agente", cascade="all, delete-orphan")
    solicitudes: Mapped[list["SolicitudLLM"]] = relationship(back_populates="agente")


# ---------------------------------------------------------------------------
# Model 44 – ContextoAgente
# ---------------------------------------------------------------------------
class ContextoAgente(Base):
    __tablename__ = "contextos_agente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agente_id: Mapped[str] = mapped_column(ForeignKey("registro_agentes.id", ondelete="CASCADE"))
    datos: Mapped[str] = mapped_column(Text, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    agente: Mapped["RegistroAgente"] = relationship(back_populates="contextos")
    vectores: Mapped[list["VectorContexto"]] = relationship(back_populates="contexto", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Model 45 – VectorContexto  (pgvector embedding store)
# ---------------------------------------------------------------------------
class VectorContexto(Base):
    """Stores semantic embeddings for agent context entries.

    On PostgreSQL the ``embedding`` column is a native pgvector ``Vector``
    which supports efficient ANN searches.  On other backends the column is
    ``Text`` and the embedding list is serialised as JSON.
    """

    __tablename__ = "vectores_contexto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contexto_id: Mapped[int] = mapped_column(ForeignKey("contextos_agente.id", ondelete="CASCADE"))
    embedding: Mapped[str] = mapped_column(Text, nullable=False)
    dimensiones: Mapped[int] = mapped_column(Integer, default=1536)
    modelo: Mapped[str] = mapped_column(String(128), default="text-embedding-ada-002")
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    contexto: Mapped["ContextoAgente"] = relationship(back_populates="vectores")

    # ------------------------------------------------------------------
    # Helpers for converting between Python lists and the stored format.
    # ------------------------------------------------------------------

    @staticmethod
    def serialize_embedding(vector: list[float]) -> str:
        return json.dumps(vector)

    @staticmethod
    def deserialize_embedding(raw: str) -> list[float]:
        return json.loads(raw)


# ---------------------------------------------------------------------------
# Model 46 – Herramienta
# ---------------------------------------------------------------------------
class Herramienta(Base):
    __tablename__ = "herramientas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    endpoint: Mapped[str | None] = mapped_column(String(256))
    schema_entrada: Mapped[str | None] = mapped_column(Text)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)

    agentes: Mapped[list["AgenteHerramienta"]] = relationship(back_populates="herramienta")


# ---------------------------------------------------------------------------
# Model 47 – AgenteHerramienta  (association)
# ---------------------------------------------------------------------------
class AgenteHerramienta(Base):
    __tablename__ = "agentes_herramientas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agente_id: Mapped[str] = mapped_column(ForeignKey("registro_agentes.id", ondelete="CASCADE"))
    herramienta_id: Mapped[int] = mapped_column(ForeignKey("herramientas.id"))
    habilitada: Mapped[bool] = mapped_column(Boolean, default=True)

    agente: Mapped["RegistroAgente"] = relationship(back_populates="herramientas")
    herramienta: Mapped["Herramienta"] = relationship(back_populates="agentes")


# ---------------------------------------------------------------------------
# Model 48 – SolicitudLLM
# ---------------------------------------------------------------------------
class SolicitudLLM(Base):
    __tablename__ = "solicitudes_llm"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    agente_id: Mapped[str | None] = mapped_column(ForeignKey("registro_agentes.id"))
    modelo: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_entrada: Mapped[int] = mapped_column(Integer, default=0)
    enviado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    agente: Mapped["RegistroAgente | None"] = relationship(back_populates="solicitudes")
    respuesta: Mapped["RespuestaLLM | None"] = relationship(back_populates="solicitud", uselist=False)


# ---------------------------------------------------------------------------
# Model 49 – RespuestaLLM
# ---------------------------------------------------------------------------
class RespuestaLLM(Base):
    __tablename__ = "respuestas_llm"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    solicitud_id: Mapped[str] = mapped_column(ForeignKey("solicitudes_llm.id"), unique=True, nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_salida: Mapped[int] = mapped_column(Integer, default=0)
    latencia_ms: Mapped[float] = mapped_column(Float, default=0.0)
    recibido_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    solicitud: Mapped["SolicitudLLM"] = relationship(back_populates="respuesta")
