import uuid
from django.db import models


class EstadoQuirurgico (models.TextChoices):
	"""Enumeración de los estados posibles del proceso quirúrgico."""

	EN_PREPARACION  = 'EN_PREPARACION',  'En preparación'
	EN_CIRUGIA      = 'EN_CIRUGIA',      'En cirugía'
	EN_RECUPERACION = 'EN_RECUPERACION', 'En recuperación'
	FINALIZADO      = 'FINALIZADO',      'Finalizado'
	OTRO            = 'OTRO',            'Otro'


class Paciente (models.Model):
	"""Modelo unificado de paciente, con origen PROGRAMADO o URGENCIAS."""

	identificacion = models.CharField (max_length=50, unique=True)
	nombre         = models.CharField (max_length=255, null=True, blank=True)
	origen         = models.CharField (
		max_length=20,
		choices=[('PROGRAMADO', 'Programado'), ('URGENCIAS', 'Urgencias')]
	)

	class Meta:
		db_table = 'pacientes'

	def __str__ (self):
		"""Retorna la identificación del paciente como representación textual."""
		return self.identificacion


class Sesion (models.Model):
	"""Registro activo de un paciente en el tablero durante su proceso quirúrgico."""

	id              = models.UUIDField (primary_key=True, default=uuid.uuid4, editable=False)
	paciente        = models.ForeignKey (Paciente, on_delete=models.PROTECT)
	estado          = models.CharField (max_length=20, choices=EstadoQuirurgico.choices)
	descripcionOtro = models.CharField (max_length=50, null=True, blank=True)
	ingresadoEn     = models.DateTimeField (auto_now_add=True)
	actualizadoEn   = models.DateTimeField (auto_now=True)
	oculto          = models.BooleanField (default=False)

	class Meta:
		db_table = 'sesiones'
		constraints = [
			models.UniqueConstraint (
				fields=['paciente'],
				condition=models.Q (oculto=False),
				name='unique_active_session_per_patient'
			)
		]
		indexes = [
			models.Index (fields=['oculto', 'ingresadoEn'])
		]

	def __str__ (self):
		"""Retorna identificación y estado como representación textual."""
		return f"{self.paciente.identificacion} — {self.estado}"


class RegistroEstado (models.Model):
	"""Auditoría de cada cambio de estado de una sesión quirúrgica."""

	id             = models.UUIDField (primary_key=True, default=uuid.uuid4, editable=False)
	sesion         = models.ForeignKey (Sesion, on_delete=models.PROTECT)
	estadoAnterior = models.CharField (max_length=20, null=True, blank=True)
	estadoNuevo    = models.CharField (max_length=20)
	cambiadoEn     = models.DateTimeField (auto_now_add=True)

	class Meta:
		db_table = 'registro_estados'
