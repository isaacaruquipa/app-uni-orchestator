from backend.db.connection import get_session
from backend.db.models.ai import ContextoAgente, RegistroAgente
from backend.db.repository import Repository
from backend.shared.models import OperationResult

import json


class AgentRegistry:
    def __init__(self) -> None:
        # In-memory fallback kept for backward compatibility when DB is
        # not yet initialised in the same process call.
        self._agents: dict[str, dict] = {}

    def register(self, agent_id: str, domain: str, description: str) -> OperationResult:
        if not agent_id or not domain:
            return OperationResult(success=False, error="agent_id y domain son requeridos")
        session = get_session()
        try:
            repo: Repository[RegistroAgente] = Repository(RegistroAgente, session)
            existing = repo.first(agent_id=agent_id)
            if existing:
                existing.dominio = domain
                existing.descripcion = description
                session.flush()
            else:
                agente = RegistroAgente(
                    agent_id=agent_id,
                    dominio=domain,
                    descripcion=description,
                )
                repo.add(agente)
            session.commit()
            # keep in-memory cache in sync
            self._agents[agent_id] = {"domain": domain, "description": description}
            return OperationResult(success=True, data={"agent_id": agent_id, "registered": True})
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

    def get(self, agent_id: str) -> OperationResult:
        session = get_session()
        try:
            repo: Repository[RegistroAgente] = Repository(RegistroAgente, session)
            agente = repo.first(agent_id=agent_id)
            if not agente:
                # fall back to in-memory
                cached = self._agents.get(agent_id)
                if cached:
                    return OperationResult(success=True, data={"agent_id": agent_id, **cached})
                return OperationResult(success=False, error="agent no encontrado")
            return OperationResult(
                success=True,
                data={
                    "agent_id": agente.agent_id,
                    "domain": agente.dominio,
                    "description": agente.descripcion,
                },
            )
        finally:
            session.close()

