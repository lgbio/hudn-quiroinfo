import os, psycopg2
from urllib.parse import urlparse
import traceback    # format_exc

class Utils:

	#----------------------------------------------------------
	#-- Parse a database URL (e.g. Railway PostgreSQL URL) into components.
	#----------------------------------------------------------
	def getVarsFromDBUrl(db_url: str) -> dict:
		p = urlparse(db_url)
		return { "user":p.username, "password":p.password, "host":p.hostname, "dbname":p.path[1:], "port":p.port or 5432 }

	#--------------------------------------------------------------------
	# Execute query from DJango API
	#--------------------------------------------------------------------
	def execute_sql_query (query, values=None):
		print (f"+++ DEBUG: query '{query}'")
		print (f"+++ DEBUG: values '{values}'")
		DB_PARAMS = Utils.getVarsFromDBUrl (os.environ.get ("DATABASE_URL"))
		conn = psycopg2.connect(**DB_PARAMS)
		with conn.cursor() as cursor:
			cursor.execute(query, values)
		conn.commit()
		conn.close()
	
	#------------------------------------------------------------------------------
	#------------------------------------------------------------------------------
	def cargarPacientesProgramadosCirugia ():
		""" Carga los pacientes programados para cirugia desde la BD del hospital"""

		table = "pacientes"
		pacientes_data = [
			(11, 'Jorge R.', "Jorge Rámirez", "PROGRAMADO"),
			(12, 'Maria B.', "María Belen", "PROGRAMADO"),
			(13, 'Lina M.', "Lina Montoya", "PROGRAMADO"),
			(14, 'Alberto C.', "Alberto Camargo", "PROGRAMADO"),
			(15, 'Diana U.', "Diana Uribe", "PROGRAMADO"),
			(16, 'Adrian C.', "Adrian Cifuentes", "PROGRAMADO") ]

		#------------------------------------------------------------------------
		# Firt: Remove old ones
		Utils.execute_sql_query ("DELETE FROM pacientes;")

		print (f"\n+++ Creando pacientes PROGRAMADOS...")
		try:
			for entry in pacientes_data:
				placeholders = ', '.join(['%s'] * len(entry))
				query = psycopg2.sql.SQL("INSERT INTO {} VALUES ({})").format(
					psycopg2.sql.Identifier(table),
					psycopg2.sql.SQL(placeholders)
				)				 
				Utils.execute_sql_query (query, entry)
		except Exception as ex:
			Utils.printException (f">>> Exception::{str(ex)}")

	#-- Print exception with added 'message' and 'text'
	def printException (message, docFilepath=None):
		try:
			stackTrace = ''.join(traceback.format_exc())
			orgMessage = f"{message}:\n{stackTrace}"
			open ("log-exceptions.log", "a").write (orgMessage)
			print (orgMessage)
		except Exception as ex:
			print (f"+++ Error en printException. Message: {message}")
			pass
