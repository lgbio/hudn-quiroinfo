# Documento de Diseño Técnico
## Sistema de Seguimiento de Pacientes Quirúrgicos — MVP

---

## Visión General

Aplicación web en tiempo casi real que permite a los familiares de pacientes quirúrgicos conocer el estado del proceso sin interactuar con el personal médico. Funciona como un tablero tipo aeropuerto proyectado en sala de espera, con actualizaciones automáticas y notificaciones vía SMS/WhatsApp.

**Stack tecnológico (MVP):**
- Backend: Python + Django, vistas basadas en clases (CBV)
- Frontend: Django Templates + HTMX + Tailwind CSS (CDN) + Alpine.js (CDN, solo para modales)
- Tiempo real: Polling con HTMX `hx-trigger="every 15s"`
- Base de datos: PostgreSQL
- Notificaciones: Twilio SDK (síncrono)
- Autenticación: `django.contrib.auth` con `AbstractUser` y sesiones

**Fuera del MVP:**
- WebSockets / Django Channels
- Celery / tareas asíncronas
- DRF / API REST
- Compatibilidad con SQL Server
- Property-Based Testing con Hypothesis
- Bloqueo de cuenta por intentos fallidos (custom)
- Sincronización con base de datos hospitalaria
- Panel de previsualización con divisor arrastrable y scaling

---

## Arquitectura

```mermaid
graph TB
    subgraph "Clientes"
        TV["Tablero Público\n(TV/Monitor sala espera)"]
        STAFF["Panel de Gestión\n(Funcionario/Admin)"]
        FAM["Familiar\n(SMS/WhatsApp)"]
    end

    subgraph "Django"
        VIEWS["Class-Based Views"]
        AUTH["django.contrib.auth\nSesiones"]
        SVC["Servicios\n(SesionServicio, NotificacionServicio)"]
    end

    subgraph "Base de datos"
        DB["PostgreSQL\nvía Django ORM"]
    end

    subgraph "Servicios externos"
        TWILIO["Twilio\nSMS + WhatsApp"]
    end

    TV -->|polling HTMX cada 15s| VIEWS
    STAFF -->|requests HTTP + HTMX| VIEWS
    VIEWS --> AUTH
    VIEWS --> SVC
    SVC --> DB
    SVC -->|síncrono| TWILIO
    TWILIO --> FAM
```

**Decisiones clave:**

- HTMX polling cada 15s cumple el requisito de actualización en ≤30s sin infraestructura adicional.
- Notificaciones Twilio síncronas: si fallan, se registra en `RegistroNotificacion` sin interrumpir el flujo.
- Unicidad de `codigo_paciente` validada en el servicio (consulta ORM), no con partial index.
- `AbstractUser` de Django sin lógica custom de bloqueo en el MVP.

---

## Estructura del proyecto

```
quiroinfo/                  # proyecto Django
├── app_autenticacion/      # User, login, logout
├── app_pacientes/          # Paciente, formulario de creación
├── app_sesiones/           # SesionActiva, RegistroEstado, lógica de negocio
├── app_notificaciones/     # RegistroNotificacion, NotificacionServicio
└── app_tablero/            # vistas públicas del Tablero
```

---

## Vistas y URLs

| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET | `/` | No | Redirige a `/tablero/` |
| GET | `/tablero/` | No | Tablero público (template completo) |
| GET | `/tablero/fragmento/` | No | Fragmento HTMX: lista de sesiones visibles |
| GET | `/login/` | No | Formulario de login |
| POST | `/login/` | No | Procesa credenciales |
| POST | `/logout/` | Sí | Cierra sesión |
| GET | `/gestion/` | Sí | Panel de gestión |
| GET | `/gestion/pacientes/crear/` | Sí | Formulario de creación de paciente |
| POST | `/gestion/pacientes/crear/` | Sí | Guarda nuevo paciente |
| POST | `/gestion/sesiones/` | Sí | Activa un paciente (crea sesión activa) |
| POST | `/gestion/sesiones/<id>/estado/` | Sí | Avanza el estado quirúrgico |
| POST | `/gestion/sesiones/<id>/codigo/` | Sí | Modifica el Código_Paciente |
| POST | `/gestion/sesiones/<id>/mensaje/` | Sí | Agrega/edita mensaje libre |
| POST | `/gestion/sesiones/<id>/eliminar/` | Sí | Elimina sesión del tablero |
| GET | `/admin/usuarios/` | Admin | Lista de usuarios |
| POST | `/admin/usuarios/` | Admin | Crea cuenta de Funcionario |
| POST | `/admin/usuarios/<id>/toggle/` | Admin | Activa/desactiva cuenta |

