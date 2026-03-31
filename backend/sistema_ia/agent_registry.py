from backend.shared.models import OperationResult


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, dict] = {}

    def register(self, agent_id: str, domain: str, description: str) -> OperationResult:
        if not agent_id or not domain:
            return OperationResult(success=False, error="agent_id y domain son requeridos")
        self._agents[agent_id] = {"domain": domain, "description": description}
        return OperationResult(success=True, data={"agent_id": agent_id, "registered": True})

    def get(self, agent_id: str) -> OperationResult:
        agent = self._agents.get(agent_id)
        if not agent:
            return OperationResult(success=False, error="agent no encontrado")
        return OperationResult(success=True, data={"agent_id": agent_id, **agent})

