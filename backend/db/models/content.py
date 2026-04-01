"""Content / Publications domain models.

Models: Articulo, EventoPublicacion, Notificacion, Canal, Suscripcion  (5 models)
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
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
# Model 38 – Canal
# ---------------------------------------------------------------------------
class Canal(Base):
    __tablename__ = "canales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(32), default="web")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    notificaciones: Mapped[list["Notificacion"]] = relationship(back_populates="canal")
    suscripciones: Mapped[list["Suscripcion"]] = relationship(back_populates="canal")


# ---------------------------------------------------------------------------
# Model 39 – Articulo
# ---------------------------------------------------------------------------
class Articulo(Base):
    __tablename__ = "articulos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    resumen: Mapped[str | None] = mapped_column(Text)
    autor_id: Mapped[str | None] = mapped_column(String(36))
    estado: Mapped[str] = mapped_column(String(32), default="published")
    publicado_en: Mapped[datetime | None] = mapped_column(DateTime)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


# ---------------------------------------------------------------------------
# Model 40 – EventoPublicacion
# ---------------------------------------------------------------------------
class EventoPublicacion(Base):
    __tablename__ = "eventos_publicacion"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    lugar: Mapped[str | None] = mapped_column(String(200))
    fecha_inicio: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime)
    canal: Mapped[str] = mapped_column(String(64), default="web")
    estado: Mapped[str] = mapped_column(String(32), default="published")
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Model 41 – Notificacion
# ---------------------------------------------------------------------------
class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    canal_id: Mapped[int | None] = mapped_column(ForeignKey("canales.id"))
    destinatario_id: Mapped[str | None] = mapped_column(String(36))
    asunto: Mapped[str | None] = mapped_column(String(256))
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    enviada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    canal: Mapped["Canal | None"] = relationship(back_populates="notificaciones")


# ---------------------------------------------------------------------------
# Model 42 – Suscripcion
# ---------------------------------------------------------------------------
class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    canal_id: Mapped[int] = mapped_column(ForeignKey("canales.id"), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    suscrito_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    canal: Mapped["Canal"] = relationship(back_populates="suscripciones")
