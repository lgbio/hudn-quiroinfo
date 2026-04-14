# Documento de Requisitos

## Introducción

Sistema de información en tiempo casi real para familiares de pacientes quirúrgicos. Funciona como un tablero tipo aeropuerto: muestra el estado del proceso quirúrgico de cada paciente de forma simple y comprensible para personas sin formación médica. Los pacientes se identifican mediante un código o número de identificación para proteger su privacidad. El sistema está diseñado para proyectarse en pantallas de TV o monitor en la sala de espera; los familiares no interactúan con el sistema. El personal que opera el sistema es mínimo: uno o más funcionarios que gestionan el estado de los pacientes con la menor cantidad de pasos posible.

## Glosario

- **Sistema**: La aplicación web de seguimiento de estado quirúrgico para familiares.
- **Tablero**: Pantalla principal de visualización pública, proyectada en TV o monitor en sala de espera. No es interactiva; solo muestra información.
- **Paciente**: Modelo unificado que representa a cualquier paciente del sistema, con campos `identificacion`, `nombre` y `origen`. Reemplaza los modelos separados `PacienteProgramado` y `PacienteUrgencias`.
- **Origen**: Campo del modelo Paciente que indica si el paciente es de tipo PROGRAMADO (cargado desde el hospital) o URGENCIAS (agregado manualmente por el Funcionario).
- **Identificacion**: Número o código del paciente visible en el Tablero, sin revelar datos personales sensibles adicionales.
- **Estado_Quirurgico**: Fase actual del proceso quirúrgico del paciente, expresada en términos comprensibles para no médicos. Valores posibles: EN_PREPARACION, EN_CIRUGIA, EN_RECUPERACION, FINALIZADO, OTRO.
- **Sesion**: Registro activo de un paciente en el tablero durante su proceso quirúrgico. Contiene el estado actual, la hora de ingreso y el campo `oculto` para controlar visibilidad.
- **Paciente_En_Sala**: Paciente con una Sesion activa (oculto=False) visible en el Tablero y en la tabla de gestión.
- **Funcionario**: Usuario del sistema con acceso al Panel de Gestión; gestiona el estado de los pacientes.
- **Interfaz_Publica**: El Tablero proyectado en sala de espera; accesible sin autenticación, solo lectura.
- **Interfaz_Privada**: El Panel de Gestión utilizado por el Funcionario; requiere autenticación.
- **Panel_Gestion**: Vista principal de la Interfaz_Privada con las dos tablas paralelas de operación.
- **Tabla_Programados**: Tabla en el Panel_Gestion que lista los Pacientes con sus botones de estado.
- **Tabla_En_Sala**: Tabla en el Panel_Gestion que lista los Pacientes_En_Sala actualmente en el Tablero.

---

## Requisitos

### Requisito 1: Carga de Pacientes Programados

**User Story:** Como Funcionario, quiero que al iniciar la aplicación se carguen automáticamente los pacientes con cirugía programada, para no tener que ingresarlos manualmente uno a uno.

#### Criterios de Aceptación

1. THE Sistema SHALL cargar al iniciar la aplicación los registros de Pacientes con `origen=PROGRAMADO` de la base de datos del hospital, con los campos `identificacion` y `nombre`.
2. THE Tabla_Programados SHALL mostrar todos los Pacientes cargados con columnas: IDENTIFICACION, NOMBRE, ESTADO.
3. THE Sistema SHALL permitir al Funcionario agregar manualmente un Paciente de urgencias desde el Panel_Gestion mediante un botón "Adicionar paciente".
4. WHEN el Funcionario agrega un Paciente de urgencias, THE Sistema SHALL crearlo con `origen=URGENCIAS` y añadirlo a la Tabla_Programados con los campos `identificacion` y `nombre`, permitiendo interactuar con sus estados.

---

### Requisito 2: Tablero de Estado Quirúrgico (Interfaz Pública)

**User Story:** Como familiar de un paciente, quiero ver en una pantalla proyectada en la sala de espera el estado actual del proceso quirúrgico de mi familiar, para saber en qué fase se encuentra sin necesidad de interrumpir al personal médico.

#### Criterios de Aceptación

1. THE Tablero SHALL ser accesible desde una URL pública sin requerir autenticación ni interacción de ningún usuario.
2. THE Tablero SHALL mostrar una lista de todos los Pacientes_En_Sala, identificados por su Identificacion.
3. THE Tablero SHALL mostrar para cada Paciente_En_Sala su Estado_Quirurgico actual y la hora de ingreso a sala.
4. WHEN el Estado_Quirurgico de un paciente cambia, THE Tablero SHALL reflejar el nuevo estado en un tiempo máximo de 30 segundos sin requerir recarga manual de la página.
5. THE Tablero SHALL ser legible en pantallas de al menos 40 pulgadas a una distancia de 3 metros, con texto de tamaño mínimo 48px para la Identificacion y el Estado_Quirurgico.
6. THE Tablero SHALL funcionar como pantalla de solo lectura proyectada en TV o monitor, sin requerir interacción del Familiar ni de ningún usuario externo.
7. IF la conexión con el servidor se interrumpe, THEN THE Tablero SHALL mostrar un indicador visible de "Sin conexión" y el último estado conocido de cada Paciente_En_Sala.

