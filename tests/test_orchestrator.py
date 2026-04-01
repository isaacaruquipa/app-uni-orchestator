import unittest

from backend.main import orchestrator
from backend.orchestrator import BackendOrchestrator


class OrchestratorTestCase(unittest.TestCase):
    def test_health_is_composed(self) -> None:
        health = orchestrator.health()
        self.assertIn("sistema_integral", health)
        self.assertIn("sistema_ia", health)
        self.assertEqual(health["sistema_ia"]["model"], "llm-gateway-v1")

    def test_routing_operations_and_agents(self) -> None:
        orchestration = BackendOrchestrator()

        enrollment = orchestration.run_integral_operation(
            domain="academic",
            action="create_enrollment",
            payload={"student_id": "STU-002", "program_id": "ING-ADM"},
        )
        self.assertTrue(enrollment.success)
        self.assertEqual(enrollment.data["status"], "enrolled")

        registration = orchestration.register_agent("agent-integral", "academic", "Registro académico")
        self.assertTrue(registration.success)

        memory = orchestration.store_agent_context("agent-integral", {"intent": "enrollment"})
        self.assertTrue(memory.success)


if __name__ == "__main__":
    unittest.main()
