import mysql.connector

try:
    # Se usa 127.0.0.1 y el puerto 3306 explícito para evitar problemas de socket local
    conexion = mysql.connector.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="",
        database="bodega_electricidad_prestamos"
    )

    cursor = conexion.cursor(dictionary=True)

    # Consulta usando la columna correcta 'id_articulo'
    cursor.execute("SELECT id_articulo, nombre, sku FROM articulos LIMIT 5")
    filas = cursor.fetchall()

    print("========================================")
    print(" ¡CONEXIÓN Y CONSULTA EXITOSA!")
    print("========================================")
    for fila in filas:
        print(f"ID: {fila['id_articulo']} | Nombre: {fila['nombre']} | SKU: {fila['sku']}")

except mysql.connector.Error as err:
    print("========================================")
    print(" ERROR DE CONEXIÓN O CONSULTA:")
    print("========================================")
    print(err)

finally:
    if 'conexion' in locals() and conexion.is_connected():
        cursor.close()
        conexion.close()