# Documento de Requisitos

## Introducción

Mejoras al MVP existente de Quiroinfo, un sistema de seguimiento de estado quirúrgico para familiares. Las mejoras abordan cuatro áreas: simplificación del botón "OTRO" (eliminando el flujo de descripción adicional y reemplazándolo por un label dinámico), edición de datos de pacientes desde el panel de gestión, actualización del tablero público con ordenamiento por `updated_at` y polling automático, y homogeneización visual de la tabla de pacientes en sala con el estilo del tablero.

La arquitectura permanece igual: Django SSR con HTMX para interacciones dinámicas, Alpine.js para comportamientos ligeros de UI, y Tailwind CSS por CDN.

## Glosario

- **Sistema**: La aplicación web Quiroinfo de seguimiento de estado quirúrgico.
- **Tablero**: Pantalla pública proyectada en sala de espera. Solo lectura, sin autenticación.
- **Funcionario**: Usuario autenticado con acceso al Panel_Gestion.
- **Panel_Gestion**: Vista privada del Funcionario con las dos tablas paralelas de operación.
- **Tabla_Programados**: Tabla izquierda del Panel_Gestion con la lista de pacientes y sus botones de estado.
- **Tabla_Pacientes_En_Sala**: Tabla derecha del Panel_Gestion con los pacientes actualmente visibles en el Tablero.
- **Botón_OTRO**: Botón de estado en la Tabla_Programados que representa el estado `OTRO` con un label configurable.
- **Modal_Edicion**: Modal que aparece al hacer clic en "Editar" en una fila de la Tabla_Programados.
- **Campo_Estado**: Campo de texto editable dentro del Modal_Edicion que representa el estado del paciente.
- **Label_OTRO**: Texto visible en el Botón_OTRO, inicialmente "Otro", actualizable desde el Modal_Edicion.
- **Sesion**: Registro activo de un paciente en el tablero con su estado actual.
- **descripcionOtro**: Campo del modelo Sesion que actualmente almacena la descripción del estado OTRO. Será eliminado en estas mejoras.
- **updated_at**: Campo `actualizadoEn` del modelo Sesion, usado para ordenar el Tablero.

---

## Requisitos

### Requisito 1: Simplificación del Botón "OTRO"

**User Story:** Como Funcionario, quiero que el botón "OTRO" se comporte igual que los demás botones de estado pero permita mostrar un valor personalizado, para mantener flexibilidad sin complejidad adicional.

#### Criterios de Aceptación

1. THE Sistema SHALL eliminar el campo `descripcionOtro` del modelo `Sesion` y toda referencia a él en la interfaz y en la lógica de negocio.
2. THE Botón_OTRO SHALL comportarse igual que los demás botones de estado: al hacer clic, SHALL enviar directamente el POST de cambio de estado sin abrir formularios ni flujos adicionales.
3. THE Sistema SHALL permitir que el Label_OTRO sea dinámico y configurable por el Funcionario desde el Modal_Edicion.
4. WHEN el Funcionario guarda el Modal_Edicion con un valor en el Campo_Estado, THEN THE Sistema SHALL actualizar el Label_OTRO del paciente correspondiente con ese valor.
5. THE Sistema SHALL inicializar el Label_OTRO con el texto "Otro" por defecto para todos los pacientes.
6. THE Sistema SHALL no solicitar ningún campo adicional al Funcionario al hacer clic en el Botón_OTRO.

---

### Requisito 2: Edición de Pacientes desde el Panel de Gestión

**User Story:** Como Funcionario, quiero editar la identificación y el estado de un paciente programado, para corregir información antes de continuar con el flujo quirúrgico.

#### Criterios de Aceptación

1. THE Tabla_Programados SHALL mostrar un botón "Editar" en cada fila de paciente.
2. WHEN el Funcionario hace clic en "Editar", THEN THE Sistema SHALL mostrar el Modal_Edicion con los siguientes campos:
   - Identificación (editable, texto libre)
   - Nombre (solo lectura)
   - Estado (editable, texto libre)
