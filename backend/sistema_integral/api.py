from backend.shared.models import OperationResult
from backend.shared.security import AuthContext, authorize
from backend.sistema_integral.config import SistemaIntegralConfig
from backend.sistema_integral.service import IntegralSystemService

config = SistemaIntegralConfig()
service = IntegralSystemService()


def healthcheck() -> dict:
    return {"service": config.service_name, "status": "ok"}


def run_operation(
    domain: str, action: str, payload: dict, auth_context: AuthContext | None = None
) -> OperationResult:
    access_controls = {
        ("academic", "create_enrollment"): "academic:enrollment:create",
    }
    required_permission = access_controls.get((domain, action))
    if required_permission:
        authz_result = authorize(auth_context=auth_context, required_permission=required_permission)
        if not authz_result.success:
            return authz_result
    return service.execute(domain=domain, action=action, payload=payload)
