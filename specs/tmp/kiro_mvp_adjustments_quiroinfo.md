# Ajustes de Requerimientos y Diseño — Quiroinfo MVP (Formato Kiro)

---

# 📌 AJUSTES — REQUERIMIENTOS

## Requisito Nuevo: Modelo Unificado de Paciente

**User Story:**  
Como sistema, quiero manejar un único tipo de paciente, para evitar duplicidad de datos y simplificar la lógica de negocio.

### Criterios de Aceptación

1. THE Sistema SHALL manejar un único modelo lógico de Paciente con los campos `identificacion`, `nombre` y `origen`.
2. THE campo `origen` SHALL permitir distinguir entre pacientes PROGRAMADO y URGENCIAS.
3. THE Sistema SHALL evitar la existencia de entidades separadas para PacienteProgramado y PacienteUrgencias.
4. THE Sistema SHALL permitir agregar pacientes de urgencias reutilizando el mismo modelo de Paciente.

---

## Requisito Nuevo: Unicidad de Sesión Activa

**User Story:**  
Como sistema, quiero asegurar que un paciente tenga una sola sesión activa, para evitar inconsistencias en el tablero.

### Criterios de Aceptación

1. THE Sistema SHALL garantizar que solo exista una Sesion activa (no oculta) por cada paciente.
2. IF se intenta crear una nueva Sesion para un paciente con sesión activa, THEN THE Sistema SHALL reutilizar la sesión existente.
3. THE Sistema SHALL prevenir condiciones de carrera mediante restricciones a nivel de base de datos.

---

## Requisito Modificado: Finalización de Paciente

### Criterios de Aceptación

1. WHEN el Funcionario selecciona el estado FINALIZADO, THEN THE Sistema SHALL marcar la Sesion como no visible en el Tablero.
2. THE Sistema SHALL conservar el registro de la Sesion en la base de datos.
3. THE Sistema SHALL NO eliminar registros físicos de Sesion.

---

## Requisito Nuevo: Autenticación Restringida (MVP)

**User Story:**  
Como sistema, quiero restringir el acceso al panel de gestión a usuarios autorizados.

### Criterios de Aceptación

1. THE Sistema SHALL validar que el email ingresado pertenezca a una lista blanca o dominio permitido.
2. IF el email no está autorizado, THEN THE Sistema SHALL denegar el acceso.
3. THE Sistema SHALL validar el formato del email antes de cualquier otra validación.

---

## Requisito Nuevo: Validación de Estado OTRO

**User Story:**  
Como sistema, quiero controlar el uso del estado OTRO para mantener consistencia visual.

### Criterios de Aceptación

1. WHEN el estado es OTRO, THEN THE Sistema SHALL requerir un texto descriptivo.
2. THE texto SHALL tener máximo 50 caracteres.
3. THE Sistema SHALL sanitizar el contenido antes de mostrarlo.
4. IF el estado no es OTRO, THEN la descripción SHALL ser nula.

---

## Requisito Nuevo: Orden del Tablero

**User Story:**  
Como familiar, quiero ver primero los pacientes más recientes.

### Criterios de Aceptación

1. THE Tablero SHALL ordenar los pacientes por `ingresadoEn` en orden descendente.
2. THE paciente más reciente SHALL aparecer en la parte superior.

---

## Requisito Nuevo: Flujo Operativo del Sistema

**User Story:**  
Como Funcionario, quiero un flujo claro y rápido.

### Criterios de Aceptación

1. THE Sistema SHALL permitir seleccionar estado desde Tabla_Programados.
2. WHEN se selecciona estado, THEN THE Sistema SHALL crear o actualizar la Sesion.
3. THE paciente SHALL aparecer en Tabla_En_Sala inmediatamente.
4. WHEN se selecciona FINALIZADO, THEN el paciente SHALL desaparecer del tablero.

---

## Requisito Nuevo: Concurrencia

**User Story:**  
Como sistema, quiero manejar actualizaciones simultáneas sin inconsistencias.

### Criterios de Aceptación

1. IF múltiples actualizaciones ocurren sobre la misma Sesion, THEN THE Sistema SHALL aplicar la última.
2. THE Sistema SHALL garantizar consistencia mediante restricciones en base de datos.

---

# ⚙️ AJUSTES — DISEÑO TÉCNICO

## Modelo Paciente

```python
class Paciente(models.Model):
    identificacion = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    origen = models.CharField(max_length=20, choices=[
        ('PROGRAMADO', 'Programado'),
        ('URGENCIAS', 'Urgencias')
    ])
```

---

## Modelo Sesion

```python
class Sesion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)

    estado = models.CharField(max_length=20, choices=EstadoQuirurgico.choices)
    descripcionOtro = models.CharField(max_length=50, null=True, blank=True)

    ingresadoEn = models.DateTimeField(auto_now_add=True)
    actualizadoEn = models.DateTimeField(auto_now=True)

    oculto = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['paciente'],
                condition=models.Q(oculto=False),
                name='unique_active_session_per_patient'
            )
        ]
        indexes = [
            models.Index(fields=['oculto', 'ingresadoEn'])
        ]
```

---

## Eliminaciones

1. THE campo `finalizado` SHALL ser eliminado.
2. THE campo `identificacion` duplicado SHALL eliminarse en modelos derivados.
3. THE modelo `RegistroEstado` MAY eliminarse en MVP.

---

## SesionServicio

### Reglas

1. THE servicio SHALL trabajar con `paciente`.
2. THE servicio SHALL reutilizar sesión activa existente.
3. WHEN estado = FINALIZADO:
   - THE Sistema SHALL marcar `oculto=True`
   - THE Sistema SHALL NO eliminar datos

---

## Eliminación de Endpoint

```
POST /gestion/sesiones/<id>/eliminar/
```

1. THE endpoint SHALL ser eliminado.
2. THE lógica SHALL manejarse mediante estados.

---

## Query de Tablero

```python
Sesion.objects.filter(oculto=False).order_by('-ingresadoEn')
```

---

## Validación OTRO

```python
if nuevoEstado == EstadoQuirurgico.OTRO:
    if not descripcionOtro:
        raise ValidationError("Descripción requerida")
    descripcionOtro = descripcionOtro[:50].strip()
else:
    descripcionOtro = None
```

---

## Autenticación

1. THE Sistema SHALL validar email contra whitelist o dominio.
2. THE validación SHALL ejecutarse antes de crear sesión.

---

# ✅ RESULTADO

Sistema MVP:
- Consistente
- Sin duplicidad
- Seguro (nivel MVP)
- Escalable
- Listo para implementación en Django + HTMX

