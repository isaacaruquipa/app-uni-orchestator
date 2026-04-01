from backend.db.connection import get_session
from backend.db.models.ai import ContextoAgente, RegistroAgente
from backend.db.repository import Repository
from backend.db.vector_store import VectorStore
from backend.shared.models import OperationResult

import json


class ContextMemory:
    def __init__(self) -> None:
        self._memory: dict[str, list[dict]] = {}

    def add(self, agent_id: str, context: dict) -> OperationResult:
        if not agent_id:
            return OperationResult(success=False, error="agent_id es requerido")
        session = get_session()
        try:
            # Resolve DB record for agent
            agent_repo: Repository[RegistroAgente] = Repository(RegistroAgente, session)
            agente = agent_repo.first(agent_id=agent_id)
            if agente:
                ctx_repo: Repository[ContextoAgente] = Repository(ContextoAgente, session)
                ctx = ContextoAgente(
                    agente_id=agente.id,
                    datos=json.dumps(context, ensure_ascii=False),
                )
                ctx_repo.add(ctx)
                session.commit()

            # keep in-memory cache regardless
            self._memory.setdefault(agent_id, []).append(context)
            return OperationResult(
                success=True,
                data={"agent_id": agent_id, "items": len(self._memory[agent_id])},
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

    def add_with_embedding(
        self, agent_id: str, context: dict, embedding: list[float]
    ) -> OperationResult:
        result = self.add(agent_id=agent_id, context=context)
        if not result.success:
            return result
        session = get_session()
        try:
            agent_repo: Repository[RegistroAgente] = Repository(RegistroAgente, session)
            agente = agent_repo.first(agent_id=agent_id)
            if not agente:
                return result

            ctx_repo: Repository[ContextoAgente] = Repository(ContextoAgente, session)
            # get most recent context entry for this agent
            entries = ctx_repo.filter_by(agente_id=agente.id)
            if not entries:
                return result
            latest = entries[-1]

            vs = VectorStore(session)
            vs.store(contexto_id=latest.id, embedding=embedding)
            session.commit()
            return OperationResult(
                success=True,
                data={"agent_id": agent_id, "embedding_stored": True},
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

    def get(self, agent_id: str) -> OperationResult:
        return OperationResult(
            success=True,
            data={"agent_id": agent_id, "history": self._memory.get(agent_id, [])},
        )

