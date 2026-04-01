from dataclasses import dataclass

from backend.shared.models import OperationResult


@dataclass(frozen=True)
class AuthContext:
    principal_id: str
    provider: str
    permissions: frozenset[str]


TRUSTED_OAUTH_ISSUERS: dict[str, str] = {
    "google": "https://accounts.google.com",
    "microsoft": "https://login.microsoftonline.com/common/v2.0",
}

SCOPE_TO_PERMISSION: dict[str, str] = {
    "academic.enrollments.write": "academic:enrollment:create",
    "agents.register": "ia:agent:register",
    "agents.context.write": "ia:context:write",
}

ROLE_TO_PERMISSIONS: dict[str, frozenset[str]] = {
    "admin": frozenset(SCOPE_TO_PERMISSION.values()),
    "academic_manager": frozenset({"academic:enrollment:create"}),
    "ai_operator": frozenset({"ia:agent:register", "ia:context:write"}),
}


def authenticate_oauth(provider: str, token_claims: dict) -> OperationResult:
    subject = token_claims.get("sub")
    if not subject:
        return OperationResult(success=False, error="token inválido: sub requerido")

    issuer = token_claims.get("iss", "")
    provider_lower = provider.lower()

    if provider_lower in TRUSTED_OAUTH_ISSUERS:
        trusted_issuer = TRUSTED_OAUTH_ISSUERS[provider_lower]
        if issuer != trusted_issuer:
            return OperationResult(success=False, error="token inválido: issuer no confiable")
    elif not issuer.startswith("https://"):
        return OperationResult(success=False, error="token inválido: issuer inválido")

    permissions: set[str] = set()

    for scope in token_claims.get("scope", "").split():
        permission = SCOPE_TO_PERMISSION.get(scope)
        if permission:
            permissions.add(permission)

    for role in token_claims.get("roles", []):
        permissions.update(ROLE_TO_PERMISSIONS.get(role, frozenset()))

    context = AuthContext(principal_id=subject, provider=provider_lower, permissions=frozenset(permissions))
    return OperationResult(success=True, data=context)


def authorize(auth_context: AuthContext | None, required_permission: str) -> OperationResult:
    if auth_context is None:
        return OperationResult(success=False, error="autenticación requerida")
    if required_permission not in auth_context.permissions:
        return OperationResult(success=False, error="permiso denegado")
    return OperationResult(success=True)
