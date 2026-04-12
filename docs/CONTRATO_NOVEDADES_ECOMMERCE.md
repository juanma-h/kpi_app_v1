# Contrato del Modulo de Novedades Ecommerce

## Proposito

Este documento define el alcance operativo del modulo de novedades ecommerce, pensado para equipos que trabajan con plataformas como Vendelo y necesitan trazabilidad diaria sobre incidentes, bloqueos, validaciones y casos con impacto en KPIs.

El objetivo del modulo no es reemplazar el sistema externo, sino capturar la gestion operativa alrededor del caso y convertirla en informacion medible dentro de KPI App.

## Alcance actual

El modulo cubre:

- catalogo de areas operativas;
- catalogo de sistemas fuente;
- registro de novedades;
- asignacion de responsable;
- cambios de estado;
- bitacora diaria por novedad;
- KPIs iniciales de gestion.

No cubre aun:

- sincronizacion automatica con APIs externas de Vendelo;
- reapertura formal de casos cerrados;
- exportaciones o auditoria avanzada;
- alertas automaticas por SLA o acumulacion.

## Modelo funcional

### 1. Operational Areas

Representan equipos o frentes operativos que trabajan las novedades.

Ejemplos:

- pagos;
- fraude;
- despacho;
- postventa;
- marketplace;
- soporte ecommerce.

Reglas:

- deben tener codigo y nombre unicos;
- pueden activarse o desactivarse sin borrar historial;
- las novedades nuevas solo pueden registrarse contra areas activas.

### 2. Source Systems

Representan el origen operativo o sistema donde nace la novedad.

Ejemplos:

- Vendelo;
- Shopify;
- ERP;
- CRM;
- pasarela de pagos.

Reglas:

- deben tener codigo y nombre unicos;
- pueden vincularse opcionalmente con un dominio de la allowlist;
- las novedades nuevas solo pueden registrarse contra sistemas fuente activos.

### 3. Novelties

Cada novedad representa un caso operativo gestionable.

Campos clave:

- area operativa;
- sistema fuente;
- usuario reportante;
- usuario asignado;
- referencia externa;
- referencia de pedido;
- referencia de cliente;
- titulo;
- descripcion;
- tipo de novedad;
- prioridad;
- estado;
- metadatos adicionales;
- fecha de reporte;
- turno y sesion cuando existen.

### 4. Novelty Logs

La bitacora registra la gestion diaria por caso.

Cada entrada puede incluir:

- fecha de trabajo;
- tipo de registro;
- contenido textual;
- minutos trabajados;
- estado resultante;
- autor;
- turno y sesion del autor cuando existen.

## Estados de negocio

Estados soportados:

- `OPEN`: caso creado sin gestion efectiva;
- `IN_PROGRESS`: caso en gestion activa;
- `BLOCKED`: caso detenido por dependencia externa o interna;
- `RESOLVED`: caso resuelto funcionalmente;
- `CLOSED`: caso cerrado operativamente.

Reglas actuales:

- toda novedad se crea en `OPEN`;
- una bitacora o cambio de estado puede mover la novedad a otro estado;
- la primera gestion valida marca `first_action_at`;
- al pasar a `RESOLVED` se registra `resolved_at`;
- al pasar a `CLOSED` se registra `closed_at`;
- en esta iteracion no se permite reabrir una novedad `RESOLVED` o `CLOSED`.

## Prioridades

Prioridades soportadas:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Se usan para filtrado, backlog y futuros KPIs de severidad o SLA.

## Tipos de bitacora

Tipos soportados:

- `DAILY_UPDATE`
- `STATUS_CHANGE`
- `ASSIGNMENT`
- `COMMENT`
- `RESOLUTION`

El tipo no reemplaza el estado del caso, pero aporta contexto operativo para analitica y auditoria futura.

## Reglas de acceso

### EMPLOYEE

Puede:

- consultar catalogos activos de areas y sistemas fuente;
- crear novedades;
- consultar novedades propias o asignadas en `GET /novelties/me`;
- consultar una novedad puntual si es reportante o asignado;
- registrar bitacora sobre una novedad a la que tenga acceso;
- consultar sus KPIs personales en `GET /novelties/kpis/me`.

No puede:

- listar backlog global;
- consultar KPIs globales o por otro usuario;
- administrar catalogos operativos;
- editar metadatos administrativos completos de una novedad.

### SUPERVISOR

Puede:

- consultar backlog global;
- consultar KPIs globales y por usuario;
- consultar catalogos operativos con filtros completos;
- reasignar novedades;
- editar novedades;
- cambiar estados.

No puede:

- crear o desactivar catalogos operativos.

### ADMIN

Puede:

- todo lo de `SUPERVISOR`;
- crear y desactivar areas operativas;
- crear y desactivar sistemas fuente.

## Endpoints operativos base

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

## KPIs actuales

El modulo ya expone una capa inicial de KPIs:

- total de novedades;
- backlog abierto;
- novedades asignadas y sin asignar;
- conteo por estado;
- conteo por prioridad;
- conteo por area;
- conteo por sistema fuente;
- conteo por tipo de novedad;
- cantidad de entradas de bitacora;
- cantidad de novedades con gestion documentada;
- minutos totales trabajados;
- promedio de minutos trabajados por novedad;
- tiempo promedio a primera accion;
- tiempo promedio de resolucion.

## Relacion con el frontend

El frontend operativo debe asumir este flujo:

1. consultar catalogos activos;
2. crear novedad;
3. mostrar backlog propio o global segun rol;
4. abrir detalle del caso;
5. registrar bitacora diaria;
6. actualizar estado o asignacion segun permisos;
7. consumir KPIs para vistas personales y de supervision.

## Limitaciones actuales

- no existe sincronizacion con APIs externas;
- no existe trazabilidad de SLA por prioridad;
- no existe archivo adjunto o evidencia documental;
- no existe workflow de reapertura;
- no existe auditoria formal de consulta o exportacion.

Estas capacidades deben entrar como nuevas subfases, no como cambios improvisados sobre el flujo actual.
