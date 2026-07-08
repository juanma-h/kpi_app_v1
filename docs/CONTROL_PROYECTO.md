# Control del Proyecto

## Proposito

Este documento define como se va a construir, revisar y cerrar cada fase del proyecto para mantener control tecnico, funcional y documental.

La regla de trabajo sera:

1. definir alcance de la fase;
2. implementar solo lo comprometido en esa fase;
3. validar codigo y pruebas;
4. documentar resultados, pendientes y riesgos;
5. hacer commit con corte limpio antes de pasar a la siguiente fase.

## Criterio de trabajo

El proyecto se construira por fases cortas y controladas, priorizando primero la solidez del backend.

Cada fase debe dejar:

- codigo integrado y consistente;
- pruebas minimas del alcance tocado;
- documentacion actualizada;
- lista clara de lo que queda pendiente;
- una base util para la siguiente fase.

## Estado actual

### Fase 1 cerrada

Objetivo:

- consolidar la base del backend;
- separar responsabilidades para acercar la arquitectura a SOLID;
- dejar lista la base del allowlist de dominios.

Resultado:

- se separo logica en `services`, `repositories`, `domain` y `core`;
- se centralizo manejo de errores;
- se incorporo el modulo inicial de allowlist de dominios;
- se agrego migracion para `allowlist_domains`;
- se agregaron pruebas unitarias base para autenticacion, turnos y allowlist;
- se actualizo el `README` y la configuracion inicial del backend.

Estado:

- completada y committeada.

## Fase 2 cerrada

Objetivo principal:

- construir el modulo de usuarios y roles sobre la arquitectura actual.

Resultado:

- se incorporo el modulo `users` con endpoints administrativos;
- se agrego un servicio dedicado para creacion, consulta, actualizacion y cambio de estado de usuarios;
- se ampliaron contratos y repositorios para soportar gestion real de usuarios;
- se formalizaron roles `ADMIN`, `SUPERVISOR` y `EMPLOYEE` en flujos administrativos;
- se agregaron validaciones de negocio como correo unico, bloqueo de autodesactivacion y bloqueo de cambio de rol propio;
- se incorporaron pruebas unitarias del servicio de usuarios;
- se incorporaron primeras pruebas HTTP para permisos por rol.

Decisiones tecnicas:

- `ADMIN` puede crear y modificar usuarios;
- `SUPERVISOR` puede consultar usuarios, pero no administrarlos;
- la baja logica del usuario se maneja con `is_active`, no con borrado fisico;
- el cambio de permisos mas fino por modulo se deja para fases posteriores.

Estado:

- completada y committeada.

## Fase 3 cerrada

Objetivo principal:

- construir el modulo de eventos de actividad web sobre la base de turnos, sesiones y allowlist.

Resultado:

- se incorporo el modelo `activity_events` con relacion a usuario, turno, sesion y dominio permitido;
- se agrego un servicio dedicado para registrar y consultar eventos de actividad;
- se incorporo validacion de dominio exacto o subdominio contra la allowlist activa;
- se restringio el registro de actividad a usuarios con turno y sesion activa;
- se definieron los tipos de evento iniciales `PAGE_VIEW`, `HEARTBEAT`, `IDLE` y `RESUME`;
- se agregaron pruebas unitarias del servicio de actividad;
- se agregaron pruebas HTTP para captura y consulta de actividad segun rol;
- se documento el contrato tecnico de captura en `docs/CONTRATO_CAPTURA_ACTIVIDAD.md`.

Decisiones tecnicas:

- la ingesta inicial se hace por `POST /activity/events`;
- el backend resuelve `user_id`, `shift_id` y `session_id` desde el usuario autenticado;
- solo se aceptan eventos sobre dominios activos de la allowlist;
- `HEARTBEAT` e `IDLE` requieren `duration_seconds`;
- `PAGE_VIEW` y `RESUME` no aceptan `duration_seconds`;
- el empleado puede consultar sus propios eventos y `SUPERVISOR` o `ADMIN` pueden consultar eventos globales;
- la captura se define como instrumentacion del cliente web autenticado y no como scraping del lado servidor.

