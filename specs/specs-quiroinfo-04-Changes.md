## Requisito 1: Botón "OTRO"

**User Story:** Como Funcionario, quiero que el botón "OTRO" se comporte igual que los demás estados pero permita mostrar un valor personalizado, para mantener flexibilidad sin complejidad adicional.

### Criterios de Aceptación

1. THE Sistema SHALL eliminar completamente el uso de descripción asociada al botón "OTRO" tanto en modelos como en la interfaz.
2. THE Botón_OTRO SHALL comportarse igual que los demás botones de estado sin abrir formularios ni flujos adicionales.
3. THE Sistema SHALL permitir que el label del botón "OTRO" sea dinámico.
4. WHEN el valor del campo `estado` es modificado desde el modal, THEN THE Sistema SHALL actualizar el label del botón "OTRO" con ese valor.
5. THE Sistema SHALL no solicitar ningún campo adicional al usuario al hacer clic en el botón "OTRO".

---

## Requisito 2: Edición de Pacientes

**User Story:** Como Funcionario, quiero editar la identificación y el estado de un paciente programado, para corregir información antes de continuar con el flujo quirúrgico.

### Criterios de Aceptación

1. THE Tabla_Programados SHALL mostrar un botón "Editar" en cada fila.
2. WHEN el Funcionario hace clic en "Editar", THEN THE Sistema SHALL mostrar un modal con los campos:
   - Identificación (editable)
   - Nombre (solo lectura)
   - Estado (editable)
3. THE Campo_Estado SHALL inicializarse con el label del botón de estado actualmente seleccionado.
4. WHEN el Funcionario presiona "Guardar", THEN THE Sistema SHALL validar que los campos no estén vacíos.
5. IF los datos son válidos, THEN THE Sistema SHALL actualizar los datos del paciente únicamente en las tablas de la interfaz (sin persistir cambios en base de datos).
6. THE Sistema SHALL actualizar la fila correspondiente en:
   - Tabla_Programados
   - Tabla_Pacientes_En_Sala
7. IF el valor de `estado` fue modificado, THEN THE Sistema SHALL:
   - asignar ese valor como label del botón "OTRO"
   - ejecutar la lógica equivalente a hacer clic en el botón "OTRO"
8. THE Sistema SHALL no actualizar directamente el Tablero desde esta acción.
9. THE Modal SHALL cerrarse automáticamente después de guardar.
10. THE Actualización de filas SHALL realizarse sin recarga completa de página.

---

## Requisito 3: Tablero de Estado Quirúrgico

**User Story:** Como familiar, quiero ver el estado actualizado de los pacientes en una pantalla, para conocer el progreso sin interrumpir al personal.

### Criterios de Aceptación

1. THE Tablero SHALL mostrar una lista de pacientes activos.
2. THE Sistema SHALL ordenar los pacientes por `updated_at` en orden descendente (más reciente primero).
3. THE Tablero SHALL mostrar por cada paciente:
   - Identificación
   - Estado
   - Fecha y hora de última actualización
4. THE Tablero SHALL renderizar cada paciente como una fila en formato:
   `ID | Estado | Fecha`
5. WHEN el estado de un paciente cambia, THEN THE Tablero SHALL actualizarse automáticamente mediante polling.
6. THE Tablero SHALL no requerir recarga manual para reflejar cambios.

---

## Requisito 4: Estilo de Pacientes en Sala

**User Story:** Como Funcionario, quiero que la tabla de pacientes en sala tenga el mismo estilo visual del tablero, para mantener coherencia visual en el sistema.

### Criterios de Aceptación

1. THE Tabla_Pacientes_En_Sala SHALL usar el mismo orden que el Tablero (más reciente primero).
2. THE Sistema SHALL aplicar el mismo estilo visual del Tablero a la tabla de Pacientes en Sala.
3. THE Estilo SHALL incluir:
   - Tema oscuro (dark)
   - Colores consistentes
   - Tipografía consistente
   - Jerarquía visual equivalente
4. THE Tabla SHALL adaptarse al espacio disponible manteniendo legibilidad.
5. THE Sistema SHALL no modificar la funcionalidad de la tabla, solo su presentación.

---

## Notas Técnicas

- Arquitectura SSR con Django Templates
- Interacciones mediante HTMX
- Sin uso de SPA
- Sin API REST obligatoria

---

## Estado del MVP

- Estados quirúrgicos definidos
- Polling definido
- Sin pendientes críticos
