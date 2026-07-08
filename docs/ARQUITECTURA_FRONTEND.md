# Arquitectura Frontend y Wireframes Funcionales

## Proposito

Este documento define la arquitectura inicial del frontend web y los wireframes funcionales base del MVP.

La intencion es evitar que la interfaz se construya pantalla por pantalla sin estructura, sin criterio de roles y sin continuidad con el backend ya cerrado.

## Objetivo del frontend

El frontend debe permitir:

- acceso rapido para empleados desde navegador;
- supervision operativa para lideres o supervisores;
- administracion controlada para usuarios con rol `ADMIN`;
- consumo ordenado de los modulos backend ya existentes;
- crecimiento posterior hacia alertas, auditoria y reportes.

## Principios del frontend

- una sola aplicacion web, con experiencia segmentada por rol;
- navegacion simple y orientada a tarea;
- primero operacion, despues analitica avanzada;
- consistencia visual entre modulos;
- responsive desde el inicio;
- estados vacios, errores y carga definidos desde el diseno.

## Roles y experiencia

### EMPLOYEE

Foco principal:

- saber si tiene turno activo;
- iniciar o cerrar turno;
- consultar horario esperado;
- ver su estado operativo y sus KPIs basicos.

### SUPERVISOR

Foco principal:

- ver como va el equipo hoy;
- detectar ausencias, retrasos o baja cobertura;
- consultar detalle por empleado, turno y horario;
- no administrar configuracion global.

### ADMIN

Foco principal:

- administrar usuarios;
- administrar dominios permitidos;
- administrar plantillas y asignaciones de horario;
- mantener el sistema operativo y consistente.

## Arquitectura de navegacion

## Rutas publicas

- `/login`
- `/unauthorized`

## Rutas autenticadas compartidas

- `/app/dashboard`
- `/app/profile`
- `/app/help`

## Rutas para EMPLOYEE

- `/app/dashboard`
- `/app/shift`
- `/app/activity`
- `/app/schedule`
- `/app/kpis/me`

## Rutas para SUPERVISOR

- `/app/team/overview`
- `/app/team/activity`
- `/app/team/shifts`
- `/app/team/schedules`
- `/app/team/kpis`
- `/app/team/users/:id`

## Rutas para ADMIN

- `/app/admin/users`
- `/app/admin/users/:id`
- `/app/admin/allowlist`
- `/app/admin/schedules`
- `/app/admin/settings`

## Rutas futuras

- `/app/alerts`
- `/app/audit`
- `/app/reports`

## Shell de aplicacion

La aplicacion debe usar un `App Shell` comun con estas zonas:

- barra lateral con navegacion por rol;
- header superior con contexto, busqueda futura y perfil;
- contenedor principal de contenido;
- area de notificaciones;
- soporte para vista desktop y mobile.

### Sidebar

Debe contener:

- logo o nombre del sistema;
- modulos habilitados segun rol;
- acceso visible al dashboard principal;
- cierre de sesion.

### Header

Debe contener:

- titulo de la vista actual;
- subtitulo o contexto de fecha;
- acciones rapidas segun pantalla;
- avatar y menu del usuario autenticado.

## Arquitectura de modulos frontend

La organizacion recomendada es por dominio funcional, no por tipo de archivo suelto.

```text
frontend/
  src/
    app/
      router/
      providers/
      guards/
      layout/
    modules/
      auth/
      shifts/
      activity/
      schedules/
      kpis/
      users/
      allowlist/
      supervisor/
    components/
      ui/
      feedback/
      data-display/
      forms/
    services/
      api/
      session/
    hooks/
    types/
    utils/
    styles/
```

## Modulos funcionales

### auth

Responsabilidad:

- login;
- persistencia de sesion;
- refresh futuro si se incorpora;
- guards por autenticacion y rol.

### shifts

Responsabilidad:

- abrir turno;
- consultar turno actual;
- cerrar turno;
- exponer estado del turno en la interfaz.

### activity

Responsabilidad:

- mostrar actividad reciente del usuario;
- mostrar trazabilidad basica;
- preparar la integracion del capturador web.

### schedules

Responsabilidad:

- visualizar horario resuelto del empleado;
- administrar plantillas;
- administrar asignaciones por usuario.

### kpis

Responsabilidad:

- overview propio;
- overview global para supervision;
- detalle por turno;
- indicadores resumidos y comparables.

### users

Responsabilidad:

- CRUD administrativo;
- filtros por rol y estado;
- activacion y desactivacion;
- detalle por usuario.

### allowlist

Responsabilidad:

- lista de dominios permitidos;
- alta o baja logica;
- descripcion operativa de cada dominio.

### supervisor

Responsabilidad:

- consolidar vistas transversales del equipo;
- mostrar alertas operativas futuras;
- conectar actividad, horarios, turnos y KPIs en una sola experiencia.

## Componentes base del sistema

Antes de implementar pantallas completas conviene definir estos componentes:

- `AppShell`
- `SidebarNav`
- `TopBar`
- `PageHeader`
- `StatCard`
- `StatusBadge`
- `DataTable`
- `FilterBar`
- `EmptyState`
- `ErrorState`
- `LoadingState`
- `PrimaryButton`
- `SecondaryButton`
- `FormField`
- `DateRangePicker`
- `UserAvatarChip`
- `RoleBadge`

