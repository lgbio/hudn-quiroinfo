# Plan de Implementación: Sistema de Seguimiento de Pacientes Quirúrgicos

## Descripción general

Implementación incremental del MVP Quiroinfo en Django + HTMX + Tailwind CSS (CDN) + Alpine.js + PostgreSQL + Twilio. Cada tarea construye sobre la anterior y termina con la integración completa del sistema.

## Tareas

- [ ] 1. Configurar el proyecto Django y estructura base
  - Crear el proyecto `quiroinfo` con `django-admin startproject`
  - Crear las cinco apps: `app_autenticacion`, `app_pacientes`, `app_sesiones`, `app_notificaciones`, `app_tablero`
  - Configurar `settings.py`: `INSTALLED_APPS`, base de datos PostgreSQL, `AUTH_USER_MODEL = 'app_autenticacion.Usuario'`, `SESSION_COOKIE_AGE = 7200`, variables de entorno para Twilio
  - Crear `requirements.txt` con: `django`, `psycopg2-binary`, `twilio`, `pytest-django`, `factory-boy`
  - Crear `pytest.ini` apuntando a `settings` de test
  - _Requisitos: 6.1, 6.2_

- [ ] 2. Implementar modelos de datos y migraciones
  - [ ] 2.1 Crear modelo `Usuario` en `app_autenticacion/models.py`
    - Extender `AbstractUser` con campo `rol` usando `RolUsuario` (TextChoices)
    - `db_table = 'usuarios'`
    - _Requisitos: 6.1, 6.3_

  - [ ] 2.2 Crear modelo `Paciente` en `app_pacientes/models.py`
    - UUID primary key, `nombreCompleto`, `creadoEn`
    - `db_table = 'pacientes'`
    - _Requisitos: 3.1, 5.2_

  - [ ] 2.3 Crear modelos `SesionActiva` y `RegistroEstado` en `app_sesiones/models.py`
    - `EstadoQuirurgico` TextChoices con los cinco estados en español
    - `SesionActiva`: UUID PK, FK a `Paciente`, `codigoPaciente`, `estado`, `mensaje` (max 80), `telefonoFamiliar`, timestamps, FK a `Usuario`
    - `RegistroEstado`: UUID PK, FK a `SesionActiva`, campos de auditoría
    - `db_table` para cada modelo
    - _Requisitos: 2.1, 3.4, 4.2, 5.1_

  - [ ] 2.4 Crear modelo `RegistroNotificacion` en `app_notificaciones/models.py`
    - UUID PK, FK a `SesionActiva`, `canal`, `estado`, `mensajeError`, `enviadoEn`
    - `db_table = 'registro_notificaciones'`
    - _Requisitos: 7.3_

  - [ ] 2.5 Generar y aplicar migraciones para todas las apps
    - `makemigrations` para cada app en orden: `app_autenticacion`, `app_pacientes`, `app_sesiones`, `app_notificaciones`
    - _Requisitos: 3.1, 3.4_

- [ ] 3. Implementar lógica de negocio en servicios
  - [ ] 3.1 Implementar `siguienteEstado()` y `SesionServicio` en `app_sesiones/servicios.py`
    - `secuenciaEstados` con los cinco estados en orden
    - `siguienteEstado (actual)`: retorna siguiente o `None` si es final
    - `SesionServicio.activarPaciente()`: valida unicidad de `codigoPaciente` y sesión activa previa, crea `SesionActiva`
    - `SesionServicio.avanzarEstado()`: avanza estado, registra `RegistroEstado`, marca `finalizadoEn` si es `FINALIZADO`
    - `SesionServicio.modificarCodigo()`: actualiza `codigoPaciente` validando unicidad
    - `SesionServicio.modificarMensaje()`: actualiza `mensaje` con validación de 80 caracteres
    - `SesionServicio.eliminarSesion()`: marca `ocultadoEn = timezone.now()`
    - _Requisitos: 2.3, 2.4, 2.5, 3.4, 3.5, 4.1, 4.2, 4.3, 4.6, 5.3_

  - [ ]* 3.2 Escribir tests unitarios para `siguienteEstado()` y `SesionServicio`
    - Cada transición válida de `siguienteEstado()` (4 transiciones + estado final retorna `None`)
    - `activarPaciente()`: unicidad de `codigoPaciente`, rechazo de paciente ya activo
    - `avanzarEstado()`: secuencia correcta, rechazo en estado final, registro de `RegistroEstado`
    - `modificarMensaje()`: rechazo si supera 80 caracteres
    - Usar `factory_boy` para fixtures y `pytest-django`
    - _Requisitos: 2.3, 2.4, 3.4, 3.5_

