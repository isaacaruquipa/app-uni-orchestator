from backend.shared.models import OperationResult
from backend.sistema_ia.agent_registry import AgentRegistry
from backend.sistema_ia.context_memory import ContextMemory


class AISystemService:
    def __init__(self) -> None:
        self.registry = AgentRegistry()
        self.memory = ContextMemory()

    def register_agent(self, agent_id: str, domain: str, description: str) -> OperationResult:
        return self.registry.register(agent_id=agent_id, domain=domain, description=description)

    def store_context(self, agent_id: str, context: dict) -> OperationResult:
        return self.memory.add(agent_id=agent_id, context=context)

    def resolve_agent(self, agent_id: str) -> OperationResult:
        return self.registry.get(agent_id=agent_id)

