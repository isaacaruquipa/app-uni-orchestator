"""Authentication and authorisation models.

Models: Usuario, Rol, Permiso, RolPermiso, UsuarioRol, SesionUsuario,
        TokenRefresco, RegistroAuditoria, EventoSeguridad  (9 models)
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
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Model 1 – Usuario
# ---------------------------------------------------------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    nombre: Mapped[str | None] = mapped_column(String(120))
    apellido: Mapped[str | None] = mapped_column(String(120))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    roles: Mapped[list["UsuarioRol"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    sesiones: Mapped[list["SesionUsuario"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    tokens: Mapped[list["TokenRefresco"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Model 2 – Rol
# ---------------------------------------------------------------------------
class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    usuarios: Mapped[list["UsuarioRol"]] = relationship(back_populates="rol")
    permisos: Mapped[list["RolPermiso"]] = relationship(back_populates="rol", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Model 3 – Permiso
# ---------------------------------------------------------------------------
class Permiso(Base):
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    roles: Mapped[list["RolPermiso"]] = relationship(back_populates="permiso")


# ---------------------------------------------------------------------------
# Model 4 – RolPermiso  (association)
# ---------------------------------------------------------------------------
class RolPermiso(Base):
    __tablename__ = "roles_permisos"
    __table_args__ = (UniqueConstraint("rol_id", "permiso_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    permiso_id: Mapped[int] = mapped_column(ForeignKey("permisos.id", ondelete="CASCADE"))

    rol: Mapped["Rol"] = relationship(back_populates="permisos")
    permiso: Mapped["Permiso"] = relationship(back_populates="roles")


# ---------------------------------------------------------------------------
# Model 5 – UsuarioRol  (association)
# ---------------------------------------------------------------------------
class UsuarioRol(Base):
    __tablename__ = "usuarios_roles"
    __table_args__ = (UniqueConstraint("usuario_id", "rol_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))

    usuario: Mapped["Usuario"] = relationship(back_populates="roles")
    rol: Mapped["Rol"] = relationship(back_populates="usuarios")


# ---------------------------------------------------------------------------
# Model 6 – SesionUsuario
# ---------------------------------------------------------------------------
class SesionUsuario(Base):
    __tablename__ = "sesiones_usuario"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    iniciada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expirada_en: Mapped[datetime | None] = mapped_column(DateTime)

    usuario: Mapped["Usuario"] = relationship(back_populates="sesiones")


# ---------------------------------------------------------------------------
# Model 7 – TokenRefresco
# ---------------------------------------------------------------------------
class TokenRefresco(Base):
    __tablename__ = "tokens_refresco"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    revocado: Mapped[bool] = mapped_column(Boolean, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expira_en: Mapped[datetime | None] = mapped_column(DateTime)

    usuario: Mapped["Usuario"] = relationship(back_populates="tokens")


# ---------------------------------------------------------------------------
# Model 8 – RegistroAuditoria
# ---------------------------------------------------------------------------
class RegistroAuditoria(Base):
    __tablename__ = "registros_auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[str | None] = mapped_column(String(36))
    accion: Mapped[str] = mapped_column(String(128), nullable=False)
    recurso: Mapped[str | None] = mapped_column(String(256))
    detalles: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Model 9 – EventoSeguridad
# ---------------------------------------------------------------------------
class EventoSeguridad(Base):
    __tablename__ = "eventos_seguridad"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(64), nullable=False)
    severidad: Mapped[str] = mapped_column(String(16), default="info")
    descripcion: Mapped[str | None] = mapped_column(Text)
    usuario_id: Mapped[str | None] = mapped_column(String(36))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
