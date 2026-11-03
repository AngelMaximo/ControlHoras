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
    CREATE TABLE IF NOT EXISTS workdays(
    id UUID PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    work_date DATE NOT NULL,
    clock_in TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    clock_out TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (employee_id) 
        REFERENCES employees (id),
        
    UNIQUE (employee_id, work_date)
    ); 
    
    """)
    #employees.id SERIAL genera identificadores de tipo INTEGER.
    #UNIQUE (employee_id, work_date) impide registrar dos jornadas para el mismo empleado en la misma fecha.
    #clock_out permite NULL mientras el empleado todavía no haya registrado su salida.

    conn.commit()
    print("Tabla workdays creada correctamente.")

except Exception as e:
    conn.rollback()
    print(f"Error al crear la tabla: {e}")

finally:
    cursor.close()
    conn.close()