---

## Modelos de Datos

### Enumeraciones

```python
# app_sesiones/models.py
from django.db import models

class EstadoQuirurgico (models.TextChoices):
    EN_PREPARACION  = 'En preparación',    'En preparación'
    EN_CIRUGIA      = 'En cirugía',        'En cirugía'
    EN_RECUPERACION = 'En recuperación',   'En recuperación'
    LISTO           = 'Listo para visita', 'Listo para visita'
    FINALIZADO      = 'Proceso finalizado','Proceso finalizado'

class RolUsuario (models.TextChoices):
    ADMINISTRADOR = 'Administrador', 'Administrador'
    FUNCIONARIO   = 'Funcionario',   'Funcionario'
```

### `Usuario` (app `app_autenticacion`)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario (AbstractUser):
    rol = models.CharField (max_length=20, choices=RolUsuario.choices, default=RolUsuario.FUNCIONARIO)

    class Meta:
        db_table = 'usuarios'
```

### `Paciente` (app `app_pacientes`)

Datos personales — nunca expuestos al Tablero.

```python
import uuid
from django.db import models

class Paciente (models.Model):
    id             = models.UUIDField (primary_key=True, default=uuid.uuid4, editable=False)
    nombreCompleto = models.CharField (max_length=255)
    creadoEn       = models.DateTimeField (auto_now_add=True)

    class Meta:
        db_table = 'pacientes'
```

### `SesionActiva` (app `app_sesiones`)

Datos del Tablero — sin datos personales.

```python
import uuid
from django.db import models

class SesionActiva (models.Model):
    id               = models.UUIDField (primary_key=True, default=uuid.uuid4, editable=False)
    paciente         = models.ForeignKey ('app_pacientes.Paciente', on_delete=models.PROTECT)
    codigoPaciente   = models.CharField (max_length=50)
    estado           = models.CharField (
                           max_length=30,
                           choices=EstadoQuirurgico.choices,
                           default=EstadoQuirurgico.EN_PREPARACION
                       )
    mensaje          = models.CharField (max_length=80, null=True, blank=True)
    telefonoFamiliar = models.CharField (max_length=20, null=True, blank=True)
    iniciadoEn       = models.DateTimeField (auto_now_add=True)
    actualizadoEn    = models.DateTimeField (auto_now=True)
    finalizadoEn     = models.DateTimeField (null=True, blank=True)
    ocultadoEn       = models.DateTimeField (null=True, blank=True)
    creadoPor        = models.ForeignKey ('app_autenticacion.Usuario', on_delete=models.PROTECT)

    class Meta:
        db_table = 'sesiones_activas'
```

### `RegistroEstado` (app `app_sesiones`)

```python
class RegistroEstado (models.Model):
    id             = models.UUIDField (primary_key=True, default=uuid.uuid4, editable=False)
    sesion         = models.ForeignKey (SesionActiva, on_delete=models.PROTECT)
    codigoPaciente = models.CharField (max_length=50)
    estadoAnterior = models.CharField (max_length=30, null=True, blank=True)
    estadoNuevo    = models.CharField (max_length=30)
    cambiadoPor    = models.ForeignKey ('app_autenticacion.Usuario', on_delete=models.PROTECT)
    cambiadoEn     = models.DateTimeField (auto_now_add=True)

    class Meta:
        db_table = 'registro_estados'
