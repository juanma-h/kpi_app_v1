# Prompts para diseñar la App en Pencil con Codex

## Proposito

Este documento contiene prompts listos para usar al probar Codex con Pencil por MCP.

La idea es no improvisar cada pantalla, sino mantener continuidad visual, jerarquia operativa y alineacion con el backend ya construido.

## Como usarlos

- usa primero el `Prompt 0` para definir la base visual del producto;
- despues ejecuta los prompts de pantallas en el orden recomendado;
- manten el mismo estilo, colores, tipografia y componentes entre pantallas;
- no mezcles experiencia de empleado con panel administrativo en una misma vista;
- diseña siempre en español.

## Orden recomendado

1. sistema visual base;
2. login;
3. dashboard del empleado;
4. mi turno;
5. mi horario;
6. mis KPIs;
7. vista general del supervisor;
8. detalle de empleado;
9. administracion de usuarios;
10. allowlist de dominios;
11. plantillas y asignaciones de horarios.

## Prompt 0. Sistema visual base

```text
diseña la base visual de una aplicacion web de supervision operativa de empleados llamada KPI App. La interfaz debe sentirse profesional, clara, moderna y orientada a operacion diaria, no a marketing. Quiero una propuesta desktop-first de 1440 px de ancho con variantes responsive previstas para mobile. Usa una identidad sobria pero con personalidad: fondo claro con capas suaves, tarjetas limpias, alto contraste, tipografia expresiva para titulos y una tipografia legible para tablas y formularios. Evita estilos genericos, evita el morado como color dominante y evita que parezca una plantilla comun de dashboard.

Define dentro del diseno:
- paleta principal con colores para exito, advertencia, error, estado neutro y accion principal;
- tipografia para headings y tipografia para texto y tablas;
- estilos base de boton primario, secundario y boton fantasma;
- estilos de cards KPI, tablas, badges de estado y filtros;
- estados visuales para activo, sin turno, tarde, baja cobertura y sin horario;
- propuesta de sidebar y topbar para una app empresarial.

Quiero una composicion elegante y operativa, con espacio suficiente para tablas, indicadores y formularios. La interfaz debe sentirse preparada para roles EMPLOYEE, SUPERVISOR y ADMIN. Usa nombres y etiquetas en español.
```

## Prompt 1. Pantalla de login

```text
diseña la pantalla web de login de KPI App para acceso de empleados, supervisores y administradores. La pantalla debe verse profesional, confiable y rapida de usar. Quiero un layout de dos columnas en desktop: a la izquierda una zona de identidad del producto y a la derecha el formulario de acceso. En mobile debe apilarse verticalmente sin perder claridad.

Incluye:
- nombre del producto KPI App;
- mensaje corto que explique que la plataforma sirve para supervision operativa, turnos, horarios y KPIs;
- formulario con correo y contrasena;
- boton principal Entrar;
- enlace o ayuda secundaria para soporte futuro;
- estado de error de credenciales;
- estado de usuario inactivo;
- estado de carga.

La pantalla no debe verse como una landing page comercial. Debe sentirse interna, corporativa y muy clara. Usa el sistema visual definido para la app, con fondo cuidado, jerarquia tipografica y foco fuerte en el formulario. Todo en español.
```

## Prompt 2. Dashboard del empleado

```text
diseña el dashboard principal del empleado para KPI App. Esta pantalla debe responder a una pregunta: que necesito hacer ahora y como voy hoy. Quiero una interfaz desktop-first dentro de un App Shell con sidebar y topbar. Debe sentirse operativa, limpia y orientada a accion rapida.

Incluye estos bloques:
- header con saludo, fecha actual y estado general del turno;
- card de turno actual con estado abierto o cerrado;
- card de horario esperado de hoy;
- card de puntualidad del ultimo turno evaluable;
- acciones rapidas para iniciar turno, cerrar turno, ver horario y ver mis KPIs;
- resumen de actividad del dia con cobertura, tiempo activo, tiempo inactivo y ultimo evento;
- timeline corta de actividad reciente;
- badges de estado claros.

Quiero que la prioridad visual sea: estado del turno, acciones rapidas y resumen operativo. No conviertas esto en un dashboard lleno de graficas innecesarias. Debe verse rapido, util y profesional. Usa etiquetas en español y deja prevista una version mobile con tarjetas apiladas.
```

## Prompt 3. Pantalla Mi Turno

