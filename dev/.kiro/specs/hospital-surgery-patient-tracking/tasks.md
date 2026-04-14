# Plan de Implementación: Sistema de Seguimiento de Pacientes Quirúrgicos

## Descripción general

Implementación incremental del MVP Quiroinfo en Django + HTMX + Tailwind CSS (CDN) + Alpine.js + PostgreSQL. Tres apps Django: `app_autenticacion`, `app_core`, `app_notificaciones`.

## Tareas

- [x] 1. Configurar el proyecto Django y estructura base
  - Crear el proyecto `quiroinfo` con `django-admin startproject`
  - Crear las tres apps: `app_autenticacion`, `app_core`, `app_notificaciones`
  - Configurar `settings.py`: `INSTALLED_APPS`, base de datos PostgreSQL, `SESSION_COOKIE_AGE = 7200`, `LOGGING` básico a consola, `EMAIL_WHITELIST` y `EMAIL_DOMINIO_PERMITIDO` (vacíos por defecto)
  - Crear `requirements.txt` con: `django`, `psycopg2-binary`, `pytest-django`, `factory-boy`
  - Crear `pytest.ini` apuntando a `settings` de test
  - _Requisitos: 6.6, 6.7_

- [x] 2. Implementar modelos de datos y migraciones
  - [x] 2.1 Crear modelos en `app_core/models.py`
    - `EstadoQuirurgico` TextChoices: EN_PREPARACION, EN_CIRUGIA, EN_RECUPERACION, FINALIZADO, OTRO
    - `Paciente`: `identificacion` (unique), `nombre` (nullable), `origen` (PROGRAMADO/URGENCIAS); `db_table = 'pacientes'`
    - `Sesion`: UUID PK, FK a `Paciente` (PROTECT), `estado`, `descripcionOtro` (nullable, max 50), `ingresadoEn`, `actualizadoEn`, `oculto`; `UniqueConstraint` sobre `paciente` cuando `oculto=False`; `Index` sobre `['oculto', 'ingresadoEn']`; `db_table = 'sesiones'`
    - `RegistroEstado` *(opcional)*: UUID PK, FK a `Sesion`, `estadoAnterior` (nullable), `estadoNuevo`, `cambiadoEn`; `db_table = 'registro_estados'`
    - _Requisitos: 1.1, 3.1, 4.7, 8.1, 8.2, 9.1, 9.2, 10.1, 10.3_

  - [x] 2.2 Generar y aplicar migraciones
    - `makemigrations app_core` y `migrate`
    - _Requisitos: 1.1_

- [x] 3. Implementar lógica de negocio en `app_core/servicios.py`
  - [x] 3.1 Implementar `SesionServicio`
    - `aplicarEstado (paciente, nuevoEstado, descripcionOtro=None)`: valida estado OTRO (descripción requerida, truncar a 50 chars, strip); `get_or_create` de `Sesion` por `paciente` con `oculto=False`; actualiza estado; marca `oculto=True` si FINALIZADO (sin eliminar); fuerza `descripcionOtro=None` si estado no es OTRO; crea `RegistroEstado`; llama a `logging.info()`
    - _Requisitos: 3.4, 3.5, 3.6, 3.7, 4.4, 4.5, 4.7, 7.1, 8.1, 10.2, 11.1, 11.2, 11.3, 13.2_

  - [x] 3.2 Implementar `obtenerSesionesVisibles ()`
    - Filtra `oculto=False`, `select_related ('paciente')`, ordena por `-ingresadoEn`, retorna solo campos necesarios
    - _Requisitos: 2.2, 2.3, 5.1, 12.1, 12.2_

  - [ ]* 3.3 Escribir tests unitarios para `SesionServicio`
    - `aplicarEstado()`: crea sesión nueva si no existe
    - `aplicarEstado()`: actualiza estado si la sesión ya existe
    - `aplicarEstado()` con FINALIZADO: `oculto=True`, registro conservado en BD
    - `aplicarEstado()` con OTRO: guarda `descripcionOtro` truncado a 50 chars
    - `aplicarEstado()` con OTRO sin descripción: lanza `ValidationError`
    - `aplicarEstado()` con estado distinto a OTRO: `descripcionOtro` es None
    - `obtenerSesionesVisibles()`: no retorna sesiones con `oculto=True`
    - `obtenerSesionesVisibles()`: retorna sesiones ordenadas por `ingresadoEn` descendente
    - Usar `factory_boy` para fixtures
    - _Requisitos: 3.4, 3.5, 3.6, 3.7, 11.1, 11.2, 12.1_

