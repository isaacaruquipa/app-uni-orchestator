# Arquitectura de Orquestador de Agentes Universitarios

## Visión general
Plataforma orquestadora para miles de agentes impulsados por LLM que colaboran con sistemas académicos, financieros, marketing, publicaciones/noticias/eventos y módulos de analítica/IA. El enfoque es modular, basado en microservicios y protocolos interoperables (REST/gRPC, MCP, Webhooks y llamadas a funciones).

## Dominios y sistemas integrados
- **Académico**: matrícula, carga académica, historial, evaluaciones, calendarios.
- **Finanzas**: facturación, pasarelas de pago, becas/descuentos, cobranzas.
- **Marketing**: campañas, segmentación, journeys, leads y seguimiento.
- **Publicaciones/Comunicaciones**: noticias, avisos, eventos, notificaciones multicanal.
- **Analítica / IA**: modelos estadísticos y ML/LLM externos, motor de recomendaciones.

## Componentes principales
1) **API Gateway / Edge**
   - Exposición REST/gRPC + WebSockets para eventos en tiempo real.
   - Autenticación (OIDC/JWT), rate limiting, WAF.

2) **Orchestrator Core**
   - Motor de flujos y política (BPMN/DSL ligera).
   - Scheduler de tareas y intervalos.
   - Coordinación de agentes (fan-out/fan-in), compensaciones, timeouts y reintentos.

3) **Agent Gateway (LLM Hub)**
   - Gestión de miles de agentes LLM.
   - Context adapters (MCP), function calling, plantillas de prompts y memoria de contexto.
   - Catálogo de herramientas conectables (APIs internas/externas, conectores).

4) **Adapters & Connectors**
   - **Académico**: integraciones SIS/ERP académico (REST/SQL/ETL).
   - **Finanzas**: pasarelas (PCI scope), asientos contables, conciliación.
   - **Marketing**: CDP/CRM, plataformas de campañas, analytics.
   - **Publicaciones**: CMS/headless, feeds RSS/Atom, push/email/SMS.
   - **IA/Estadística**: endpoints de modelos, feature store, batch/stream scoring.

5) **Data & Knowledge Layer**
   - Almacenamiento transaccional (PostgreSQL/SQL Server), colas/eventos (Kafka/NATS).
   - Data lake/warehouse para trazas y features.
   - Vector store para contexto semántico de agentes.

6) **Observabilidad y Fiabilidad**
   - Logs estructurados, métricas, trazas distribuidas (OpenTelemetry).
   - Circuit breakers, bulkheads, retries, DLQ.
   - Paneles SLO/SLI y alertas.

7) **Seguridad y Gobierno**
   - IAM, RBAC/ABAC, secretos con KMS.
   - Auditoría, PII vault, encriptado en tránsito y en reposo.
   - Controles de uso seguro de LLM (redacción, P0/P1 guardrails).

## Flujos clave
- **Orquestación de solicitud académica**: API recibe petición → motor de flujos → fan-out a agentes LLM especializados (plan de estudios, finanzas, marketing) → consulta conectores → consolidación y respuesta.
- **Publicación de noticias/eventos**: ingestión desde CMS → normalización → publicación multicanal (web, app, email, SMS) → seguimiento de engagement → feedback al motor de marketing.
- **Tareas programadas**: scheduler dispara jobs (ej. renovación de matrícula, recordatorios de pagos, campañas).
- **Analítica/IA**: batch scoring para riesgo/abandono; realtime features para recomendaciones personalizadas.

## APIs y contratos (ejemplo)
- REST/gRPC para dominios (`/academic/enrollments`, `/finance/invoices`, `/marketing/campaigns`, `/content/events`).
- Webhooks salientes para eventos de negocio y callbacks de agentes.
- MCP para estandarizar acceso de agentes LLM a herramientas internas.
- Estandarización de errores (códigos, trazas, correlación) y observabilidad por request-id.

## Despliegue y plataforma
- Kubernetes + Ingress + Service Mesh.
- Mensajería (Kafka/NATS) para event-driven y desacoplamiento.
- Horizontal auto-scaling para orquestador y gateways de agentes.

## Roadmap incremental
1. Esqueleto de servicios (Gateway, Orchestrator Core, Agent Gateway) y contratos iniciales.
2. Conectores prioritarios: Académico y Finanzas; luego Marketing y Publicaciones.
3. Observabilidad básica (logs/metrics) y seguridad (OIDC, RBAC).
4. Memoria contextual y vector store para agentes; prompts y tools catalog.
5. Expansión a analítica/ML y enriquecimiento de flujos BPMN.

## Estructura backend implementada
Se agregó una base inicial en `backend/` con dos sistemas:

- `backend/sistema_integral/`: módulos por dominio (académico, finanzas, marketing y publicaciones) y API de operaciones.
- `backend/sistema_ia/`: registro básico de agentes, memoria de contexto y API de integración.
- `backend/shared/`: modelos compartidos (`OperationResult`).
- `backend/main.py`: healthcheck consolidado de ambos sistemas.

### Pruebas mínimas
- Archivo: `tests/test_backend_modules.py`
- Ejecución:
  - `python -m unittest discover -v`
