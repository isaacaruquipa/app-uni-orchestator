from backend.shared.models import OperationResult


class ContentModule:
    def publish_event(self, title: str, channel: str) -> OperationResult:
        if not title or not channel:
            return OperationResult(success=False, error="title y channel son requeridos")
        return OperationResult(
            success=True,
            data={"title": title, "channel": channel, "status": "published"},
        )

