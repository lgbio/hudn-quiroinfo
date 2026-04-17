# Documento de Requisitos

## Introducción

Mejoras al MVP existente de Quiroinfo, un sistema de seguimiento de estado quirúrgico para familiares. Las mejoras abordan las siguientes áreas: simplificación del botón "OTRO" con label persistido en BD, edición de datos de pacientes desde el panel de gestión, actualización del tablero público como pantalla TV responsiva, homogeneización visual de la tabla de pacientes en sala, orden consistente entre tablas, eliminación del modelo RegistroEstado, carga manual de pacientes programados, limpieza de integridad referencial, y registro de teléfono para notificaciones al familiar del paciente.

La arquitectura permanece igual: Django SSR con HTMX para interacciones dinámicas, Alpine.js para comportamientos ligeros de UI, y Tailwind CSS por CDN.

## Glosario

- **Sistema**: La aplicación web Quiroinfo de seguimiento de estado quirúrgico.
- **Tablero**: Pantalla pública proyectada en sala de espera. Solo lectura, sin autenticación. Optimizada para TV.
- **Funcionario**: Usuario autenticado con acceso al Panel_Gestion.
- **Panel_Gestion**: Vista privada del Funcionario con las dos tablas paralelas de operación.
- **Tabla_Programados**: Tabla izquierda del Panel_Gestion con la lista de pacientes y sus botones de estado.
- **Tabla_Pacientes_En_Sala**: Tabla derecha del Panel_Gestion con los pacientes actualmente visibles en el Tablero.
- **Botón_OTRO**: Botón de estado en la Tabla_Programados que representa el estado `OTRO` con un label configurable.
- **Modal_Edicion**: Modal que aparece al hacer clic en "Editar" en una fila de la Tabla_Programados.
- **Campo_Estado**: Campo de texto editable dentro del Modal_Edicion que representa el label personalizado del estado OTRO.
- **Label_OTRO**: Texto visible en el Botón_OTRO, inicialmente "Otro", persistido en la BD en el campo `labelOtro` de `Sesion`.
- **Teléfono_Notificacion**: Número de teléfono móvil colombiano (10 dígitos, sin prefijo de país) asociado a un `Paciente`, usado para futuras comunicaciones con el familiar.
- **Sesion**: Registro activo de un paciente en el tablero con su estado actual.
- **actualizadoEn**: Campo `actualizadoEn` del modelo Sesion (`auto_now=True`), usado para ordenar ambas tablas y el Tablero.

---

## Requisitos

### Requisito 1: Simplificación del Botón "OTRO"

**User Story:** Como Funcionario, quiero que el botón "OTRO" se comporte igual que los demás botones de estado pero permita mostrar un valor personalizado, para mantener flexibilidad sin complejidad adicional.

#### Criterios de Aceptación

1. THE Sistema SHALL eliminar el campo `descripcionOtro` del modelo `Sesion` y toda referencia a él en la interfaz y en la lógica de negocio.
2. THE Botón_OTRO SHALL comportarse igual que los demás botones de estado: al hacer clic, SHALL enviar directamente el POST de cambio de estado sin abrir formularios ni flujos adicionales.
3. THE Sistema SHALL permitir que el Label_OTRO sea dinámico y configurable por el Funcionario desde el Modal_Edicion.
4. WHEN el Funcionario guarda el Modal_Edicion con un valor modificado en el Campo_Estado, THEN THE Sistema SHALL persistir el Label_OTRO en la base de datos en el campo `labelOtro` de `Sesion`.
5. THE Sistema SHALL inicializar el Label_OTRO con el texto "Otro" por defecto para todos los pacientes.
6. THE Sistema SHALL no solicitar ningún campo adicional al Funcionario al hacer clic en el Botón_OTRO.
7. THE Label_OTRO SHALL ser leído desde la base de datos en cada render, garantizando consistencia entre Tabla_Programados, Tabla_Pacientes_En_Sala y Tablero.

---

### Requisito 2: Edición de Pacientes desde el Panel de Gestión

**User Story:** Como Funcionario, quiero editar la identificación y el estado de un paciente programado, para corregir información antes de continuar con el flujo quirúrgico.

#### Criterios de Aceptación

1. THE Tabla_Programados SHALL mostrar un botón "Editar" en cada fila de paciente.
2. WHEN el Funcionario hace clic en "Editar", THEN THE Sistema SHALL mostrar el Modal_Edicion con los siguientes campos:
   - Identificación (editable, texto libre)
   - Nombre (solo lectura)
   - Estado (editable, texto libre, pre-cargado con el label actual)