```

### `RegistroNotificacion` (app `app_notificaciones`)

```python
class RegistroNotificacion (models.Model):
    CANALES = [('sms', 'SMS'), ('whatsapp', 'WhatsApp')]
    ESTADOS = [('enviado', 'Enviado'), ('fallido', 'Fallido')]

    id             = models.UUIDField (primary_key=True, default=uuid.uuid4, editable=False)
    sesion         = models.ForeignKey ('app_sesiones.SesionActiva', on_delete=models.PROTECT)
    codigoPaciente = models.CharField (max_length=50)
    canal          = models.CharField (max_length=10, choices=CANALES)
    estado         = models.CharField (max_length=10, choices=ESTADOS)
    mensajeError   = models.TextField (null=True, blank=True)
    enviadoEn      = models.DateTimeField (auto_now_add=True)

    class Meta:
        db_table = 'registro_notificaciones'
```

---

## Lógica de negocio

### Transición de estados

```python
# app_sesiones/servicios.py
secuenciaEstados = [
    EstadoQuirurgico.EN_PREPARACION,
    EstadoQuirurgico.EN_CIRUGIA,
    EstadoQuirurgico.EN_RECUPERACION,
    EstadoQuirurgico.LISTO,
    EstadoQuirurgico.FINALIZADO,
]

def siguienteEstado (actual: str) -> str | None:
    """Retorna el siguiente estado válido, o None si es el estado final."""
    try:
        indice = secuenciaEstados.index (actual)
        return secuenciaEstados [indice + 1] if indice + 1 < len (secuenciaEstados) else None
    except ValueError:
        return None
```

### `SesionServicio`

```python
# app_sesiones/servicios.py
from django.utils import timezone

class SesionServicio:

    def activarPaciente (self, pacienteId, codigoPaciente, telefonoFamiliar, creadoPor):
        if SesionActiva.objects.filter (paciente_id=pacienteId, ocultadoEn__isnull=True).exists ():
            raise ValidationError ("El paciente ya tiene una sesión activa.")
        if SesionActiva.objects.filter (codigoPaciente=codigoPaciente, ocultadoEn__isnull=True).exists ():
            raise ValidationError (f"El código '{codigoPaciente}' ya está en uso.")
        return SesionActiva.objects.create (
            paciente_id=pacienteId,
            codigoPaciente=codigoPaciente,
            telefonoFamiliar=telefonoFamiliar,
            creadoPor=creadoPor,
        )

    def avanzarEstado (self, sesion: SesionActiva, cambiadoPor) -> SesionActiva:
        nuevoEstado = siguienteEstado (sesion.estado)
        if nuevoEstado is None:
            raise ValidationError ("El paciente ya se encuentra en el estado final.")
        estadoAnterior = sesion.estado
        sesion.estado = nuevoEstado
        if nuevoEstado == EstadoQuirurgico.FINALIZADO:
            sesion.finalizadoEn = timezone.now ()
        sesion.save ()
        RegistroEstado.objects.create (
            sesion=sesion,
            codigoPaciente=sesion.codigoPaciente,
            estadoAnterior=estadoAnterior,
            estadoNuevo=nuevoEstado,
            cambiadoPor=cambiadoPor,
        )
        return sesion
```

### Sesiones visibles en el Tablero

```python
# app_tablero/vistas.py
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

coloresEstado = {
    EstadoQuirurgico.EN_PREPARACION:  'bg-yellow-400',
    EstadoQuirurgico.EN_CIRUGIA:      'bg-orange-500',
    EstadoQuirurgico.EN_RECUPERACION: 'bg-blue-500',
    EstadoQuirurgico.LISTO:           'bg-green-500',
    EstadoQuirurgico.FINALIZADO:      'bg-gray-400',
}

def obtenerSesionesVisibles ():
    """Sesiones visibles en el Tablero. Excluye finalizadas hace más de 60 min."""
    limite = timezone.now () - timedelta (minutes=60)
    return (
        SesionActiva.objects
        .filter (ocultadoEn__isnull=True)
        .exclude (Q (estado=EstadoQuirurgico.FINALIZADO) & Q (finalizadoEn__lt=limite))
        .only ('id', 'codigoPaciente', 'estado', 'mensaje', 'actualizadoEn')
        .order_by ('iniciadoEn')
    )
```

### `NotificacionServicio`

```python
# app_notificaciones/servicios.py
from twilio.rest import Client
from django.conf import settings

