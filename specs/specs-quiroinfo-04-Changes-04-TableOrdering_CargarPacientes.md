Other additional changes:

- The ordering in the table of 'programados'  must be the same used for table "en sala".

- I want to remove the model 'RegistroEstdo" and its DB entity from the app. Also, remove the correspondig code involving them. For now, this log is not necessary.  

- I want to add a button at botton of table 'Pacientes programados' named "Cargar pacientes programados".

- When pressed this buttoon, it clears the table of "Pacientes programados" and call the function 'Utils.cargarPacientesProgramados()' from the module app_core.utils. 

- This function deletes the data from entity "pacientes" and load new data on it.
