# Documento de Requisitos

## Introducción

Sistema de información en tiempo casi real para familiares de pacientes quirúrgicos. Funciona como un tablero tipo aeropuerto: muestra el estado del proceso quirúrgico de cada paciente de forma simple y comprensible para personas sin formación médica. Los pacientes se identifican mediante un código o alias para proteger su privacidad. El sistema está diseñado para proyectarse en pantallas de TV o monitor en la sala de espera; los familiares no interactúan con el sistema, sino que reciben notificaciones automáticas vía SMS y WhatsApp cuando el estado de su familiar cambia. El personal que opera el sistema es mínimo: un Administrador y uno o más Funcionarios que gestionan el estado de los pacientes con la menor cantidad de pasos posible.

## Glosario

- **Sistema**: La aplicación web de seguimiento de estado quirúrgico para familiares.
- **Tablero**: Pantalla principal de visualización pública, proyectada en TV o monitor en sala de espera. No es interactiva; solo muestra información.
- **Paciente**: Persona sometida a un procedimiento quirúrgico, identificada en el sistema mediante un Código_Paciente.
- **Código_Paciente**: Identificador visible en el Tablero (código alfanumérico, alias o apodo acordado con la familia) asignado al paciente para su visualización pública, sin revelar datos personales sensibles.
- **Estado_Quirúrgico**: Fase actual del proceso quirúrgico del paciente, expresada en términos comprensibles para no médicos.
- **Paciente_Activo**: Paciente registrado en el sistema por el Funcionario que tiene un proceso quirúrgico en curso y aparece en el Tablero.
- **Funcionario**: Usuario del sistema con rol operativo diario; gestiona el estado de los pacientes y realiza las modificaciones permitidas.
- **Administrador**: Usuario único con acceso completo a todas las opciones del sistema, incluyendo gestión de cuentas.
- **Familiar**: Persona externa al hospital que observa el Tablero proyectado en sala de espera o recibe notificaciones vía SMS o WhatsApp.
- **Sesión_Activa**: Período de tiempo en que un Paciente_Activo tiene un proceso quirúrgico en curso registrado en el sistema.
- **Interfaz_Pública**: El Tablero proyectado en sala de espera; accesible sin autenticación, solo lectura.
- **Interfaz_Privada**: El Panel de Gestión utilizado por el Funcionario o Administrador; requiere autenticación.
- **Panel_Gestión**: Vista principal de la Interfaz_Privada que contiene las herramientas de administración y operación del sistema.

---

## Requisitos

### Requisito 1: Tablero de Estado Quirúrgico (Interfaz Pública)

**User Story:** Como familiar de un paciente, quiero ver en una pantalla proyectada en la sala de espera el estado actual del proceso quirúrgico de mi familiar, para saber en qué fase se encuentra sin necesidad de interrumpir al personal médico.

#### Criterios de Aceptación

1. THE Tablero SHALL ser accesible desde una URL pública sin requerir autenticación ni interacción de ningún usuario.
2. THE Tablero SHALL mostrar una lista de todos los Pacientes_Activos con Sesión_Activa, identificados únicamente por su Código_Paciente.
3. THE Tablero SHALL mostrar para cada Paciente_Activo su Estado_Quirúrgico actual y la hora de la última actualización.
4. WHEN el Estado_Quirúrgico de un paciente cambia, THE Tablero SHALL reflejar el nuevo estado en un tiempo máximo de 30 segundos sin requerir recarga manual de la página.
5. THE Tablero SHALL ser legible en pantallas de al menos 40 pulgadas a una distancia de 3 metros, con texto de tamaño mínimo 48px para el Código_Paciente y el Estado_Quirúrgico.
6. THE Tablero SHALL funcionar como pantalla de solo lectura proyectada en TV o monitor, sin requerir interacción del Familiar ni de ningún usuario externo.
7. IF la conexión con el servidor se interrumpe, THEN THE Tablero SHALL mostrar un indicador visible de "Sin conexión" y el último estado conocido de cada Paciente_Activo.

