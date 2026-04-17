# Plan de Implementación: Mejoras MVP Quiroinfo

## Visión General

Implementación incremental de las mejoras al MVP: eliminación de `descripcionOtro`, simplificación del Botón_OTRO, modal de edición de pacientes, actualización del tablero y estilo oscuro en Tabla_En_Sala. Incluye cambios post-spec: persistencia de `labelOtro` e `identificacion` en BD, refactorización del Tablero como pantalla TV, orden consistente entre tablas, eliminación de `RegistroEstado`, carga manual de pacientes programados, CASCADE delete y fix del modal.

## Tareas

- [x] 1. Eliminar `descripcionOtro` del modelo y la capa de servicio
  - [x] 1.1 Eliminar el campo `descripcionOtro` del modelo `Sesion` en `app_core/models.py`
    - _Requisitos: 1.1_
  - [x] 1.2 Crear migración para eliminar la columna `descripcion_otro`
    - _Requisitos: 1.1_
  - [x] 1.3 Simplificar `SesionServicio.aplicarEstado` en `app_core/servicios.py`
    - _Requisitos: 1.1, 1.6_
  - [x] 1.4 Eliminar lectura de `descripcionOtro` del POST en `AplicarEstadoVista`
    - _Requisitos: 1.1_
  - [x] 1.5 Actualizar `obtenerSesionesVisibles`: cambiar orden a `-actualizadoEn`
    - _Requisitos: 3.2, 4.1_

- [x] 2. Actualizar tests existentes que referencian `descripcionOtro`
  - [x] 2.1 Eliminar tests de `descripcionOtro`; agregar `test_otro_sin_descripcion_no_lanza_error`
    - _Requisitos: 1.1, 1.6, 3.2_
  - [x] 2.2 Propiedad 1: `obtenerSesionesVisibles` retorna solo sesiones con `oculto=False`
    - _Requisitos: 3.1_
  - [x] 2.3 Propiedad 2: resultados ordenados por `actualizadoEn` descendente
    - _Requisitos: 3.2, 4.1_

- [x] 3. Checkpoint — verificar capa de modelo y servicio

- [x] 4. Simplificar Botón_OTRO en `fragmento_tablas.html`
  - [x] 4.1 Botón_OTRO con `hx-post` directo; label desde `sesion.labelOtro` (BD)
    - _Requisitos: 1.2, 1.3, 1.5, 1.6_

- [x] 5. Implementar Modal_Edicion en `fragmento_tablas.html`
  - [x] 5.1 Ampliar `x-data` con estado del modal
    - _Requisitos: 2.1, 2.2_
  - [x] 5.2 Agregar columna "Acciones" y botón "Editar"
    - _Requisitos: 2.1, 2.3_
  - [x] 5.3 Markup del Modal_Edicion
    - _Requisitos: 2.2, 2.4, 2.5_
  - [x] 5.4 Lógica de guardado en Alpine.js
    - _Requisitos: 2.4, 2.5, 2.6, 2.9, 2.11_

- [x] 6. Actualizar layout del Tablero en `tablero/fragmento.html`
  - [x] 6.1 Reemplazar grid de cards por layout flex con filas
    - _Requisitos: 3.3, 3.4, 3.5_

- [x] 7. Aplicar estilo oscuro a `Tabla_Pacientes_En_Sala`
  - [x] 7.1 Tema oscuro en contenedor derecho
    - _Requisitos: 4.2, 4.3_
  - [x] 7.2 Actualizar filas, badges y columna `actualizadoEn`
    - _Requisitos: 4.1, 4.6, 1.1_

- [x] 8. Checkpoint final — ejecutar pytest y verificar todos los tests

- [x] 9. Persistir `labelOtro` en BD
  - [x] 9.1 Agregar `labelOtro = models.CharField(max_length=50, default='Otro')` al modelo `Sesion`; migración `0003_sesion_labelotro`
    - _Requisitos: 1.4, 1.7_
  - [x] 9.2 Actualizar `SesionServicio.aplicarEstado` para aceptar y persistir `labelOtro`
    - _Requisitos: 1.4_
  - [x] 9.3 Incluir `labelOtro` en `.only()` de `obtenerSesionesVisibles`
    - _Requisitos: 1.7_
  - [x] 9.4 Actualizar templates para leer `sesion.labelOtro` desde BD
    - _Requisitos: 1.7_

