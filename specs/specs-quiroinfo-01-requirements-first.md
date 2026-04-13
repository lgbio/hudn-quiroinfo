# Documento de Requisitos

## Introducción

Sistema de información en tiempo casi real para familiares de pacientes quirúrgicos. Funciona como un tablero tipo aeropuerto: muestra el estado del proceso quirúrgico de cada paciente de forma simple y comprensible para personas sin formación médica. Los pacientes se identifican mediante un código o alias para proteger su privacidad. El personal médico actualiza los estados con mínimos clics, sin formularios complejos. El sistema debe estar disponible en todo momento, tanto en pantallas de sala de espera como desde dispositivos móviles de los familiares.

## Glosario

- **Sistema**: La aplicación web de seguimiento de estado quirúrgico para familiares.
- **Tablero**: Pantalla principal de visualización pública, similar a un panel de vuelos de aeropuerto.
- **Paciente**: Persona sometida a un procedimiento quirúrgico, identificada en el sistema mediante un Código_Paciente.
- **Código_Paciente**: Identificador anónimo (código alfanumérico o alias) asignado al paciente para su visualización pública, sin revelar datos personales.
- **Estado_Quirúrgico**: Fase actual del proceso quirúrgico del paciente, expresada en términos comprensibles para no médicos.
- **Personal_Médico**: Enfermero, técnico o cualquier miembro del equipo autorizado para actualizar el Estado_Quirúrgico de un paciente.
- **Familiar**: Persona externa al hospital que consulta el Tablero para conocer el estado de un paciente.
- **Sesión_Activa**: Período de tiempo en que un paciente tiene un proceso quirúrgico en curso registrado en el sistema.

---

## Requisitos

### Requisito 1: Tablero de Estado Quirúrgico

**User Story:** Como familiar de un paciente, quiero ver en una pantalla el estado actual del proceso quirúrgico de mi familiar, para saber en qué fase se encuentra sin necesidad de interrumpir al personal médico.

#### Criterios de Aceptación

1. THE Tablero SHALL mostrar una lista de todos los pacientes con Sesión_Activa, identificados únicamente por su Código_Paciente.
2. THE Tablero SHALL mostrar para cada paciente su Estado_Quirúrgico actual y la hora de la última actualización.
3. WHEN el Estado_Quirúrgico de un paciente cambia, THE Tablero SHALL reflejar el nuevo estado en un tiempo máximo de 30 segundos sin requerir recarga manual de la página.
4. THE Tablero SHALL ser legible en pantallas de al menos 40 pulgadas a una distancia de 3 metros, con texto de tamaño mínimo 48px para el Código_Paciente y el Estado_Quirúrgico.
5. THE Tablero SHALL ser accesible desde navegadores web en dispositivos móviles sin requerir instalación de aplicación.
6. IF la conexión con el servidor se interrumpe, THEN THE Tablero SHALL mostrar un indicador visible de "Sin conexión" y el último estado conocido de cada paciente.

---

### Requisito 2: Estados Quirúrgicos Comprensibles

**User Story:** Como familiar de un paciente, quiero que los estados del proceso quirúrgico estén expresados en lenguaje simple, para entender la situación sin conocimientos médicos.

#### Criterios de Aceptación

1. THE Sistema SHALL manejar exactamente los siguientes Estados_Quirúrgicos: "En preparación", "En cirugía", "En recuperación", "Listo para visita", "Proceso finalizado".
2. THE Tablero SHALL mostrar cada Estado_Quirúrgico acompañado de un color distintivo: "En preparación" en amarillo, "En cirugía" en naranja, "En recuperación" en azul, "Listo para visita" en verde, "Proceso finalizado" en gris.
3. THE Sistema SHALL permitir que el Personal_Médico transite el Estado_Quirúrgico únicamente en la secuencia: "En preparación" → "En cirugía" → "En recuperación" → "Listo para visita" → "Proceso finalizado".
4. IF el Personal_Médico intenta asignar un Estado_Quirúrgico fuera de la secuencia permitida, THEN THE Sistema SHALL rechazar el cambio y mostrar los estados válidos disponibles.
5. WHERE el hospital lo requiera, THE Sistema SHALL permitir al administrador agregar un mensaje de texto libre opcional visible junto al Estado_Quirúrgico de un paciente específico, con un máximo de 80 caracteres.

---

### Requisito 3: Registro de Pacientes en Proceso Quirúrgico

**User Story:** Como Personal_Médico, quiero registrar a un paciente en el sistema al inicio de su proceso quirúrgico, para que sus familiares puedan seguir su estado desde el Tablero.

#### Criterios de Aceptación

1. WHEN el Personal_Médico registra un nuevo paciente, THE Sistema SHALL requerir únicamente el Código_Paciente y establecer el Estado_Quirúrgico inicial en "En preparación".
2. THE Sistema SHALL garantizar que cada Código_Paciente sea único entre todas las Sesiones_Activas simultáneas.
3. IF el Personal_Médico intenta registrar un Código_Paciente que ya existe en una Sesión_Activa, THEN THE Sistema SHALL rechazar el registro y mostrar un mensaje de código duplicado.
4. THE Sistema SHALL completar el registro de un nuevo paciente en un máximo de 3 campos de entrada y 1 acción de confirmación.
5. WHEN un paciente es registrado exitosamente, THE Sistema SHALL mostrar el Código_Paciente en el Tablero en un tiempo máximo de 30 segundos.

---

