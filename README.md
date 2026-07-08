# KPI App

Plataforma en desarrollo para la supervision operativa de empleados, control de turnos, sesiones de trabajo y captura inicial de actividad para futuros indicadores de productividad.

El repositorio contiene una base backend en FastAPI y un frontend operativo en React que consume esos endpoints. La intencion de este README es dejar claro que existe, que falta y bajo que lineamientos conviene seguir construyendo la aplicacion.

## Documentacion de control

La documentacion de seguimiento por fases del proyecto se llevara en:

- `docs/CONTROL_PROYECTO.md`
- `docs/PLAN_MAESTRO_PROYECTO.md`
- `docs/CONTRATO_CAPTURA_ACTIVIDAD.md`
- `docs/CONTRATO_NOVEDADES_ECOMMERCE.md`
- `docs/ARQUITECTURA_FRONTEND.md`
- `docs/PROMPTS_PENCIL_FRONTEND.md`

## Objetivo del producto

Construir una aplicacion que permita:

- autenticar usuarios y diferenciar roles;
- iniciar, consultar y cerrar turnos de trabajo;
- registrar sesiones activas por dispositivo o equipo;
- capturar eventos operativos sobre sitios autorizados;
- gestionar novedades operativas de ecommerce sobre sistemas como Vendelo;
- documentar bitacoras diarias de gestion por caso;
- evolucionar hacia supervision basada en eventos, KPIs, alertas y tableros;
- mantener trazabilidad, control operativo y criterios minimos de privacidad.

## Estado actual del repositorio

Implementado:

- backend con FastAPI;
- autenticacion con JWT;
- endpoint de salud;
- gestion administrativa de usuarios y roles;
- apertura, consulta y cierre de turnos;
- creacion de sesion activa asociada al turno;
- allowlist de dominios para sitios autorizados de medicion KPI;
- captura controlada de eventos de actividad web;
- plantillas de horario y asignaciones por usuario;
- catalogos operativos para areas y sistemas fuente;
- modulo de novedades ecommerce con bitacora diaria y KPIs iniciales;
- modelos `users`, `shifts`, `sessions`, `allowlist_domains`, `activity_events`, `schedule_templates`, `user_schedule_assignments`, `operational_areas`, `source_systems`, `novelties` y `novelty_logs`;
- capa inicial de servicios, repositorios, enums y excepciones de dominio;
- migracion inicial con Alembic;
- script para sembrar un usuario administrador;
- pruebas unitarias base sobre servicios criticos;
- pruebas HTTP iniciales sobre permisos, usuarios y actividad.

- frontend operativo en React con autenticacion, dashboard por rol, turnos, horario, actividad, KPIs, novedades y panel administrativo (usuarios, allowlist, horarios, catalogos).

Pendiente o no implementado aun:

- KPIs y reportes historicos mas alla del rango consultable actual;
- alertas operativas automaticas;
- pruebas de integracion con base de datos real;
- pruebas automatizadas de frontend;
- integracion real con APIs externas de Vendelo u otros sistemas fuente;
- CI/CD, observabilidad y politicas de seguridad mas completas.

## Stack actual

- FastAPI para la API HTTP;
- SQLAlchemy como ORM;
- PostgreSQL como base de datos principal;
- Alembic para migraciones;
- JWT para autenticacion;
- Passlib y Bcrypt para hashing de contrasenas.

## Arquitectura actual

