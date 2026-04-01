from backend.db.connection import get_session
from backend.db.models.finance import Factura, Pago
from backend.db.repository import Repository
from backend.shared.models import OperationResult

import uuid as _uuid_mod


class FinanceModule:
    def create_invoice(self, student_id: str, amount: float) -> OperationResult:
        if not student_id:
            return OperationResult(success=False, error="student_id es requerido")
        if amount <= 0:
            return OperationResult(success=False, error="amount debe ser mayor a cero")
        session = get_session()
        try:
            repo: Repository[Factura] = Repository(Factura, session)
            numero = f"FAC-{_uuid_mod.uuid4().hex[:8].upper()}"
            factura = Factura(
                numero=numero,
                estudiante_id=student_id,
                monto_total=amount,
                estado="pending_payment",
            )
            repo.add(factura)
            session.commit()
            return OperationResult(
                success=True,
                data={
                    "student_id": student_id,
                    "invoice_id": factura.id,
                    "numero": numero,
                    "amount": amount,
                    "status": factura.estado,
                },
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

    def register_payment(self, invoice_id: str, amount: float) -> OperationResult:
        if amount <= 0:
            return OperationResult(success=False, error="amount debe ser mayor a cero")
        session = get_session()
        try:
            inv_repo: Repository[Factura] = Repository(Factura, session)
            factura = inv_repo.get_by_id(invoice_id)
            if not factura:
                return OperationResult(success=False, error="factura no encontrada")
            pay_repo: Repository[Pago] = Repository(Pago, session)
            pago = Pago(factura_id=invoice_id, monto=amount)
            pay_repo.add(pago)
            factura.monto_pagado = (factura.monto_pagado or 0.0) + amount
            if factura.monto_pagado >= factura.monto_total:
                factura.estado = "paid"
            session.commit()
            return OperationResult(
                success=True,
                data={"invoice_id": invoice_id, "payment_id": pago.id, "status": factura.estado},
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