---

### Requisito 3: Estados Quirúrgicos

**User Story:** Como familiar de un paciente, quiero que los estados del proceso quirúrgico estén expresados en lenguaje simple, para entender la situación sin conocimientos médicos.

#### Criterios de Aceptación

1. THE Sistema SHALL manejar exactamente los siguientes Estados_Quirurgicos: EN_PREPARACION, EN_CIRUGIA, EN_RECUPERACION, FINALIZADO, OTRO.
2. THE Tablero SHALL mostrar cada Estado_Quirurgico acompañado de un color distintivo: EN_PREPARACION en amarillo, EN_CIRUGIA en naranja, EN_RECUPERACION en azul, FINALIZADO en gris, OTRO en morado.
3. THE Sistema SHALL permitir al Funcionario seleccionar cualquier Estado_Quirurgico para un paciente mediante radio buttons visuales, sin restricción de secuencia lineal.
4. WHEN el estado es OTRO, THEN THE Sistema SHALL requerir un texto descriptivo con máximo 50 caracteres que aparecerá en el Tablero junto al estado.
5. THE Sistema SHALL sanitizar el contenido de la descripción antes de mostrarlo en el Tablero.
6. IF el estado no es OTRO, THEN la descripción SHALL ser nula.
7. WHEN el Funcionario selecciona FINALIZADO, THEN THE Sistema SHALL marcar la Sesion como no visible en el Tablero (oculto=True) y el paciente desaparecerá del Tablero y de la Tabla_En_Sala.

---

### Requisito 4: Panel de Gestión — Dos Tablas Paralelas

**User Story:** Como Funcionario, quiero ver en el Panel de Gestión dos tablas lado a lado: una con los pacientes programados y otra con los pacientes en sala, para gestionar el estado de cada paciente con el mínimo de pasos posible.

#### Criterios de Aceptación

1. THE Panel_Gestion SHALL mostrar dos tablas paralelas (lado a lado): Tabla_Programados a la izquierda y Tabla_En_Sala a la derecha.
2. THE Tabla_Programados SHALL mostrar columnas: IDENTIFICACION, NOMBRE, ESTADO; donde ESTADO contiene cinco radio buttons visuales representando los cinco Estados_Quirurgicos.
3. THE Tabla_En_Sala SHALL mostrar columnas: IDENTIFICACION, ESTADO, HORA INGRESO.
4. WHEN el Funcionario presiona un radio button de estado para un paciente que NO está en la Tabla_En_Sala, THE Sistema SHALL agregar al paciente a la Tabla_En_Sala con ese estado y registrar la hora de ingreso.
5. WHEN el Funcionario presiona un radio button de estado para un paciente que YA está en la Tabla_En_Sala, THE Sistema SHALL actualizar su estado sin crear una nueva entrada.
6. THE Sistema SHALL permitir al Funcionario actualizar el Estado_Quirurgico de un Paciente_En_Sala en un máximo de 2 interacciones desde el Panel_Gestion.
7. WHEN el Estado_Quirurgico se actualiza, THE Sistema SHALL registrar el cambio con la marca de tiempo correspondiente.
8. IF la actualización de estado falla por error del servidor, THEN THE Sistema SHALL notificar al Funcionario con un mensaje de error y conservar el estado anterior sin modificación.

---

### Requisito 5: Privacidad de los Pacientes

**User Story:** Como responsable del hospital, quiero que el sistema no exponga datos personales de los pacientes en el Tablero público, para cumplir con las obligaciones de privacidad.

#### Criterios de Aceptación

1. THE Tablero SHALL mostrar exclusivamente la Identificacion como identificador, sin nombre, apellido, edad, diagnóstico ni ningún otro dato personal sensible.
2. THE Sistema SHALL almacenar el nombre del paciente únicamente en el modelo Paciente, sin vincularlo en ninguna respuesta enviada al Tablero.
3. THE Sistema SHALL transmitir todos los datos entre cliente y servidor mediante HTTPS.

---

### Requisito 6: Autenticación Simplificada por Email

**User Story:** Como Funcionario, quiero ingresar al sistema con mi correo electrónico, para acceder al Panel de Gestión de forma simple y segura.

#### Criterios de Aceptación

1. THE Sistema SHALL requerir únicamente una dirección de correo electrónico para acceder a la pantalla de gestión.
2. WHEN el Funcionario ingresa su correo electrónico, THE Sistema SHALL verificar que el formato del correo sea válido antes de cualquier otra validación.
3. IF el correo electrónico ingresado no tiene un formato válido, THEN THE Sistema SHALL mostrar un mensaje de error indicando el problema sin redirigir al Panel_Gestion.
4. THE Sistema SHALL validar que el email ingresado pertenezca a una lista blanca o dominio permitido, configurable en la configuración del sistema.
5. IF el email no está autorizado por la lista blanca o dominio permitido, THEN THE Sistema SHALL denegar el acceso y mostrar un mensaje de error.
6. WHILE una sesión permanece inactiva por más de 120 minutos, THE Sistema SHALL cerrar la sesión automáticamente y requerir nueva autenticación.
7. IF un usuario no autenticado intenta acceder a la pantalla de gestión, THEN THE Sistema SHALL redirigirlo a la pantalla de inicio de sesión.

