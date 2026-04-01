from backend.db.connection import get_session
from backend.db.models.marketing import Campana, Lead, Segmento
from backend.db.repository import Repository
from backend.shared.models import OperationResult


class MarketingModule:
    def create_campaign(self, campaign_name: str, segment: str) -> OperationResult:
        if not campaign_name or not segment:
            return OperationResult(success=False, error="campaign_name y segment son requeridos")
        session = get_session()
        try:
            seg_repo: Repository[Segmento] = Repository(Segmento, session)
            segmento = seg_repo.first(nombre=segment)
            if not segmento:
                segmento = Segmento(nombre=segment)
                seg_repo.add(segmento)
                session.flush()

            camp_repo: Repository[Campana] = Repository(Campana, session)
            campana = Campana(
                nombre=campaign_name,
                segmento_id=segmento.id,
                estado="scheduled",
            )
            camp_repo.add(campana)
            session.commit()
            return OperationResult(
                success=True,
                data={
                    "campaign_id": campana.id,
                    "campaign_name": campaign_name,
                    "segment": segment,
                    "status": campana.estado,
                },
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

    def create_lead(self, nombres: str, email: str, segment: str | None = None) -> OperationResult:
        if not nombres or not email:
            return OperationResult(success=False, error="nombres y email son requeridos")
        session = get_session()
        try:
            seg_id = None
            if segment:
                seg_repo: Repository[Segmento] = Repository(Segmento, session)
                seg = seg_repo.first(nombre=segment)
                if seg:
                    seg_id = seg.id

            lead_repo: Repository[Lead] = Repository(Lead, session)
            lead = Lead(nombres=nombres, email=email, segmento_id=seg_id)
            lead_repo.add(lead)
            session.commit()
            return OperationResult(
                success=True,
                data={"lead_id": lead.id, "nombres": nombres, "email": email},
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

