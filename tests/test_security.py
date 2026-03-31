import unittest
import uuid

from backend.security.api import authenticate_user, authorize_action, register_user
from backend.sistema_integral.api import run_operation_secure


class SecurityModulesTestCase(unittest.TestCase):
    def test_register_and_authenticate(self) -> None:
        username = f"user-{uuid.uuid4()}"
        register_result = register_user(username=username, password="secret123", roles=["admin"])
        self.assertTrue(register_result.success)

        auth_result = authenticate_user(username=username, password="secret123")
        self.assertTrue(auth_result.success)
        token = auth_result.data["token"]

        authorization = authorize_action(token=token, resource="sistema_ia", action="agents.register")
        self.assertTrue(authorization.success)
        self.assertTrue(authorization.data["authorized"])

    def test_denied_without_role(self) -> None:
        username = f"viewer-{uuid.uuid4()}"
        register_result = register_user(username=username, password="viewerpass", roles=["viewer"])
        self.assertTrue(register_result.success)
        auth_result = authenticate_user(username=username, password="viewerpass")
        self.assertTrue(auth_result.success)
        token = auth_result.data["token"]

        result = run_operation_secure(
            domain="finance",
            action="create_invoice",
            payload={"student_id": "STU-900", "amount": 100.0},
            token=token,
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error, "acceso denegado")

    def test_authorized_finance_operation(self) -> None:
        username = f"finance-{uuid.uuid4()}"
        register_result = register_user(username=username, password="finpass", roles=["finance"])
        self.assertTrue(register_result.success)
        auth_result = authenticate_user(username=username, password="finpass")
        self.assertTrue(auth_result.success)
        token = auth_result.data["token"]

        result = run_operation_secure(
            domain="finance",
            action="create_invoice",
            payload={"student_id": "STU-901", "amount": 120.0},
            token=token,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["status"], "pending_payment")


if __name__ == "__main__":
    unittest.main()

