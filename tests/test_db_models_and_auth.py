"""Comprehensive tests for the database layer, models, and auth module.

Uses an in-process SQLite database so no external PostgreSQL instance
is required.  The DATABASE_URL environment variable is forced to the
SQLite in-memory URL before any modules that import the engine are
loaded.
"""

import os
import unittest

# Must be set BEFORE importing any backend module that touches the engine.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from backend.db.connection import init_db, reset_db, get_session
from backend.db.repository import Repository
from backend.db.vector_store import VectorStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_session():
    """Return a brand-new session after resetting the schema."""
    reset_db()
    return get_session()


# ===========================================================================
# Test: database initialisation
# ===========================================================================
class TestDBInit(unittest.TestCase):
    def test_init_db_creates_tables(self):
        reset_db()
        from sqlalchemy import inspect
        from backend.db.connection import get_engine
        inspector = inspect(get_engine())
        tables = inspector.get_table_names()
        # spot-check some expected tables
        expected = [
            "usuarios", "roles", "permisos", "sesiones_usuario", "tokens_refresco",
            "registro_agentes", "contextos_agente", "vectores_contexto",
            "facturas", "pagos", "matriculas", "estudiantes", "campanas",
            "articulos", "notificaciones",
        ]
        for t in expected:
            self.assertIn(t, tables, f"tabla '{t}' no encontrada")


# ===========================================================================
# Test: model count (≥ 40)
# ===========================================================================
class TestModelCount(unittest.TestCase):
    def test_at_least_40_models(self):
        import backend.db.models.auth as m_auth
        import backend.db.models.academic as m_acad
        import backend.db.models.finance as m_fin
        import backend.db.models.marketing as m_mkt
        import backend.db.models.content as m_cnt
        import backend.db.models.ai as m_ai

        from backend.db.base import Base
        count = len(Base.metadata.tables)
        self.assertGreaterEqual(count, 40, f"Se esperaban ≥40 tablas, hay {count}")


