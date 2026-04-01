from backend.orchestrator import BackendOrchestrator


orchestrator = BackendOrchestrator()


def get_backend_health() -> dict:
    return orchestrator.health()


def run_integral_operation(domain: str, action: str, payload: dict):
    return orchestrator.run_integral_operation(domain=domain, action=action, payload=payload)


def register_orchestrated_agent(agent_id: str, domain: str, description: str):
    return orchestrator.register_agent(agent_id=agent_id, domain=domain, description=description)


def store_orchestrated_context(agent_id: str, context: dict):
    return orchestrator.store_agent_context(agent_id=agent_id, context=context)
