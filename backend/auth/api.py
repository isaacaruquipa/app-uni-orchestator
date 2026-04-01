"""Authentication API facade.

Thin layer that wires the AuthService to a single shared session per
call.  In a real framework (FastAPI, Django, etc.) each request would
get its own session injected via dependency injection.
"""

from __future__ import annotations

from backend.auth.service import AuthService
from backend.shared.models import OperationResult


def register(
    username: str,
    email: str,
    password: str,
    nombre: str | None = None,
    apellido: str | None = None,
) -> OperationResult:
    return AuthService().register(
        username=username,
        email=email,
        password=password,
        nombre=nombre,
        apellido=apellido,
    )


def login(
    username: str,
    password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> OperationResult:
    return AuthService().login(
        username=username,
        password=password,
        ip_address=ip_address,
        user_agent=user_agent,
    )


def validate_token(token: str) -> OperationResult:
    return AuthService().validate_token(token)


def refresh_token(refresh_raw: str) -> OperationResult:
    return AuthService().refresh_token(refresh_raw)


def logout(user_id: str, refresh_raw: str | None = None) -> OperationResult:
    return AuthService().logout(user_id=user_id, refresh_raw=refresh_raw)


def get_user(user_id: str) -> OperationResult:
    return AuthService().get_user(user_id=user_id)
