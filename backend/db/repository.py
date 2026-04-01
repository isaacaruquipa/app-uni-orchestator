"""Generic repository pattern for database access.

Provides a thin CRUD wrapper around SQLAlchemy sessions so that domain
modules do not depend directly on session management details.
"""

from __future__ import annotations

from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT], session: Session) -> None:
        self._model = model
        self._session = session

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add(self, instance: ModelT) -> ModelT:
        self._session.add(instance)
        self._session.flush()
        return instance

    def delete(self, instance: ModelT) -> None:
        self._session.delete(instance)
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_by_id(self, pk: Any) -> ModelT | None:
        return self._session.get(self._model, pk)

    def get_all(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        stmt = select(self._model).limit(limit).offset(offset)
        return list(self._session.scalars(stmt))

    def filter_by(self, **kwargs: Any) -> list[ModelT]:
        stmt = select(self._model).filter_by(**kwargs)
        return list(self._session.scalars(stmt))

    def first(self, **kwargs: Any) -> ModelT | None:
        stmt = select(self._model).filter_by(**kwargs)
        return self._session.scalars(stmt).first()