3. THE Campo_Estado SHALL inicializarse con el Label_OTRO actualmente asignado al paciente si el estado activo es `OTRO`, o con el label del botón de estado actualmente seleccionado en cualquier otro caso.
4. WHEN el Funcionario presiona "Guardar", THEN THE Sistema SHALL validar que los campos Identificación y Estado no estén vacíos.
5. IF alguno de los campos requeridos está vacío, THEN THE Sistema SHALL mostrar un mensaje de error en el Modal_Edicion sin cerrarlo.
6. IF los datos son válidos, THEN THE Sistema SHALL actualizar la Identificación y el Label_OTRO del paciente únicamente en las tablas de la interfaz, sin persistir cambios en la base de datos.
7. THE Sistema SHALL actualizar la fila correspondiente del paciente en la Tabla_Programados con la nueva identificación.
8. THE Sistema SHALL actualizar la fila correspondiente del paciente en la Tabla_Pacientes_En_Sala con la nueva identificación, si el paciente tiene una sesión activa.
9. IF el valor del Campo_Estado fue modificado, THEN THE Sistema SHALL asignar ese valor como Label_OTRO del paciente y ejecutar la lógica equivalente a hacer clic en el Botón_OTRO para ese paciente.
10. THE Sistema SHALL no actualizar directamente el Tablero desde esta acción; el Tablero se actualizará mediante su ciclo de polling habitual.
11. THE Modal_Edicion SHALL cerrarse automáticamente después de que el Funcionario presione "Guardar" con datos válidos.
12. THE actualización de filas SHALL realizarse sin recarga completa de la página.

---

### Requisito 3: Actualización del Tablero de Estado Quirúrgico

**User Story:** Como familiar, quiero ver el estado actualizado de los pacientes en una pantalla, para conocer el progreso sin interrumpir al personal.

#### Criterios de Aceptación

1. THE Tablero SHALL mostrar todos los pacientes con sesión activa (`oculto=False`).
2. THE Sistema SHALL ordenar los pacientes en el Tablero por `actualizadoEn` en orden descendente (más reciente primero).
3. THE Tablero SHALL mostrar por cada paciente: Identificación, Estado y fecha/hora de última actualización (`actualizadoEn`).
4. THE Tablero SHALL renderizar cada paciente como una fila de tabla con las columnas: Identificación, Estado (con badge de color) y Hora de última actualización — coherente con el layout de la Tabla_Pacientes_En_Sala.
5. THE Tablero SHALL reemplazar el layout de tarjetas actual por un layout de tabla de filas para mantener coherencia visual con el Panel_Gestion.
5. WHEN el estado de un paciente cambia, THEN THE Tablero SHALL actualizarse automáticamente mediante polling HTMX sin requerir recarga manual de la página.
6. THE Tablero SHALL realizar polling al endpoint `/tablero/fragmento/` con un intervalo máximo de 30 segundos.

---

### Requisito 4: Estilo Visual de la Tabla de Pacientes en Sala

**User Story:** Como Funcionario, quiero que la tabla de pacientes en sala tenga el mismo estilo visual del tablero, para mantener coherencia visual en el sistema.

#### Criterios de Aceptación

1. THE Tabla_Pacientes_En_Sala SHALL ordenar los pacientes por `actualizadoEn` en orden descendente, igual que el Tablero.
2. THE Sistema SHALL aplicar a la Tabla_Pacientes_En_Sala el mismo esquema visual del Tablero: fondo oscuro (`bg-gray-900` o equivalente), texto claro, badges de estado con los mismos colores.
3. THE Estilo SHALL incluir: tema oscuro (dark), colores de estado consistentes con el Tablero, tipografía de tamaño legible, y jerarquía visual equivalente a las tarjetas del Tablero.
4. THE Tabla_Pacientes_En_Sala SHALL adaptarse al espacio disponible en el Panel_Gestion manteniendo legibilidad.
5. THE Sistema SHALL no modificar la funcionalidad de la Tabla_Pacientes_En_Sala, únicamente su presentación visual.
6. THE Tabla_Pacientes_En_Sala SHALL mostrar las columnas: Identificación, Estado y Hora de última actualización (`actualizadoEn`).

---

## Notas Técnicas

- Arquitectura SSR con Django Templates; sin SPA ni API REST obligatoria.
- Interacciones dinámicas mediante HTMX; comportamientos ligeros de UI con Alpine.js.
- El campo `descripcionOtro` del modelo `Sesion` debe eliminarse con su migración correspondiente.
- El Label_OTRO es estado de UI (frontend); no requiere persistencia en base de datos.
- El ordenamiento del Tablero cambia de `ingresadoEn` a `actualizadoEn` para reflejar la actividad más reciente.
- El campo `actualizadoEn` ya existe en el modelo `Sesion` (`auto_now=True`).
