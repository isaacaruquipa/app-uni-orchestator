from backend.db.connection import get_session
from backend.db.models.academic import (
    CalendarioAcademico,
    Calificacion,
    Matricula,
)
from backend.db.repository import Repository
from backend.shared.models import OperationResult


class AcademicModule:
    def create_enrollment(self, student_id: str, program_id: str) -> OperationResult:
        if not student_id or not program_id:
            return OperationResult(success=False, error="student_id y program_id son requeridos")
        session = get_session()
        try:
            repo: Repository[Matricula] = Repository(Matricula, session)
            matricula = Matricula(
                estudiante_id=student_id,
                programa_id=program_id,
                estado="enrolled",
            )
            repo.add(matricula)
            session.commit()
            return OperationResult(
                success=True,
                data={
                    "student_id": student_id,
                    "program_id": program_id,
                    "enrollment_id": matricula.id,
                    "status": matricula.estado,
                },
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

    def get_enrollment(self, enrollment_id: str) -> OperationResult:
        session = get_session()
        try:
            repo: Repository[Matricula] = Repository(Matricula, session)
            matricula = repo.get_by_id(enrollment_id)
            if not matricula:
                return OperationResult(success=False, error="matrícula no encontrada")
            return OperationResult(
                success=True,
                data={
                    "enrollment_id": matricula.id,
                    "student_id": matricula.estudiante_id,
                    "program_id": matricula.programa_id,
                    "status": matricula.estado,
                },
            )
        finally:
            session.close()

    def add_grade(
        self,
        student_id: str,
        seccion_id: str,
        nota: float,
        tipo: str = "parcial",
    ) -> OperationResult:
        if nota < 0:
            return OperationResult(success=False, error="nota no puede ser negativa")
        session = get_session()
        try:
            repo: Repository[Calificacion] = Repository(Calificacion, session)
            cal = Calificacion(
                estudiante_id=student_id,
                seccion_id=seccion_id,
                nota=nota,
                tipo_evaluacion=tipo,
            )
            repo.add(cal)
            session.commit()
            return OperationResult(
                success=True,
                data={"student_id": student_id, "nota": nota, "tipo": tipo},
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

