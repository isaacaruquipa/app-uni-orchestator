from backend.security.config import SecurityConfig
from backend.security.service import SecurityService
from backend.shared.models import OperationResult

config = SecurityConfig()
service = SecurityService(config=config)


def healthcheck() -> dict:
    return {"service": "security", "issuer": config.issuer, "status": "ok"}


def register_user(username: str, password: str, roles: list[str] | None = None) -> OperationResult:
    return service.register_user(username=username, password=password, roles=roles)


def authenticate_user(username: str, password: str) -> OperationResult:
    return service.authenticate(username=username, password=password)


def authorize_action(token: str, resource: str, action: str) -> OperationResult:
    return service.authorize(token=token, resource=resource, action=action)


def set_policy(resource: str, action: str, roles: list[str]) -> OperationResult:
    return service.set_policy(resource=resource, action=action, roles=roles)

