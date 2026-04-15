# Plan de Implementación: Mejoras MVP Quiroinfo

## Visión General

Implementación incremental de las cuatro mejoras al MVP: eliminación de `descripcionOtro`, simplificación del Botón_OTRO, modal de edición de pacientes, actualización del tablero y estilo oscuro en Tabla_En_Sala.

## Tareas

- [x] 1. Eliminar `descripcionOtro` del modelo y la capa de servicio
  - [x] 1.1 Eliminar el campo `descripcionOtro` del modelo `Sesion` en `app_core/models.py`
    - Remover la línea `descripcionOtro = models.CharField (...)` del modelo
    - _Requisitos: 1.1_

  - [x] 1.2 Crear migración para eliminar la columna `descripcion_otro`
    - Generar con `python manage.py makemigrations` y verificar que la migración elimina la columna
    - _Requisitos: 1.1_

  - [x] 1.3 Simplificar `SesionServicio.aplicarEstado` en `app_core/servicios.py`
    - Eliminar el parámetro `descripcionOtro` de la firma del método
    - Eliminar la llamada a `self._validarDescripcion` y la asignación `sesion.descripcionOtro`
    - Eliminar el método privado `_validarDescripcion` completo
    - Eliminar `descripcionOtro` del `defaults` en `get_or_create`
    - _Requisitos: 1.1, 1.6_

  - [x] 1.4 Eliminar lectura de `descripcionOtro` del POST en `AplicarEstadoVista` en `app_core/vistas.py`
    - Remover la línea `descripcionOtro = request.POST.get ('descripcionOtro', None) or None`
    - Remover el parámetro `descripcionOtro` de la llamada a `servicio.aplicarEstado`
    - _Requisitos: 1.1_

  - [x] 1.5 Actualizar `obtenerSesionesVisibles` en `app_core/servicios.py`
    - Cambiar `order_by ('-ingresadoEn')` por `order_by ('-actualizadoEn')`
    - Eliminar `'descripcionOtro'` del `.only (...)` si está presente
    - Actualizar el docstring para reflejar el nuevo ordenamiento
    - _Requisitos: 3.2, 4.1_

- [x] 2. Actualizar tests existentes que referencian `descripcionOtro`
  - [x] 2.1 Actualizar `test_servicios.py`: eliminar o reemplazar tests de `descripcionOtro`
    - Eliminar `test_otro_guarda_descripcion_truncada_a_50_chars`
    - Eliminar `test_otro_sin_descripcion_lanza_validation_error`
    - Eliminar `test_otro_con_descripcion_vacia_lanza_validation_error`
    - Eliminar `test_estado_distinto_a_otro_fuerza_descripcion_none`
    - Agregar `test_otro_sin_descripcion_no_lanza_error`: verifica que `aplicarEstado (paciente, 'OTRO')` retorna sesión sin error
    - Actualizar `test_retorna_sesiones_ordenadas_por_ingresado_en_descendente` → renombrar a `test_retorna_sesiones_ordenadas_por_actualizado_en_descendente` y ajustar el docstring
    - _Requisitos: 1.1, 1.6, 3.2_

  - [x] 2.2 Escribir test de propiedad: `obtenerSesionesVisibles` retorna solo sesiones con `oculto=False`
    - **Propiedad 1: Filtrado de sesiones visibles**
    - **Valida: Requisito 3.1**
    - Usar `@given (st.lists (st.booleans (), min_size=1))` con `@settings (max_examples=100)`
    - Crear sesiones con la lista de valores `oculto` generada; verificar que el resultado contiene exactamente las de `oculto=False`
    - Agregar en `test_servicios.py` bajo la clase `TestObtenerSesionesVisibles`

  - [x] 2.3 Escribir test de propiedad: resultados ordenados por `actualizadoEn` descendente
    - **Propiedad 2: Ordenamiento por actualizadoEn descendente**
    - **Valida: Requisitos 3.2, 4.1**
    - Usar `@given (st.lists (st.datetimes (timezones=st.just (timezone.utc)), min_size=2))` con `@settings (max_examples=100)`
    - Crear sesiones con `actualizadoEn` forzado mediante `update()`; verificar que pares consecutivos cumplen `s_i.actualizadoEn >= s_{i+1}.actualizadoEn`
    - Agregar en `test_servicios.py` bajo la clase `TestObtenerSesionesVisibles`

- [x] 3. Checkpoint — verificar capa de modelo y servicio
  - Asegurarse de que todos los tests pasan hasta este punto. Consultar al usuario si surgen dudas.

- [x] 4. Simplificar Botón_OTRO en `fragmento_tablas.html`
  - [x] 4.1 Agregar `labelOtro: 'Otro'` al bloque `x-data` de cada fila en `Tabla_Programados`
    - El bloque `x-data` de la fila debe incluir `labelOtro: 'Otro'` junto a `estadoActual` y `mostrarOtro`
    - Eliminar `mostrarOtro` del `x-data` ya que el flujo de confirmación desaparece
    - _Requisitos: 1.3, 1.5_

  - [x] 4.2 Reemplazar el bloque condicional del Botón_OTRO por un botón con `hx-post` directo
    - El botón OTRO debe tener `hx-post`, `hx-target`, `hx-swap` y `hx-vals` igual que los demás botones
    - Usar `x-text="labelOtro"` para renderizar el label dinámico en lugar del texto estático `{{ etiqueta }}`
    - Eliminar el bloque `<div x-show="mostrarOtro">` con el input de descripción y el botón Confirmar
    - _Requisitos: 1.2, 1.3, 1.5, 1.6_

