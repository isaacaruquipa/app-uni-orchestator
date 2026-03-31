from dataclasses import dataclass


@dataclass(frozen=True)
class SistemaIAConfig:
    service_name: str = "sistema_ia"
    default_model: str = "llm-gateway-v1"