- [ ] 4. Implementar `NotificacionServicio`
  - [ ] 4.1 Implementar `NotificacionServicio` en `app_notificaciones/servicios.py`
    - `enviarNotificacion (sesion)`: omite si no hay `telefonoFamiliar`
    - `_enviarPorCanal (sesion, mensaje, canal)`: llama a Twilio, registra `RegistroNotificacion` con estado `enviado` o `fallido`
    - Captura excepciones sin propagar; nunca interrumpe el flujo principal
    - _Requisitos: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 4.2 Escribir tests unitarios para `NotificacionServicio`
    - Mock de `twilio.rest.Client` con `unittest.mock`
    - Caso: teléfono registrado → crea dos `RegistroNotificacion` (sms + whatsapp) con estado `enviado`
    - Caso: sin teléfono → no llama a Twilio, no crea registros
    - Caso: Twilio lanza excepción → crea `RegistroNotificacion` con estado `fallido`, no propaga error
    - _Requisitos: 7.1, 7.2, 7.3_

- [ ] 5. Checkpoint — Asegurarse de que todos los tests pasen
  - Ejecutar `pytest` y verificar que todos los tests unitarios de servicios pasen. Consultar al usuario si hay dudas.

- [ ] 6. Implementar autenticación y gestión de usuarios
  - [ ] 6.1 Configurar URLs de login/logout en `app_autenticacion/urls.py`
    - Usar `django.contrib.auth.views.LoginView` y `LogoutView`
    - Template `login.html` con formulario Tailwind CSS
    - _Requisitos: 6.1, 6.4_

  - [ ] 6.2 Implementar vistas de administración de usuarios en `app_autenticacion/vistas.py`
    - `ListaUsuariosVista` (CBV, solo Administrador): lista usuarios con estado activo/inactivo
    - `CrearUsuarioVista` (CBV, solo Administrador): formulario para crear Funcionario
    - `ToggleUsuarioVista` (CBV, solo Administrador): activa/desactiva cuenta con POST
    - Proteger con `LoginRequiredMixin` y verificación de rol `Administrador`
    - _Requisitos: 6.1, 6.3_

  - [ ] 6.3 Crear templates de autenticación y usuarios
    - `login.html`: formulario centrado, Tailwind CSS, mensajes de error
    - `usuarios/lista.html`: tabla de usuarios con botón toggle
    - `usuarios/crear.html`: formulario de creación
    - _Requisitos: 6.1, 6.3_

- [ ] 7. Implementar gestión de pacientes
  - [ ] 7.1 Implementar vistas de pacientes en `app_pacientes/vistas.py`
    - `CrearPacienteVista` (CBV, `LoginRequiredMixin`): GET muestra formulario, POST crea `Paciente` y redirige a activación
    - Formulario Django con `nombreCompleto` y `codigoPaciente`
    - _Requisitos: 3.1, 3.3_

  - [ ] 7.2 Crear template `pacientes/crear.html`
    - Formulario Tailwind CSS con campos `nombreCompleto`, `codigoPaciente`, `telefonoFamiliar`
    - Mensajes de error inline
    - _Requisitos: 3.1, 3.3_

- [ ] 8. Implementar vistas del Panel de Gestión
  - [ ] 8.1 Implementar `GestionVista` en `app_sesiones/vistas.py`
    - CBV con `LoginRequiredMixin`, GET retorna lista de sesiones activas (no ocultas)
    - Contexto: sesiones con siguiente estado disponible para cada una
    - _Requisitos: 4.1, 4.3, 8.1, 8.2_

  - [ ] 8.2 Implementar `ActivarPacienteVista` en `app_sesiones/vistas.py`
    - POST: llama a `SesionServicio.activarPaciente()`, retorna fragmento HTMX o error HTTP 409
    - _Requisitos: 3.2, 3.4, 3.5_

  - [ ] 8.3 Implementar `AvanzarEstadoVista` en `app_sesiones/vistas.py`
    - POST `/<id>/estado/`: llama a `SesionServicio.avanzarEstado()`, luego `NotificacionServicio.enviarNotificacion()`
    - Retorna fragmento HTMX actualizado o HTTP 400 si estado inválido
    - HTTP 500 con mensaje si falla la persistencia
    - _Requisitos: 2.3, 2.4, 4.1, 4.2, 4.5, 7.1_

  - [ ] 8.4 Implementar `ModificarCodigoVista` y `ModificarMensajeVista` en `app_sesiones/vistas.py`
    - POST `/<id>/codigo/`: llama a `SesionServicio.modificarCodigo()`, HTTP 409 si duplicado
    - POST `/<id>/mensaje/`: llama a `SesionServicio.modificarMensaje()`, HTTP 400 si > 80 chars
    - Ambas retornan fragmento HTMX
    - _Requisitos: 2.5, 5.3_

  - [ ] 8.5 Implementar `EliminarSesionVista` en `app_sesiones/vistas.py`
    - POST `/<id>/eliminar/`: llama a `SesionServicio.eliminarSesion()`, retorna fragmento HTMX vacío
    - _Requisitos: 4.6_

  - [ ]* 8.6 Escribir tests de vistas para el Panel de Gestión
    - `/gestion/` redirige a login sin sesión activa (req. 6.4, 8.4)
    - `AvanzarEstadoVista` retorna HTTP 400 en transición inválida (req. 2.4)
    - `ActivarPacienteVista` retorna HTTP 409 con código duplicado (req. 3.4)
    - Usar `factory_boy` para crear usuarios y sesiones de prueba
    - _Requisitos: 2.4, 3.4, 6.4, 8.4_

