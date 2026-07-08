# Plan Maestro del Proyecto

## Proposito

Este documento define el plan integral de desarrollo, despliegue y mantenimiento de la plataforma de supervision operativa de empleados.

El objetivo es que el proyecto pueda crecer con control tecnico, funcional y operativo, evitando decisiones aisladas o desarrollo desordenado.

## Objetivo del producto

La aplicacion debe permitir:

- autenticar usuarios con roles diferenciados;
- gestionar empleados, supervisores y administradores;
- iniciar y cerrar turnos;
- registrar sesiones de trabajo por dispositivo o entorno;
- permitir una allowlist de dominios autorizados para captura de actividad;
- capturar eventos operativos para construir KPIs reales;
- exponer tableros, alertas e historial para supervision.

## Principios rectores

- backend primero, frontend despues;
- fases cortas y validables;
- arquitectura alineada con SOLID;
- trazabilidad tecnica por commit y por documento;
- seguridad y privacidad desde el diseno;
- despliegue reproducible y mantenimiento previsible.

## Estado base actual

Completado al cierre de Subfase 4.1:

- autenticacion JWT;
- modulo de turnos y sesiones;
- modulo de usuarios y roles;
- allowlist inicial de dominios;
- modulo de eventos de actividad web;
- modulo de novedades ecommerce y bitacora diaria;
- separacion por `routers`, `services`, `repositories`, `domain` y `core`;
- pruebas unitarias de servicios;
- pruebas HTTP iniciales por permisos y actividad.

## Arquitectura objetivo

### Backend

Estructura prevista:

- `routers`: capa HTTP y validacion de entrada/salida;
- `services`: logica de negocio y reglas del dominio;
- `repositories`: acceso a persistencia;
- `domain`: enums, contratos y reglas compartidas;
- `models`: entidades SQLAlchemy;
- `core`: configuracion, seguridad, dependencias y manejo de errores.

### Frontend

El frontend se incorporara cuando el backend operativo este suficientemente cerrado.

Objetivo del frontend inicial:

- login;
- vista de turnos;
- vista administrativa de usuarios;
- vista de dominios permitidos;
- pantalla minima para supervisores.

## Roadmap de desarrollo

## Fase 1. Base del backend

Estado:

- completada.

Entregables:

- autenticacion;
- turnos;
- sesiones;
- base arquitectonica;
- allowlist inicial;
- pruebas base.

## Fase 2. Usuarios y roles

Estado:

- completada.

Entregables:

- CRUD administrativo de usuarios;
- activacion y desactivacion;
- reglas iniciales por rol;
- pruebas del modulo;
- documentacion actualizada.

## Fase 3. Eventos de actividad

Estado:

- completada.

Objetivo:

- modelar y capturar eventos para sitios permitidos.

Entregables:

- modelo `activity_events`;
- relacion con `user`, `shift`, `session` y `allowlist_domain`;
- validacion de origen permitido;
- endpoints o ingesta controlada;
- pruebas unitarias e integracion.

Decisiones cerradas en esta fase:

- se capturan `PAGE_VIEW`, `HEARTBEAT`, `IDLE` y `RESUME`;
- `HEARTBEAT` e `IDLE` usan `duration_seconds` y el resto no;
- el mecanismo inicial de captura se define como instrumentacion del cliente web autenticado;
- el backend solo acepta eventos sobre dominios activos de la allowlist;
- el criterio de captura minima y privacidad queda documentado en `docs/CONTRATO_CAPTURA_ACTIVIDAD.md`;
- la frecuencia recomendada inicial queda cerrada con `HEARTBEAT` cada 60 segundos y transiciones puntuales para `PAGE_VIEW`, `IDLE` y `RESUME`.

## Fase 4. KPIs operativos

Estado:

- completada.

Objetivo:

- transformar eventos y sesiones en indicadores utiles.

Entregables:

- consultas base para productividad;
- medicion de tiempo activo, pausas y puntualidad;
- indicadores por usuario y turno;
- endpoints de consulta para supervisores.

Avance actual:

- ya existe una primera capa de KPIs operativos basada en `activity_events`, `sessions` y `shifts`;
- ya existe un submodulo de horarios y asignaciones para soportar puntualidad futura;
- se exponen consultas para vista propia, vista global, vista por usuario y vista por turno;
- la puntualidad ya se calcula sobre horarios asignados, turnos reales y tolerancia;
- todavia no existen alertas operativas ni materializacion analitica.

## Subfase 4.1. Novedades ecommerce

Estado:

- completada.

Objetivo:

- incorporar el dominio de novedades operativas del ecommerce antes del frontend.

Entregables:

- catalogos `operational_areas` y `source_systems`;
- modulo `novelties` con estado, prioridad, referencias externas y asignacion;
- bitacora diaria `novelty_logs` con tiempo trabajado;
- endpoints de consulta personal y global;
- KPIs iniciales de novedades por usuario y vista global.

Soporte documental:

- `docs/CONTRATO_NOVEDADES_ECOMMERCE.md`

## Fase 5. Frontend operativo

Estado:

- completada.

Objetivo:

- habilitar uso web real para empleados y supervisores sobre turnos, horarios, actividad y novedades.

Entregables:

- autenticacion web;
- panel operativo para usuarios;
- panel administrativo para usuarios y dominios;
- vistas de supervision basadas en KPIs;
- control de acceso por rol.

Avance actual:

