from backend.shared.models import OperationResult


class AcademicModule:
    def create_enrollment(self, student_id: str, program_id: str) -> OperationResult:
        if not student_id or not program_id:
            return OperationResult(success=False, error="student_id y program_id son requeridos")
        return OperationResult(
            success=True,
            data={"student_id": student_id, "program_id": program_id, "status": "enrolled"},
        )