- [x] 4. Implementar `NotificacionServicio` en `app_notificaciones/servicios.py`
  - `notificarCambioEstado (identificacion, nuevoEstado)`: `logging.info()` con identificacion y nuevo estado
  - Sin dependencias externas; sin modelos propios
  - _Requisitos: 7.1, 7.2, 7.3_

- [x] 5. Checkpoint — Asegurarse de que todos los tests pasen
  - Ejecutar `pytest` y verificar que los tests de servicios pasen. Consultar al usuario si hay dudas.

- [x] 6. Implementar autenticación simplificada por email
  - [x] 6.1 Crear `LoginRequeridoMixin` en `app_autenticacion/mixins.py`
    - Verifica `request.session['email']`; redirige a `login` si no existe
    - _Requisitos: 6.7_

  - [x] 6.2 Implementar `LoginVista` y `LogoutVista` en `app_autenticacion/vistas.py`
    - `LoginVista`: GET muestra formulario; POST valida formato email con regex; si formato válido, verifica whitelist/dominio desde settings; guarda en sesión y redirige a `gestion`
    - `LogoutVista`: POST limpia sesión, redirige a `login`
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.3 Crear template `autenticacion/login.html`
    - Formulario centrado, Tailwind CSS, campo email, mensaje de error inline
    - _Requisitos: 6.1, 6.3, 6.5_

- [x] 7. Implementar vistas del Panel de Gestión en `app_core/vistas.py`
  - [x] 7.1 Implementar `GestionVista`
    - CBV con `LoginRequeridoMixin`
    - GET: retorna contexto con `pacientes` (todos), `sesionesActivas` (no ocultas), `estados` (lista de EstadoQuirurgico)
    - _Requisitos: 1.2, 4.1, 4.2, 4.3_

  - [x] 7.2 Implementar `AplicarEstadoVista`
    - CBV con `LoginRequeridoMixin`, POST
    - Recibe `pacienteId`, `estado`, `descripcionOtro` (opcional); obtiene instancia `Paciente`
    - Llama a `SesionServicio.aplicarEstado()` y `NotificacionServicio.notificarCambioEstado()`
    - Retorna fragmento HTMX con las dos tablas actualizadas, o HTTP 400/500 con mensaje de error
    - _Requisitos: 3.4, 3.5, 3.6, 4.4, 4.5, 4.6, 4.7, 4.8, 13.1, 13.2, 13.3, 13.4_

  - [x] 7.3 Implementar `AgregarPacienteVista`
    - CBV con `LoginRequeridoMixin`, POST
    - Crea `Paciente` con `identificacion`, `nombre` y `origen=URGENCIAS`
    - Retorna fragmento HTMX con la Tabla_Programados actualizada
    - _Requisitos: 1.3, 1.4, 9.4_

- [x] 8. Implementar vistas del Tablero Público en `app_core/vistas.py`
  - [x] 8.1 Implementar `TableroVista` y `TableroFragmentoVista`
    - `TableroVista`: sin auth, template completo con layout TV
    - `TableroFragmentoVista`: sin auth, retorna solo el fragmento de lista para HTMX polling
    - Ambas usan `obtenerSesionesVisibles()` y `coloresEstado`
    - _Requisitos: 2.1, 2.2, 2.3, 2.4, 5.1, 5.2, 12.1, 12.2_

  - [x] 8.2 Escribir tests básicos de vistas
    - `/tablero/` carga sin autenticación (HTTP 200)
    - `/tablero/fragmento/` no retorna sesiones con `oculto=True`
    - `/tablero/fragmento/` no incluye el campo `nombre` en la respuesta
    - `/gestion/` redirige a `/login/` sin sesión activa
    - Login con email de dominio no autorizado retorna error HTTP 200 con mensaje
    - _Requisitos: 2.1, 5.1, 5.2, 6.5, 6.7_

