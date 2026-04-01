"""Finance domain models.

Models: Factura, ItemFactura, Pago, PasarelaPago, Beca,
        SolicitudBeca, Descuento, AsientoContable, Cobranza  (9 models)
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
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
# Model 22 – Factura
# ---------------------------------------------------------------------------
class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    numero: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    estudiante_id: Mapped[str | None] = mapped_column(String(36), index=True)
    monto_total: Mapped[float] = mapped_column(Float, nullable=False)
    monto_pagado: Mapped[float] = mapped_column(Float, default=0.0)
    estado: Mapped[str] = mapped_column(String(32), default="pending_payment")
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date)
    descripcion: Mapped[str | None] = mapped_column(Text)

    items: Mapped[list["ItemFactura"]] = relationship(back_populates="factura", cascade="all, delete-orphan")
    pagos: Mapped[list["Pago"]] = relationship(back_populates="factura")


# ---------------------------------------------------------------------------
# Model 23 – ItemFactura
# ---------------------------------------------------------------------------
class ItemFactura(Base):
    __tablename__ = "items_factura"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    factura_id: Mapped[str] = mapped_column(ForeignKey("facturas.id", ondelete="CASCADE"))
    descripcion: Mapped[str] = mapped_column(String(256), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    factura: Mapped["Factura"] = relationship(back_populates="items")


# ---------------------------------------------------------------------------
# Model 24 – PasarelaPago
# ---------------------------------------------------------------------------
class PasarelaPago(Base):
    __tablename__ = "pasarelas_pago"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    proveedor: Mapped[str] = mapped_column(String(64), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    configuracion: Mapped[str | None] = mapped_column(Text)

    pagos: Mapped[list["Pago"]] = relationship(back_populates="pasarela")


# ---------------------------------------------------------------------------
# Model 25 – Pago
# ---------------------------------------------------------------------------
class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    factura_id: Mapped[str] = mapped_column(ForeignKey("facturas.id"), nullable=False)
    pasarela_id: Mapped[int | None] = mapped_column(ForeignKey("pasarelas_pago.id"))
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    moneda: Mapped[str] = mapped_column(String(8), default="PEN")
    referencia_externa: Mapped[str | None] = mapped_column(String(128))
    estado: Mapped[str] = mapped_column(String(32), default="completed")
    fecha_pago: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    factura: Mapped["Factura"] = relationship(back_populates="pagos")
    pasarela: Mapped["PasarelaPago | None"] = relationship(back_populates="pagos")


# ---------------------------------------------------------------------------
# Model 26 – Beca
# ---------------------------------------------------------------------------
class Beca(Base):
    __tablename__ = "becas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    porcentaje_descuento: Mapped[float] = mapped_column(Float, default=0.0)
    monto_fijo: Mapped[float] = mapped_column(Float, default=0.0)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)

    solicitudes: Mapped[list["SolicitudBeca"]] = relationship(back_populates="beca")


# ---------------------------------------------------------------------------
# Model 27 – SolicitudBeca
# ---------------------------------------------------------------------------
class SolicitudBeca(Base):
    __tablename__ = "solicitudes_beca"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    beca_id: Mapped[int] = mapped_column(ForeignKey("becas.id"), nullable=False)
    estudiante_id: Mapped[str] = mapped_column(String(36), nullable=False)
    estado: Mapped[str] = mapped_column(String(32), default="pending")
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    observaciones: Mapped[str | None] = mapped_column(Text)

    beca: Mapped["Beca"] = relationship(back_populates="solicitudes")


# ---------------------------------------------------------------------------
# Model 28 – Descuento
# ---------------------------------------------------------------------------
class Descuento(Base):
    __tablename__ = "descuentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    porcentaje: Mapped[float] = mapped_column(Float, default=0.0)
    monto_fijo: Mapped[float] = mapped_column(Float, default=0.0)
    valido_desde: Mapped[date | None] = mapped_column(Date)
    valido_hasta: Mapped[date | None] = mapped_column(Date)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


# ---------------------------------------------------------------------------
# Model 29 – AsientoContable
# ---------------------------------------------------------------------------
class AsientoContable(Base):
    __tablename__ = "asientos_contables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referencia: Mapped[str] = mapped_column(String(64), nullable=False)
    cuenta_debito: Mapped[str] = mapped_column(String(32), nullable=False)
    cuenta_credito: Mapped[str] = mapped_column(String(32), nullable=False)
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Model 30 – Cobranza
# ---------------------------------------------------------------------------
class Cobranza(Base):
    __tablename__ = "cobranzas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    factura_id: Mapped[str] = mapped_column(ForeignKey("facturas.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(32), default="pendiente")
    intentos: Mapped[int] = mapped_column(Integer, default=0)
    proximo_contacto: Mapped[date | None] = mapped_column(Date)
    observaciones: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
