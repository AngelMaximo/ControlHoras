from server.database.connection import databases_connection
import psycopg
import uuid

def start_break(workday_id):

    conn=databases_connection()

    try:
        # Verificar que la jornada exista y siga abierta.
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM workdays
                WHERE id = %s
                    AND clock_out is NULL 
                FOR UPDATE;
                """,(workday_id,))# FOR UPDATE: bloquea temporalmente la fila de la jornada durante la transacción para evitar que dos solicitudes concurrentes inicien descansos simultáneamente.

            workday=cursor.fetchone()

            if workday is None:
                raise ValueError(
                    "La jornada no existe o ya está cerrada"
                )
            
            # Verificar que no haya un descanso pendiente.
            cursor.execute("""
                SELECT id FROM breaks
                WHERE workday_id = %s
                    AND break_end IS NULL;
            """,(workday_id,))

            active_break= cursor.fetchone()

            if active_break is not None:
                raise ValueError(
                    "Ya existe un descanso sin finalizar"
                )

            # Generar el ID e insertar el nuevo descanso.
            break_id = uuid.uuid4()
            cursor.execute("""
                INSERT INTO breaks (id, workday_id)
                VALUES (%s, %s)
                RETURNING id;
            """, (break_id,workday_id))

            break_id = cursor.fetchone()[0] #extrae el primer elemento de esa fila: el UUID del descanso.
        
        conn.commit()
        return break_id

    except (psycopg.Error, ValueError):
        conn.rollback()
        raise
    
    finally:
        conn.close()


def end_break(break_id):
    
    conn=databases_connection()

    try:
        with conn.cursor() as cursor:

            #Verificar que el descanso y su jornada existan
            #y que ambos sigan abiertos 
            cursor.execute("""
            SELECT b.id
            FROM breaks AS b
            INNER JOIN workdays AS w
                ON w.id = b.workday_id
            WHERE b.id=%s
                AND b.break_end IS NULL
                AND w.clock_out IS NULL
            FOR UPDATE OF w, b;
            """,(break_id,))

            active_break=cursor.fetchone()

            if active_break is None:
                raise ValueError(
                    "El descanso no existe, ya ha sido finalizado"
                    "o la jornada está cerrada"
                )

            # Registrar automáticamente la hora de finalización.
            cursor.execute("""
                UPDATE breaks
                SET break_end = CURRENT_TIMESTAMP
                WHERE id = %s
                    AND break_end IS NULL
                RETURNING id;
            """, (break_id,))

            finished_break = cursor.fetchone()

            conn.commit()

            return finished_break[0]

    except (psycopg.Error, ValueError):
        conn.rollback()
        raise
    
    finally:
        conn.close()