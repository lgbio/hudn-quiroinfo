# KIRO — Backlog MVP Quiroinfo

## Reglas globales del proyecto

- Nombres en español
- Clases en PascalCase
- Funciones y variables en PascalCase
- Apps Django con prefijo `app_`
- Funciones cortas (máx. ~30 líneas)
- Una sola responsabilidad por función
- Usar Class-Based Views cuando aplique
- Evitar JavaScript personalizado; preferir HTMX
- Templates simples y reutilizables

---

# FASE 1 — Setup del Proyecto

## Task 1.1 — Crear proyecto Django

**Objetivo**  
Inicializar el proyecto base.

**Acciones**
- Crear proyecto `quiroinfo`
- Configurar PostgreSQL
- Configurar archivo `.env`
- Configurar `settings/base.py` y `settings/dev.py`

## Task 1.2 — Crear apps

Apps iniciales:

```text
app_authentication
app_patients
app_sessions
app_notifications
app_board
```

**Acciones**
- Registrar apps en `INSTALLED_APPS`
- Crear estructura base por app

## Task 1.3 — Setup frontend base

**Acciones**
- Integrar Tailwind por CDN para el MVP
- Integrar HTMX
- Crear template base `base.html`

---

# FASE 2 — Autenticación

## Task 2.1 — Modelo User básico

**Requerimientos**
- `username`
- `password`
- `is_active`

**Decisión**
- Usar `AbstractUser`

## Task 2.2 — Login y Logout

**URLs**

```text
/login/
/logout/
```

**Acciones**
- Usar `LoginView`
- Usar `LogoutView`
- Crear template simple de login

## Task 2.3 — Protección de vistas

**Acciones**
- Aplicar `LoginRequiredMixin` en `/manage/`

---

# FASE 3 — Pacientes

## Task 3.1 — Modelo Patient

Campos base:

```python
id
full_name
created_at
```

## Task 3.2 — Crear paciente

**Vista**

```text
/manage/patients/create/
```

**Funcionalidad**
- Formulario simple
- Guardar paciente en base de datos

---

# FASE 4 — Sesiones activas (CORE)

## Task 4.1 — Modelo ActiveSession

Campos:

```python
patient
patient_code
status
message
family_phone
started_at
last_updated_at
finished_at
```

## Task 4.2 — Modelo StatusLog

**Objetivo**
- Registrar cambios de estado

## Task 4.3 — Activar paciente

**Endpoint**

```text
POST /manage/sessions/
```

**Reglas**
- Un paciente no puede tener una sesión activa previa
- `patient_code` debe ser único entre sesiones activas

## Task 4.4 — Lógica de estados

Secuencia:

```text
En preparación → En cirugía → En recuperación → Listo → Finalizado
```

Crear función:

```python
def NextStatus(Actual):
    ...
```

## Task 4.5 — Cambiar estado

**Endpoint**

```text
POST /manage/sessions/<id>/status/
```

**Acciones**
- Validar transición
- Guardar nuevo estado
- Crear registro en `StatusLog`

## Task 4.6 — Editar mensaje

**Endpoint**

```text
POST /manage/sessions/<id>/message/
```

## Task 4.7 — Eliminar sesión

**Endpoint**

```text
POST /manage/sessions/<id>/delete/
```

---

# FASE 5 — Tablero Público

## Task 5.1 — Vista principal del tablero

**URL**

```text
/board/
```

**Características**
- Sin autenticación
- Diseño tipo TV / sala de espera
- Tipografía grande y alta legibilidad

## Task 5.2 — Fragmento HTMX del tablero

**URL**

```text
/board/fragment/
```

**Retorna**
- Lista de sesiones activas visibles en el tablero

## Task 5.3 — Polling con HTMX

Usar en el tablero:

```html
hx-get="/board/fragment/"
hx-trigger="every 15s"
hx-swap="innerHTML"
```

## Task 5.4 — Filtrado de sesiones visibles

**Mostrar**
- Sesiones activas
- Sesiones no finalizadas o finalizadas recientemente

---

# FASE 6 — Panel de Gestión

## Task 6.1 — Vista principal de gestión

**URL**

```text
/manage/
```

## Task 6.2 — Lista de sesiones activas

Mostrar una tabla con:
- código
- estado
- mensaje
- acciones

## Task 6.3 — Acciones con HTMX

Permitir sin recargar la página:
- cambiar estado
- editar mensaje
- eliminar sesión

---

# FASE 7 — Notificaciones

## Task 7.1 — Integrar Twilio

**Canales**
- SMS
- WhatsApp

## Task 7.2 — Servicio de notificación

Crear función o servicio:

```python
def EnviarNotificacion(Session):
    ...
```

## Task 7.3 — Trigger al cambiar estado

**Acción**
- Enviar notificación automáticamente cuando cambie el estado

## Task 7.4 — Modelo NotificationLog

Registrar:
- canal
- éxito o fallo
- fecha de envío

---

# FASE 8 — Validaciones

## Task 8.1 — Unicidad de código

**Regla**
- Validar en servicio que no exista otro `patient_code` activo igual

## Task 8.2 — Validación de estado

**Regla**
- Solo se permite avanzar al siguiente estado

## Task 8.3 — Validación de mensaje

**Regla**
- Máximo 80 caracteres

---

# FASE 9 — Testing mínimo

## Task 9.1 — Test de estados

Validar:
- transición correcta
- rechazo de transición inválida

## Task 9.2 — Test de unicidad

Validar:
- no permitir códigos duplicados en sesiones activas

## Task 9.3 — Test de vistas

Validar:
- `/board/` carga correctamente
- `/manage/` requiere login

---

# FASE 10 — Deploy básico

## Task 10.1 — Configuración de producción

**Acciones**
- `DEBUG = False`
- configurar `ALLOWED_HOSTS`
- forzar HTTPS

## Task 10.2 — Archivos estáticos

**Acciones**
- configurar static files
- ejecutar `collectstatic`

## Task 10.3 — Variables de entorno

Configurar:
- base de datos
- Twilio
- secret key

---

# Orden de ejecución recomendado

```text
1 → Setup proyecto
2 → Auth
3 → Patients
4 → Sessions (CORE)
5 → Board
6 → Panel
7 → Notificaciones
8 → Validaciones
9 → Testing
10 → Deploy
```

---

# MVP ultra rápido opcional

Si quieres validar la idea en muy poco tiempo, construir primero solo:

```text
- ActiveSession
- Board
- Cambio de estado
```

Sin incluir todavía:
- patients completos
- notificaciones
- auth más allá de lo básico
