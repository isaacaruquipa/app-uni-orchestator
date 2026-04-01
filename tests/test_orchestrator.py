import unittest

from backend.main import orchestrator
from backend.orchestrator import BackendOrchestrator
from backend.sistema_ia.config import SistemaIAConfig
from backend.sistema_integral.config import SistemaIntegralConfig


class OrchestratorTestCase(unittest.TestCase):
    def test_health_is_composed(self) -> None:
        health = orchestrator.health()
        integral_name = SistemaIntegralConfig().service_name
        ia_name = SistemaIAConfig().service_name

        self.assertIn(integral_name, health)
        self.assertIn(ia_name, health)
        self.assertEqual(health[ia_name]["model"], SistemaIAConfig().default_model)

    def test_routing_operations_and_agents(self) -> None:
        orchestration = BackendOrchestrator()

        enrollment = orchestration.run_integral_operation(
            domain="academic",
            action="create_enrollment",
            payload={"student_id": "STU-002", "program_id": "ING-ADM"},
        )
        self.assertTrue(enrollment.success)
        self.assertEqual(enrollment.data["status"], "enrolled")

        registration = orchestration.register_agent("agent-integral", "academic", "Registro academico")
        self.assertTrue(registration.success)

        memory = orchestration.store_agent_context("agent-integral", {"intent": "enrollment"})
        self.assertTrue(memory.success)


if __name__ == "__main__":
    unittest.main()