```text
kpi_app_v1/
|-- backend/
|   |-- app/
|   |   |-- core/        # configuracion, seguridad, errores y dependencias
|   |   |-- db/          # base SQLAlchemy y sesion
|   |   |-- domain/      # enums y contratos de dominio
|   |   |-- models/      # tablas principales
|   |   |-- repositories/# acceso a datos
|   |   |-- routers/     # endpoints HTTP
|   |   |-- schemas/     # contratos Pydantic
|   |   |-- services/    # casos de uso y reglas de negocio
|   |   |-- main.py      # aplicacion FastAPI
|   |   `-- seed_admin.py
|   |-- alembic/         # migraciones
|   |-- .env.example
|   |-- tests/
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- app/          # router, guards por rol, layout (sidebar/topbar)
|   |   |-- modules/      # auth, dashboard, shifts, schedules, activity, kpis, novelties, supervisor, admin
|   |   |-- components/ui/# kit de UI (Button, Badge, Card, DataTable, Form, Modal, Tabs, iconos)
|   |   |-- components/charts/ # graficos (Recharts) para desgloses de KPIs
|   |   |-- lib/api/      # cliente HTTP (axios) por dominio
|   |   |-- lib/session/  # contexto de autenticacion
|   |   `-- types/        # tipos alineados a los esquemas Pydantic del backend
|   `-- package.json
`-- README.md
```

## Backend actual

### Modulos

- `auth`: login y consulta del usuario autenticado.
- `users`: gestion administrativa de usuarios, estados y roles.
- `shifts`: iniciar turno, consultar turno actual y cerrar turno.
- `allowlist`: administracion de dominios autorizados para captura y medicion de KPIs.
- `activity`: ingesta y consulta inicial de eventos de actividad ligados a turno, sesion y dominio permitido.
- `kpis`: consultas operativas sobre actividad, sesiones y turnos para empleados y supervisores.
- `schedules`: plantillas de horario, asignaciones por usuario y resolucion del horario esperado por fecha.
- `novelties`: catalogos operativos, novedades ecommerce, bitacora diaria y KPIs de gestion.
- `core`: carga de configuracion, JWT, hashing y dependencias compartidas.
- `repositories`: acceso desacoplado a persistencia.
- `services`: logica de negocio aislada de FastAPI.
- `domain`: enums y consistencia de estados/roles.
- `db`: engine, sesion y base declarativa.
- `models`: entidades persistidas en PostgreSQL.

### Endpoints disponibles

- `GET /health`
- `POST /auth/login`
- `GET /auth/me`
- `GET /users`
- `GET /users/{user_id}`
- `POST /users`
- `PATCH /users/{user_id}`
- `PATCH /users/{user_id}/status`
- `POST /shifts/start`
- `GET /shifts/current`
- `POST /shifts/end`
- `GET /allowlist/domains`
- `POST /allowlist/domains`
- `PATCH /allowlist/domains/{domain_id}/status`
- `POST /activity/events`
- `GET /activity/events/me`
- `GET /activity/events`
- `GET /kpis/me/overview`
- `GET /kpis/overview`
- `GET /kpis/users/{user_id}/overview`
- `GET /kpis/shifts/{shift_id}`
- `GET /schedules/templates`
- `GET /schedules/templates/{template_id}`
- `POST /schedules/templates`
- `PATCH /schedules/templates/{template_id}`
- `PATCH /schedules/templates/{template_id}/status`
- `GET /schedules/assignments`
- `POST /schedules/assignments`
- `GET /schedules/me/resolved`
- `GET /schedules/users/{user_id}/resolved`
- `GET /novelties/areas`
- `POST /novelties/areas`
- `PATCH /novelties/areas/{area_id}/status`
- `GET /novelties/source-systems`
- `POST /novelties/source-systems`
- `PATCH /novelties/source-systems/{source_system_id}/status`
- `GET /novelties/me`
- `GET /novelties`
- `POST /novelties`
- `GET /novelties/{novelty_id}`
- `PATCH /novelties/{novelty_id}`
- `PATCH /novelties/{novelty_id}/assignment`
- `PATCH /novelties/{novelty_id}/status`
- `GET /novelties/{novelty_id}/logs`
- `POST /novelties/{novelty_id}/logs`
- `GET /novelties/kpis/me`
- `GET /novelties/kpis/overview`
- `GET /novelties/kpis/users/{user_id}`

### Contratos importantes

