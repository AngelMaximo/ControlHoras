from server.database.connection import databases_connection
import psycopg

def insert_employees(name, employee_type):
    
    conn = databases_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""INSERT INTO employees 
            (name, employee_type) 
            VALUES (%s, %s)
            RETURNING id;
            """,
            (name, employee_type))

            employee_id = cursor.fetchone()[0]
        conn.commit()
        print("Usuario insertado correctamente")
        return employee_id
    
    
    except psycopg.Error as e:
        conn.rollback()#para deshacer la transacción en caso de error
        print(f"Error al insertar usuario: {e}")
        raise
    finally:
        conn.close()


def update_employees(employee_id,employee_type,active):
    
    conn = databases_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""UPDATE employees 
            SET employee_type = %s, 
            active = %s 
            WHERE id = %s;
            """, 
            (employee_type,active,employee_id)
            )
        
            if cursor.rowcount == 1:
                conn.commit()
                print("Registro actualizado correctamente")
            else:
                conn.rollback()
                print("No se encontró el empleado con el ID proporcionado")
            
    except psycopg.Error as e:
        conn.rollback()
        print(f"Error al actualizar el registro: {e}")
        raise
    finally:
        conn.close()

def deactivate_employee(employee_id):
   
    conn = databases_connection()
        
    try:
        with conn.cursor() as cursor:
            cursor.execute( """
            UPDATE employees
            SET active = FALSE
            WHERE id = %s;
            """,
            (employee_id,))

            if cursor.rowcount == 1:
                conn.commit()#Guardar cambios
                print("Registro actualizado correctamente")
            else:
                conn.rollback()
                print("No se encontró el empleado con el ID proporcionado")

    except psycopg.Error as e:
        conn.rollback()
        print(f"Error al actualizar el registro: {e}")
        raise

    finally:
        conn.close()


def consult_employees(employee_id):

    conn = databases_connection()

    try:
        with conn.cursor() as cursor: #el cursor se cierra con el bloque with
            cursor.execute("""
                SELECT * FROM employees 
                where id = %s;
                """, 
                (employee_id,)
            )
    
            registro = cursor.fetchone()

            if registro is None:
                print("No se encontró el empleado")
            else:
                print(registro)

            return registro

    except psycopg.Error as e:
        print(f"Error al consultar el registro: {e}") 
        raise

    finally:
        conn.close()

def get_employees():

    conn = databases_connection()

    try:
        with conn.cursor() as cursor: #el cursor se cierra con el bloque with
            cursor.execute("""
                SELECT * FROM employees
                WHERE active = TRUE
                ORDER BY id;
                """
            )
    
            registros = cursor.fetchall()#Obtiene todas las filas encontradas.

            if not registros:#Comprueba si la lista está vacía.
                print("No se encontraron empleados activos")
            else:
                for registro in registros:
                    print(registro)

            return registros#Devuelve la lista completa a quien llamó la función.|


    except psycopg.Error as e:
        print(f"Error al consultar el registro: {e}") 
        raise

    finally:
        conn.close()
