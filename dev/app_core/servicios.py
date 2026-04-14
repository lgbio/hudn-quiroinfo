import logging

from django.core.exceptions import ValidationError

from .models import EstadoQuirurgico, Paciente, RegistroEstado, Sesion

logger = logging.getLogger (__name__)


coloresEstado = {
	EstadoQuirurgico.EN_PREPARACION:  'bg-yellow-400',
	EstadoQuirurgico.EN_CIRUGIA:      'bg-orange-500',
	EstadoQuirurgico.EN_RECUPERACION: 'bg-blue-500',
	EstadoQuirurgico.FINALIZADO:      'bg-gray-400',
	EstadoQuirurgico.OTRO:            'bg-purple-500',
}


class SesionServicio:
	"""Gestiona la creación y actualización de sesiones quirúrgicas."""

	def aplicarEstado (self, paciente: Paciente, nuevoEstado: str, descripcionOtro: str = None) -> Sesion:
		print (f"+++ {paciente=} {nuevoEstado=} {descripcionOtro=}")

		"""Crea la sesión si no existe, o actualiza el estado si ya existe."""
		descripcionOtro = self._validarDescripcion (nuevoEstado, descripcionOtro)

		sesion, creada = Sesion.objects.get_or_create (
			paciente=paciente,
			oculto=False,
			defaults={'estado': nuevoEstado, 'descripcionOtro': descripcionOtro},
		)
		estadoAnterior = None if creada else sesion.estado

		if not creada:
			sesion.estado          = nuevoEstado
			sesion.descripcionOtro = descripcionOtro

		if nuevoEstado == EstadoQuirurgico.FINALIZADO:
			sesion.oculto = True

		sesion.save ()

		RegistroEstado.objects.create (
			sesion=sesion,
			estadoAnterior=estadoAnterior,
			estadoNuevo=nuevoEstado,
		)

		logger.info (f"Estado aplicado: {paciente.identificacion} → {nuevoEstado}")
		return sesion

	def _validarDescripcion (self, nuevoEstado: str, descripcionOtro: str) -> str | None:
		"""Valida y normaliza descripcionOtro según el estado recibido."""
		if nuevoEstado == EstadoQuirurgico.OTRO:
			if not descripcionOtro or not descripcionOtro.strip ():
				raise ValidationError ("Descripción requerida para estado OTRO")
			return descripcionOtro [:50].strip ()
		return None


def obtenerSesionesVisibles ():
	"""Retorna sesiones activas no ocultas, ordenadas por ingresadoEn descendente."""
	return (
		Sesion.objects
		.filter (oculto=False)
		.select_related ('paciente')
		.only ('id', 'paciente__identificacion', 'estado', 'descripcionOtro', 'ingresadoEn', 'actualizadoEn')
		.order_by ('-ingresadoEn')
	)
