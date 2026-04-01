import unittest

from backend.main import get_backend_health
from backend.shared.security import authenticate_oauth
from backend.sistema_ia.api import register_agent, store_context
from backend.sistema_integral.api import run_operation


class BackendModulesTestCase(unittest.TestCase):
    def test_healthcheck_contains_both_systems(self) -> None:
        response = get_backend_health()
        self.assertIn("sistema_integral", response)
        self.assertIn("sistema_ia", response)

    def test_integral_academic_enrollment(self) -> None:
        auth = authenticate_oauth(
            "google", {"sub": "user-1", "iss": "https://accounts.google.com", "roles": ["admin"]}
        )
        self.assertTrue(auth.success)
        result = run_operation(
            domain="academic",
            action="create_enrollment",
            payload={"student_id": "STU-001", "program_id": "ING-SIS"},
            auth_context=auth.data,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["status"], "enrolled")

    def test_ia_agent_registry_and_context(self) -> None:
        auth = authenticate_oauth(
            "microsoft",
            {
                "sub": "operator-1",
                "iss": "https://login.microsoftonline.com/common/v2.0",
                "scope": "agents.register agents.context.write",
            },
        )
        self.assertTrue(auth.success)
        register_result = register_agent(
            "agent-academic-01", "academic", "Asistente académico", auth_context=auth.data
        )
        self.assertTrue(register_result.success)
        context_result = store_context(
            "agent-academic-01", {"intent": "enrollment"}, auth_context=auth.data
        )
        self.assertTrue(context_result.success)

    def test_authz_denies_without_permissions(self) -> None:
        denied_auth = authenticate_oauth(
            "google", {"sub": "viewer-1", "iss": "https://accounts.google.com", "scope": ""}
        )
        self.assertTrue(denied_auth.success)
        result = run_operation(
            domain="academic",
            action="create_enrollment",
            payload={"student_id": "STU-002", "program_id": "ING-SIS"},
            auth_context=denied_auth.data,
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error, "permiso denegado")

    def test_oauth_rejects_untrusted_issuer(self) -> None:
        invalid = authenticate_oauth(
            "google", {"sub": "user-2", "iss": "https://evil.example.com", "roles": ["admin"]}
        )
        self.assertFalse(invalid.success)
        self.assertEqual(invalid.error, "token inválido: issuer no confiable")


if __name__ == "__main__":
    unittest.main()