Estado:

- completada y committeada.

## Fase 4 cerrada

Objetivo principal:

- transformar turnos, sesiones y actividad en KPIs operativos consultables.

Resultado:

- se incorporo el modulo `kpis` con endpoints de consulta para usuario autenticado y supervision;
- se agrego un servicio dedicado para calcular cobertura de actividad, tiempo activo, tiempo inactivo y trazabilidad por turno;
- se agrego un repositorio de lectura separado para evitar mezclar analitica con repositorios transaccionales;
- se incorporo el submodulo `schedules` con plantillas de horario, franjas por dia y asignaciones por usuario;
- se agrego resolucion del horario esperado por fecha para usuario autenticado y supervision;
- se integro la puntualidad real comparando turnos abiertos contra horario esperado y margen de tolerancia;
- se incorporaron pruebas unitarias del servicio de KPIs;
- se incorporaron pruebas unitarias del servicio de horarios;
- se incorporaron pruebas HTTP para permisos y consultas de ambos modulos.

Decisiones tecnicas:

- la Fase 4 usa calculos derivados de `activity_events`, `sessions` y `shifts` sin crear tablas analiticas nuevas por ahora;
- la cobertura se mide sobre tiempo de sesion frente a tiempo trazado por eventos `HEARTBEAT` e `IDLE`;
- la puntualidad se evalua por turno usando horario asignado, zona horaria del horario y tolerancia configurada;
- `EMPLOYEE` puede consultar solo `GET /kpis/me/overview`;
- `SUPERVISOR` y `ADMIN` pueden consultar vistas globales, por usuario y por turno.
- `ADMIN` administra plantillas y asignaciones de horario; `SUPERVISOR` puede consultarlas.

Estado:

- completada y committeada.

## Subfase 4.1 cerrada

Objetivo principal:

- incorporar el dominio de novedades ecommerce antes de iniciar el frontend operativo.

Resultado:

- se incorporaron catalogos de `operational_areas` y `source_systems` para modelar equipos y sistemas como Vendelo;
- se agrego el modulo `novelties` con alta, consulta, edicion, asignacion y cambio de estado;
- se agrego la bitacora diaria `novelty_logs` para documentar gestion por caso y minutos trabajados;
- se vinculo la novedad con usuario reportante, usuario asignado, turno y sesion cuando existe contexto operativo;
- se agregaron KPIs iniciales de novedades por usuario y vista global;
- se incorporaron pruebas unitarias y HTTP del nuevo modulo.

Decisiones tecnicas:

- el modulo se implementa como capa generica de novedades operativas, no acoplada exclusivamente a Vendelo;
- Vendelo entra como `source_system` y puede vincularse a la allowlist existente;
- `EMPLOYEE` puede registrar novedades, consultar sus propias novedades o asignadas y documentar bitacora;
- `SUPERVISOR` y `ADMIN` pueden consultar vistas globales y KPIs de novedades;
- `ADMIN` administra catalogos operativos y puede cambiar estados o asignaciones sin limitar el modulo a un solo sistema fuente;
- la reapertura de novedades cerradas se deja fuera de esta iteracion para no introducir flujo incompleto sin reglas de auditoria.

Estado:

- completada, validada y lista para commit cuando se decida cerrar el corte actual.

Documentacion operativa asociada:

- `docs/CONTRATO_NOVEDADES_ECOMMERCE.md`

## Fase 5 cerrada

Objetivo principal:

- construir el frontend operativo sobre los modulos ya cerrados del backend (turnos, horarios, actividad, KPIs, novedades, usuarios y allowlist).

Resultado:

