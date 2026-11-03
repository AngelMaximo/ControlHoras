import os 
import psycopg #adaptador de base de datos PostgreSQL
from dotenv import load_dotenv #libreria Lee el .env

load_dotenv()

conn=psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    employee_type VARCHAR(20) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    ); 
    
    """)

    conn.commit()
    print("Tabla employees creada correctamente.")

except Exception as e:
    conn.rollback()
    print(f"Error al crear la tabla: {e}")

finally:
    cursor.close()
    conn.close()