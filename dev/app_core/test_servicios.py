import pytest
import factory

from django.core.exceptions import ValidationError

from .models import EstadoQuirurgico, Paciente, Sesion, RegistroEstado
from .servicios import SesionServicio, obtenerSesionesVisibles


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

class PacienteFactory (factory.django.DjangoModelFactory):
	"""Factory para crear instancias de Paciente en tests."""

	class Meta:
		model = Paciente

	identificacion = factory.Sequence (lambda n: f"PAC-{n:04d}")
	nombre         = factory.Sequence (lambda n: f"Paciente {n}")
	origen         = 'PROGRAMADO'


class SesionFactory (factory.django.DjangoModelFactory):
	"""Factory para crear instancias de Sesion en tests."""

	class Meta:
		model = Sesion

	paciente = factory.SubFactory (PacienteFactory)
	estado   = EstadoQuirurgico.EN_PREPARACION
	oculto   = False


# ---------------------------------------------------------------------------
# Tests de SesionServicio.aplicarEstado
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAplicarEstado:
	"""Tests unitarios para SesionServicio.aplicarEstado."""

	def setup_method (self):
		"""Inicializa el servicio antes de cada test."""
		self.servicio = SesionServicio ()

	def test_crea_sesion_nueva_si_no_existe (self):
		"""aplicarEstado() crea una sesión nueva cuando el paciente no tiene sesión activa."""
		paciente = PacienteFactory ()

		sesion = self.servicio.aplicarEstado (paciente, EstadoQuirurgico.EN_PREPARACION)

		assert Sesion.objects.filter (paciente=paciente, oculto=False).count () == 1
		assert sesion.estado == EstadoQuirurgico.EN_PREPARACION
		assert sesion.paciente == paciente

	def test_actualiza_estado_si_sesion_ya_existe (self):
		"""aplicarEstado() actualiza el estado cuando el paciente ya tiene sesión activa."""
		paciente = PacienteFactory ()
		SesionFactory (paciente=paciente, estado=EstadoQuirurgico.EN_PREPARACION)

		sesion = self.servicio.aplicarEstado (paciente, EstadoQuirurgico.EN_CIRUGIA)

		assert sesion.estado == EstadoQuirurgico.EN_CIRUGIA
		assert Sesion.objects.filter (paciente=paciente, oculto=False).count () == 1

	def test_finalizado_marca_oculto_true (self):
		"""aplicarEstado() con FINALIZADO marca oculto=True y conserva el registro en BD."""
		paciente = PacienteFactory ()
		SesionFactory (paciente=paciente, estado=EstadoQuirurgico.EN_CIRUGIA)

		sesion = self.servicio.aplicarEstado (paciente, EstadoQuirurgico.FINALIZADO)

		sesion.refresh_from_db ()
		assert sesion.oculto is True
		assert Sesion.objects.filter (paciente=paciente).exists ()

	def test_otro_guarda_descripcion_truncada_a_50_chars (self):
		"""aplicarEstado() con OTRO guarda descripcionOtro truncado a 50 caracteres."""
		paciente     = PacienteFactory ()
		descripcion  = "A" * 80

		sesion = self.servicio.aplicarEstado (paciente, EstadoQuirurgico.OTRO, descripcion)

		assert sesion.descripcionOtro == "A" * 50

	def test_otro_sin_descripcion_lanza_validation_error (self):
		"""aplicarEstado() con OTRO y sin descripción lanza ValidationError."""
		paciente = PacienteFactory ()

		with pytest.raises (ValidationError):
			self.servicio.aplicarEstado (paciente, EstadoQuirurgico.OTRO)

	def test_otro_con_descripcion_vacia_lanza_validation_error (self):
		"""aplicarEstado() con OTRO y descripción vacía lanza ValidationError."""
		paciente = PacienteFactory ()

		with pytest.raises (ValidationError):
			self.servicio.aplicarEstado (paciente, EstadoQuirurgico.OTRO, "   ")

	def test_estado_distinto_a_otro_fuerza_descripcion_none (self):
		"""aplicarEstado() con estado distinto a OTRO establece descripcionOtro=None."""
		paciente = PacienteFactory ()

		sesion = self.servicio.aplicarEstado (paciente, EstadoQuirurgico.EN_PREPARACION, "ignorar esto")

		assert sesion.descripcionOtro is None

	def test_crea_registro_estado_al_aplicar (self):
		"""aplicarEstado() crea un RegistroEstado por cada llamada."""
		paciente = PacienteFactory ()

		self.servicio.aplicarEstado (paciente, EstadoQuirurgico.EN_PREPARACION)
		self.servicio.aplicarEstado (paciente, EstadoQuirurgico.EN_CIRUGIA)

		assert RegistroEstado.objects.filter (sesion__paciente=paciente).count () == 2


# ---------------------------------------------------------------------------
# Tests de obtenerSesionesVisibles
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestObtenerSesionesVisibles:
	"""Tests unitarios para obtenerSesionesVisibles."""

	def test_no_retorna_sesiones_ocultas (self):
		"""obtenerSesionesVisibles() no incluye sesiones con oculto=True."""
		SesionFactory (oculto=True)
		SesionFactory (oculto=False)

		resultado = list (obtenerSesionesVisibles ())

		assert len (resultado) == 1
		assert resultado [0].oculto is False

	def test_retorna_sesiones_ordenadas_por_ingresado_en_descendente (self):
		"""obtenerSesionesVisibles() retorna sesiones ordenadas por ingresadoEn descendente."""
		sesion1 = SesionFactory ()
		sesion2 = SesionFactory ()
		sesion3 = SesionFactory ()

		resultado = list (obtenerSesionesVisibles ())
		ids       = [s.id for s in resultado]

		assert ids == [sesion3.id, sesion2.id, sesion1.id]