---

### Requisito 7: Notificaciones Internas (Log)

**User Story:** Como desarrollador del sistema, quiero que los cambios de estado queden registrados en el log de la aplicación, para poder auditar la actividad sin infraestructura adicional en esta primera versión.

#### Criterios de Aceptación

1. WHEN el Estado_Quirurgico de un Paciente_En_Sala cambia, THE Sistema SHALL registrar el evento mediante `logging.info()` indicando la Identificacion del paciente y el nuevo estado.
2. IF ocurre un error interno durante el cambio de estado, THEN THE Sistema SHALL registrar el error mediante `logging.error()` sin interrumpir la respuesta al Funcionario.
3. THE Sistema SHALL omitir el envío de notificaciones externas (SMS, WhatsApp, email) en esta primera versión.

---

### Requisito 8: Auditoría de Cambios de Estado

**User Story:** Como responsable del hospital, quiero que cada cambio de estado quede registrado con su marca de tiempo, para poder revisar el historial de un paciente si es necesario.

#### Criterios de Aceptación

1. WHEN el Estado_Quirurgico de un Paciente_En_Sala cambia, THE Sistema SHALL crear un registro de auditoría con: Identificacion, estado anterior, estado nuevo y marca de tiempo del cambio.
2. THE Sistema SHALL conservar los registros de auditoría aunque la Sesion del paciente haya finalizado.

---

### Requisito 9: Modelo Unificado de Paciente

**User Story:** Como sistema, quiero manejar un único tipo de paciente, para evitar duplicidad de datos y simplificar la lógica de negocio.

#### Criterios de Aceptación

1. THE Sistema SHALL manejar un único modelo lógico de Paciente con los campos `identificacion`, `nombre` y `origen`.
2. THE campo `origen` SHALL permitir distinguir entre pacientes PROGRAMADO y URGENCIAS.
3. THE Sistema SHALL evitar la existencia de entidades separadas para PacienteProgramado y PacienteUrgencias.
4. THE Sistema SHALL permitir agregar pacientes de urgencias reutilizando el mismo modelo de Paciente.

---

### Requisito 10: Unicidad de Sesión Activa

**User Story:** Como sistema, quiero asegurar que un paciente tenga una sola sesión activa, para evitar inconsistencias en el tablero.

#### Criterios de Aceptación

1. THE Sistema SHALL garantizar que solo exista una Sesion activa (oculto=False) por cada Paciente.
2. IF se intenta crear una nueva Sesion para un Paciente con sesión activa, THEN THE Sistema SHALL reutilizar la sesión existente.
3. THE Sistema SHALL prevenir condiciones de carrera mediante restricciones a nivel de base de datos.

---

### Requisito 11: Finalización de Paciente

**User Story:** Como Funcionario, quiero finalizar el seguimiento de un paciente sin perder el historial, para mantener trazabilidad del proceso.

#### Criterios de Aceptación

1. WHEN el Funcionario selecciona el estado FINALIZADO, THEN THE Sistema SHALL marcar la Sesion como no visible en el Tablero (oculto=True).
2. THE Sistema SHALL conservar el registro de la Sesion en la base de datos.
3. THE Sistema SHALL no eliminar registros físicos de Sesion.

---

### Requisito 12: Orden del Tablero

**User Story:** Como familiar, quiero ver primero los pacientes más recientes, para identificar rápidamente los ingresos nuevos.

#### Criterios de Aceptación

1. THE Tablero SHALL ordenar los pacientes por `ingresadoEn` en orden descendente.
2. THE paciente más reciente SHALL aparecer en la parte superior del Tablero.

---

### Requisito 13: Flujo Operativo del Sistema

**User Story:** Como Funcionario, quiero un flujo claro y rápido para gestionar el estado de los pacientes, para minimizar el tiempo de operación.

#### Criterios de Aceptación

1. THE Sistema SHALL permitir seleccionar estado desde la Tabla_Programados.
2. WHEN se selecciona un estado, THEN THE Sistema SHALL crear o actualizar la Sesion del Paciente correspondiente.
3. THE Paciente SHALL aparecer en la Tabla_En_Sala inmediatamente tras la selección de estado.
4. WHEN se selecciona FINALIZADO, THEN el Paciente SHALL desaparecer del Tablero y de la Tabla_En_Sala.

---

### Requisito 14: Concurrencia

**User Story:** Como sistema, quiero manejar actualizaciones simultáneas sin inconsistencias, para garantizar la integridad de los datos.

#### Criterios de Aceptación

1. IF múltiples actualizaciones ocurren sobre la misma Sesion, THEN THE Sistema SHALL aplicar la última actualización recibida.
2. THE Sistema SHALL garantizar consistencia mediante restricciones en base de datos.