- [x] 5. Implementar Modal_Edicion en `fragmento_tablas.html`
  - [x] 5.1 Ampliar el bloque `x-data` de cada fila para incluir el estado del modal
    - Agregar al `x-data`: `modalAbierto: false`, `editId: '{{ paciente.identificacion }}'`, `editNombre: '{{ paciente.nombre|default:"" }}'`, `editEstado: ''`, `errorEdicion: ''`
    - _Requisitos: 2.1, 2.2_

  - [x] 5.2 Agregar columna "Acciones" y botón "Editar" en el `<thead>` y en cada fila de `Tabla_Programados`
    - Agregar `<th>` para "Acciones" en el encabezado
    - Agregar `<td>` con botón "Editar" que ejecute `x-on:click="modalAbierto = true; editEstado = estadoActual === 'OTRO' ? labelOtro : estadoActual"`
    - _Requisitos: 2.1, 2.3_

  - [x] 5.3 Implementar el markup del Modal_Edicion dentro de la fila
    - Renderizar el modal con `x-show="modalAbierto"` y `x-cloak`
    - Campos: Identificación (`x-model="editId"`, editable), Nombre (`x-text="editNombre"`, solo lectura), Estado (`x-model="editEstado"`, editable)
    - Mostrar `<p x-show="errorEdicion" x-text="errorEdicion">` para errores de validación
    - Botón "Guardar" con `x-on:click` que ejecuta la lógica de guardado
    - Botón "Cancelar" que cierra el modal sin guardar
    - _Requisitos: 2.2, 2.4, 2.5_

  - [x] 5.4 Implementar la lógica de guardado del modal en Alpine.js
    - Validar que `editId.trim()` y `editEstado.trim()` no estén vacíos; si fallan, asignar mensaje a `errorEdicion` y no cerrar
    - Si válidos: actualizar `labelOtro = editEstado`; si el estado fue modificado, disparar `htmx.ajax ('POST', url, { values: { pacienteId, estado: 'OTRO' }, target: '#fragmento-tablas', swap: 'outerHTML' })`
    - Cerrar modal: `modalAbierto = false; errorEdicion = ''`
    - _Requisitos: 2.4, 2.5, 2.6, 2.9, 2.11_

  - [ ]* 5.5 Escribir tests de vista para el flujo del modal
    - Verificar que POST a `aplicar-estado` con `estado=OTRO` sin `descripcionOtro` retorna HTTP 200
    - Verificar que el fragmento renderizado contiene la identificación del paciente
    - Agregar en `test_vistas.py`
    - _Requisitos: 1.2, 2.9_

- [x] 6. Actualizar layout del Tablero en `tablero/fragmento.html`
  - [x] 6.1 Reemplazar el grid de cards por una tabla HTML con filas
    - Eliminar el `<div class="grid ...">` y los `<div class="bg-gray-800 rounded-2xl ...">` por fila
    - Crear `<table>` con `<thead>` (columnas: Identificación, Estado, Última actualización) y `<tbody>` con `{% for sesion in sesiones %}`
    - Cada `<tr>` muestra: `sesion.paciente.identificacion`, badge de estado con los mismos colores del diseño, `sesion.actualizadoEn|date:"d/m/Y H:i"`
    - Eliminar el bloque `{% if sesion.estado == 'OTRO' and sesion.descripcionOtro %}` que ya no aplica
    - _Requisitos: 3.3, 3.4, 3.5_

- [x] 7. Aplicar estilo oscuro a `Tabla_Pacientes_En_Sala` en `fragmento_tablas.html`
  - [x] 7.1 Cambiar el contenedor de la columna derecha a tema oscuro
    - Reemplazar `bg-white` por `bg-gray-900` y ajustar texto a `text-white` en el `<div>` contenedor
    - Actualizar el `<h2>` a color claro (ej. `text-gray-100`)
    - Actualizar el `<thead>` a `text-gray-400 border-gray-700`
    - _Requisitos: 4.2, 4.3_

  - [x] 7.2 Actualizar filas y badges de `Tabla_Pacientes_En_Sala`
    - Cambiar `border-b` de filas a `border-gray-700`
    - Reemplazar la columna "Hora ingreso" (`ingresadoEn`) por "Última actualización" (`actualizadoEn`)
    - Actualizar el texto de la celda vacía a color claro (`text-gray-500`)
    - Eliminar el bloque `{% if sesion.estado == 'OTRO' and sesion.descripcionOtro %}` de la columna Estado
    - _Requisitos: 4.1, 4.6, 1.1_

- [x] 8. Checkpoint final — ejecutar pytest y verificar todos los tests
  - Asegurarse de que todos los tests pasan. Consultar al usuario si surgen dudas.

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia requisitos específicos para trazabilidad
- Los tests de propiedad usan Hypothesis con `@settings(max_examples=100)`
- El Label_OTRO es estado de UI (Alpine.js); no requiere persistencia en base de datos
- La actualización de identificación en Tabla_En_Sala se logra mediante el re-render del fragmento HTMX tras el POST de `aplicar-estado`
