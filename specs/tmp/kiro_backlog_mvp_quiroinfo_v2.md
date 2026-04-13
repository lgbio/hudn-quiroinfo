# KIRO — Backlog MVP Quiroinfo

## Propósito de este backlog

Este backlog define **solo el MVP real** de Quiroinfo. Está recortado para evitar sobreingeniería y para que el agente implemente una primera versión funcional, simple y desplegable.

## Modificaciones a los archivos de 'steering'
"""
---
inclusion: always
---

# Coding Rules

## Naming Scope
- These rules apply ONLY to domain-specific code of the application.
- DO NOT modify or translate standard Django names, conventions, or built-in routes.
- Framework-related names (Django, Python, libraries) must remain in English.

## Naming (Domain Code)
- All domain-specific identifiers MUST be in Spanish.
- This includes:
  - Models
  - Variables
  - Functions
  - Classes
  - Custom URLs
  - Business logic
- DO NOT use English for domain concepts.

## Naming Style
- Functions, variables, and classes must use PascalCase.

## Django Apps
- Django apps must start with the prefix "app_".

## URLs and Routes
- Custom application routes must be in Spanish.
- Standard Django routes can remain in English:
  - /login/
  - /logout/
  - /admin/

## Constants and Enums
- Domain enums and constants must be in Spanish.
- Example:
  - EN_PREPARACION
  - EN_CIRUGIA
  - EN_RECUPERACION

## Syntax style
- Leave one space between function or variable names and parentheses/brackets.
  - Example: FuncionEjemplo () , variableEjemplo []

## Function design
- Functions must be short to medium size.
- Functions must follow single responsibility principle.
"""



## Decisiones obligatorias para el MVP

### Sí incluir en el MVP
- Tablero público sin autenticación
- Panel de gestión con autenticación simple
- Creación manual de pacientes
- Activación manual de sesión quirúrgica
- Flujo secuencial de estados
- Notificaciones básicas por SMS y/o WhatsApp
- Actualización automática del tablero con HTMX polling cada 15 segundos
- Registro básico de cambios de estado
- Privacidad: nunca mostrar datos personales en el tablero
- Base de datos PostgreSQL
- Tests mínimos unitarios y de vistas

### No incluir en el MVP
- Property-Based Testing con Hypothesis
- Diseño formal de propiedades avanzadas
- Serialización round-trip
- AuthService custom complejo
- Bloqueo de cuenta tras intentos fallidos en implementación custom
- PotentialPatient
- Sincronización con base de datos hospitalaria
- Preview panel con scaling, resize o comportamiento avanzado
- WebSockets
- Celery
- DRF / API REST
- Compatibilidad PostgreSQL + SQL Server desde inicio
- Manejo de errores exhaustivo tipo enterprise
- Arquitectura por fases demasiado detallada dentro del código inicial
- Integraciones hospitalarias externas
- SPA o frontend separado

## Reglas globales del proyecto

- Nombres en español
- Clases en PascalCase
- Funciones y variables en PascalCase
- Apps Django con prefijo `app_`
- Funciones cortas, preferiblemente hasta 30 líneas
- Una sola responsabilidad por función
- Usar Django Templates + HTMX
- Evitar JavaScript personalizado salvo casos mínimos muy justificados
- Reutilizar templates parciales
- El alcance MVP prima sobre mejoras futuras

## Alcance funcional del MVP

### Flujo de usuario obligatorio

#### Funcionario
1. Inicia sesión
2. Crea un paciente manualmente
3. Activa una sesión quirúrgica para ese paciente
4. Asigna un `patient_code`
5. Cambia el estado del paciente a lo largo del proceso
6. Opcionalmente escribe un mensaje corto
7. El sistema actualiza el tablero y envía notificación

#### Familiar
1. Recibe el código del paciente por SMS o WhatsApp
2. Consulta el tablero público en sala de espera
3. Identifica el estado del paciente usando el código

