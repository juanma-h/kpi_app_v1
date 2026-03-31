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

## Fase 2 planificada

Objetivo principal:

- construir el modulo de usuarios y roles sobre la arquitectura actual.

Alcance propuesto:

- CRUD de usuarios;
- activacion y desactivacion de usuarios;
- roles base `ADMIN`, `SUPERVISOR`, `EMPLOYEE`;
- reglas de permisos mas claras por endpoint;
- validaciones de negocio en servicios;
- pruebas unitarias y, si el entorno acompana, primeras pruebas HTTP.

Entregables esperados:

- modelos y schemas alineados;
- servicios y repositorios del modulo de usuarios;
- endpoints administrativos para gestion de usuarios;
- ampliacion de documentacion del backend;
- commit de cierre de fase.

## Regla documental a partir de ahora

Al cerrar cada fase se actualizara este documento con:

- objetivo de la fase;
- cambios implementados;
- decisiones tecnicas tomadas;
- riesgos o limitaciones;
- siguiente fase recomendada.

## Plan maestro posterior a Fase 2

Cuando la Fase 2 quede cerrada, se creara un documento adicional:

- `docs/PLAN_MAESTRO_PROYECTO.md`

Ese documento concentrara el plan completo de:

- desarrollo;
- despliegue;
- seguridad;
- operacion;
- monitoreo;
- mantenimiento correctivo y evolutivo;
- roadmap de producto y backend/frontend.

La razon para hacerlo despues de la Fase 2 es simple: para ese momento ya tendremos una base backend mas madura y el plan general podra definirse sobre una arquitectura menos provisional.

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
