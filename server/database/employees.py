from server.database.connection import databases_connection
import psycopg
import re

# Valores permitidos para el tipo de empleado.
VALID_EMPLOYEE_TYPES = ("permanent","temporary")

def validate_employee_type(employee_type):
    """valida el tipo de empleado"""

    if employee_type not in VALID_EMPLOYEE_TYPES:
        raise ValueError(
            "El tipo de empleado debe ser 'permanent' o 'temporary'"
        )

def validate_active(active):
    """Valida que active sea realmente booleano"""

    if type(active) is not bool:
        raise ValueError (
            "El estado active debe ser True o False"
        )

def validate_employee_name(name):
    # 1. Comprobar que sea una cadena de texto
    if not isinstance(name,str):
        raise TypeError(
            "El nombre debe ser una cadena de texto"
            )
    
    # 2. Eliminar espacios al principio y al final
    name = name.strip()

    # 3. Comprobar que no esté vacío
    if not name:
        raise ValueError(
            "EL nombre no puede estar vacio"
        )
    # 4. Comprobar que no supere los 100 caracteres
    if len(name)>100:
        raise ValueError(
            "El nombre no puede superar los 100 caracteres"
        )
    
    # 5. Aceptar únicamente letras y espacios entre palabras
    if not re.fullmatch(r"[^\W\d_]+(?: +[^\W\d_]+)*", name):
        raise ValueError(
            "El nombre solo puede contener letras y espacios"
        )
    
    return name

    
def insert_employees(name, employee_type):
    """Registra un empleado y devuelve su ID"""

    name = validate_employee_name(name)

    validate_employee_type(employee_type)

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
        return employee_id
    
    
    except psycopg.Error:
        conn.rollback()#para deshacer la transacción en caso de error
        raise
    finally:
        conn.close()


def update_employees(employee_id, name, employee_type, active):
    """Actualiza el tipo y estado de un empleado"""

    #Validar datos antes de conectar con PostgreSQL
    name = validate_employee_name(name)
    validate_employee_type(employee_type)
    validate_active(active)
    
    conn = databases_connection()
    
    try:
        with conn.cursor() as cursor:

            #Comprobar que el empleado exista y bloquear su registro
            cursor.execute("""
                SELECT id 
                FROM employees
                WHERE id = %s
                FOR UPDATE;
            """,(employee_id,))

            employee = cursor.fetchone()
            
            if employee is None:
                conn.rollback()
                return False
            
            #Si intenta desactivar, comprobar que no tenga un jornada
            #laboral abierta
            if active is False:
                cursor.execute(""" 
                    SELECT EXISTS(
                        SELECT 1
                        FROM workdays
                        WHERE employee_id = %s
                        AND clock_out IS NULL
                    );
                """,(employee_id,))

                has_open_worday=cursor.fetchone()[0]

                if has_open_worday:
                    raise ValueError(
                        "No No se puede desactivar un empleado "
                        "que tiene una jornada laboral abierta."
                    )
            
            #Actualiza los datos del empleado
            cursor.execute("""
            UPDATE employees 
            SET name = %s,
                employee_type = %s, 
                active = %s 
            WHERE id = %s
            RETURNING id;
            """, (name,employee_type,active,employee_id))
        
            updated_employee = cursor.fetchone()

        conn.commit()
        return True
            
    except (psycopg.Error,ValueError):
        conn.rollback()
        raise

    finally:
        conn.close()

def deactivate_employee(employee_id):
    """
    Desactiva un empleado y distingue estos resultados:
    - deactivated
    - already_inactive
    - not_found

    Impide desactivar empleados con una jornada abierta.
    """
   
    conn = databases_connection()
        
    try:
        with conn.cursor() as cursor:

            # Comprobar que el empleado exista y bloquear su registro
            cursor.execute( """
            SELECT active
            FROM employees
            WHERE id = %s
            FOR UPDATE;
            """,
            (employee_id,))

            employee = cursor.fetchone()

            if employee is None:
                conn.commit()
                return "not_found"

            #Comprobar que el empleado ya está desactivado
            if employee[0] is False:
                conn.commit()
                return "already_inactive"

            #Comprobar si el empleado tiene una jornada laboral abierta
            cursor.execute("""
            SELECT EXISTS(
                SELECT 1
                FROM workdays
                WHERE employee_id = %s
                    AND clock_out IS NULL
                    );
                    """,(employee_id,)                
            )

            has_open_worday=cursor.fetchone()[0]

            if has_open_worday:
                raise ValueError(
                    "No se puede desactivar un empleado"
                    "que tiene una jornada laboral abierta."
                )

            #Desactivar al empleado
            cursor.execute(
                """UPDATE employees
                SET active = FALSE
                WHERE id = %s
                RETURNING id;
                """,(employee_id,)
            )

            employee = cursor.fetchone()

        conn.commit()
        return "desactivated"

    except (psycopg.Error,ValueError):
        conn.rollback()
        raise

    finally:
        conn.close()


def consult_employees(employee_id):
    """Consulta un empleado por su ID"""

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

        return registro

    except psycopg.Error:
        raise

    finally:
        conn.close()

def get_employees():
    """Devuelve todos los empleados activos"""

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

            return registros#Devuelve la lista completa a quien llamó la función.|


    except psycopg.Error:
        raise

    finally:
        conn.close()
