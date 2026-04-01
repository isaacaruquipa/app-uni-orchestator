import hashlib
import secrets
import time
from typing import Iterable

from backend.security.config import SecurityConfig
from backend.shared.models import OperationResult


class SecurityService:
    def __init__(self, config: SecurityConfig | None = None) -> None:
        self.config = config or SecurityConfig()
        self._users: dict[str, dict] = {}
        self._tokens: dict[str, dict] = {}
        self._policies: dict[tuple[str, str], set[str]] = self._default_policies()

    def _default_policies(self) -> dict[tuple[str, str], set[str]]:
        return {
            ("sistema_integral", "academic.create_enrollment"): {"admin", "academic"},
            ("sistema_integral", "finance.create_invoice"): {"admin", "finance"},
            ("sistema_integral", "marketing.create_campaign"): {"admin", "marketing"},
            ("sistema_integral", "content.publish_event"): {"admin", "communications"},
            ("sistema_ia", "agents.register"): {"admin", "ops"},
            ("sistema_ia", "context.store"): {"admin", "ops", "llm"},
        }

    def register_user(self, username: str, password: str, roles: Iterable[str] | None = None) -> OperationResult:
        if not username or not password:
            return OperationResult(success=False, error="username y password son requeridos")
        if username in self._users:
            return OperationResult(success=False, error="usuario ya existe")
        normalized_roles = set(roles or self.config.default_roles)
        self._users[username] = {"password": self._hash_password(password), "roles": normalized_roles}
        return OperationResult(success=True, data={"username": username, "roles": sorted(normalized_roles)})

    def authenticate(self, username: str, password: str) -> OperationResult:
        user = self._users.get(username)
        if not user or user["password"] != self._hash_password(password):
            return OperationResult(success=False, error="credenciales inválidas")
        token = secrets.token_hex(16)
        expires_at = time.time() + self.config.token_ttl_seconds
        self._tokens[token] = {"username": username, "expires_at": expires_at}
        return OperationResult(
            success=True, data={"token": token, "expires_at": expires_at, "issuer": self.config.issuer}
        )

    def validate_token(self, token: str) -> OperationResult:
        record = self._tokens.get(token)
        if not record:
            return OperationResult(success=False, error="token inválido")
        if record["expires_at"] < time.time():
            return OperationResult(success=False, error="token expirado")
        username = record["username"]
        user = self._users.get(username)
        if not user:
            return OperationResult(success=False, error="usuario no encontrado")
        return OperationResult(success=True, data={"username": username, "roles": sorted(user["roles"])})

    def authorize(self, token: str, resource: str, action: str) -> OperationResult:
        validation = self.validate_token(token)
        if not validation.success:
            return validation
        roles = set(validation.data.get("roles", []))
        required_roles = self._policies.get((resource, action))
        if required_roles is None:
            return OperationResult(success=True, data={"authorized": True, "resource": resource, "action": action})
        if roles.intersection(required_roles):
            return OperationResult(
                success=True,
                data={
                    "authorized": True,
                    "resource": resource,
                    "action": action,
                    "roles": sorted(roles),
                    "matched_roles": sorted(roles.intersection(required_roles)),
                },
            )
        return OperationResult(
            success=False,
            error="acceso denegado",
            data={"authorized": False, "required_roles": sorted(required_roles), "resource": resource, "action": action},
        )

    def set_policy(self, resource: str, action: str, roles: Iterable[str]) -> OperationResult:
        normalized_roles = set(roles)
        if not normalized_roles:
            return OperationResult(success=False, error="debe especificar roles para la política")
        self._policies[(resource, action)] = normalized_roles
        return OperationResult(
            success=True,
            data={"resource": resource, "action": action, "roles": sorted(normalized_roles)},
        )

    def _hash_password(self, raw_password: str) -> str:
        digest = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
        return f"sha256:{digest}"