- `POST /auth/login` usa `OAuth2PasswordRequestForm`, por lo tanto recibe formulario `application/x-www-form-urlencoded`.
- `GET /users` y `GET /users/{user_id}` permiten administracion y consulta por `ADMIN` o `SUPERVISOR`.
- `POST /users`, `PATCH /users/{user_id}` y `PATCH /users/{user_id}/status` quedan reservados para `ADMIN`.
- `POST /shifts/start` recibe `device_label` opcional.
- `GET /auth/me`, `GET /shifts/current` y `POST /shifts/end` requieren token Bearer.
- los endpoints de `allowlist` quedan reservados para administracion.
- `POST /activity/events` solo acepta eventos con turno activo, sesion activa y URL `http` o `https` dentro de la allowlist.
- `HEARTBEAT` e `IDLE` requieren `duration_seconds`; `PAGE_VIEW` y `RESUME` no lo admiten.
- `GET /activity/events/me` permite al usuario consultar su propia actividad.
- `GET /activity/events` queda reservado para `ADMIN` y `SUPERVISOR`.
- `GET /kpis/me/overview` expone resumen operativo del usuario autenticado.
- `GET /kpis/overview`, `GET /kpis/users/{user_id}/overview` y `GET /kpis/shifts/{shift_id}` quedan reservados para `ADMIN` y `SUPERVISOR`.
- la puntualidad ya se calcula comparando el turno real contra el horario asignado y su tolerancia.
- `POST /schedules/templates`, `PATCH /schedules/templates/{template_id}`, `PATCH /schedules/templates/{template_id}/status` y `POST /schedules/assignments` quedan reservados para `ADMIN`.
- `GET /schedules/templates`, `GET /schedules/assignments` y `GET /schedules/users/{user_id}/resolved` pueden ser consultados por `ADMIN` y `SUPERVISOR`.
- `GET /schedules/me/resolved` permite al usuario autenticado consultar su horario esperado para una fecha.
- `POST /novelties` permite registrar una novedad operativa ligada a un area y un sistema fuente.
- `GET /novelties/areas` y `GET /novelties/source-systems` exponen catalogos activos a cualquier usuario autenticado para soportar el alta de novedades desde el frontend.
- `ADMIN` y `SUPERVISOR` pueden usar esos mismos catalogos con filtro completo, incluyendo registros inactivos.
- `GET /novelties/me` expone las novedades propias o asignadas al usuario autenticado.
- `GET /novelties` queda reservado para `ADMIN` y `SUPERVISOR`.
- `POST /novelties/areas`, `PATCH /novelties/areas/{area_id}/status`, `POST /novelties/source-systems` y `PATCH /novelties/source-systems/{source_system_id}/status` quedan reservados para `ADMIN`.
- `POST /novelties/{novelty_id}/logs` permite documentar bitacora diaria de gestion, con minutos trabajados y cambio de estado opcional.
- `GET /novelties/kpis/me` expone KPIs personales de gestion de novedades y las vistas globales o por usuario quedan reservadas para `ADMIN` y `SUPERVISOR`.

## Frontend actual

### Stack

- React 19 + TypeScript + Vite;
- Tailwind CSS v4 (tema oscuro con acentos degradados, tokens de color en `src/index.css`);
- React Router para navegacion y guards por autenticacion/rol;
- TanStack Query para datos remotos, cache y mutaciones;
- Recharts para los desgloses de KPIs;
- axios como cliente HTTP con interceptor de token y manejo central de errores.

### Experiencia por rol

- `EMPLOYEE`: dashboard propio, turno, horario, actividad, KPIs personales y novedades propias/asignadas.
- `SUPERVISOR`: equipo hoy, KPIs de equipo, turnos de hoy, actividad del equipo, horarios (consulta) y novedades globales.
- `ADMIN`: todo lo anterior mas administracion de usuarios, dominios permitidos, plantillas/asignaciones de horario y catalogos operativos (areas y sistemas fuente).

El detalle de rutas por rol sigue lo definido en `docs/ARQUITECTURA_FRONTEND.md`.

### Puesta en marcha local (frontend)

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

