# KPI App

Plataforma en desarrollo para la supervision operativa de empleados, control de turnos, sesiones de trabajo y captura inicial de actividad para futuros indicadores de productividad.

El repositorio hoy contiene una base backend en FastAPI y el espacio reservado para el frontend. La intencion de este README es dejar claro que existe, que falta y bajo que lineamientos conviene seguir construyendo la aplicacion.

## Documentacion de control

La documentacion de seguimiento por fases del proyecto se llevara en:

- `docs/CONTROL_PROYECTO.md`
- `docs/PLAN_MAESTRO_PROYECTO.md`
- `docs/CONTRATO_CAPTURA_ACTIVIDAD.md`

## Objetivo del producto

Construir una aplicacion que permita:

- autenticar usuarios y diferenciar roles;
- iniciar, consultar y cerrar turnos de trabajo;
- registrar sesiones activas por dispositivo o equipo;
- capturar eventos operativos sobre sitios autorizados;
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
- modelos `users`, `shifts`, `sessions`, `allowlist_domains` y `activity_events`;
- capa inicial de servicios, repositorios, enums y excepciones de dominio;
- migracion inicial con Alembic;
- script para sembrar un usuario administrador;
- pruebas unitarias base sobre servicios criticos;
- pruebas HTTP iniciales sobre permisos, usuarios y actividad.

Pendiente o no implementado aun:

- frontend;
- CRUD de empleados, supervisores y areas;
- KPIs y reportes historicos;
- panel de supervision;
- pruebas de integracion con base de datos real;
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
|-- frontend/            # reservado para la interfaz, aun sin implementacion
`-- README.md
```

## Backend actual

### Modulos

- `auth`: login y consulta del usuario autenticado.
- `users`: gestion administrativa de usuarios, estados y roles.
- `shifts`: iniciar turno, consultar turno actual y cerrar turno.
- `allowlist`: administracion de dominios autorizados para captura y medicion de KPIs.
- `activity`: ingesta y consulta inicial de eventos de actividad ligados a turno, sesion y dominio permitido.
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

## Lineamientos para el desarrollo de la aplicacion

### 1. Construir por modulos de negocio

Cada capacidad nueva deberia entrar como modulo completo, no como endpoint aislado. Por ejemplo:

- empleados;
- supervisores;
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
- capa analitica: KPIs, productividad, reportes y tendencias.

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
- vistas web de supervision pendientes.

### Fase 3. KPIs y alertas

- puntualidad;
- tiempo activo;
- pausas;
- productividad por turno;
- alertas por inactividad o anomalas.

### Fase 4. Gobierno y escalado

- auditoria;
- exportaciones;
- observabilidad;
- tareas programadas;
- integracion con SSO o directorio corporativo.

## Brechas tecnicas identificadas en este analisis

- `frontend/` esta vacio;
- ya existen pruebas unitarias de servicios y primeras pruebas HTTP, pero faltan pruebas de integracion con persistencia real;
- no hay `.env.example` en el estado original del repo;
- `requirements.txt` estaba incompleto y con una dependencia invalida;
- el control de permisos ya diferencia `ADMIN` y `SUPERVISOR`, pero aun falta definir permisos por modulo futuro;
- ya existe captura controlada de actividad, pero falta convertirla en KPIs, reportes y politicas de retencion automatizadas;
- no hay estrategia de logging, monitoreo ni manejo formal de errores operativos.

## Siguiente paso recomendado

El siguiente hito razonable no es agregar mas endpoints sueltos, sino cerrar un MVP controlable:

1. construir KPIs operativos sobre `activity_events`, `sessions` y `shifts`;
2. ampliar pruebas de integracion con persistencia real;
3. definir el frontend minimo para operacion diaria;
4. exponer vistas de supervision sobre actividad y cumplimiento;
5. avanzar a tableros y alertas sin romper el contrato de captura ya definido.

## Notas de trabajo

Este README debe tratarse como documento vivo del proyecto. Si cambia el alcance, la arquitectura o el flujo de negocio, actualizalo junto con el codigo y las migraciones.