---

### Requisito 2: Estados Quirúrgicos Comprensibles

**User Story:** Como familiar de un paciente, quiero que los estados del proceso quirúrgico estén expresados en lenguaje simple, para entender la situación sin conocimientos médicos.

#### Criterios de Aceptación

1. THE Sistema SHALL manejar exactamente los siguientes Estados_Quirúrgicos: "En preparación", "En cirugía", "En recuperación", "Listo para visita", "Proceso finalizado".
2. THE Tablero SHALL mostrar cada Estado_Quirúrgico acompañado de un color distintivo: "En preparación" en amarillo, "En cirugía" en naranja, "En recuperación" en azul, "Listo para visita" en verde, "Proceso finalizado" en gris.
3. THE Sistema SHALL permitir que el Funcionario transite el Estado_Quirúrgico únicamente en la secuencia: "En preparación" → "En cirugía" → "En recuperación" → "Listo para visita" → "Proceso finalizado".
4. IF el Funcionario intenta asignar un Estado_Quirúrgico fuera de la secuencia permitida, THEN THE Sistema SHALL rechazar el cambio y mostrar el estado válido disponible.
5. WHERE el hospital lo requiera, THE Sistema SHALL permitir al Funcionario agregar un mensaje de texto libre opcional visible junto al Estado_Quirúrgico de un Paciente_Activo específico, con un máximo de 80 caracteres.

---

### Requisito 3: Registro y Activación de Pacientes

**User Story:** Como Funcionario, quiero registrar un paciente ingresando su nombre y asignarle un código visible en el Tablero, para activarlo en el seguimiento quirúrgico de forma rápida y sin depender de sistemas externos.

#### Criterios de Aceptación

1. THE Sistema SHALL permitir al Funcionario crear un paciente ingresando únicamente su nombre completo y un Código_Paciente.
2. WHEN el Funcionario crea y activa un paciente, THE Sistema SHALL establecer su Estado_Quirúrgico inicial en "En preparación" y mostrarlo en el Tablero en un tiempo máximo de 30 segundos.
3. WHEN el Funcionario activa un paciente, THE Sistema SHALL ofrecer la opción de registrar el número de teléfono del Familiar para el envío de notificaciones vía SMS y WhatsApp.
4. THE Sistema SHALL garantizar que cada Código_Paciente sea único entre todas las Sesiones_Activas simultáneas.
5. IF el Funcionario intenta activar un paciente que ya tiene una Sesión_Activa, THEN THE Sistema SHALL rechazar la activación y mostrar un mensaje indicando que el paciente ya se encuentra activo.

---

### Requisito 4: Actualización de Estado por el Funcionario

**User Story:** Como Funcionario, quiero actualizar el estado de un paciente con el mínimo de pasos posible y poder retirarlo del tablero si ocurre algún problema, para no interrumpir mi flujo de trabajo y mantener la información del Tablero precisa.

#### Criterios de Aceptación

1. THE Sistema SHALL permitir al Funcionario actualizar el Estado_Quirúrgico de un Paciente_Activo en un máximo de 3 interacciones desde la pantalla de gestión.
2. WHEN el Funcionario selecciona un Paciente_Activo y confirma el cambio de estado, THE Sistema SHALL registrar el nuevo Estado_Quirúrgico junto con la marca de tiempo del cambio.
3. THE Sistema SHALL mostrar al Funcionario únicamente el siguiente estado válido disponible para cada Paciente_Activo, sin exponer toda la lista de estados.
4. WHEN el Estado_Quirúrgico se actualiza a "Proceso finalizado", THE Sistema SHALL mantener al Paciente_Activo visible en el Tablero durante 60 minutos adicionales y luego ocultarlo automáticamente.
5. IF la actualización de estado falla por error del servidor, THEN THE Sistema SHALL notificar al Funcionario con un mensaje de error y conservar el estado anterior sin modificación.
6. THE Sistema SHALL ofrecer al Funcionario la opción de eliminar a un Paciente_Activo de la lista en pantalla mediante una única acción de confirmación, para los casos en que haya un problema con el proceso del paciente y el Familiar deba consultar directamente al personal.