`frontend/.env` define `VITE_API_URL` (por defecto `http://localhost:8000`). El backend debe tener `BACKEND_CORS_ORIGINS` incluyendo el origen del frontend (por defecto `http://localhost:5173`) en `backend/.env`.

### Decisiones tecnicas

- se prioriza cobertura funcional de los modulos ya cerrados del backend (turnos, horarios, actividad, KPIs, novedades, usuarios, allowlist) antes que analitica avanzada;
- la vista "Equipo hoy" y "KPIs del equipo" combinan `GET /users` con `GET /kpis/users/{id}/overview` por usuario (aceptable para equipos pequenos/medianos; si el equipo crece de forma significativa conviene un endpoint agregado en backend);
- los filtros de fecha (`started_from`/`started_to`) siempre se envian con zona horaria (ISO 8601 con offset) porque el backend los exige asi;
- `GET /kpis/shifts/{shift_id}` es exclusivo de `ADMIN`/`SUPERVISOR`; la vista "Mi turno" del empleado usa `GET /kpis/me/overview` acotado a la fecha de inicio del turno abierto para mostrar el mismo tipo de detalle sin violar permisos.

## Variables de entorno

Crear `backend/.env` a partir de `backend/.env.example`.

Variables requeridas:

- `DATABASE_URL`
- `APP_NAME`
- `JWT_SECRET`
- `JWT_ALG`
- `ACCESS_TOKEN_EXPIRE_MIN`
- `BACKEND_CORS_ORIGINS`

Ejemplo:

```env
APP_NAME=KPI App API
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/kpi_app
JWT_SECRET=change_this_secret
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MIN=60
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## Puesta en marcha local

### 1. Crear entorno virtual

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```powershell
Copy-Item .env.example .env
```

Editar `backend/.env` con los valores reales de tu entorno.

### 4. Ejecutar migraciones

```powershell
alembic upgrade head
```

### 5. Crear usuario administrador inicial

```powershell
python -m app.seed_admin
```

El script actual crea:

- email: `admin@kpi.com`
- password: `Admin123*`

Conviene cambiar estas credenciales en cuanto el flujo de usuarios quede formalizado.

### 6. Iniciar la API

```powershell
uvicorn app.main:app --reload
```

### 7. Ejecutar pruebas base

```powershell
python -m unittest discover -s tests -v
```

Documentacion interactiva:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Ejemplos de uso

### Login

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@kpi.com&password=Admin123*"
```

### Iniciar turno

```bash
curl -X POST "http://127.0.0.1:8000/shifts/start" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"device_label\":\"PC-SUP-01\"}"
```

### Crear usuario

```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Authorization: Bearer TU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Ana Perez\",\"email\":\"ana@kpi.com\",\"password\":\"Secreta123\",\"role\":\"SUPERVISOR\",\"is_active\":true}"
```

### Consultar turno actual

```bash
curl "http://127.0.0.1:8000/shifts/current" \
  -H "Authorization: Bearer TU_TOKEN"
```

### Cerrar turno

```bash
curl -X POST "http://127.0.0.1:8000/shifts/end" \
  -H "Authorization: Bearer TU_TOKEN"
```

### Crear dominio en allowlist

```bash
curl -X POST "http://127.0.0.1:8000/allowlist/domains" \
  -H "Authorization: Bearer TU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d "{\"domain\":\"https://portal.example.com\",\"description\":\"Portal oficial KPI\"}"
```

### Registrar evento de actividad

```bash
curl -X POST "http://127.0.0.1:8000/activity/events" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"event_type\":\"PAGE_VIEW\",\"source_url\":\"https://portal.example.com/reportes\",\"page_title\":\"Reporte diario\"}"
```

### Consultar eventos propios

```bash
curl "http://127.0.0.1:8000/activity/events/me?limit=20" \
  -H "Authorization: Bearer TU_TOKEN"
```

### Consultar KPIs propios

