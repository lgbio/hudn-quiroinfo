
## codigoPaciente: 
- Habrá una tabla en la BD de 'pacientes_programados' para cirugía, con la mínima información de 'identificacion' (número o código) y 'nombre'. Esta tabla se cargará con los datos del hospital al iniciar la aplicación.

## INICIO DE SESION
- El inicio de la sesión debe ser más simple ya que pueden ser muchos los funcionarios que puedan interacturar con el sistema por motivos de la rotación de turnos. Entonces, el ingreso se hace solo con solicitud del correo de la persona o del número del móvil, para que el sistema le envíe un código y lo ingrese para autenticarse. 

- En esta primera versión, solo se solicita el correo y solo se verifica que sea un correo bien construido. Para la segunda versión ya se hace la verificación.

- Entonces se elimina ROLES Y CRUD completo por login por email y un unico rol (staff).

## NOTIFICACIONES AL USUARIO
- Para esta primera versión, las notificaciones al usuario van a ser simples a través de prints o logs, sin twinglo para SMSs o Whatsapps.

## LAYOUT E INTERACCION
- El layout de gestión de la app va a mostrar dos tablas paralelas: una con la información de  los pacientes programados y otra con la información de los pacientes en sala que están en el tablero. 

### TABLA PACIENTES PROGRAMADOS
- En los pacientes programados, se va a mostrar las columnas de 'IDENTIFICACION' 'NOMBRE' y 'ESTADO'

- En la columna de 'Estado' se va a mostrar cuatro botones que representan los estados quirúrgicos que puede tener un paciente. Uno de los cuales es el que se va a mostrar en el tablero. 
	
- Los estados quirúrgicos van a ser: EN_PREPARACION, EN_CIRUGIA, EN_ RECUPERACION, FINALIZADO, y OTRO.

- Los botones de estado quirúrgico van a comportarse como 'radio buttons' de tal forma que solo un estado va a estar activo. El botón seleccionado se debe colocar en un color que permita destacarse claramente de los demás.

- El usuario puede seleccionar el estado presionando uno de los botones de estados quirúrgicos y este se reflejará automáticamente en el tablero.

- Cuando el funcionario presione un botón de estado, la app verifica si el paciente ya está adicionado a la tabla de pacientes en sala y le cambia de estado. Si no está adicionado entonces lo adiciona con el estado del boton presionado.

- Cuando el funcionario seleccione el estado OTRO, la app va a mostrar un widget para que el funcionario ingrese un texto que represente este estado y este texto es el que aparece en el tablero.

- Cuando el funcionario presiona el botón de estado "FINALIZADO", el paciente se elimina de la tabla de pacientes en sala. 

- Debajo de la tabla de pacientes programados va a existir un botón 'Adicionar paciente' para adicionar un paciente que no está en la tabla de programados, ya que hay casos de pacientes que llegan de urgencias y no están programados pero se deben operar inmediatamente. Por tanto, al adicionar el nuevo paciente, este aparecerá en la tabla de programados y el funcionario ya podrá adicionarlo a la tabla de pacientes en sala e interactuar con sus estados.


### TABLA DE PACIENTES EN SALA
- Esta tabla va a contener las columnas de: 'IDENTIFICACION', 'ESTADO'. 'HORA INGRESO'

- Esta misma información es la que se va a mostrar en el tablero.

### TESTING
- Para los tests, de esta funcionalidad del tablero, la tabla de la BD de 'pacientes_programados' se puede llenar con datos fake.

- Se evitarán los Tests de servicios + vistas completos, para este MVP Solo tests de servicios críticos 1 test básico de vista (opcional)
	
## OTRAS OBSERVACIONES:
1. Simplificaciones clave
1.1 Modelo de datos

ANTES:

Paciente
SesionActiva
RegistroEstado
RegistroNotificacion

PROPUESTA MVP:

Sesion (única entidad central)
RegistroEstado (auditoría mínima)

Eliminar:

Paciente (por ahora)
RegistroNotificacion (por ahora)
	

1.2 Sesión unificada

Reemplazar SesionActiva por:

Una sola entidad Sesion
Controlar estado mediante campos:
finalizadoEn
ocultadoEn

1.3 Apps Django

ANTES:

5 apps separadas

PROPUESTA MVP:

Reducir a:
core (sesiones)
notificaciones (simple)
autenticacion

1.4 Notificaciones

ANTES:

Twilio desde el inicio

PROPUESTA MVP:

Simulación (print/log)
Integración real en fase posterior


