"""Marketing domain models.

Models: Campana, MetricaCampana, Segmento, Lead,
        JornadaMarketing, PasoJornada, PlantillaEmail  (7 models)
"""

from __future__ import annotations

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
# Model 31 – Segmento
# ---------------------------------------------------------------------------
class Segmento(Base):
    __tablename__ = "segmentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    criterios: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    campanas: Mapped[list["Campana"]] = relationship(back_populates="segmento")
    leads: Mapped[list["Lead"]] = relationship(back_populates="segmento")


# ---------------------------------------------------------------------------
# Model 32 – Campana
# ---------------------------------------------------------------------------
class Campana(Base):
    __tablename__ = "campanas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(32), default="email")
    estado: Mapped[str] = mapped_column(String(32), default="scheduled")
    segmento_id: Mapped[int | None] = mapped_column(ForeignKey("segmentos.id"))
    fecha_inicio: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime)
    presupuesto: Mapped[float] = mapped_column(Float, default=0.0)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    segmento: Mapped["Segmento | None"] = relationship(back_populates="campanas")
    metricas: Mapped[list["MetricaCampana"]] = relationship(back_populates="campana", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Model 33 – MetricaCampana
# ---------------------------------------------------------------------------
class MetricaCampana(Base):
    __tablename__ = "metricas_campana"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campana_id: Mapped[str] = mapped_column(ForeignKey("campanas.id", ondelete="CASCADE"))
    enviados: Mapped[int] = mapped_column(Integer, default=0)
    abiertos: Mapped[int] = mapped_column(Integer, default=0)
    clics: Mapped[int] = mapped_column(Integer, default=0)
    conversiones: Mapped[int] = mapped_column(Integer, default=0)
    tasa_apertura: Mapped[float] = mapped_column(Float, default=0.0)
    tasa_clic: Mapped[float] = mapped_column(Float, default=0.0)
    registrado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    campana: Mapped["Campana"] = relationship(back_populates="metricas")


# ---------------------------------------------------------------------------
# Model 34 – Lead
# ---------------------------------------------------------------------------
class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    nombres: Mapped[str] = mapped_column(String(120), nullable=False)
    apellidos: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    telefono: Mapped[str | None] = mapped_column(String(20))
    segmento_id: Mapped[int | None] = mapped_column(ForeignKey("segmentos.id"))
    estado: Mapped[str] = mapped_column(String(32), default="nuevo")
    fuente: Mapped[str | None] = mapped_column(String(64))
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    segmento: Mapped["Segmento | None"] = relationship(back_populates="leads")


# ---------------------------------------------------------------------------
# Model 35 – JornadaMarketing
# ---------------------------------------------------------------------------
class JornadaMarketing(Base):
    __tablename__ = "jornadas_marketing"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    pasos: Mapped[list["PasoJornada"]] = relationship(back_populates="jornada", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Model 36 – PasoJornada
# ---------------------------------------------------------------------------
class PasoJornada(Base):
    __tablename__ = "pasos_jornada"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jornada_id: Mapped[str] = mapped_column(ForeignKey("jornadas_marketing.id", ondelete="CASCADE"))
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_accion: Mapped[str] = mapped_column(String(64), nullable=False)
    configuracion: Mapped[str | None] = mapped_column(Text)
    delay_horas: Mapped[int] = mapped_column(Integer, default=0)

    jornada: Mapped["JornadaMarketing"] = relationship(back_populates="pasos")


# ---------------------------------------------------------------------------
# Model 37 – PlantillaEmail
# ---------------------------------------------------------------------------
class PlantillaEmail(Base):
    __tablename__ = "plantillas_email"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    asunto: Mapped[str] = mapped_column(String(256), nullable=False)
    cuerpo_html: Mapped[str] = mapped_column(Text, nullable=False)
    cuerpo_texto: Mapped[str | None] = mapped_column(Text)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