```bash
curl "http://127.0.0.1:8000/kpis/me/overview" \
  -H "Authorization: Bearer TU_TOKEN"
```

### Consultar KPIs globales

```bash
curl "http://127.0.0.1:8000/kpis/overview" \
  -H "Authorization: Bearer TU_TOKEN_SUPERVISOR"
```

### Crear plantilla de horario

```bash
curl -X POST "http://127.0.0.1:8000/schedules/templates" \
  -H "Authorization: Bearer TU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Horario oficina\",\"description\":\"Lunes a viernes\",\"timezone_name\":\"America/Bogota\",\"grace_minutes\":10,\"is_active\":true,\"slots\":[{\"weekday\":\"MONDAY\",\"start_time\":\"08:00:00\",\"end_time\":\"17:00:00\"},{\"weekday\":\"TUESDAY\",\"start_time\":\"08:00:00\",\"end_time\":\"17:00:00\"}]}"
```

### Consultar horario esperado propio

```bash
curl "http://127.0.0.1:8000/schedules/me/resolved?target_date=2026-04-01" \
  -H "Authorization: Bearer TU_TOKEN"
```

### Crear novedad operativa

```bash
curl -X POST "http://127.0.0.1:8000/novelties" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"area_id\":1,\"source_system_id\":1,\"assigned_user_id\":2,\"external_reference\":\"VDL-200\",\"order_reference\":\"ORD-200\",\"title\":\"Pedido con novedad de pago\",\"description\":\"El pedido requiere validacion manual en Vendelo y seguimiento diario.\",\"novelty_type\":\"PAGO\",\"priority\":\"HIGH\",\"extra_data\":{\"canal\":\"vendelo\"}}"
```

### Registrar bitacora diaria de una novedad

```bash
curl -X POST "http://127.0.0.1:8000/novelties/1/logs" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"work_date\":\"2026-04-11\",\"log_type\":\"DAILY_UPDATE\",\"content\":\"Se contacta al operador y se deja gestion documentada.\",\"worked_minutes\":25,\"status_after\":\"IN_PROGRESS\"}"
```

### Consultar KPIs propios de novedades

```bash
curl "http://127.0.0.1:8000/novelties/kpis/me" \
  -H "Authorization: Bearer TU_TOKEN"
```

## Lineamientos para el desarrollo de la aplicacion

### 1. Construir por modulos de negocio

Cada capacidad nueva deberia entrar como modulo completo, no como endpoint aislado. Por ejemplo:

- empleados;
- supervisores;
- novedades ecommerce;
- eventos de actividad;
- alertas;
- reportes;
- auditoria.
- allowlist y origenes de datos.

Cada modulo nuevo deberia incluir:

- modelo;
- schema;
- router;
- migracion;
- validaciones de negocio;
- pruebas minimas.

### 2. Separar claramente lo operativo de lo analitico

La app va a necesitar dos capas:

- capa transaccional: usuarios, turnos, sesiones, eventos;
- capa analitica: KPIs, productividad, novedades, reportes y tendencias.

No mezclar consultas operativas con agregaciones complejas en el mismo punto de crecimiento.

### 3. Mantener supervision con criterio de privacidad

Si la aplicacion evoluciona hacia seguimiento de actividad, deberia registrar:

- eventos relevantes para operacion;
- timestamps;
- relacion con usuario, turno y dispositivo;
- auditoria de quien consulta o exporta informacion.

Evitar recolectar datos invasivos sin definir antes:

- base legal o politica interna;
- retencion de datos;
- acceso por rol;
- trazabilidad de consultas.

### 4. Forzar consistencia de dominio

Estados como `OPEN` y `CLOSED` no deberian quedar dispersos a largo plazo. Conviene centralizar enums o constantes de dominio para:

- roles;
- estados de turno;
- estados de sesion;
- dominios permitidos de captura;
- tipos de evento;
- severidad de alertas.

### 5. No avanzar sin pruebas en los flujos criticos

Los primeros tests deberian cubrir:

