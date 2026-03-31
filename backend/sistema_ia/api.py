from backend.sistema_ia.config import SistemaIAConfig
from backend.sistema_ia.service import AISystemService
from backend.shared.models import OperationResult

config = SistemaIAConfig()
service = AISystemService()


def healthcheck() -> dict:
    return {"service": config.service_name, "status": "ok", "model": config.default_model}


def register_agent(agent_id: str, domain: str, description: str) -> OperationResult:
    return service.register_agent(agent_id=agent_id, domain=domain, description=description)


def store_context(agent_id: str, context: dict) -> OperationResult:
    return service.store_context(agent_id=agent_id, context=context)