# ===========================================================================
# Test: Auth models via Repository
# ===========================================================================
class TestAuthModels(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_usuario_crud(self):
        from backend.db.models.auth import Usuario
        session = get_session()
        repo: Repository[Usuario] = Repository(Usuario, session)
        user = Usuario(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed",
        )
        repo.add(user)
        session.commit()
        fetched = repo.get_by_id(user.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.username, "testuser")

    def test_rol_and_permiso(self):
        from backend.db.models.auth import Rol, Permiso, RolPermiso
        session = get_session()
        rol = Rol(nombre="admin", descripcion="Administrador")
        permiso = Permiso(codigo="users:write", descripcion="Escribir usuarios")
        session.add(rol)
        session.add(permiso)
        session.flush()
        rp = RolPermiso(rol_id=rol.id, permiso_id=permiso.id)
        session.add(rp)
        session.commit()
        self.assertEqual(rp.rol_id, rol.id)

    def test_sesion_and_token(self):
        from backend.db.models.auth import Usuario, SesionUsuario, TokenRefresco
        session = get_session()
        user = Usuario(username="u2", email="u2@x.com", hashed_password="x")
        session.add(user)
        session.flush()
        ses = SesionUsuario(usuario_id=user.id, ip_address="127.0.0.1")
        tok = TokenRefresco(usuario_id=user.id, token_hash="abc123")
        session.add(ses)
        session.add(tok)
        session.commit()
        self.assertTrue(ses.activa)

    def test_auditoria_and_seguridad(self):
        from backend.db.models.auth import RegistroAuditoria, EventoSeguridad
        session = get_session()
        audit = RegistroAuditoria(accion="login", recurso="/auth/login")
        event = EventoSeguridad(tipo="login_failed", severidad="warning")
        session.add(audit)
        session.add(event)
        session.commit()
        self.assertIsNotNone(audit.id)
        self.assertIsNotNone(event.id)


# ===========================================================================
# Test: Academic models
# ===========================================================================
class TestAcademicModels(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_departamento_and_programa(self):
        from backend.db.models.academic import Departamento, ProgramaAcademico
        session = get_session()
        depto = Departamento(nombre="Ingeniería", codigo="ING")
        session.add(depto)
        session.flush()
        prog = ProgramaAcademico(codigo="ING-SIS", nombre="Ing. de Sistemas", departamento_id=depto.id)
        session.add(prog)
        session.commit()
        self.assertEqual(prog.nivel, "pregrado")

    def test_estudiante_matricula(self):
        from backend.db.models.academic import Estudiante, Matricula
        session = get_session()
        est = Estudiante(codigo="E001", nombres="Ana", apellidos="López", email="ana@uni.edu")
        session.add(est)
        session.flush()
        mat = Matricula(estudiante_id=est.id, estado="enrolled")
        session.add(mat)
        session.commit()
        self.assertEqual(mat.estado, "enrolled")

    def test_docente_and_seccion(self):
        from backend.db.models.academic import Docente, Curso, SeccionCurso
        session = get_session()
        doc = Docente(codigo="D001", nombres="Carlos", apellidos="Ríos", email="carlos@uni.edu")
        curso = Curso(codigo="CS101", nombre="Programación I")
        session.add(doc)
        session.add(curso)
        session.flush()
        sec = SeccionCurso(curso_id=curso.id, docente_id=doc.id, semestre="2024-1", anio=2024)
        session.add(sec)
        session.commit()
        self.assertIsNotNone(sec.id)

    def test_calificacion_asistencia_historial(self):
        from backend.db.models.academic import (
            Estudiante, Curso, SeccionCurso, Calificacion, Asistencia, HistorialAcademico
        )
        import datetime
        session = get_session()
        est = Estudiante(codigo="E002", nombres="Luis", apellidos="Pérez", email="luis@uni.edu")
        curso = Curso(codigo="CS102", nombre="Estructuras de Datos")
        session.add(est)
        session.add(curso)
        session.flush()
        sec = SeccionCurso(curso_id=curso.id, semestre="2024-1", anio=2024)
        session.add(sec)
        session.flush()
        cal = Calificacion(estudiante_id=est.id, seccion_id=sec.id, nota=18.5)
        asis = Asistencia(
            estudiante_id=est.id, seccion_id=sec.id,
            fecha=datetime.date.today(), presente=True
        )
        hist = HistorialAcademico(estudiante_id=est.id, promedio_ponderado=16.0, creditos_aprobados=30)
        session.add_all([cal, asis, hist])
        session.commit()
        self.assertEqual(cal.nota, 18.5)

    def test_calendario_and_horario(self):
        from backend.db.models.academic import CalendarioAcademico, Curso, SeccionCurso, HorarioCurso
        import datetime
        session = get_session()
        cal = CalendarioAcademico(
            anio=2024, semestre="2024-1",
            fecha_inicio=datetime.date(2024, 3, 1),
            fecha_fin=datetime.date(2024, 7, 31),
        )
        session.add(cal)
        curso = Curso(codigo="MAT101", nombre="Cálculo I")
        session.add(curso)
        session.flush()
        sec = SeccionCurso(curso_id=curso.id, semestre="2024-1", anio=2024)
        session.add(sec)
        session.flush()
        horario = HorarioCurso(seccion_id=sec.id, dia_semana="Lunes", hora_inicio="08:00", hora_fin="10:00")
        session.add(horario)
        session.commit()
        self.assertIsNotNone(horario.id)


# ===========================================================================
# Test: Finance models
# ===========================================================================
class TestFinanceModels(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_factura_item_pago(self):
        from backend.db.models.finance import Factura, ItemFactura, Pago
        session = get_session()
        fac = Factura(numero="FAC-0001", estudiante_id="E001", monto_total=1500.0)
        session.add(fac)
        session.flush()
        item = ItemFactura(factura_id=fac.id, descripcion="Matrícula", cantidad=1, precio_unitario=1500.0, subtotal=1500.0)
        session.add(item)
        pago = Pago(factura_id=fac.id, monto=1500.0)
        session.add(pago)
        session.commit()
        self.assertEqual(fac.estado, "pending_payment")

    def test_beca_solicitud(self):
        from backend.db.models.finance import Beca, SolicitudBeca
        session = get_session()
        beca = Beca(nombre="Beca Excelencia", porcentaje_descuento=50.0)
        session.add(beca)
        session.flush()
        sol = SolicitudBeca(beca_id=beca.id, estudiante_id="E002")
        session.add(sol)
        session.commit()
        self.assertEqual(sol.estado, "pending")

    def test_descuento_asiento_cobranza(self):
        from backend.db.models.finance import Descuento, AsientoContable, Cobranza, Factura
        session = get_session()
        desc = Descuento(codigo="DESC10", porcentaje=10.0)
        asiento = AsientoContable(referencia="REF-001", cuenta_debito="1101", cuenta_credito="4101", monto=500.0)
        fac = Factura(numero="FAC-0002", monto_total=500.0)
        session.add_all([desc, asiento, fac])
        session.flush()
        cob = Cobranza(factura_id=fac.id)
        session.add(cob)
        session.commit()
        self.assertIsNotNone(cob.id)


# ===========================================================================
# Test: Marketing models
# ===========================================================================
class TestMarketingModels(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_campana_segmento_metrica(self):
        from backend.db.models.marketing import Segmento, Campana, MetricaCampana
        session = get_session()
        seg = Segmento(nombre="Nuevos Ingresos")
        session.add(seg)
        session.flush()
        camp = Campana(nombre="Bienvenida 2024", segmento_id=seg.id)
        session.add(camp)
        session.flush()
        metrica = MetricaCampana(campana_id=camp.id, enviados=1000, abiertos=450)
        session.add(metrica)
        session.commit()
        self.assertEqual(metrica.enviados, 1000)

    def test_lead_jornada_paso_plantilla(self):
        from backend.db.models.marketing import Lead, JornadaMarketing, PasoJornada, PlantillaEmail
        session = get_session()
        lead = Lead(nombres="María García", email="maria@example.com")
        jornada = JornadaMarketing(nombre="Onboarding")
        session.add(lead)
        session.add(jornada)
        session.flush()
        paso = PasoJornada(jornada_id=jornada.id, orden=1, tipo_accion="send_email")
        tmpl = PlantillaEmail(nombre="Bienvenida", asunto="¡Bienvenido!", cuerpo_html="<p>Hola</p>")
        session.add(paso)
        session.add(tmpl)
        session.commit()
        self.assertEqual(paso.orden, 1)


# ===========================================================================
# Test: Content models
# ===========================================================================
class TestContentModels(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_canal_articulo_evento_notif_suscripcion(self):
        from backend.db.models.content import Canal, Articulo, EventoPublicacion, Notificacion, Suscripcion
        session = get_session()
        canal = Canal(nombre="web", tipo="web")
        session.add(canal)
        session.flush()
        art = Articulo(titulo="Noticia 1", slug="noticia-1", contenido="Contenido de la noticia.")
        evento = EventoPublicacion(titulo="Feria Universitaria", canal="web")
        notif = Notificacion(canal_id=canal.id, cuerpo="Nuevo evento disponible")
        sus = Suscripcion(usuario_id="U001", canal_id=canal.id)
        session.add_all([art, evento, notif, sus])
        session.commit()
        self.assertFalse(notif.leida)
        self.assertTrue(sus.activa)


# ===========================================================================
# Test: AI models
# ===========================================================================
class TestAIModels(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_registro_agente_contexto(self):
        from backend.db.models.ai import RegistroAgente, ContextoAgente
        session = get_session()
        agente = RegistroAgente(agent_id="agent-001", dominio="academic", descripcion="Asistente académico")
        session.add(agente)
        session.flush()
        ctx = ContextoAgente(agente_id=agente.id, datos='{"intent":"enrollment"}')
        session.add(ctx)
        session.commit()
        self.assertTrue(agente.activo)

    def test_herramienta_agente_herramienta(self):
        from backend.db.models.ai import RegistroAgente, Herramienta, AgenteHerramienta
        session = get_session()
        agente = RegistroAgente(agent_id="agent-002", dominio="finance")
        herr = Herramienta(nombre="consulta_facturas", endpoint="/finance/invoices")
        session.add(agente)
        session.add(herr)
        session.flush()
        ah = AgenteHerramienta(agente_id=agente.id, herramienta_id=herr.id)
        session.add(ah)
        session.commit()
        self.assertTrue(ah.habilitada)

    def test_solicitud_respuesta_llm(self):
        from backend.db.models.ai import RegistroAgente, SolicitudLLM, RespuestaLLM
        session = get_session()
        agente = RegistroAgente(agent_id="agent-003", dominio="ia")
        session.add(agente)
        session.flush()
        sol = SolicitudLLM(agente_id=agente.id, modelo="gpt-4", prompt="¿Cuántos créditos necesito?")
        session.add(sol)
        session.flush()
        resp = RespuestaLLM(solicitud_id=sol.id, contenido="Necesitas 200 créditos.", tokens_salida=12)
        session.add(resp)
        session.commit()
        self.assertEqual(resp.tokens_salida, 12)


# ===========================================================================
# Test: Vector store
# ===========================================================================
class TestVectorStore(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_store_and_search_embedding(self):
        from backend.db.models.ai import RegistroAgente, ContextoAgente
        session = get_session()
        agente = RegistroAgente(agent_id="agent-vec", dominio="ia")
        session.add(agente)
        session.flush()
        ctx = ContextoAgente(agente_id=agente.id, datos='{"text":"hello"}')
        session.add(ctx)
        session.flush()

        vs = VectorStore(session)
        embedding = [0.1, 0.2, 0.3, 0.4]
        vec = vs.store(contexto_id=ctx.id, embedding=embedding)
        session.commit()
        self.assertEqual(vec.dimensiones, 4)

        # Search should return the stored vector
        results = vs.search(query_embedding=[0.1, 0.2, 0.3, 0.4], top_k=5)
        self.assertEqual(len(results), 1)
        self.assertIn("similitud", results[0])
        self.assertAlmostEqual(results[0]["similitud"], 1.0, places=5)

    def test_embedding_serialise_roundtrip(self):
        from backend.db.models.ai import VectorContexto
        emb = [0.5, -0.3, 0.8]
        serialised = VectorContexto.serialize_embedding(emb)
        recovered = VectorContexto.deserialize_embedding(serialised)
        self.assertEqual(recovered, emb)


# ===========================================================================
# Test: AuthService
# ===========================================================================
class TestAuthService(unittest.TestCase):
    def setUp(self):
        reset_db()

    def _service(self):
        from backend.auth.service import AuthService
        return AuthService(session=get_session())

    def test_register_and_login(self):
        svc = self._service()
        reg = svc.register("alice", "alice@uni.edu", "secret123")
        self.assertTrue(reg.success)
        self.assertIn("user_id", reg.data)

        login = svc.login("alice", "secret123", ip_address="127.0.0.1")
        self.assertTrue(login.success)
        self.assertIn("access_token", login.data)
        self.assertIn("refresh_token", login.data)

    def test_login_wrong_password(self):
        svc = self._service()
        svc.register("bob", "bob@uni.edu", "password")
        result = svc.login("bob", "wrongpassword")
        self.assertFalse(result.success)

    def test_validate_token(self):
        svc = self._service()
        svc.register("carol", "carol@uni.edu", "mypass")
        login = svc.login("carol", "mypass")
        token = login.data["access_token"]
        val = svc.validate_token(token)
        self.assertTrue(val.success)
        self.assertIn("user_id", val.data)

    def test_invalid_token_rejected(self):
        svc = self._service()
        val = svc.validate_token("not.a.valid.token")
        self.assertFalse(val.success)

    def test_refresh_token(self):
        svc = self._service()
        svc.register("dave", "dave@uni.edu", "pass")
        login = svc.login("dave", "pass")
        refresh_raw = login.data["refresh_token"]
        result = svc.refresh_token(refresh_raw)
        self.assertTrue(result.success)
        self.assertIn("access_token", result.data)

    def test_logout(self):
        svc = self._service()
        svc.register("eve", "eve@uni.edu", "pass")
        login = svc.login("eve", "pass")
        user_id = login.data["user_id"]
        refresh_raw = login.data["refresh_token"]
        out = svc.logout(user_id=user_id, refresh_raw=refresh_raw)
        self.assertTrue(out.success)

    def test_duplicate_username_rejected(self):
        svc = self._service()
        svc.register("frank", "frank@uni.edu", "pass")
        dup = svc.register("frank", "frank2@uni.edu", "pass")
        self.assertFalse(dup.success)

    def test_get_user(self):
        svc = self._service()
        reg = svc.register("grace", "grace@uni.edu", "pass")
        uid = reg.data["user_id"]
        result = svc.get_user(uid)
        self.assertTrue(result.success)
        self.assertEqual(result.data["username"], "grace")


# ===========================================================================
# Test: Domain modules using DB (integration)
# ===========================================================================
class TestDomainModulesWithDB(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_academic_create_enrollment(self):
        from backend.sistema_integral.domains.academico import AcademicModule
        mod = AcademicModule()
        result = mod.create_enrollment("STU-001", "ING-SIS")
        self.assertTrue(result.success)
        self.assertIn("enrollment_id", result.data)

    def test_academic_invalid_enrollment(self):
        from backend.sistema_integral.domains.academico import AcademicModule
        result = AcademicModule().create_enrollment("", "")
        self.assertFalse(result.success)

    def test_finance_create_invoice(self):
        from backend.sistema_integral.domains.finanzas import FinanceModule
        result = FinanceModule().create_invoice("STU-001", 1500.0)
        self.assertTrue(result.success)
        self.assertIn("invoice_id", result.data)

    def test_finance_invalid_invoice(self):
        from backend.sistema_integral.domains.finanzas import FinanceModule
        result = FinanceModule().create_invoice("STU-001", -100.0)
        self.assertFalse(result.success)

    def test_marketing_create_campaign(self):
        from backend.sistema_integral.domains.marketing import MarketingModule
        result = MarketingModule().create_campaign("Campaña Verano", "Estudiantes Nuevos")
        self.assertTrue(result.success)
        self.assertIn("campaign_id", result.data)

    def test_content_publish_event(self):
        from backend.sistema_integral.domains.publicaciones import ContentModule
        result = ContentModule().publish_event("Feria de Ciencias", "web")
        self.assertTrue(result.success)
        self.assertIn("event_id", result.data)

    def test_content_publish_article(self):
        from backend.sistema_integral.domains.publicaciones import ContentModule
        result = ContentModule().publish_article("Nuevo Curso de IA", "Aprende IA desde cero.")
        self.assertTrue(result.success)
        self.assertIn("article_id", result.data)

    def test_ia_agent_register_and_context(self):
        from backend.sistema_ia.api import register_agent, store_context
        reg = register_agent("agent-ia-01", "academic", "Asistente académico")
        self.assertTrue(reg.success)
        ctx = store_context("agent-ia-01", {"intent": "enrollment"})
        self.assertTrue(ctx.success)


# ===========================================================================
# Test: Repository generic CRUD
# ===========================================================================
class TestRepository(unittest.TestCase):
    def setUp(self):
        reset_db()

    def test_add_get_delete(self):
        from backend.db.models.marketing import PlantillaEmail
        session = get_session()
        repo: Repository[PlantillaEmail] = Repository(PlantillaEmail, session)
        tmpl = PlantillaEmail(nombre="Test", asunto="Asunto", cuerpo_html="<p>Hola</p>")
        repo.add(tmpl)
        session.commit()
        fetched = repo.get_by_id(tmpl.id)
        self.assertIsNotNone(fetched)
        repo.delete(fetched)
        session.commit()
        self.assertIsNone(repo.get_by_id(tmpl.id))

    def test_filter_by(self):
        from backend.db.models.content import Canal
        session = get_session()
        session.add(Canal(nombre="email", tipo="email"))
        session.add(Canal(nombre="sms", tipo="sms"))
        session.commit()
        repo: Repository[Canal] = Repository(Canal, session)
        results = repo.filter_by(tipo="email")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].nombre, "email")


if __name__ == "__main__":
    unittest.main()
