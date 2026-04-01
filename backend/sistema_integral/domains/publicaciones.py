from backend.db.connection import get_session
from backend.db.models.content import Articulo, Canal, EventoPublicacion, Notificacion
from backend.db.repository import Repository
from backend.shared.models import OperationResult

import re as _re


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = _re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = _re.sub(r"[\s]+", "-", slug)
    return slug[:290]


class ContentModule:
    def publish_event(self, title: str, channel: str) -> OperationResult:
        if not title or not channel:
            return OperationResult(success=False, error="title y channel son requeridos")
        session = get_session()
        try:
            repo: Repository[EventoPublicacion] = Repository(EventoPublicacion, session)
            evento = EventoPublicacion(titulo=title, canal=channel, estado="published")
            repo.add(evento)
            session.commit()
            return OperationResult(
                success=True,
                data={"event_id": evento.id, "title": title, "channel": channel, "status": evento.estado},
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

    def publish_article(self, title: str, content: str, author_id: str | None = None) -> OperationResult:
        if not title or not content:
            return OperationResult(success=False, error="title y content son requeridos")
        session = get_session()
        try:
            repo: Repository[Articulo] = Repository(Articulo, session)
            slug = _slugify(title)
            articulo = Articulo(
                titulo=title,
                slug=slug,
                contenido=content,
                autor_id=author_id,
                estado="published",
            )
            repo.add(articulo)
            session.commit()
            return OperationResult(
                success=True,
                data={"article_id": articulo.id, "title": title, "slug": slug, "status": articulo.estado},
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

    def send_notification(self, body: str, recipient_id: str | None = None, channel_name: str = "web") -> OperationResult:
        if not body:
            return OperationResult(success=False, error="body es requerido")
        session = get_session()
        try:
            canal_repo: Repository[Canal] = Repository(Canal, session)
            canal = canal_repo.first(nombre=channel_name)
            canal_id = canal.id if canal else None

            notif_repo: Repository[Notificacion] = Repository(Notificacion, session)
            notif = Notificacion(cuerpo=body, destinatario_id=recipient_id, canal_id=canal_id)
            notif_repo.add(notif)
            session.commit()
            return OperationResult(
                success=True,
                data={"notification_id": notif.id, "channel": channel_name},
            )
        except Exception as exc:
            session.rollback()
            return OperationResult(success=False, error=str(exc))
        finally:
            session.close()

