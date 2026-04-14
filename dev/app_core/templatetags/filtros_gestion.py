from django import template

register = template.Library ()


@register.filter
def get_item (diccionario, clave):
	"""Retorna el valor de un diccionario dado su clave."""
	return diccionario.get (clave)