### UX mínima del tablero
- Debe verse correctamente en TV o monitor grande
- Debe mostrar tipografía grande y legible
- Debe mostrar columnas mínimas: código, estado, mensaje opcional, hora de última actualización
- Debe evitar saturación visual
- Debe ordenar por hora de inicio o última actualización, de manera consistente
- Debe mostrar solo sesiones activas o finalizadas recientemente
- No debe mostrar ningún dato personal

## FASE 1 — Setup del proyecto

### Task 1.1 — Crear proyecto Django

**Objetivo**
Inicializar el proyecto base.

**Acciones**
- Crear proyecto `quiroinfo`
- Configurar PostgreSQL como única base de datos del MVP
- Configurar archivo `.env`
- Separar settings en archivos simples si se desea, sin complejidad innecesaria

### Task 1.2 — Crear apps Django

Crear estas apps:

```text
app_authentication
app_patients
app_sessions
app_notifications
app_board
```

**Acciones**
- Registrar apps en `INSTALLED_APPS`
- Crear estructura mínima de modelos, vistas, urls y templates

### Task 1.3 — Setup frontend base

**Acciones**
- Integrar Tailwind CSS por CDN en el MVP
- Integrar HTMX
- Crear `base.html`
- Definir layout simple y limpio

## FASE 2 — Autenticación simple

### Task 2.1 — Modelo de usuario

**Requerimiento**
Usar `AbstractUser` de Django, evitando auth custom complejo.

**No hacer en MVP**
- No crear `AuthService` custom complejo
- No implementar bloqueo por intentos fallidos
- No implementar reglas avanzadas de seguridad propias

### Task 2.2 — Login y logout

**URLs**
```text
/login/
/logout/
```

**Acciones**
- Usar `LoginView`
- Usar `LogoutView`
- Crear templates simples

### Task 2.3 — Protección de vistas

**Acciones**
- Proteger `/manage/` con `LoginRequiredMixin`

## FASE 3 — Pacientes

### Task 3.1 — Modelo Patient

```python
id
full_name
created_at
```

**Nota**
El paciente se crea manualmente en el MVP.

**No hacer en MVP**
- No crear `PotentialPatient`
- No sincronizar con base hospitalaria

### Task 3.2 — Crear paciente desde panel

**Vista**
```text
/manage/patients/create/
```

**Funcionalidad**
- Formulario simple
- Guardar paciente
- Redirigir o actualizar lista interna

## FASE 4 — Sesiones activas (núcleo del sistema)

### Task 4.1 — Modelo ActiveSession

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

### Task 4.2 — Modelo StatusLog

Registrar cambios de estado.

### Task 4.3 — Activar paciente

**Endpoint**
```text
POST /manage/sessions/
```

**Reglas**
- Un paciente no puede tener dos sesiones activas
- `patient_code` debe ser único entre sesiones activas

### Task 4.4 — Definir estados del proceso

```text
En preparación → En cirugía → En recuperación → Listo → Finalizado
```

Crear función:

```python
NextStatus(actual)
```

**No hacer en MVP**
- No permitir flujos complejos
- No permitir ramas alternas
- No crear motor de reglas

### Task 4.5 — Cambiar estado

**Endpoint**
```text
POST /manage/sessions/<id>/status/
```

**Acciones**
- Validar transición secuencial
- Guardar nuevo estado
- Crear `StatusLog`
- Disparar notificación

### Task 4.6 — Editar mensaje

**Endpoint**
```text
POST /manage/sessions/<id>/message/
```

**Regla**
- Mensaje corto, máximo 80 caracteres

### Task 4.7 — Eliminar u ocultar sesión

**Endpoint**
```text
POST /manage/sessions/<id>/delete/
```

**Nota**
Puede ser borrado lógico u ocultamiento simple, según implementación más sencilla.

## FASE 5 — Tablero público

### Task 5.1 — Vista principal del tablero

**URL**
```text
/board/
```

**Características obligatorias**
- Sin autenticación
- Diseño para TV/monitor
- Tipografía grande
- Solo datos no sensibles

### Task 5.2 — Fragmento HTMX

