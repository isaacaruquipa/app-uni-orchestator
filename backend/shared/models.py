from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OperationResult:
    success: bool
    data: Any = None
    error: str | None = None

