from backend.shared.models import OperationResult


class MarketingModule:
    def create_campaign(self, campaign_name: str, segment: str) -> OperationResult:
        if not campaign_name or not segment:
            return OperationResult(success=False, error="campaign_name y segment son requeridos")
        return OperationResult(
            success=True,
            data={"campaign_name": campaign_name, "segment": segment, "status": "scheduled"},
        )

