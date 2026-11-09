from server.database.connection import databases_connection
import psycopg
import re

# Valores permitidos para el tipo de empleado.
VALID_EMPLOYEE_TYPES = ("permanent","temporary")

def validate_employee_type(employe_type):
    """valida el tipo de empleado"""

    if employe_type not in VALID_EMPLOYEE_TYPES:
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


def update_employees(employee_id,employee_type,active):
    """Actualiza el tipo y estado de un empleado"""

    validate_employee_type(employee_type)
    validate_active(active)
    
    conn = databases_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""UPDATE employees 
            SET employee_type = %s, 
            active = %s 
            WHERE id = %s
            RETURNING id;
            """, 
            (employee_type,active,employee_id)
            )
        
            employee = cursor.fetchone()

        if employee is None:
            conn.rollback
            return False

        conn.commit()
        return True
            
    except psycopg.Error:
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
    """
   
    conn = databases_connection()
        
    try:
        with conn.cursor() as cursor:
            # Intentar desactivar al empleado activo.
            cursor.execute( """
            UPDATE employees
            SET active = FALSE
            WHERE id = %s
                AND active = TRUE
            RETURNING id;
            """,
            (employee_id,))

            employee = cursor.fetchone()

            if employee is not None:
                conn.commit()
                return "deactivated"
            
            # Si no se actualizó, comprobar si el ID existe.
            cursor.execute("""
                SELECT active 
                FROM employees
                WHERE id = %s;
            """,(employee_id,))

            employee = cursor.fetchone()
        conn.rollback()

        if employee is None:
            return "not_found"
        
        return "already_inactive"

    except psycopg.Error:
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
