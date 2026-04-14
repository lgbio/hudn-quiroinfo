import logging

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from app_autenticacion.mixins import LoginRequeridoMixin
from app_notificaciones.servicios import NotificacionServicio

from .models import EstadoQuirurgico, Paciente
from .servicios import SesionServicio, coloresEstado, obtenerSesionesVisibles

logger = logging.getLogger (__name__)


class GestionVista (LoginRequeridoMixin, View):
	"""Panel de gestión principal: muestra pacientes y sesiones activas."""

	def get (self, request):
		"""Retorna el panel con pacientes, sesiones activas y lista de estados."""
		contexto = _contextoGestion ()
		return render (request, 'gestion/gestion.html', contexto)


class AplicarEstadoVista (LoginRequeridoMixin, View):
	"""Aplica un nuevo estado quirúrgico a la sesión de un paciente."""

	def post (self, request):
		"""Recibe pacienteId y estado; actualiza la sesión y retorna fragmento HTMX."""
		pacienteId      = request.POST.get ('pacienteId')
		estado          = request.POST.get ('estado')
		descripcionOtro = request.POST.get ('descripcionOtro', None) or None

		if not pacienteId or not estado:
			return HttpResponse ('Datos incompletos.', status=400)

		paciente = get_object_or_404 (Paciente, pk=pacienteId)

		try:
			servicio = SesionServicio ()
			sesion   = servicio.aplicarEstado (paciente, estado, descripcionOtro)
			NotificacionServicio ().notificarCambioEstado (paciente.identificacion, estado)
		except ValidationError as e:
			return HttpResponse (str (e), status=400)
		except Exception as e:
			print (f"+++ Error al aplicar estado: {e}")
			logger.error (f"Error al aplicar estado: {e}")
			return HttpResponse ('Error interno al actualizar el estado.', status=500)

		return self._renderizarFragmento (request)

	def _renderizarFragmento (self, request):
		"""Construye el contexto y renderiza el fragmento de tablas."""
		return render (request, 'gestion/fragmento_tablas.html', _contextoGestion ())


class AgregarPacienteVista (LoginRequeridoMixin, View):
	"""Agrega un paciente de urgencias y retorna el fragmento de tablas actualizado."""

	def post (self, request):
		"""Crea un Paciente con origen URGENCIAS y retorna fragmento HTMX."""
		identificacion = request.POST.get ('identificacion', '').strip ()
		nombre         = request.POST.get ('nombre', '').strip () or None

		if not identificacion:
			return HttpResponse ('La identificación es requerida.', status=400)

		Paciente.objects.get_or_create (
			identificacion=identificacion,
			defaults={'nombre': nombre, 'origen': 'URGENCIAS'},
		)

		return render (request, 'gestion/fragmento_tablas.html', _contextoGestion ())


class TableroVista (View):
	"""Tablero público de seguimiento quirúrgico para pantallas TV."""

	def get (self, request):
		"""Retorna el tablero completo con layout TV, sin autenticación."""
		contexto = {
			'sesiones':      obtenerSesionesVisibles (),
			'coloresEstado': coloresEstado,
		}
		return render (request, 'tablero/tablero.html', contexto)


class TableroFragmentoVista (View):
	"""Retorna solo el fragmento de lista para polling HTMX del tablero."""

	def get (self, request):
		"""Retorna el fragmento HTML con las sesiones visibles actualizadas."""
		contexto = {
			'sesiones':      obtenerSesionesVisibles (),
			'coloresEstado': coloresEstado,
		}
		return render (request, 'tablero/fragmento.html', contexto)


def _contextoGestion ():
	"""Construye el contexto compartido para las vistas del panel de gestión."""
	sesiones = list (obtenerSesionesVisibles ())
	sesionPorPaciente = {s.paciente_id: s for s in sesiones}
	return {
		'pacientes':         Paciente.objects.all (),
		'sesionesActivas':   sesiones,
		'estados':           EstadoQuirurgico,
		'sesionPorPaciente': sesionPorPaciente,
	}
