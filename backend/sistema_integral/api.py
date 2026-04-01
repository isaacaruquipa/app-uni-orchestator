from backend.shared.models import OperationResult
from backend.sistema_integral.config import SistemaIntegralConfig
from backend.sistema_integral.service import IntegralSystemService
from backend.security.api import authorize_action

config = SistemaIntegralConfig()
service = IntegralSystemService()


def healthcheck() -> dict:
    return {"service": config.service_name, "status": "ok"}


def run_operation(domain: str, action: str, payload: dict) -> OperationResult:
    return service.execute(domain=domain, action=action, payload=payload)


def run_operation_secure(domain: str, action: str, payload: dict, token: str) -> OperationResult:
    decision = authorize_action(token=token, resource=config.service_name, action=f"{domain}.{action}")
    if not decision.success:
        return decision
    return service.execute(domain=domain, action=action, payload=payload)