**URL**
```text
/board/fragment/
```

Retorna lista parcial de sesiones visibles.

### Task 5.3 — Polling con HTMX

```html
hx-get="/board/fragment/"
hx-trigger="every 15s"
hx-swap="innerHTML"
```

### Task 5.4 — Lógica de visibilidad del tablero

Mostrar:
- sesiones activas
- sesiones finalizadas recientemente, solo si así se define

No mostrar:
- nombre del paciente
- identificaciones
- datos clínicos

### Task 5.5 — UX mínima del tablero

**Definir explícitamente**
- orden de visualización
- cantidad razonable de filas visibles
- uso consistente de colores por estado
- hora de última actualización visible
- comportamiento simple si no hay pacientes activos

## FASE 6 — Panel de gestión

### Task 6.1 — Vista principal

**URL**
```text
/manage/
```

### Task 6.2 — Lista de sesiones activas

Mostrar por fila:
- código
- estado
- mensaje
- acciones

### Task 6.3 — Acciones con HTMX

Permitir sin recargar página:
- cambiar estado
- editar mensaje
- eliminar u ocultar sesión

## FASE 7 — Notificaciones

### Task 7.1 — Integrar proveedor

Usar Twilio para SMS y/o WhatsApp.

### Task 7.2 — Servicio simple de notificación

```python
EnviarNotificacion(session)
```

### Task 7.3 — Enviar notificación al cambiar estado

Definir inicialmente si notifica en todos los cambios de estado o solo en ciertos estados. Para el MVP se recomienda:
- notificar en todos los cambios

### Task 7.4 — Modelo NotificationLog

Registrar:
- sesión
- canal
- estado de envío
- fecha de envío
- mensaje de error opcional

## FASE 8 — Validaciones mínimas

### Task 8.1 — Unicidad de código

Validar en servicio o vista antes de guardar.

### Task 8.2 — Secuencia de estados

Solo permitir el siguiente estado válido.

### Task 8.3 — Mensaje corto

Máximo 80 caracteres.

### Task 8.4 — Privacidad del tablero

Asegurar que el contexto y template del tablero no incluyan datos personales.

## FASE 9 — Manejo de errores básico

Implementar solo errores mínimos y útiles para MVP:
- código duplicado
- transición de estado inválida
- usuario no autenticado
- falla en envío de notificación sin romper flujo principal

**No hacer en MVP**
- No documentar ni construir una matriz exhaustiva de errores enterprise
- No crear sistema avanzado de recuperación

## FASE 10 — Testing mínimo viable

### Sí hacer
- tests unitarios para transición de estados
- tests unitarios para unicidad de `patient_code`
- tests de vistas para `/board/`
- tests de autenticación para `/manage/`

### No hacer
- no usar Hypothesis
- no hacer Property-Based Testing
- no implementar pruebas formales de serialización round-trip

## FASE 11 — Deploy básico

### Task 11.1 — Configuración de producción

- `DEBUG = False`
- `ALLOWED_HOSTS`
- HTTPS

### Task 11.2 — Static files

- `collectstatic`

### Task 11.3 — Variables de entorno

- base de datos
- Twilio
- secret key

## Orden recomendado de implementación

```text
1 → Setup proyecto
2 → Auth simple
3 → Patients manuales
4 → Sessions
5 → Board
6 → Panel
7 → Notificaciones
8 → Validaciones
9 → Errores mínimos
10 → Testing mínimo
11 → Deploy
```

## Primera iteración ultrarrápida opcional

Si se desea validar el concepto en muy pocos días, construir primero:

```text
- ActiveSession
- Board
- Cambio de estado
```

Y dejar temporalmente fuera:

```text
- Patients completos
- notificaciones
- auth más allá de lo básico
```

## Instrucción final para Kiro

Implementar únicamente el MVP definido en este documento. Si surge una decisión ambigua, preferir siempre la opción más simple, más directa y con menor complejidad técnica, sin introducir componentes pensados para escalamiento futuro que todavía no sean necesarios.
