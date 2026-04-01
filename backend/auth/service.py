"""Authentication service.

Handles user creation, login (JWT issuance), token validation,
session management and audit logging using the PostgreSQL models.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.db.connection import get_session
from backend.db.models.auth import (
    RegistroAuditoria,
    SesionUsuario,
    TokenRefresco,
    Usuario,
)
from backend.db.repository import Repository
from backend.shared.models import OperationResult

_SECRET_KEY: str = os.environ.get("AUTH_SECRET_KEY", "")
if not _SECRET_KEY:
    import warnings
    _SECRET_KEY = "cambiar-en-produccion-secret-key-256bits"
    warnings.warn(
        "AUTH_SECRET_KEY no está configurado. Se usa un valor de respaldo inseguro. "
        "Defina AUTH_SECRET_KEY en producción.",
        stacklevel=2,
    )
_ALGORITHM = "HS256"
_ACCESS_TOKEN_EXPIRE_MINUTES = 60
_REFRESH_TOKEN_EXPIRE_DAYS = 30

def _utcnow() -> datetime:
    """Return the current UTC time as a naive datetime (no tzinfo)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: Session | None = None) -> None:
        self._session = session or get_session()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(
        self,
        username: str,
        email: str,
        password: str,
        nombre: str | None = None,
        apellido: str | None = None,
    ) -> OperationResult:
        if not username or not email or not password:
            return OperationResult(success=False, error="username, email y password son requeridos")

        repo: Repository[Usuario] = Repository(Usuario, self._session)

        if repo.first(username=username):
            return OperationResult(success=False, error="username ya existe")
        if repo.first(email=email):
            return OperationResult(success=False, error="email ya registrado")

        hashed = _pwd_context.hash(password)
        user = Usuario(
            username=username,
            email=email,
            hashed_password=hashed,
            nombre=nombre,
            apellido=apellido,
        )
        repo.add(user)
        self._session.commit()

        self._audit(user.id, "register", f"usuarios/{user.id}")
        return OperationResult(success=True, data={"user_id": user.id, "username": username})

    def login(
        self,
        username: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> OperationResult:
        repo: Repository[Usuario] = Repository(Usuario, self._session)
        user = repo.first(username=username)

        if not user or not _pwd_context.verify(password, user.hashed_password):
            self._security_event("login_failed", "warning", username, ip_address)
            return OperationResult(success=False, error="credenciales inválidas")

        if not user.activo:
            return OperationResult(success=False, error="cuenta desactivada")

        access_token = self._create_access_token({"sub": user.id, "username": user.username})
        refresh_raw = str(uuid.uuid4())
        refresh_hash = hashlib.sha256(refresh_raw.encode()).hexdigest()
        expire_at = _utcnow() + timedelta(days=_REFRESH_TOKEN_EXPIRE_DAYS)

        session = SesionUsuario(
            usuario_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            expirada_en=expire_at,
        )
        token = TokenRefresco(
            usuario_id=user.id,
            token_hash=refresh_hash,
            expira_en=expire_at,
        )
        self._session.add(session)
        self._session.add(token)
        self._session.commit()

        self._audit(user.id, "login", f"sesiones/{session.id}", ip_address=ip_address)
        return OperationResult(
            success=True,
            data={
                "access_token": access_token,
                "refresh_token": refresh_raw,
                "token_type": "bearer",
                "user_id": user.id,
                "username": user.username,
            },
        )

    def validate_token(self, token: str) -> OperationResult:
        try:
            payload: dict[str, Any] = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
            user_id: str | None = payload.get("sub")
            if not user_id:
                return OperationResult(success=False, error="token inválido")
            return OperationResult(success=True, data={"user_id": user_id, "payload": payload})
        except JWTError as exc:
            return OperationResult(success=False, error=f"token inválido: {exc}")

    def refresh_token(self, refresh_raw: str) -> OperationResult:
        token_hash = hashlib.sha256(refresh_raw.encode()).hexdigest()
        repo: Repository[TokenRefresco] = Repository(TokenRefresco, self._session)
        token = repo.first(token_hash=token_hash, revocado=False)
        if not token:
            return OperationResult(success=False, error="refresh token inválido o revocado")

        if token.expira_en and token.expira_en < _utcnow():
            return OperationResult(success=False, error="refresh token expirado")

        user_repo: Repository[Usuario] = Repository(Usuario, self._session)
        user = user_repo.get_by_id(token.usuario_id)
        if not user or not user.activo:
            return OperationResult(success=False, error="usuario no encontrado o inactivo")

        new_access = self._create_access_token({"sub": user.id, "username": user.username})
        return OperationResult(
            success=True,
            data={"access_token": new_access, "token_type": "bearer"},
        )

    def logout(self, user_id: str, refresh_raw: str | None = None) -> OperationResult:
        if refresh_raw:
            token_hash = hashlib.sha256(refresh_raw.encode()).hexdigest()
            repo: Repository[TokenRefresco] = Repository(TokenRefresco, self._session)
            token = repo.first(token_hash=token_hash)
            if token:
                token.revocado = True
                self._session.flush()

        session_repo: Repository[SesionUsuario] = Repository(SesionUsuario, self._session)
        for ses in session_repo.filter_by(usuario_id=user_id, activa=True):
            ses.activa = False

        self._session.commit()
        self._audit(user_id, "logout", f"usuarios/{user_id}")
        return OperationResult(success=True, data={"logged_out": True})

    def get_user(self, user_id: str) -> OperationResult:
        repo: Repository[Usuario] = Repository(Usuario, self._session)
        user = repo.get_by_id(user_id)
        if not user:
            return OperationResult(success=False, error="usuario no encontrado")
        return OperationResult(
            success=True,
            data={
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "activo": user.activo,
            },
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = _utcnow() + timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode["exp"] = expire
        return jwt.encode(to_encode, _SECRET_KEY, algorithm=_ALGORITHM)

    def _audit(
        self,
        user_id: str | None,
        accion: str,
        recurso: str | None = None,
        detalles: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        entry = RegistroAuditoria(
            usuario_id=user_id,
            accion=accion,
            recurso=recurso,
            detalles=detalles,
            ip_address=ip_address,
        )
        self._session.add(entry)
        self._session.flush()

    def _security_event(
        self,
        tipo: str,
        severidad: str,
        descripcion: str | None,
        ip_address: str | None = None,
    ) -> None:
        from backend.db.models.auth import EventoSeguridad

        event = EventoSeguridad(
            tipo=tipo,
            severidad=severidad,
            descripcion=descripcion,
            ip_address=ip_address,
        )
        self._session.add(event)
        self._session.flush()
