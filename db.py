import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="",
        database="bodega_electricidad_prestamos"
    )

def obtener_materiales(busqueda=""):
    """Recupera los materiales del inventario, opcionalmente filtrados por nombre o código."""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        if busqueda:
            query = """
                SELECT id, codigo, nombre, stock, ubicacion 
                FROM materiales 
                WHERE nombre LIKE %s OR codigo LIKE %s
                ORDER BY nombre ASC
            """
            param = f"%{busqueda}%"
            cursor.execute(query, (param, param))
        else:
            query = "SELECT id, codigo, nombre, stock, ubicacion FROM materiales ORDER BY nombre ASC"
            cursor.execute(query)
            
        resultados = cursor.fetchall()
        return resultados
    finally:
        conn.close()

def registrar_solicitud(profesor_id, materiales_lista, mensaje=""):
    """
    Registra una nueva solicitud de materiales y sus detalles en una transacción.
    materiales_lista es una lista de dicts: [{'id': 1, 'cantidad': 2}, ...]
    """
    conn = get_connection()
    if not conn:
        return False, "Error de conexión"

    try:
        cursor = conn.cursor()
        
        # 1. Insertar cabecera de la solicitud
        query_solicitud = """
            INSERT INTO solicitudes (profesor_id, mensaje, estado) 
            VALUES (%s, %s, 'pendiente')
        """
        cursor.execute(query_solicitud, (profesor_id, mensaje))
        solicitud_id = cursor.lastrowid

        # 2. Insertar los ítems del carrito en el detalle
        query_detalle = """
            INSERT INTO detalle_solicitud (solicitud_id, material_id, cantidad) 
            VALUES (%s, %s, %s)
        """
        detalles_data = [
            (solicitud_id, item['id'], item['cantidad']) 
            for item in materiales_lista
        ]
        cursor.executemany(query_detalle, detalles_data)

        # Confirmar la transacción
        conn.commit()
        return True, solicitud_id
    except Error as e:
        conn.rollback()
        print(f"Error al registrar la solicitud: {e}")
        return False, str(e)
    finally:
        conn.close()

def obtener_cola_fifo():
    """
    Obtiene todas las solicitudes pendientes ordenadas estrictamente 
    por fecha de creación ascendente (FIFO).
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        # Consulta para cabeceras en orden FIFO
        query_cabecera = """
            SELECT s.id AS solicitud_id, p.nombre AS profesor, p.correo, 
                   s.mensaje, s.fecha_creacion AS fecha
            FROM solicitudes s
            JOIN profesores p ON s.profesor_id = p.id
            WHERE s.estado = 'pendiente'
            ORDER BY s.fecha_creacion ASC
        """
        cursor.execute(query_cabecera)
        solicitudes = cursor.fetchall()

        # Obtener los detalles de cada solicitud
        for sol in solicitudes:
            query_detalle = """
                SELECT m.nombre, d.cantidad, m.ubicacion
                FROM detalle_solicitud d
                JOIN materiales m ON d.material_id = m.id
                WHERE d.solicitud_id = %s
            """
            cursor.execute(query_detalle, (sol['solicitud_id'],))
            sol['materiales'] = cursor.fetchall()
            # Convertir timestamp a formato legible en string
            sol['fecha'] = str(sol['fecha'])

        return solicitudes
    finally:
        conn.close()

def cambiar_estado_solicitud(solicitud_id, nuevo_estado):
    """
    Actualiza el estado de una solicitud ('entregado' o 'cancelado').
    Si el estado es 'entregado', descuenta el stock de los materiales.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)

        if nuevo_estado == 'entregado':
            # Obtener materiales solicitados para descontar stock
            cursor.execute(
                "SELECT material_id, cantidad FROM detalle_solicitud WHERE solicitud_id = %s", 
                (solicitud_id,)
            )
            items = cursor.fetchall()

            # Descontar el stock de cada material
            for item in items:
                cursor.execute(
                    "UPDATE materiales SET stock = stock - %s WHERE id = %s",
                    (item['cantidad'], item['material_id'])
                )

        # Actualizar el estado de la solicitud
        cursor.execute(
            "UPDATE solicitudes SET estado = %s WHERE id = %s",
            (nuevo_estado, solicitud_id)
        )

        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        print(f"Error al actualizar estado: {e}")
        return False
    finally:
        conn.close()