from dataclasses import dataclass


@dataclass(frozen=True)
class SistemaIntegralConfig:
    service_name: str = "sistema_integral"
    api_prefix: str = "/api/v1"

