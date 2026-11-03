from server.database.connection import databases_connection
import psycopg
import uuid

def employee_entrance(employee_id):

    conn=databases_connection()


    try:
        #  Validar que el empleado exista y esté activo.
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id
                FROM employees
                WHERE id = %s
                AND active = TRUE;
            """, (employee_id,))

            employee = cursor.fetchone()

            if employee is None:
                raise ValueError("El empleado no existe o está inactivo")
        
            uuid_id = uuid.uuid4()

            #  Registrar la entrada del empleado.
            cursor.execute("""
                INSERT INTO workdays
                    (id, employee_id, work_date)
                VALUES (%s, %s, CURRENT_DATE)
                RETURNING id;
                """,
                (uuid_id, employee_id))

            workday_id = cursor.fetchone()[0]

        conn.commit()

        print("Entrada registrada correctamente")
        return workday_id

    except (psycopg.Error, ValueError) as e:
        conn.rollback()
        print(f"Error al registrar la entrada del empelado: {e}" )
        raise
    finally:
        conn.close()

def employee_exit(workday_id):
    
    conn=databases_connection()

    try:
        with conn.cursor() as cursor:

            #  Verificar que la jornada exista y siga abierta.
            #  verificar y bloquea esa fila para evitar que otra transacción la modifique simultáneamente.
            cursor.execute("""
                SELECT id 
                FROM workdays
                WHERE id = %s
                    AND clock_out IS NULL
                FOR UPDATE;
            """,(workday_id,))

            workday=cursor.fetchone()

            if workday is None:
                raise ValueError(
                    "La jornada no existe o ya tiene registrada la salida"
                )

            #Verificar que no haya descansos pendientes
            cursor.execute("""
                SELECT id
                FROM breaks
                WHERE workday_id = %s
                    AND break_end IS NULL; 
            """,(workday_id,))

            active_break=cursor.fetchone()#devuelve el ID del descanso si encuentra uno pendiente
            #Si no encuentra ninguno, devuelve None

            if active_break is not None:
                raise ValueError(
                    "Existe un descanso pendiente"
                )

            # Registrar la hora de salida.
            cursor.execute("""
                UPDATE workdays
                SET clock_out = CURRENT_TIMESTAMP
                WHERE id = %s
                    AND clock_out IS NULL
                RETURNING id;
            """, (workday_id,))

            # Verificar si se actualizó alguna jornada.
            workday_id = cursor.fetchone()[0]

            
        conn.commit()

        print("Salida registrada correctamente")
        return workday_id
    except (psycopg.Error, ValueError) as e:
        conn.rollback()
        print(f"Error al registrar la salida: {e}" )
        raise
    finally:
        conn.close()