from backend.sistema_ia.config import SistemaIAConfig
from backend.sistema_ia.service import AISystemService
from backend.shared.models import OperationResult
from backend.shared.security import AuthContext, authorize

config = SistemaIAConfig()
service = AISystemService()


def healthcheck() -> dict:
    return {"service": config.service_name, "status": "ok", "model": config.default_model}


def register_agent(
    agent_id: str, domain: str, description: str, auth_context: AuthContext | None = None
) -> OperationResult:
    authz_result = authorize(auth_context=auth_context, required_permission="ia:agent:register")
    if not authz_result.success:
        return authz_result
    return service.register_agent(agent_id=agent_id, domain=domain, description=description)


def store_context(agent_id: str, context: dict, auth_context: AuthContext | None = None) -> OperationResult:
    authz_result = authorize(auth_context=auth_context, required_permission="ia:context:write")
    if not authz_result.success:
        return authz_result
    return service.store_context(agent_id=agent_id, context=context)
