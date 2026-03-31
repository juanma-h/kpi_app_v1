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

- completada, validada y lista para commit cuando se decida cerrar el corte actual.

## Regla documental a partir de ahora

Al cerrar cada fase se actualizara este documento con:

- objetivo de la fase;
- cambios implementados;
- decisiones tecnicas tomadas;
- riesgos o limitaciones;
- siguiente fase recomendada.

## Plan maestro del proyecto

Con la Fase 2 cerrada, el plan completo de:

- desarrollo;
- despliegue;
- seguridad;
- operacion;
- monitoreo;
- mantenimiento correctivo y evolutivo;
- roadmap de producto y backend/frontend;

queda documentado en:

- `docs/PLAN_MAESTRO_PROYECTO.md`

## Siguiente fase recomendada

- modelado de eventos de actividad web;
- relacion entre evento, usuario, turno, sesion y dominio permitido;
- definicion del mecanismo de captura de datos para sitios dentro de la allowlist;
- primeras consultas base para indicadores operativos.

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