3. THE Campo_Estado SHALL inicializarse con el Label_OTRO actualmente asignado al paciente si el estado activo es `OTRO`, o con el valor del estado activo en cualquier otro caso.
4. WHEN el Funcionario presiona "Guardar", THE Sistema SHALL validar que el campo Identificación no esté vacío.
5. IF la Identificación está vacía, THEN THE Sistema SHALL mostrar un mensaje de error en el Modal_Edicion sin cerrarlo.
6. IF los datos son válidos, THEN THE Sistema SHALL persistir la nueva Identificación en la base de datos (`Paciente.identificacion`).
7. IF el Campo_Estado fue modificado respecto al valor original, THEN THE Sistema SHALL persistir el nuevo Label_OTRO en `Sesion.labelOtro` y aplicar el estado `OTRO` al paciente.
8. IF el Campo_Estado NO fue modificado, THEN THE Sistema SHALL no alterar el estado ni el Label_OTRO del paciente.
9. THE Modal_Edicion SHALL cerrarse automáticamente después de que el Funcionario presione "Guardar" con datos válidos.
10. THE actualización SHALL realizarse sin recarga completa de la página, mediante HTMX.

---

### Requisito 3: Actualización del Tablero de Estado Quirúrgico

**User Story:** Como familiar, quiero ver el estado actualizado de los pacientes en una pantalla TV, para conocer el progreso sin interrumpir al personal.

#### Criterios de Aceptación

1. THE Tablero SHALL mostrar todos los pacientes con sesión activa (`oculto=False`).
2. THE Sistema SHALL ordenar los pacientes en el Tablero por `actualizadoEn` en orden descendente (más reciente primero).
3. THE Tablero SHALL mostrar por cada paciente: Identificación, Estado (con Label_OTRO si aplica) y hora de última actualización.
4. THE Tablero SHALL usar un layout de filas flex que ocupe el 100% del viewport sin scroll.
5. THE Tablero SHALL distribuir las filas de pacientes equitativamente en la altura disponible (1 paciente = 100%, 9 pacientes = ~11% cada uno).
6. THE Tablero SHALL escalar el tamaño de fuente proporcionalmente a la altura de cada fila usando unidades `vh` con `clamp()`.
7. WHEN el estado de un paciente cambia, THEN THE Tablero SHALL actualizarse automáticamente mediante polling HTMX cada 15 segundos.
8. THE Tablero SHALL mostrar la hora en formato de 12 horas (ej. "08:50 am"), sin fecha.
9. THE Tablero SHALL ser legible en pantallas de al menos 40 pulgadas a una distancia de 3 metros.

---

### Requisito 4: Estilo Visual de la Tabla de Pacientes en Sala

**User Story:** Como Funcionario, quiero que la tabla de pacientes en sala tenga el mismo estilo visual del tablero, para mantener coherencia visual en el sistema.

#### Criterios de Aceptación

1. THE Tabla_Pacientes_En_Sala SHALL ordenar los pacientes por `actualizadoEn` en orden descendente, igual que el Tablero.
2. THE Sistema SHALL aplicar a la Tabla_Pacientes_En_Sala el mismo esquema visual del Tablero: fondo oscuro (`bg-gray-900`), texto claro, badges de estado con los mismos colores.
3. THE Tabla_Pacientes_En_Sala SHALL mostrar las columnas: Identificación, Estado y Hora de última actualización (`actualizadoEn`).
4. THE Estado SHALL mostrar el Label_OTRO cuando el estado sea `OTRO`.
5. THE Sistema SHALL no modificar la funcionalidad de la Tabla_Pacientes_En_Sala, únicamente su presentación visual.

---

### Requisito 5: Orden Consistente entre Tablas

**User Story:** Como Funcionario, quiero que la Tabla_Programados tenga el mismo orden que la Tabla_Pacientes_En_Sala, para mantener consistencia visual y operativa.

#### Criterios de Aceptación

1. THE Tabla_Programados SHALL usar el mismo criterio de ordenamiento que Tabla_Pacientes_En_Sala: `actualizadoEn` descendente.
2. THE Sistema SHALL aplicar el ordenamiento en backend (queryset) para ambas tablas.
3. Los pacientes sin sesión activa SHALL aparecer al final de la Tabla_Programados, ordenados por `identificacion`.
4. THE orden SHALL ser determinístico y consistente en cada render.

---

### Requisito 6: Eliminación de RegistroEstado

**User Story:** Como desarrollador, quiero eliminar el modelo RegistroEstado para simplificar el sistema en el MVP.

#### Criterios de Aceptación

1. THE Sistema SHALL eliminar el modelo `RegistroEstado` del código y su tabla de la base de datos mediante migración.
2. THE Sistema SHALL remover toda lógica que dependa de `RegistroEstado`.
3. THE Sistema SHALL mantener el estado actual de `Sesion` como única fuente de verdad.

---

### Requisito 7: Carga Manual de Pacientes Programados

**User Story:** Como Funcionario, quiero cargar manualmente los pacientes programados mediante un botón, para actualizar la información cuando sea necesario.

#### Criterios de Aceptación

