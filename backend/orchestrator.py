from typing import NotRequired, TypedDict

from backend.sistema_ia.config import SistemaIAConfig
from backend.sistema_ia.service import AISystemService
from backend.sistema_integral.config import SistemaIntegralConfig
from backend.sistema_integral.service import IntegralSystemService
from backend.shared.models import OperationResult


class HealthResponse(TypedDict):
    service: str
    status: str
    model: NotRequired[str]


class BackendOrchestrator:
    def __init__(
        self,
        integral_service: IntegralSystemService | None = None,
        ia_service: AISystemService | None = None,
        integral_config: SistemaIntegralConfig | None = None,
        ia_config: SistemaIAConfig | None = None,
    ) -> None:
        self.integral_service = integral_service or IntegralSystemService()
        self.ia_service = ia_service or AISystemService()
        self.integral_config = integral_config or SistemaIntegralConfig()
        self.ia_config = ia_config or SistemaIAConfig()

    def health(self) -> dict[str, HealthResponse]:
        return {
            self.integral_config.service_name: {
                "service": self.integral_config.service_name,
                "status": "ok",
            },
            self.ia_config.service_name: {
                "service": self.ia_config.service_name,
                "status": "ok",
                "model": self.ia_config.default_model,
            },
        }

    def run_integral_operation(self, domain: str, action: str, payload: dict) -> OperationResult:
        return self.integral_service.execute(domain=domain, action=action, payload=payload)

    def register_agent(self, agent_id: str, domain: str, description: str) -> OperationResult:
        return self.ia_service.register_agent(agent_id=agent_id, domain=domain, description=description)

    def store_agent_context(self, agent_id: str, context: dict) -> OperationResult:
        return self.ia_service.store_context(agent_id=agent_id, context=context)
