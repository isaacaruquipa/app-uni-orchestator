from backend.shared.models import OperationResult


class ContextMemory:
    def __init__(self) -> None:
        self._memory: dict[str, list[dict]] = {}

    def add(self, agent_id: str, context: dict) -> OperationResult:
        if not agent_id:
            return OperationResult(success=False, error="agent_id es requerido")
        self._memory.setdefault(agent_id, []).append(context)
        return OperationResult(success=True, data={"agent_id": agent_id, "items": len(self._memory[agent_id])})

    def get(self, agent_id: str) -> OperationResult:
        return OperationResult(success=True, data={"agent_id": agent_id, "history": self._memory.get(agent_id, [])})