1. THE Panel_Gestion SHALL mostrar un botón "Cargar pacientes programados" debajo de la Tabla_Programados.
2. WHEN el Funcionario presiona el botón, THE Sistema SHALL mostrar un mensaje de confirmación: "Va a limpiar la tabla, ¿Está seguro?".
3. IF el Funcionario confirma, THE Sistema SHALL ejecutar `Utils.cargarPacientesProgramadosCirugia()` via POST a `/gestion/programados/cargar/`.
4. THE función SHALL eliminar todos los registros de `Paciente` (y sus `Sesion` asociadas por CASCADE) y cargar los nuevos registros.
5. THE Sistema SHALL mostrar feedback visual de carga (spinner) mientras se ejecuta la operación.
6. THE Sistema SHALL prevenir ejecuciones concurrentes de la carga.
7. AFTER la ejecución, THE Sistema SHALL refrescar la Tabla_Programados usando HTMX (partial update).
8. THE endpoint SHALL estar protegido (login requerido).

---

### Requisito 8: Integridad Referencial al Eliminar Pacientes

**User Story:** Como Sistema, quiero que al eliminar un Paciente también se eliminen automáticamente sus Sesiones asociadas, para permitir la limpieza completa del tablero sin errores de integridad.

#### Criterios de Aceptación

1. THE relación `Sesion.paciente` SHALL usar `on_delete=CASCADE`.
2. WHEN un `Paciente` es eliminado, THE Sistema SHALL eliminar automáticamente todas sus `Sesion` asociadas.
3. THE `Utils.cargarPacientesProgramadosCirugia()` SHALL usar el ORM de Django para la limpieza, garantizando que el CASCADE se aplique correctamente.

---

## Notas Técnicas

- Arquitectura SSR con Django Templates; sin SPA ni API REST obligatoria.
- Interacciones dinámicas mediante HTMX; comportamientos ligeros de UI con Alpine.js.
- El campo `labelOtro` del modelo `Sesion` persiste el label del botón OTRO en la BD (CharField, default='Otro').
- El ordenamiento de ambas tablas y el Tablero usa `-actualizadoEn`.
- El Tablero usa layout flex con `height: 100vh` y filas con `flex: 1` para distribución dinámica.
- Fuentes del Tablero escalan con `clamp(min, Xvh, max)` para adaptarse a cualquier tamaño de pantalla.

---

### Requisito 9: Registro de Teléfono para Notificar a Familiar de Paciente

**User Story:** Como Funcionario, quiero registrar un teléfono para notificar asociado al paciente, para poder usarlo en futuras comunicaciones.

#### Criterios de Aceptación

1. THE Modal_Edicion SHALL agregar un campo "Teléfono para notificaciones" al formulario de edición del paciente.
2. THE Campo SHALL ser opcional — el Funcionario puede guardar sin completarlo.
3. THE Campo SHALL mostrar el texto de ayuda: "Ingrese un número de teléfono para notificar al familiar del paciente".
4. THE Campo SHALL aceptar únicamente números de teléfono móviles colombianos en formato local, sin prefijo de país:
   - Solo dígitos
   - Longitud exacta de 10 caracteres
   - Ejemplo válido: `3176753151`
5. IF el valor contiene caracteres no numéricos, THEN THE Sistema SHALL rechazar el valor y mostrar un mensaje de error en el modal sin cerrarlo.
6. IF el valor no tiene exactamente 10 dígitos, THEN THE Sistema SHALL rechazar el valor y mostrar un mensaje de error en el modal sin cerrarlo.
7. IF el valor es válido o está vacío, THEN THE Sistema SHALL permitir guardar el paciente.
8. THE Sistema SHALL persistir el Teléfono_Notificacion en la base de datos en el modelo `Paciente`.
9. THE Sistema SHALL permitir editar o eliminar el número en cualquier momento desde el Modal_Edicion.

---

### Requisito 10: Notificación por SMS ante Cambio de Estado Quirúrgico

**User Story:** Como Funcionario, quiero que el sistema envíe automáticamente una notificación por SMS al teléfono registrado del paciente cuando su estado quirúrgico cambie, para mantener informados a sus familiares sin intervención manual.

#### Criterios de Aceptación

1. WHEN el estado quirúrgico de un Paciente es actualizado, THE Sistema SHALL verificar si el campo `telefono` del Paciente tiene un valor.
2. IF el campo `telefono` está vacío o es nulo, THEN THE Sistema SHALL no realizar ninguna acción de envío de SMS y SHALL continuar el flujo sin errores.
3. IF el campo `telefono` tiene un valor válido, THEN THE Sistema SHALL enviar un SMS usando el servicio externo Twilio.
4. THE contenido del mensaje SHALL incluir al menos: nombre del paciente y estado quirúrgico actualizado.
5. THE número telefónico SHALL ser transformado a formato internacional (`+57`) antes del envío.
6. THE Sistema SHALL NO bloquear la operación principal de actualización de estado en caso de fallo en el envío del SMS.
7. IF ocurre un error durante el envío del SMS, THEN THE Sistema SHALL registrar el error en logs internos sin interrumpir la operación del usuario.
8. THE Sistema SHALL NO requerir confirmación visual al usuario tras el envío (MVP).
9. THE Sistema SHALL NO almacenar historial de mensajes enviados (MVP).
