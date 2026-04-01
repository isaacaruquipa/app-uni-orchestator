from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityConfig:
    issuer: str = "app-uni-orchestrator"
    token_ttl_seconds: int = 3600
    default_roles: tuple[str, ...] = ("viewer",)