---

### Requisito 5: Privacidad de los Pacientes

**User Story:** Como Administrador del hospital, quiero que el sistema no exponga datos personales de los pacientes en el Tablero público y que el Código_Paciente sea reconocible por los familiares, para cumplir con las obligaciones de privacidad y facilitar la identificación.

#### Criterios de Aceptación

1. THE Tablero SHALL mostrar exclusivamente el Código_Paciente como identificador, sin nombre, apellido, edad, diagnóstico ni ningún otro dato personal sensible.
2. THE Sistema SHALL almacenar cualquier dato personal del paciente separado del Código_Paciente, sin vincularlos en ninguna respuesta enviada al Tablero.
3. THE Sistema SHALL permitir al Funcionario modificar el Código_Paciente de un Paciente_Activo en cualquier momento, para asignar un alias o apodo acordado previamente con la familia que resulte más reconocible en el Tablero.
4. THE Sistema SHALL transmitir todos los datos entre cliente y servidor mediante HTTPS.

---

### Requisito 6: Autenticación de Usuarios

**User Story:** Como Administrador del hospital, quiero que solo los usuarios autorizados puedan modificar estados en el sistema, para evitar actualizaciones no autorizadas.

#### Criterios de Aceptación

1. THE Sistema SHALL requerir autenticación mediante usuario y contraseña para acceder a la pantalla de gestión.
2. WHILE una sesión permanece inactiva por más de 120 minutos, THE Sistema SHALL cerrar la sesión automáticamente y requerir nueva autenticación.
3. THE Sistema SHALL permitir únicamente al Administrador crear y desactivar cuentas de Funcionario.
4. IF un usuario no autenticado intenta acceder a la pantalla de gestión, THEN THE Sistema SHALL redirigirlo a la pantalla de inicio de sesión.

---

### Requisito 7: Notificaciones a Familiares vía SMS y WhatsApp

**User Story:** Como familiar de un paciente, quiero recibir una notificación en mi teléfono cuando el estado de mi familiar cambie, para estar informado sin necesidad de permanecer frente a la pantalla de la sala de espera.

#### Criterios de Aceptación

1. WHEN el Estado_Quirúrgico de un Paciente_Activo cambia, THE Sistema SHALL enviar automáticamente una notificación al número de teléfono del Familiar registrado, tanto por SMS como por WhatsApp, indicando el nuevo Estado_Quirúrgico y el Código_Paciente.
2. IF no se ha registrado un número de teléfono para el Familiar de un Paciente_Activo, THEN THE Sistema SHALL omitir el envío de notificaciones para ese paciente sin generar un error en el flujo de trabajo del Funcionario.
3. IF el envío de una notificación falla, THEN THE Sistema SHALL registrar el fallo en el log interno con la marca de tiempo y el Código_Paciente, sin interrumpir la actualización del Estado_Quirúrgico en el Tablero.
4. THE Sistema SHALL transmitir en la notificación únicamente el Código_Paciente y el nuevo Estado_Quirúrgico, sin incluir datos personales del paciente.

---

### Requisito 8: Panel de Gestión (Interfaz Privada)

**User Story:** Como Funcionario, quiero acceder a un panel de gestión donde pueda ver y operar todas las sesiones activas, para administrar el estado de los pacientes de forma eficiente.

#### Criterios de Aceptación

1. THE Interfaz_Privada SHALL requerir autenticación válida para ser accedida.
2. THE Panel_Gestión SHALL mostrar la lista de sesiones activas con código, estado, mensaje y acciones disponibles.
3. THE Panel_Gestión SHALL permitir al Funcionario cambiar estado, editar mensaje y eliminar sesión sin recargar la página completa.
4. THE Panel_Gestión SHALL ser de uso exclusivo para usuarios autenticados; cualquier acceso sin sesión válida redirige al login.
