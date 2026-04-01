"""Vector store backed by PostgreSQL + pgvector.

When the database is PostgreSQL and the ``pgvector`` extension is
installed, this module uses the native ``<->`` L2-distance operator
for nearest-neighbour search.  On other backends (e.g. SQLite used
in tests) it falls back to an in-process cosine-similarity search
over JSON-encoded embeddings.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.db.connection import get_session
from backend.db.models.ai import ContextoAgente, RegistroAgente, VectorContexto


class VectorStore:
    """Thin wrapper around the ``vectores_contexto`` table."""

    def __init__(self, session: Session | None = None) -> None:
        self._session = session or get_session()
        self._is_postgres = "postgresql" in os.environ.get("DATABASE_URL", "")

    # ------------------------------------------------------------------
    # Store an embedding for an agent context entry.
    # ------------------------------------------------------------------

    def store(
        self,
        contexto_id: int,
        embedding: list[float],
        modelo: str = "text-embedding-ada-002",
    ) -> VectorContexto:
        vec = VectorContexto(
            contexto_id=contexto_id,
            embedding=VectorContexto.serialize_embedding(embedding),
            dimensiones=len(embedding),
            modelo=modelo,
        )
        self._session.add(vec)
        self._session.flush()
        return vec

    # ------------------------------------------------------------------
    # Nearest-neighbour search
    # ------------------------------------------------------------------

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        agent_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return the *top_k* most similar context vectors.

        On PostgreSQL (with pgvector) the query uses the ``<->``
        operator directly in SQL for efficiency.  On other databases
        it fetches all rows and computes cosine similarity in Python.
        """
        if self._is_postgres:
            return self._pg_search(query_embedding, top_k, agent_id)
        return self._fallback_search(query_embedding, top_k, agent_id)

    # ------------------------------------------------------------------
    # PostgreSQL / pgvector path
    # ------------------------------------------------------------------

    def _pg_search(
        self,
        query_embedding: list[float],
        top_k: int,
        agent_id: str | None,
    ) -> list[dict[str, Any]]:
        """Use pgvector's ``<->`` operator via a parameterised ORM query."""
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        stmt = (
            select(
                VectorContexto.id,
                VectorContexto.contexto_id,
                VectorContexto.embedding,
            )
            .order_by(
                text("embedding::vector <-> :emb::vector")
            )
            .limit(top_k)
            .params(emb=embedding_str)
        )

        if agent_id:
            stmt = (
                stmt
                .join(ContextoAgente, ContextoAgente.id == VectorContexto.contexto_id)
                .join(RegistroAgente, RegistroAgente.id == ContextoAgente.agente_id)
                .where(RegistroAgente.agent_id == agent_id)
            )

        rows = self._session.execute(stmt).mappings().all()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Fallback in-process cosine similarity (SQLite / tests)
    # ------------------------------------------------------------------

    def _fallback_search(
        self,
        query_embedding: list[float],
        top_k: int,
        agent_id: str | None,
    ) -> list[dict[str, Any]]:
        stmt = select(VectorContexto)
        if agent_id:
            stmt = (
                stmt
                .join(ContextoAgente, ContextoAgente.id == VectorContexto.contexto_id)
                .join(RegistroAgente, RegistroAgente.id == ContextoAgente.agente_id)
                .where(RegistroAgente.agent_id == agent_id)
            )

        rows = list(self._session.scalars(stmt))
        scored: list[tuple[float, VectorContexto]] = []
        for row in rows:
            vec = VectorContexto.deserialize_embedding(row.embedding)
            sim = _cosine_similarity(query_embedding, vec)
            scored.append((sim, row))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": r.id,
                "contexto_id": r.contexto_id,
                "embedding": r.embedding,
                "similitud": sim,
            }
            for sim, r in scored[:top_k]
        ]

    def commit(self) -> None:
        self._session.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