- [x] 9. Checkpoint — Asegurarse de que todos los tests pasen
  - Ejecutar `pytest` y verificar que tests de servicios y vistas pasen. Consultar al usuario si hay dudas.

- [x] 10. Crear templates
  - [x] 10.1 Crear template base `base.html`
    - Tailwind CSS CDN, Alpine.js CDN, HTMX CDN
    - Bloque `{% block contenido %}`
    - _Requisitos: 4.1_

  - [x] 10.2 Crear template `tablero/tablero.html`
    - Layout pantalla completa, texto mínimo 48px para `identificacion` y estado
    - `hx-get="/tablero/fragmento/"`, `hx-trigger="every 15s"`, `hx-swap="innerHTML"`
    - Indicador "Sin conexión" con Alpine.js cuando HTMX falla (`htmx:sendError`)
    - Mensaje "No hay pacientes en seguimiento" si lista vacía
    - _Requisitos: 2.1, 2.4, 2.5, 2.6, 2.7_

  - [x] 10.3 Crear template `tablero/fragmento.html`
    - Tarjetas: `identificacion`, badge de estado con color Tailwind, `descripcionOtro` (si OTRO), `ingresadoEn`
    - Sin datos personales (sin `nombre`)
    - Orden descendente por `ingresadoEn` (más reciente arriba)
    - _Requisitos: 2.2, 2.3, 3.2, 5.1, 12.1, 12.2_

  - [x] 10.4 Crear template `gestion/gestion.html`
    - Layout dos columnas paralelas (`grid grid-cols-2` o `flex`)
    - Columna izquierda: Tabla_Programados con radio buttons de estado por fila; botón "Adicionar paciente" al pie
    - Columna derecha: Tabla_En_Sala con IDENTIFICACION, ESTADO, HORA INGRESO
    - Radio buttons: cinco botones visuales por fila, el activo destacado con color; Alpine.js para mostrar campo de texto (máx. 50 chars) cuando se selecciona OTRO
    - HTMX: cada radio button hace POST a `/gestion/sesiones/estado/` y actualiza ambas tablas
    - _Requisitos: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 3.4, 3.5, 13.1, 13.3_

  - [x] 10.5 Crear template `gestion/fragmento_tablas.html` (fragmento HTMX)
    - Contiene ambas tablas para ser reemplazadas en bloque tras cada acción
    - _Requisitos: 4.4, 4.5_

- [x] 11. Configurar URLs y cablear todas las vistas
  - `quiroinfo/urls.py`: incluye URLs de las tres apps
  - `app_autenticacion/urls.py`: `/login/`, `/logout/`
  - `app_core/urls.py`: `/`, `/tablero/`, `/tablero/fragmento/`, `/gestion/`, `/gestion/pacientes/agregar/`, `/gestion/sesiones/estado/`
  - _Requisitos: 2.1, 6.1, 6.7, 4.1_

- [x] 12. Checkpoint final — Asegurarse de que todos los tests pasen
  - Ejecutar `pytest` y verificar que la suite completa pase sin errores. Consultar al usuario si hay dudas.

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- `RegistroEstado` es opcional; si se omite, eliminar su creación en `SesionServicio.aplicarEstado()`
- La tabla `pacientes` se puede poblar con datos fake en tests y en desarrollo con un fixture o comando de management
- No usar Celery, DRF, WebSockets, Twilio ni Hypothesis en ninguna tarea
- Nomenclatura: clases PascalCase, funciones/variables camelCase, identificadores de dominio en español
- Espacio entre nombre de función y paréntesis: `funcion ()`, `variable []`
- `EMAIL_WHITELIST` y `EMAIL_DOMINIO_PERMITIDO` se configuran en `settings.py`; si ambos están vacíos, el login deniega acceso por defecto