### Requisito 4: Actualización de Estado por Personal Médico

**User Story:** Como Personal_Médico, quiero actualizar el estado de un paciente con el mínimo de pasos posible, para no interrumpir mi flujo de trabajo clínico.

#### Criterios de Aceptación

1. THE Sistema SHALL permitir al Personal_Médico actualizar el Estado_Quirúrgico de un paciente en un máximo de 3 interacciones desde la pantalla de gestión.
2. WHEN el Personal_Médico selecciona un paciente y confirma el cambio de estado, THE Sistema SHALL registrar el nuevo Estado_Quirúrgico junto con la marca de tiempo del cambio.
3. THE Sistema SHALL mostrar al Personal_Médico únicamente el siguiente estado válido disponible para cada paciente, sin exponer toda la lista de estados.
4. WHEN el Estado_Quirúrgico se actualiza a "Proceso finalizado", THE Sistema SHALL mantener al paciente visible en el Tablero durante 60 minutos adicionales y luego ocultarlo automáticamente.
5. IF la actualización de estado falla por error del servidor, THEN THE Sistema SHALL notificar al Personal_Médico con un mensaje de error y conservar el estado anterior sin modificación.

---

### Requisito 5: Privacidad de los Pacientes

**User Story:** Como administrador del hospital, quiero que el sistema no exponga datos personales de los pacientes en el Tablero público, para cumplir con las obligaciones de privacidad y protección de datos.

#### Criterios de Aceptación

1. THE Tablero SHALL mostrar exclusivamente el Código_Paciente como identificador, sin nombre, apellido, edad, diagnóstico ni ningún otro dato personal.
2. THE Sistema SHALL almacenar cualquier dato personal del paciente separado del Código_Paciente, sin vincularlos en ninguna respuesta enviada al Tablero público.
3. WHEN un Familiar accede al Tablero, THE Sistema SHALL servir la información sin requerir autenticación ni registro.
4. THE Sistema SHALL transmitir todos los datos entre cliente y servidor mediante HTTPS.
5. IF el Personal_Médico necesita asociar un Código_Paciente a un paciente real, THEN THE Sistema SHALL proveer una vista interna autenticada que muestre esa asociación, accesible únicamente para Personal_Médico autenticado.

---

### Requisito 6: Autenticación del Personal Médico

**User Story:** Como administrador del hospital, quiero que solo el Personal_Médico autorizado pueda modificar estados en el sistema, para evitar actualizaciones no autorizadas.

#### Criterios de Aceptación

1. THE Sistema SHALL requerir autenticación mediante usuario y contraseña para acceder a la pantalla de gestión del Personal_Médico.
2. WHEN un usuario introduce credenciales incorrectas 5 veces consecutivas, THE Sistema SHALL bloquear el acceso a esa cuenta durante 15 minutos.
3. WHILE una sesión de Personal_Médico permanece inactiva por más de 60 minutos, THE Sistema SHALL cerrar la sesión automáticamente y requerir nueva autenticación.
4. THE Sistema SHALL permitir al administrador crear, desactivar y restablecer contraseñas de cuentas de Personal_Médico.
5. IF un usuario no autenticado intenta acceder a la pantalla de gestión, THEN THE Sistema SHALL redirigirlo a la pantalla de inicio de sesión.

---

### Requisito 7: Disponibilidad y Confiabilidad

**User Story:** Como administrador del hospital, quiero que el sistema esté disponible en todo momento durante el horario quirúrgico, para que los familiares siempre puedan consultar el estado de sus pacientes.

#### Criterios de Aceptación

1. THE Sistema SHALL estar disponible el 99.5% del tiempo durante el horario quirúrgico definido por el hospital.
2. WHEN el servidor de base de datos no responde, THE Sistema SHALL mostrar el último estado conocido en el Tablero e indicar la hora de la última actualización exitosa.
3. THE Sistema SHALL soportar al menos 200 conexiones simultáneas al Tablero sin degradación del tiempo de respuesta por encima de 2 segundos.
4. WHEN se realiza una actualización de Estado_Quirúrgico, THE Sistema SHALL confirmar la persistencia del cambio antes de mostrarlo en el Tablero.
5. THE Sistema SHALL registrar en un log interno cada cambio de Estado_Quirúrgico con marca de tiempo, Código_Paciente y usuario que realizó el cambio, conservando el historial durante al menos 90 días.

---

### Requisito 8: Notificación por Código de Paciente

**User Story:** Como familiar de un paciente, quiero poder consultar el estado de mi familiar directamente desde mi celular ingresando su código, para no depender de estar frente a la pantalla de la sala de espera.

#### Criterios de Aceptación

1. THE Sistema SHALL proveer una URL pública donde el Familiar pueda ingresar un Código_Paciente y ver su Estado_Quirúrgico actual.
2. WHEN el Familiar ingresa un Código_Paciente válido con Sesión_Activa, THE Sistema SHALL mostrar el Estado_Quirúrgico actual y la hora de la última actualización.
3. IF el Familiar ingresa un Código_Paciente que no corresponde a ninguna Sesión_Activa, THEN THE Sistema SHALL mostrar un mensaje indicando que el código no se encuentra activo, sin revelar si el código existió previamente.
4. THE Sistema SHALL actualizar automáticamente el estado en la vista del Familiar cada 30 segundos sin requerir recarga manual.
5. THE Sistema SHALL mostrar la vista de consulta por código de forma funcional en pantallas de dispositivos móviles con ancho mínimo de 320px.