```text
diseña la pantalla Mi Turno de KPI App para el rol EMPLOYEE. La vista debe permitir abrir, consultar y cerrar el turno actual con el menor esfuerzo posible. Quiero una pantalla muy clara, centrada en el estado del turno y en las acciones disponibles.

Incluye:
- header con titulo Mi turno y contexto del dia;
- card principal con estado del turno actual;
- hora real de inicio;
- dispositivo o equipo asociado;
- boton principal para iniciar turno cuando no exista uno activo;
- boton de cerrar turno cuando el turno este abierto;
- bloque de sesion actual;
- bloque pequeno con horario esperado del dia y margen de tolerancia;
- mensajes de estado para sin turno, turno activo, turno cerrado y error operativo.

La pantalla debe evitar ruido visual. El objetivo es que un empleado entienda en segundos si ya esta en turno o si necesita abrirlo. Todo en español, siguiendo el sistema visual definido para la aplicacion.
```

## Prompt 4. Pantalla Mi Horario

```text
diseña la pantalla Mi Horario para KPI App. Esta vista debe mostrar al empleado su horario esperado de forma simple y confiable. Quiero un layout claro dentro del App Shell, con foco en la jornada del dia y un contexto semanal.

Incluye:
- header con titulo Mi horario;
- card principal con horario resuelto para la fecha seleccionada;
- hora esperada de entrada;
- hora esperada de salida;
- zona horaria;
- margen de tolerancia;
- estado visual cuando no exista horario asignado;
- bloque secundario con vista semanal simple o lista de dias con franjas horarias;
- selector de fecha;
- mensajes de estado para horario normal, turno nocturno y sin horario.

La pantalla debe sentirse util para consulta diaria, no como un modulo de administracion. Usa español y prioriza legibilidad.
```

## Prompt 5. Pantalla Mis KPIs

```text
diseña la pantalla Mis KPIs para KPI App enfocada en el empleado. Quiero una vista operativa y comprensible, no una pantalla analitica excesiva. El objetivo es que el empleado vea rapidamente sus indicadores recientes y entienda su cumplimiento.

Incluye:
- header con titulo Mis KPIs y selector de rango de fechas;
- cards KPI para cobertura, tiempo activo, tiempo inactivo, puntualidad y turnos evaluados;
- bloque de detalle del ultimo turno con inicio real, horario esperado, retraso y cobertura;
- grafica simple o barra comparativa de actividad del rango;
- lista breve de observaciones o insights operativos;
- estados de vacio y datos parciales.

Quiero un diseno claro, con lenguaje visual corporativo y sin sobrecargar de graficas decorativas. La prioridad debe ser la lectura rapida y la comprension del estado personal del empleado.
```

## Prompt 6. Vista general del supervisor

```text
diseña la pantalla principal de supervision del equipo para KPI App. Esta vista corresponde al rol SUPERVISOR y debe permitir entender rapidamente como va el equipo hoy. Quiero una interfaz desktop-first con App Shell, filtros y una tabla central robusta.

Incluye:
- header con titulo Equipo hoy;
- filtros por fecha, estado y criterio operativo;
- cards KPI con empleados activos, retrasos, sin turno y baja cobertura;
- tabla principal del equipo con nombre, estado del turno, horario esperado, puntualidad, cobertura de actividad, ultimo evento y accion ver detalle;
- panel secundario con llegadas tarde, empleados sin horario y actividad reciente del equipo;
- estados visuales de prioridad usando badges y colores operativos.

La pantalla debe sentirse como una consola de supervision real, no como una landing analitica. Prioriza tabla, filtros y alertas operativas por encima de graficas decorativas. Todo en español.
```

## Prompt 7. Detalle del empleado para supervisor

```text
diseña la pantalla de detalle de un empleado para KPI App, accesible desde supervision. El objetivo es que un SUPERVISOR vea en una sola vista el estado operativo del empleado, su turno, su horario y sus KPIs recientes.

Incluye:
- header con nombre del empleado, rol y estado;
- resumen superior con turno actual, horario esperado, puntualidad y cobertura;
- bloque de actividad reciente con timeline o lista ordenada;
- bloque de KPIs del rango seleccionado;
- bloque de historial corto de turnos;
- bloque de horario asignado o resuelto;
- acciones secundarias de filtrado por fecha.

Quiero una vista densa pero clara, preparada para supervision y no para administracion. Debe sentirse precisa, confiable y profesional. Usa tablas compactas, cards limpias y etiquetas en español.
```

