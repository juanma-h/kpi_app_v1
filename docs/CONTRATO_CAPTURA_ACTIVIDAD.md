# Contrato de Captura de Actividad

## Proposito

Este documento define el contrato tecnico base para la captura de actividad web durante la Fase 3.

Su objetivo es evitar una ingesta improvisada de datos y dejar reglas minimas claras antes de construir KPIs operativos.

## Alcance inicial

La captura de actividad de esta fase queda limitada a:

- usuarios autenticados;
- turnos abiertos;
- sesiones activas;
- dominios incluidos y activos en la allowlist;
- eventos minimos de navegacion y presencia operativa.

No se captura informacion fuera de esos limites.

## Endpoint de ingesta

Ruta:

- `POST /activity/events`

Reglas base:

- requiere token Bearer valido;
- el backend resuelve `user_id`, `shift_id` y `session_id` desde el contexto autenticado;
- el cliente solo envia el evento y la URL de origen;
- el backend rechaza eventos fuera de la allowlist o sin turno/sesion activa.

## Tipos de evento permitidos

Los tipos de evento iniciales quedan cerrados en:

- `PAGE_VIEW`: cambio de pagina o carga relevante dentro de un dominio permitido;
- `HEARTBEAT`: confirmacion periodica de presencia activa en una pagina permitida;
- `IDLE`: cambio a estado de inactividad;
- `RESUME`: retorno desde inactividad a actividad.

No se aceptan otros tipos en esta fase.

## Reglas de payload

Campos esperados:

- `event_type`
- `source_url`
- `page_title` opcional
- `occurred_at` opcional, pero si se envia debe incluir zona horaria
- `duration_seconds` solo para `HEARTBEAT` e `IDLE`
- `event_data` opcional como diccionario plano y acotado

Reglas:

- `source_url` debe ser `http` o `https`;
- `duration_seconds` no se admite para `PAGE_VIEW` ni `RESUME`;
- `duration_seconds` es obligatorio para `HEARTBEAT` e `IDLE`;
- los eventos no pueden llegar con desfase futuro invalido;
- los eventos demasiado antiguos se rechazan.

## Frecuencia operativa recomendada

La frecuencia acordada para la etapa web inicial es:

- `PAGE_VIEW`: en cada cambio de ruta o carga relevante;
- `HEARTBEAT`: cada 60 segundos mientras exista actividad real en una pagina permitida;
- `IDLE`: cuando se supere un umbral de inactividad del cliente, recomendado en 300 segundos;
- `RESUME`: inmediatamente al salir del estado `IDLE`.

Estas reglas sirven como contrato de referencia para el frontend o agente web que se implemente despues.

## Mecanismo de captura definido para el proyecto

La captura de actividad del proyecto se hara por instrumentacion del cliente web autenticado.

Esto significa:

- no se haran scrapers del lado servidor para actividad de usuario;
- no se haran capturas ciegas de navegacion sin sesion autenticada;
- el frontend o agente web debera emitir eventos al backend usando el token del usuario;
- la validacion final siempre queda del lado del backend.

## Regla de allowlist

Un evento solo es valido si el `source_url` pertenece a:

- un dominio exacto activo de la allowlist; o
- un subdominio de un dominio activo de la allowlist.

Ejemplos validos si existe `example.com`:

- `https://example.com/home`
- `https://portal.example.com/reportes`

Ejemplos invalidos:

- `https://example.net/home`
- `chrome://settings`
- `file:///documento-local`

## Criterio de privacidad y captura minima

En esta fase queda expresamente fuera de alcance capturar:

- contenido de formularios;
- teclas presionadas;
- portapapeles;
- capturas de pantalla;
- contenido textual sensible;
- credenciales o datos privados de terceros.

La captura minima aceptada es:

- tipo de evento;
- URL de origen;
- dominio normalizado;
- titulo de pagina si existe;
- timestamp del evento;
- duracion si aplica;
- metadatos tecnicos acotados.

## Acceso operativo a los eventos

Durante esta fase se define:

- el empleado puede registrar eventos y consultar sus propios eventos;
- `SUPERVISOR` y `ADMIN` pueden consultar eventos globales;
- la administracion de dominios permitidos sigue reservada para `ADMIN`.

## Retencion operativa inicial

Como regla tecnica inicial para desarrollo y primeras pruebas de despliegue:

- los eventos crudos se deben tratar como datos operativos de retencion limitada;
- la politica objetivo de referencia para produccion sera de 90 dias, salvo que una politica interna obligue otro periodo;
- la automatizacion de purga no se implementa en esta fase y queda para operacion y gobierno.

## Uso de esta fase para la Fase 4

La Fase 4 debe apoyarse en este contrato para construir KPIs sin redefinir la ingesta.

Los primeros indicadores deberian derivarse solo de:

- `PAGE_VIEW`
- `HEARTBEAT`
- `IDLE`
- `RESUME`

y no de datos mas invasivos.
