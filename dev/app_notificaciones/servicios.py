import logging

logger = logging.getLogger (__name__)


class NotificacionServicio:
	"""Gestiona el registro de notificaciones internas del sistema."""

	def notificarCambioEstado (self, identificacion: str, nuevoEstado: str) -> None:
		"""Registra el cambio de estado en el log. Sin envío externo en v1."""
		logger.info (f"[NOTIFICACION] Paciente {identificacion}: nuevo estado → {nuevoEstado}")