## Prompt 8. Administracion de usuarios

```text
diseña la pantalla administrativa de usuarios para KPI App. Esta vista corresponde al rol ADMIN y debe permitir consultar, filtrar y gestionar usuarios de manera ordenada. Quiero una pantalla enfocada en tabla, filtros y acciones seguras.

Incluye:
- header con titulo Usuarios;
- boton principal Crear usuario;
- filtros por rol, estado y busqueda;
- tabla con nombre, correo, rol, estado, fecha de creacion y acciones;
- panel o modal previsto para crear o editar usuario;
- badges para roles EMPLOYEE, SUPERVISOR y ADMIN;
- estados vacios y de error;
- estilo sobrio y muy claro.

La experiencia debe sentirse administrativa, estable y confiable. No quiero una interfaz recargada. Todo en español y alineado con el sistema visual del producto.
```

## Prompt 9. Allowlist de dominios

```text
diseña la pantalla administrativa de allowlist de dominios para KPI App. Esta vista debe permitir al rol ADMIN gestionar los dominios autorizados desde donde se capturara actividad para medir KPIs.

Incluye:
- header con titulo Dominios permitidos;
- descripcion breve del objetivo del modulo;
- boton principal Agregar dominio;
- tabla con dominio, descripcion, estado, fecha de creacion y acciones;
- formulario o panel lateral para crear dominio;
- estados claros para activo e inactivo;
- mensaje explicativo de que solo dominios activos participan en la captura de actividad.

La pantalla debe verse tecnica pero limpia, con foco en la tabla y en la comprension del modulo. Usa español y evita exceso de elementos decorativos.
```

## Prompt 10. Plantillas de horario

```text
diseña la pantalla administrativa de plantillas de horario para KPI App. Esta vista debe permitir al rol ADMIN definir horarios reutilizables por nombre, zona horaria, tolerancia y franjas por dia.

Incluye:
- header con titulo Plantillas de horario;
- boton principal Crear plantilla;
- tabla o lista de plantillas con nombre, zona horaria, tolerancia, estado y acciones;
- panel de detalle o formulario para editar una plantilla;
- representacion visual clara de franjas por dia de la semana;
- estado para plantilla activa e inactiva;
- ayuda visual para turnos nocturnos.

La pantalla debe sentirse administrativa y tecnica, pero no compleja. Quiero que el usuario entienda rapidamente la estructura de una plantilla y pueda editarla con seguridad.
```

## Prompt 11. Asignaciones de horario por usuario

```text
diseña la pantalla administrativa para asignar horarios a usuarios en KPI App. Esta vista corresponde al rol ADMIN y debe conectar usuarios con plantillas de horario dentro de una vigencia de fechas.

Incluye:
- header con titulo Asignaciones de horario;
- filtros por usuario, plantilla y estado;
- tabla con usuario, plantilla, vigencia, estado y acciones;
- boton principal Nueva asignacion;
- formulario o panel lateral con selector de usuario, plantilla, fecha inicial, fecha final y notas;
- indicador visual para conflictos o traslapes;
- mensajes de estado claros.

La pantalla debe priorizar seguridad operativa y legibilidad. Debe sentirse como una herramienta de configuracion confiable para operacion diaria. Usa español y consistencia total con las demas pantallas.
```

## Prompt 12. Prompt maestro para consistencia entre pantallas

```text
Manten consistencia total con el sistema visual ya definido para KPI App. Todas las pantallas deben compartir la misma paleta, tipografia, estructura base de App Shell, estilo de cards, badges, tablas, botones y formularios. La app es una plataforma web de supervision operativa de empleados con enfoque corporativo y funcional. No usar estilos genericos de startup, no usar morado dominante, no saturar con graficas decorativas y no mezclar experiencia de empleado con administracion. diseñar siempre en español, con alta legibilidad y prioridad en operacion diaria.
```

## Recomendacion practica

Cuando uses Codex con Pencil, lo ideal es:

- ejecutar primero `Prompt 0`;
- luego ejecutar `Prompt 12`;
- despues generar una pantalla por prompt, en orden.

Si quieres mejorar la calidad visual de las pruebas, puedes reutilizar esta instruccion al inicio de cada corrida:

```text
Quiero una interfaz web empresarial moderna, clara y sobria para supervision operativa. Prioriza jerarquia, legibilidad, tablas y tarjetas utiles. Evita una estetica generica y evita llenar la pantalla de elementos sin funcion real.
```