- [x] 10. Persistir `identificacion` en BD + `ActualizarPacienteVista`
  - [x] 10.1 Crear `ActualizarPacienteVista` (`POST /gestion/pacientes/actualizar/`)
    - _Requisitos: 2.6, 2.7_
  - [x] 10.2 Registrar URL en `app_core/urls.py`
    - _Requisitos: 2.6_
  - [x] 10.3 Actualizar Modal_Edicion para enviar POST a `ActualizarPacienteVista`
    - _Requisitos: 2.6, 2.10_

- [x] 11. Refactorizar Tablero como pantalla TV
  - [x] 11.1 `tablero.html`: `html/body` con `height: 100vh; overflow: hidden`
    - _Requisitos: 3.4_
  - [x] 11.2 `fragmento.html`: flex column con filas `flex: 1 1 0; min-height: 0`
    - _Requisitos: 3.4, 3.5_
  - [x] 11.3 Fuentes con `clamp(min, Xvh, max)` en el Tablero
    - _Requisitos: 3.6, 3.9_
  - [x] 11.4 Hora en formato 12h: `{{ sesion.actualizadoEn|date:"g:i a" }}`
    - _Requisitos: 3.8_

- [x] 12. Orden consistente entre tablas
  - [x] 12.1 Refactorizar `_contextoGestion`: pacientes con sesión en orden `-actualizadoEn`; sin sesión al final por `identificacion`
    - _Requisitos: 5.1, 5.2, 5.3_

- [x] 13. Eliminar `RegistroEstado`
  - [x] 13.1 Eliminar modelo de `models.py`; migración `0005_eliminar_registroestado`
    - _Requisitos: 6.1_
  - [x] 13.2 Eliminar lógica de creación en `servicios.py` y tests relacionados
    - _Requisitos: 6.2_

- [x] 14. Carga manual de pacientes programados
  - [x] 14.1 Crear `CargarProgramadosVista` (`POST /gestion/programados/cargar/`) con lock `_ejecutando`
    - _Requisitos: 7.3, 7.6, 7.8_
  - [x] 14.2 Registrar URL en `app_core/urls.py`
    - _Requisitos: 7.3_
  - [x] 14.3 Refactorizar `Utils.cargarPacientesProgramadosCirugia` para usar ORM
    - _Requisitos: 7.4, 8.3_
  - [x] 14.4 Botón "Cargar pacientes programados" con Alpine.js confirm + spinner
    - _Requisitos: 7.1, 7.2, 7.5_

- [x] 15. CASCADE delete en `Sesion.paciente`
  - [x] 15.1 Cambiar `on_delete=PROTECT` por `on_delete=CASCADE`; migración `0007_sesion_paciente_cascade`
    - _Requisitos: 8.1_

- [x] 16. Fix modal — no modificar estado si no cambió explícitamente
  - [x] 16.1 Agregar `editEstadoOriginal` al `x-data`; inicializar al abrir modal
    - _Requisitos: 2.7, 2.8_
  - [x] 16.2 En `guardar()`: solo enviar `labelOtro`/`estadoOtro` si `editEstado !== editEstadoOriginal`
    - _Requisitos: 2.7, 2.8_
  - [x] 16.3 Solo `identificacion` es campo requerido para guardar
    - _Requisitos: 2.4_

## Notas

- Las tareas marcadas con `*` son opcionales
- Cada tarea referencia requisitos específicos para trazabilidad
- Los tests de propiedad usan Hypothesis con `@settings(max_examples=100)`
- `labelOtro` persiste en BD (`Sesion.labelOtro`); no es estado Alpine.js
- El ordenamiento de ambas tablas y el Tablero usa `-actualizadoEn`
- El Tablero usa layout flex con `height: 100vh` y filas con `flex: 1` para distribución dinámica
- Fuentes del Tablero escalan con `clamp(min, Xvh, max)` para adaptarse a cualquier tamaño de pantalla