- se construyo el frontend en React 19 + TypeScript + Vite + Tailwind CSS v4, consumiendo todos los modulos backend cerrados (turnos, horarios, actividad, KPIs, novedades, usuarios y allowlist);
- se implementaron las tres experiencias por rol (`EMPLOYEE`, `SUPERVISOR`, `ADMIN`) con guards de autenticacion y de rol;
- todavia no existen pruebas automatizadas de frontend ni alertas operativas; quedan para la Fase 6.

## Fase 6. Operacion y gobierno

Objetivo:

- preparar la aplicacion para uso sostenido y crecimiento.

Entregables:

- auditoria;
- exportaciones;
- observabilidad;
- mantenimiento programado;
- backups y recuperacion;
- politicas de seguridad y soporte.

## Estrategia de despliegue

## Entornos

Se recomienda mantener al menos tres entornos:

- `dev`: desarrollo local y validacion diaria;
- `staging`: pruebas previas a produccion;
- `prod`: entorno estable de uso real.

## Stack de despliegue recomendado

- backend FastAPI ejecutado con Uvicorn o Gunicorn+Uvicorn workers;
- PostgreSQL como base de datos principal;
- proxy reverso con Nginx o servicio equivalente;
- variables de entorno gestionadas por secretos del entorno;
- migraciones ejecutadas con Alembic en cada despliegue controlado.

## Estrategia recomendada de empaquetado

Idealmente:

- contenedores Docker para backend;
- archivo de composicion para `dev` y `staging`;
- pipeline CI/CD para construir, probar y desplegar.

Si no se usa Docker en la primera etapa, al menos debe existir:

- entorno virtual reproducible;
- archivo `.env.example` mantenido;
- procedimiento documentado de despliegue.

## Flujo de despliegue recomendado

1. correr pruebas en CI;
2. construir artefacto o imagen;
3. aplicar migraciones;
4. desplegar backend;
5. validar healthcheck;
6. habilitar trafico;
7. monitorear logs y metricas post despliegue.

## Seguridad y privacidad

## Reglas base

- no almacenar credenciales en el repositorio;
- usar secretos por entorno;
- restringir CORS a origenes permitidos;
- proteger endpoints administrativos por rol;
- registrar eventos de auditoria en operaciones criticas;
- definir retencion de datos para sesiones y eventos.

## Politica de captura de actividad

La captura base de actividad queda definida por:

- `docs/CONTRATO_CAPTURA_ACTIVIDAD.md`;
- alcance minimo de informacion operativa;
- validacion estricta contra allowlist;
- restriccion por turno y sesion activa;
- acceso por rol a consultas globales.

Antes de pasar a produccion formal debe cerrarse ademas:

- base legal o politica interna aplicable;
- tiempo de retencion definitivo;
- criterio de exportacion y auditoria;
- automatizacion de purga o archivado si aplica.

## Operacion y monitoreo

## Salud y observabilidad

El sistema debe evolucionar para incluir:

- `healthcheck`;
- `readiness check`;
- logs estructurados;
- correlacion por request o sesion;
- metricas de errores, latencia y uso;
- alertas minimas por caida de API o fallos de BD.

## Monitoreo recomendado

- disponibilidad del backend;
- errores 4xx y 5xx por endpoint;
- latencia de autenticacion y turnos;
- ejecucion de migraciones;
- crecimiento de tablas de eventos;
- consumo de recursos del servidor.

## Backups y recuperacion

Debe existir un procedimiento documentado para:

- backups diarios de PostgreSQL;
- verificacion periodica de restauracion;
- retencion diferenciada por entorno;
- recuperacion ante falla de despliegue o corrupcion.

## Estrategia de mantenimiento

## Mantenimiento correctivo

- correccion de bugs con reproduccion documentada;
- pruebas obligatorias antes de cerrar la correccion;
- commits pequenos y trazables;
- despliegue controlado en staging antes de produccion.

## Mantenimiento evolutivo

- cada cambio relevante entra como fase o subfase;
- cada modulo nuevo debe incluir documentacion y pruebas;
- no se agregan features si la base del modulo actual no esta cerrada.

## Mantenimiento preventivo

- actualizacion de dependencias;
- revision de seguridad de paquetes;
- revision de logs y errores repetitivos;
- limpieza de deuda tecnica priorizada por impacto.

## Estrategia de calidad

## Minimo por cada cambio relevante

- compilacion correcta;
- pruebas unitarias del modulo tocado;
- pruebas HTTP cuando aplique;
- documentacion actualizada;
- revision de permisos y seguridad.

## Objetivo a mediano plazo

Agregar:

- pruebas de integracion con base real o temporal;
- pipeline automatizado;
- validacion previa a merge;
- cobertura minima sobre modulos criticos.

## Riesgos principales del proyecto

- crecer frontend antes de cerrar el backend operativo;
- capturar eventos sin criterio legal o tecnico claro;
- mezclar logica de negocio con controladores HTTP;
- sobrecargar la base transaccional con analitica prematura;
- no definir permisos por rol de forma estricta;
- documentar tarde y perder trazabilidad del proyecto.

## Regla de gobierno del proyecto

Toda decision de arquitectura, despliegue o captura de datos que cambie el alcance del sistema debe reflejarse en:

- `README.md` si afecta la vista general del proyecto;
- `docs/CONTROL_PROYECTO.md` si afecta una fase en curso o cerrada;
- este documento si cambia el plan maestro de desarrollo, despliegue o mantenimiento.

## Siguiente hito recomendado

Con la Fase 5 cerrada, el siguiente hito es la Fase 6:

- definir alertas operativas sobre inactividad, baja cobertura y acumulacion de novedades;
- incorporar auditoria, exportaciones y observabilidad;
- ampliar pruebas de integracion con persistencia real y agregar pruebas automatizadas de frontend.
