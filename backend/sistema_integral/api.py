from backend.shared.models import OperationResult
from backend.sistema_integral.config import SistemaIntegralConfig
from backend.sistema_integral.service import IntegralSystemService

config = SistemaIntegralConfig()
service = IntegralSystemService()


def healthcheck() -> dict:
    return {"service": config.service_name, "status": "ok"}


def run_operation(domain: str, action: str, payload: dict) -> OperationResult:
    return service.execute(domain=domain, action=action, payload=payload)