- [ ] 9. Implementar Tablero Público
  - [ ] 9.1 Implementar `obtenerSesionesVisibles()` y vistas del tablero en `app_tablero/vistas.py`
    - `coloresEstado`: dict estado → clase Tailwind
    - `obtenerSesionesVisibles()`: filtra ocultas, excluye finalizadas hace > 60 min, ordena por `iniciadoEn`
    - `TableroVista` (CBV, sin auth): template completo con layout TV
    - `TableroFragmentoVista` (CBV, sin auth): retorna solo el fragmento de lista para HTMX polling
    - _Requisitos: 1.1, 1.2, 1.3, 1.4, 4.4, 5.1, 5.2_

  - [ ] 9.2 Crear template `tablero/tablero.html`
    - Layout pantalla completa, Tailwind CSS, texto mínimo 48px para `codigoPaciente` y estado
    - `hx-get="/tablero/fragmento/"`, `hx-trigger="every 15s"`, `hx-swap="innerHTML"`
    - Indicador "Sin conexión" con Alpine.js cuando HTMX falla (`htmx:sendError`)
    - Mensaje "No hay pacientes en seguimiento" si lista vacía
    - _Requisitos: 1.1, 1.4, 1.5, 1.6, 1.7_

  - [ ] 9.3 Crear template `tablero/fragmento.html`
    - Lista de tarjetas: `codigoPaciente`, badge de estado con color Tailwind, `mensaje`, `actualizadoEn`
    - Sin datos personales del paciente
    - _Requisitos: 1.2, 1.3, 2.2, 5.1_

  - [ ]* 9.4 Escribir tests de vistas para el Tablero
    - `/tablero/` carga sin autenticación (req. 1.1)
    - `/tablero/fragmento/` no retorna sesiones con `ocultadoEn` ni finalizadas hace > 60 min (req. 4.4, 5.1)
    - `/tablero/fragmento/` no incluye `nombreCompleto` ni datos personales en la respuesta (req. 5.1, 5.2)
    - _Requisitos: 1.1, 4.4, 5.1, 5.2_

- [ ] 10. Checkpoint — Asegurarse de que todos los tests pasen
  - Ejecutar `pytest` y verificar que todos los tests de vistas y servicios pasen. Consultar al usuario si hay dudas.

- [ ] 11. Crear templates del Panel de Gestión
  - [ ] 11.1 Crear template base `base.html` con Tailwind CSS CDN, Alpine.js CDN y bloque HTMX
    - Incluir `<script src="https://unpkg.com/htmx.org">` y Tailwind CDN
    - Bloque `{% block contenido %}` para herencia
    - _Requisitos: 8.1_

  - [ ] 11.2 Crear template `gestion/gestion.html`
    - Layout dividido: sección superior con tablero en vivo (`hx-get="/tablero/fragmento/"`, `hx-trigger="every 15s"`), sección inferior con lista de sesiones y acciones
    - Botón "Avanzar estado" con `hx-post` y confirmación Alpine.js para eliminar
    - Formularios inline para editar `codigoPaciente` y `mensaje` con HTMX
    - _Requisitos: 4.1, 4.3, 8.2, 8.3_

  - [ ] 11.3 Crear template `gestion/fila_sesion.html` (fragmento HTMX)
    - Fila de sesión con código, estado, mensaje, acciones (avanzar, editar código, editar mensaje, eliminar)
    - Modal Alpine.js de confirmación para eliminar
    - _Requisitos: 4.6, 8.3_

- [ ] 12. Configurar URLs y cablear todas las vistas
  - Crear `quiroinfo/urls.py` incluyendo URLs de todas las apps
  - `app_autenticacion/urls.py`: `/login/`, `/logout/`, `/admin/usuarios/`
  - `app_pacientes/urls.py`: `/gestion/pacientes/crear/`
  - `app_sesiones/urls.py`: `/gestion/`, `/gestion/sesiones/`, `/gestion/sesiones/<id>/estado/`, `/gestion/sesiones/<id>/codigo/`, `/gestion/sesiones/<id>/mensaje/`, `/gestion/sesiones/<id>/eliminar/`
  - `app_tablero/urls.py`: `/`, `/tablero/`, `/tablero/fragmento/`
  - _Requisitos: 1.1, 6.1, 6.4, 8.1_

- [ ] 13. Checkpoint final — Asegurarse de que todos los tests pasen
  - Ejecutar `pytest` y verificar que la suite completa pase sin errores. Consultar al usuario si hay dudas.

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia requisitos específicos para trazabilidad
- Los checkpoints garantizan validación incremental
- No usar Celery, DRF, WebSockets ni Hypothesis en ninguna tarea
- Nomenclatura: clases PascalCase, funciones/variables camelCase, todo en español para dominio