- se creo la aplicacion en `frontend/` con React 19, TypeScript, Vite, Tailwind CSS v4, React Router y TanStack Query;
- se definio un sistema de diseno oscuro con acentos degradados, componentes reutilizables (`Button`, `Badge`, `Card`, `DataTable`, `Form`, `Modal`, `Tabs`, iconografia propia) y una paleta de graficos validada con el criterio de accesibilidad del equipo;
- se implemento autenticacion (login, sesion persistida, guard por autenticacion y por rol) y un `AppShell` con sidebar por rol y topbar;
- se construyo la experiencia de `EMPLOYEE`: dashboard propio, turno (iniciar/cerrar con detalle en vivo), horario resuelto por fecha, actividad reciente, KPIs personales con graficos y novedades propias/asignadas con bitacora;
- se construyo la experiencia de `SUPERVISOR`: equipo hoy, KPIs de equipo, turnos de hoy, actividad del equipo, horarios (consulta) y novedades globales, ademas del detalle por empleado;
- se construyo la experiencia de `ADMIN`: administracion de usuarios, dominios permitidos, plantillas y asignaciones de horario, y catalogos operativos (areas y sistemas fuente), sumado a todo lo de `SUPERVISOR`;
- se probo el flujo completo contra el backend real (login, inicio/cierre de turno, creacion de usuario, dominio, plantilla de horario, asignacion, area operativa, sistema fuente, novedad y entrada de bitacora) usando un navegador headless.

Decisiones tecnicas:

- la vista "Equipo hoy" y "KPIs del equipo" combinan `GET /users` con `GET /kpis/users/{id}/overview` por usuario en paralelo; es valido para equipos pequenos o medianos y queda identificado como candidato a un endpoint agregado si el equipo crece;
- los filtros de fecha del frontend siempre se envian en ISO 8601 con zona horaria porque el backend rechaza fechas sin offset;
- `GET /kpis/shifts/{shift_id}` es exclusivo de `ADMIN`/`SUPERVISOR`, asi que la vista "Mi turno" del empleado usa `GET /kpis/me/overview` acotado a la fecha de inicio del turno abierto en su lugar;
- la creacion de novedades y la bitacora quedan disponibles para cualquier usuario autenticado; la reasignacion de novedades queda restringida a `ADMIN`/`SUPERVISOR` en el frontend, en linea con el permiso ya existente en el backend.

Riesgos o limitaciones:

- el frontend aun no tiene pruebas automatizadas propias (unitarias o end-to-end);
- la resolucion de KPIs por equipo mediante multiples consultas paralelas puede degradar con equipos grandes;
- las alertas operativas siguen sin implementarse, tanto en backend como en frontend.

Estado:

- completada y lista para commit.

Siguiente fase recomendada:

- Fase 6, gobierno y escalado: auditoria, exportaciones, observabilidad y alertas operativas.

## Regla documental a partir de ahora

Al cerrar cada fase se actualizara este documento con:

- objetivo de la fase;
- cambios implementados;
- decisiones tecnicas tomadas;
- riesgos o limitaciones;
- siguiente fase recomendada.

## Plan maestro del proyecto

Con la Fase 4 cerrada, el plan completo de:

- desarrollo;
- despliegue;
- seguridad;
- operacion;
- monitoreo;
- mantenimiento correctivo y evolutivo;
- roadmap de producto y backend/frontend;

queda documentado en:

- `docs/PLAN_MAESTRO_PROYECTO.md`
- `docs/CONTRATO_CAPTURA_ACTIVIDAD.md`
- `docs/CONTRATO_NOVEDADES_ECOMMERCE.md`

## Siguiente fase recomendada

- definir alertas operativas sobre inactividad, baja cobertura y acumulacion de novedades;
- ampliar pruebas de integracion con persistencia real y agregar pruebas automatizadas de frontend;
- evaluar un endpoint agregado de KPIs por equipo si el numero de empleados crece de forma relevante.

## Regla de calidad minima

No se avanza de fase si falta alguno de estos puntos:

- el codigo compila o ejecuta correctamente en su alcance;
- las pruebas del alcance nuevo pasan;
- la documentacion de la fase queda actualizada;
- el corte queda listo para commit.

## Decision de formato

Se usara Markdown dentro de `docs/` en lugar de `.txt` porque:

- es mas legible;
- permite estructura clara por fases;
- es mejor para control de cambios en Git;
- sirve tanto para trabajo tecnico como para gestion del proyecto.