class NotificacionServicio:

    def enviarNotificacion (self, sesion):
        if not sesion.telefonoFamiliar:
            return
        mensaje = f"Paciente {sesion.codigoPaciente}: {sesion.estado}"
        self._enviarPorCanal (sesion, mensaje, 'sms')
        self._enviarPorCanal (sesion, mensaje, 'whatsapp')

    def _enviarPorCanal (self, sesion, mensaje, canal):
        try:
            cliente = Client (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            destino = f"whatsapp:{sesion.telefonoFamiliar}" if canal == 'whatsapp' else sesion.telefonoFamiliar
            cliente.messages.create (body=mensaje, from_=settings.TWILIO_FROM, to=destino)
            RegistroNotificacion.objects.create (
                sesion=sesion, codigoPaciente=sesion.codigoPaciente,
                canal=canal, estado='enviado'
            )
        except Exception as error:
            RegistroNotificacion.objects.create (
                sesion=sesion, codigoPaciente=sesion.codigoPaciente,
                canal=canal, estado='fallido', mensajeError=str (error)
            )
```

---

## Tablero Público (`/tablero/`)

- Sin autenticación
- Template completo con layout para TV/monitor (texto mínimo 48px)
- Tailwind CSS: colores de estado, tipografía grande, layout de pantalla completa
- HTMX polling: `hx-get="/tablero/fragmento/"`, `hx-trigger="every 15s"`, `hx-swap="innerHTML"`
- Muestra: `CodigoPaciente`, `Estado` con color, `Mensaje`, `ActualizadoEn`
- Orden: por `IniciadoEn` ascendente
- Si no hay sesiones activas: mensaje simple "No hay pacientes en seguimiento"
- Sin interacción de usuario

---

## Panel de Gestión (`/gestion/`)

- Requiere autenticación (`LoginRequiredMixin`)
- Layout dividido verticalmente: tablero arriba, panel de gestión abajo
- La división es fija (sin resize ni scaling); proporciones simples con Tailwind (`flex-col`, alturas relativas)

**Sección superior — Tablero en vivo:**
- Embebe el fragmento `/tablero/fragmento/` con `hx-trigger="every 15s"`
- Misma visualización que el tablero público pero en tamaño reducido
- Solo lectura; sin interacción

**Sección inferior — Panel de operaciones:**
- Lista de sesiones activas con código, estado, mensaje y acciones
- HTMX: cambio de estado, edición de mensaje y eliminación sin recargar la página completa
- Alpine.js: modal de confirmación para acciones destructivas (eliminar sesión)

Si el layout dividido resulta problemático en pantallas pequeñas, la alternativa es un botón "Ver tablero" que abre el tablero en un modal o en una nueva pestaña (`target="_blank"`). La decisión final se toma durante la implementación según lo que resulte más simple.

---

## Manejo de Errores (MVP)

| Escenario | Comportamiento |
|-----------|---------------|
| Transición de estado inválida | HTTP 400; muestra el estado válido disponible |
| Código_Paciente duplicado | HTTP 409; mensaje de conflicto |
| Mensaje > 80 caracteres | HTTP 400; validación en formulario Django |
| Fallo de notificación | Registrado en `RegistroNotificacion`; no interrumpe el flujo |
| Fallo de persistencia al actualizar estado | HTTP 500; conserva estado anterior; notifica al Funcionario |
| Usuario no autenticado en `/gestion/` | Redirección 302 a `/login/` |
| Sesión inactiva > 120 minutos | Django expira la sesión; redirige a login |

---

## Testing Mínimo

### Herramientas
- `pytest-django`
- `factory_boy`
- `unittest.mock` para Twilio

### Tests unitarios
- `siguienteEstado()`: cada transición válida e inválida
- `SesionServicio.activarPaciente()`: unicidad de `codigoPaciente`
- `SesionServicio.avanzarEstado()`: secuencia correcta y rechazo de saltos
- Validación de mensaje: límite de 80 caracteres

### Tests de vistas
- `/tablero/` carga sin autenticación y no expone datos personales
- `/gestion/` redirige a login sin sesión activa
- `/tablero/fragmento/` no retorna sesiones ocultas