- login exitoso y fallido;
- usuario inactivo;
- iniciar turno con y sin turno abierto;
- cerrar turno inexistente;
- integridad entre turno y sesion;
- normalizacion y duplicados de la allowlist;
- validacion de actividad fuera de allowlist;
- registro de actividad solo con turno y sesion activa.

### 6. Documentar primero el MVP real

Antes de construir dashboards o monitoreo avanzado, cerrar el MVP operativo con:

- gestion de usuarios;
- turnos;
- sesiones;
- allowlist de dominios fuente;
- permisos por rol;
- historial basico;
- frontend minimo para operacion diaria.

## Roadmap sugerido

### Fase 1. Base operativa

- endurecer autenticacion;
- crear CRUD de usuarios;
- definir roles;
- registrar historial de turnos y sesiones;
- consolidar allowlist de dominios y politicas de captura;
- agregar pruebas automatizadas.

### Fase 2. Supervision funcional

- registrar eventos de actividad;
- vincular eventos con turno y sesion;
- construir vistas para supervisores;
- agregar filtros por fecha, usuario y equipo.

Estado actual:

- backend de eventos y filtros base ya implementado;
- vistas web de supervision (equipo hoy, turnos de hoy, actividad del equipo) ya implementadas en el frontend.

### Fase 3. KPIs y alertas

- puntualidad;
- tiempo activo;
- pausas;
- productividad por turno;
- alertas por inactividad o anomalas.

Estado actual:

- ya existe una primera capa backend de KPIs operativos sobre `activity_events`, `sessions` y `shifts`;
- ya existe el submodulo de horarios y asignaciones para usuarios;
- la puntualidad ya se calcula sobre horarios asignados, turnos reales y tolerancia;
- ya existen vistas de KPIs (propias y de equipo) con graficos en el frontend;
- las alertas aun no estan implementadas y quedan fuera del cierre de esta fase.

### Fase 4. Gobierno y escalado

- auditoria;
- exportaciones;
- observabilidad;
- tareas programadas;
- integracion con SSO o directorio corporativo.

## Brechas tecnicas identificadas en este analisis

- ya existe un frontend operativo, pero aun no tiene pruebas automatizadas propias;
- ya existen pruebas unitarias de servicios y primeras pruebas HTTP, pero faltan pruebas de integracion con persistencia real;
- no hay `.env.example` en el estado original del repo;
- `requirements.txt` estaba incompleto y con una dependencia invalida;
- el control de permisos ya diferencia `ADMIN` y `SUPERVISOR`, pero aun falta definir permisos por modulo futuro;
- ya existe captura controlada de actividad, pero falta convertirla en reportes historicos y politicas de retencion automatizadas;
- ya existe una base de KPIs operativos y horarios con puntualidad real, y ya tienen vistas web, pero aun faltan alertas operativas;
- ya existe una base para novedades ecommerce, bitacora diaria y su vista web, pero aun falta integracion real con sistemas externos;
- la vista "Equipo hoy"/"KPIs del equipo" del frontend resuelve el detalle por usuario con una consulta por empleado (`GET /kpis/users/{id}/overview`); si el equipo crece mucho conviene un endpoint agregado en backend;
- no hay estrategia de logging, monitoreo ni manejo formal de errores operativos.

## Siguiente paso recomendado

El siguiente hito razonable no es agregar mas endpoints sueltos, sino cerrar el ciclo de operacion real:

1. ampliar pruebas de integracion con persistencia real y agregar pruebas automatizadas de frontend;
2. definir alertas operativas sobre inactividad, baja cobertura y acumulacion de novedades;
3. evaluar un endpoint agregado de KPIs por equipo para evitar N+1 consultas cuando el equipo crezca;
4. avanzar hacia auditoria, exportaciones y observabilidad (Fase 6 del plan maestro).

## Notas de trabajo

Este README debe tratarse como documento vivo del proyecto. Si cambia el alcance, la arquitectura o el flujo de negocio, actualizalo junto con el codigo y las migraciones.