## Wireframes funcionales del MVP

Las primeras pantallas a diseñar deben ser:

- login;
- dashboard del empleado;
- vista general del supervisor.

## Pantalla 1. Login

Ruta:

- `/login`

Objetivo:

- autenticar al usuario con rapidez y claridad.

Estructura funcional:

```text
+-----------------------------------------------------------+
| Branding / mensaje de valor        | Formulario login     |
| supervision operativa              | Email                |
| control de turnos y actividad      | Password             |
| breve texto institucional          | Recordarme despues   |
|                                    | Boton entrar         |
|                                    | enlace ayuda futura  |
+-----------------------------------------------------------+
```

Bloques:

- panel visual o institucional;
- formulario de acceso;
- feedback de error de credenciales;
- estado de carga al enviar.

Reglas de UX:

- el formulario debe ser el foco principal;
- el mensaje de error debe quedar junto al formulario, no como modal;
- si la sesion ya existe, redirigir al dashboard correspondiente por rol.

Estados:

- inicial;
- cargando;
- credenciales invalidas;
- usuario inactivo;
- error de conectividad.

Mobile:

- apilar branding arriba y formulario abajo;
- mantener boton visible sin scroll excesivo.

## Pantalla 2. Dashboard del empleado

Ruta:

- `/app/dashboard`

Objetivo:

- mostrar al empleado lo que necesita hacer ahora y su estado del dia.

Estructura funcional:

```text
+---------------------------------------------------------------+
| Header: saludo, fecha, estado del turno                       |
+---------------------------------------------------------------+
| Card turno actual | Card horario de hoy | Card puntualidad    |
+---------------------------------------------------------------+
| Acciones rapidas: iniciar turno / cerrar turno / ver horario  |
+---------------------------------------------------------------+
| Resumen de actividad de hoy                                   |
| cobertura | tiempo activo | tiempo inactivo | ultimo evento   |
+---------------------------------------------------------------+
| Timeline o lista corta de actividad reciente                  |
+---------------------------------------------------------------+
```

Bloques:

- estado del turno actual;
- horario esperado del dia;
- puntualidad del ultimo turno evaluable;
- acciones rapidas;
- resumen KPI personal;
- actividad reciente.

Acciones principales:

- iniciar turno;
- cerrar turno;
- ir a mi horario;
- ir a mis KPIs.

Estados:

- sin turno iniciado;
- turno activo;
- sin horario asignado;
- sin actividad aun;
- error de carga parcial.

Mobile:

- cards apiladas;
- acciones rapidas en botones grandes;
- timeline resumida a los ultimos eventos relevantes.

## Pantalla 3. Vista general del supervisor

Ruta:

- `/app/team/overview`

Objetivo:

- permitir supervision diaria del equipo sin entrar primero al detalle de cada empleado.

Estructura funcional:

```text
+-------------------------------------------------------------------+
| Header: equipo hoy, filtros de fecha, area futura, refresco       |
+-------------------------------------------------------------------+
| KPI cards: activos | retrasos | sin turno | baja cobertura        |
+-------------------------------------------------------------------+
| Tabla principal de equipo                                          |
| empleado | turno | horario | puntualidad | cobertura | estado      |
+-------------------------------------------------------------------+
| Panel secundario                                                   |
| llegadas tarde | dominios activos | actividad reciente del equipo  |
+-------------------------------------------------------------------+
```

Bloques:

- filtros globales;
- KPIs resumidos del dia;
- tabla priorizada de empleados;
- panel lateral o inferior con focos operativos.

Columnas clave de la tabla:

- nombre del empleado;
- rol o area futura;
- estado del turno;
- horario esperado;
- puntualidad;
- cobertura de actividad;
- ultimo evento;
- accion de ver detalle.

Acciones principales:

- abrir detalle del empleado;
- filtrar por estado;
- filtrar por fecha;
- filtrar por baja cobertura o retraso.

Estados:

- equipo sin actividad registrada;
- sin empleados en el rango;
- datos parciales por falta de horario;
- error de consulta global.

Mobile:

- la tabla debe pasar a tarjetas compactas por empleado;
- mantener primero los estados criticos y despues el resto.

## Reglas visuales para el diseno

- no mezclar panel administrativo con experiencia de empleado;
- usar color para prioridad operativa, no como decoracion;
- reservar rojo y amarillo para alertas y retrasos;
- usar badges claros para `activo`, `sin turno`, `tarde`, `sin horario`;
- priorizar legibilidad de tablas y cards sobre elementos decorativos.

## Estados transversales obligatorios

Toda pantalla del frontend debe contemplar:

- carga inicial;
- error de API;
- vacio sin datos;
- vacio por permisos;
- datos parciales;
- accion deshabilitada por contexto.

## Secuencia recomendada de diseno

El siguiente orden de trabajo es el correcto:

1. definir estilo base y componentes comunes;
2. diseñar `login`;
3. diseñar `dashboard` del empleado;
4. diseñar `team overview` del supervisor;
5. diseñar pantallas administrativas de `users`, `allowlist` y `schedules`;
6. diseñar detalles y variantes mobile.

## Siguiente entregable recomendado

Despues de este documento, el siguiente paso deberia ser uno de estos dos:

- bajar estos wireframes a Figma o Pencil para validacion visual;
- crear la arquitectura tecnica del frontend y elegir stack de implementacion.
