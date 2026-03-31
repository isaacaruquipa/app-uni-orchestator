from backend.shared.models import OperationResult


class FinanceModule:
    def create_invoice(self, student_id: str, amount: float) -> OperationResult:
        if not student_id:
            return OperationResult(success=False, error="student_id es requerido")
        if amount <= 0:
            return OperationResult(success=False, error="amount debe ser mayor a cero")
        return OperationResult(
            success=True,
            data={"student_id": student_id, "amount": amount, "status": "pending_payment"},
        )

