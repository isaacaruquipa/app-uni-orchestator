from backend.sistema_ia.api import healthcheck as ia_healthcheck
from backend.sistema_integral.api import healthcheck as integral_healthcheck


def get_backend_health() -> dict:
    return {"sistema_integral": integral_healthcheck(), "sistema_ia": ia_healthcheck()}

