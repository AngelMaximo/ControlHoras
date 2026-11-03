import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def databases_connection():
    try:
        connection = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        
        print("conexion exitosa")
        return connection #entrega la conexión a la función que la necesita.
        

    except psycopg.Error as e:
        print(f"Error en la conexión: {e}")
        raise #propaga el error si no se puede conectar, para que la función que llama pueda manejarlo
