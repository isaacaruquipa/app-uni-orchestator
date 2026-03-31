from backend.sistema_integral.domains.academico import AcademicModule
from backend.sistema_integral.domains.finanzas import FinanceModule
from backend.sistema_integral.domains.marketing import MarketingModule
from backend.sistema_integral.domains.publicaciones import ContentModule
from backend.shared.models import OperationResult


class IntegralSystemService:
    def __init__(self) -> None:
        self.academic = AcademicModule()
        self.finance = FinanceModule()
        self.marketing = MarketingModule()
        self.content = ContentModule()

    def execute(self, domain: str, action: str, payload: dict) -> OperationResult:
        handlers = {
            ("academic", "create_enrollment"): lambda: self.academic.create_enrollment(
                payload.get("student_id", ""), payload.get("program_id", "")
            ),
            ("finance", "create_invoice"): lambda: self.finance.create_invoice(
                payload.get("student_id", ""), float(payload.get("amount", 0))
            ),
            ("marketing", "create_campaign"): lambda: self.marketing.create_campaign(
                payload.get("campaign_name", ""), payload.get("segment", "")
            ),
            ("content", "publish_event"): lambda: self.content.publish_event(
                payload.get("title", ""), payload.get("channel", "")
            ),
        }
        handler = handlers.get((domain, action))
        if not handler:
            return OperationResult(success=False, error="domain/action no soportado")
        return handler()

