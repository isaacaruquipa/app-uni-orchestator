import unittest

from backend.main import get_backend_health
from backend.sistema_ia.api import register_agent, store_context
from backend.sistema_integral.api import run_operation


class BackendModulesTestCase(unittest.TestCase):
    def test_healthcheck_contains_both_systems(self) -> None:
        response = get_backend_health()
        self.assertIn("sistema_integral", response)
        self.assertIn("sistema_ia", response)

    def test_integral_academic_enrollment(self) -> None:
        result = run_operation(
            domain="academic",
            action="create_enrollment",
            payload={"student_id": "STU-001", "program_id": "ING-SIS"},
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["status"], "enrolled")

    def test_ia_agent_registry_and_context(self) -> None:
        register_result = register_agent("agent-academic-01", "academic", "Asistente académico")
        self.assertTrue(register_result.success)
        context_result = store_context("agent-academic-01", {"intent": "enrollment"})
        self.assertTrue(context_result.success)


if __name__ == "__main__":
    unittest.main()

