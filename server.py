from flask import Flask, render_template, request, jsonify, session, redirect
import pymysql

app = Flask(__name__)
app.secret_key = 'clave_secreta_bodega_electricidad'

def obtener_conexion():
    return pymysql.connect(
        host='127.0.0.1',
        port=3307,  # Puerto configurado en tu MariaDB / MySQL local
        user='root',
        password='',
        database='bodega_electricidad_prestamos',
        cursorclass=pymysql.cursors.DictCursor
    )

# =============================================================
# 1. RUTAS DE NAVEGACIÓN Y PLANTILLAS
# =============================================================

@app.route('/')
def inicio():
    if 'rol' not in session:
        return redirect('/login')
    if session['rol'] == 'encargado':
        return redirect('/encargado')
    return render_template('index.html')

@app.route('/login')
@app.route('/login.html')
def vista_login():
    return render_template('login.html')

@app.route('/encargado')
@app.route('/encargado.html')
def vista_encargado():
    if 'rol' not in session or session['rol'] != 'encargado':
        return redirect('/login')
    return render_template('encargado.html')

# =============================================================
# 2. AUTENTICACIÓN, REGISTRO Y SESIONES
# =============================================================

@app.route('/api/session', methods=['GET'])
def obtener_sesion():
    if 'rol' in session:
        return jsonify({
            'activa': True,
            'id': session.get('usuario_id'),
            'nombre': session.get('nombre'),
            'rol': session.get('rol')
        })
    return jsonify({'activa': False})

@app.route('/api/login', methods=['POST'])
def login():
    datos = request.get_json() or {}
    usuario = datos.get('usuario', '').strip()
    password = datos.get('password', '').strip()

    if usuario == 'admin' and password == 'admin123':
        session['usuario_id'] = 0
        session['nombre'] = 'Encargado Bodega'
        session['rol'] = 'encargado'
        return jsonify({'status': 'ok', 'rol': 'encargado', 'redirect': '/encargado'})

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "SELECT id_profesor, nombre, apellido FROM profesores WHERE (email = %s OR rut = %s) AND password = %s"
            cursor.execute(sql, (usuario, usuario, password))
            profesor = cursor.fetchone()
        conexion.close()

        if profesor:
            session['usuario_id'] = profesor['id_profesor']
            session['nombre'] = f"{profesor['nombre']} {profesor['apellido']}".strip()
            session['rol'] = 'profesor'
            return jsonify({'status': 'ok', 'rol': 'profesor', 'redirect': '/'})

        return jsonify({'status': 'error', 'message': 'Usuario o contraseña incorrectos'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error de BD: {str(e)}'}), 500

@app.route('/api/profesores/registro', methods=['POST'])
def registrar_profesor():
    datos = request.get_json() or {}
    rut = datos.get('rut', '').strip()
    nombre = datos.get('nombre', '').strip()
    apellido = datos.get('apellido', '').strip()
    email = datos.get('email', '').strip()
    password = datos.get('password', '').strip()

    if not (rut and nombre and email and password):
        return jsonify({'status': 'error', 'message': 'Todos los campos obligatorios deben estar completos.'}), 400

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_profesor FROM profesores WHERE email = %s OR rut = %s", (email, rut))
            if cursor.fetchone():
                conexion.close()
                return jsonify({'status': 'error', 'message': 'El RUT o Correo ya se encuentra registrado.'}), 400

            sql = "INSERT INTO profesores (rut, nombre, apellido, email, password) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (rut, nombre, apellido, email, password))
            conexion.commit()
        conexion.close()
        return jsonify({'status': 'ok', 'message': 'Profesor registrado con éxito. Ya puedes iniciar sesión.'})
    except Exception as e:
        print("Error en registro:", str(e))
        return jsonify({'status': 'error', 'message': f'Error de BD: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'ok', 'redirect': '/login'})

# =============================================================
# 3. CHAT Y MENSAJES MULTI-PROFESOR
# =============================================================

@app.route('/api/profesores', methods=['GET'])
def obtener_profesores():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_profesor, nombre, apellido, email FROM profesores")
            profesores = cursor.fetchall()
        conexion.close()
        return jsonify(profesores)
    except Exception as e:
        return jsonify([])

@app.route('/api/mensajes', methods=['GET', 'POST'])
def gestionar_mensajes():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            if request.method == 'POST':
                datos = request.get_json() or {}
                mensaje = datos.get('mensaje', '').strip()
                remitente = datos.get('remitente', '').strip()
                id_profesor = datos.get('id_profesor')

                if not id_profesor and session.get('rol') == 'profesor':
                    id_profesor = session.get('usuario_id')
                    remitente = 'Profesor'

                if not id_profesor or not mensaje:
                    conexion.close()
                    return jsonify({'status': 'error', 'message': 'Faltan datos obligatorios'}), 400

                sql = "INSERT INTO mensajes (id_profesor, remitente, mensaje) VALUES (%s, %s, %s)"
                cursor.execute(sql, (int(id_profesor), str(remitente), str(mensaje)))
                conexion.commit()
                conexion.close()
                return jsonify({'status': 'ok', 'message': 'Mensaje guardado.'})

            else:
                id_profesor = request.args.get('id_profesor')
                if not id_profesor and session.get('rol') == 'profesor':
                    id_profesor = session.get('usuario_id')

                if not id_profesor or id_profesor in ['null', 'undefined', '']:
                    conexion.close()
                    return jsonify([])

                sql = """
                    SELECT id_mensaje, id_profesor, remitente, mensaje, 
                           DATE_FORMAT(fecha, '%%H:%%i') as fecha 
                    FROM mensajes 
                    WHERE id_profesor = %s 
                    ORDER BY id_mensaje ASC
                """
                cursor.execute(sql, (int(id_profesor),))
                mensajes = cursor.fetchall()
                conexion.close()
                return jsonify(mensajes)
    except Exception as e:
        print("Error en /api/mensajes:", str(e))
        return jsonify([])

# =============================================================
# 4. BUSCADOR, SOLICITUDES, HISTORIAL Y CRUD
# =============================================================

@app.route('/api/sugerencias', methods=['GET'])
def buscar_sugerencias():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    a.id_articulo, 
                    a.sku, 
                    a.nombre, 
                    IFNULL(SUM(i.cantidad_total - i.cantidad_prestada), 0) AS stock
                FROM articulos a
                LEFT JOIN inventario_stock i ON a.id_articulo = i.id_articulo
                WHERE LOWER(a.nombre) LIKE LOWER(%s) OR LOWER(a.sku) LIKE LOWER(%s)
                GROUP BY a.id_articulo, a.sku, a.nombre
                LIMIT 10
            """
            patron = f"%{q}%"
            cursor.execute(sql, (patron, patron))
            articulos = cursor.fetchall()
        conexion.close()
        return jsonify(articulos)
    except Exception as e:
        print("Error en /api/sugerencias:", str(e))
        return jsonify([])

@app.route('/api/solicitudes', methods=['GET', 'POST'])
def gestionar_solicitudes():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            if request.method == 'POST':
                datos = request.get_json() or {}
                id_profesor = session.get('usuario_id') or datos.get('id_profesor')
                items = datos.get('items', [])

                if not items:
                    conexion.close()
                    return jsonify({'status': 'error', 'message': 'Selecciona materiales válidos.'}), 400

                # CORRECCIÓN: Guardar el id_profesor al crear el préstamo
                cursor.execute("INSERT INTO prestamos (id_profesor, estado) VALUES (%s, 'Pendiente')", (id_profesor,))
                id_prestamo = cursor.lastrowid

                for item in items:
                    cursor.execute(
                        "INSERT INTO detalle_prestamos (id_prestamo, id_articulo, cantidad) VALUES (%s, %s, %s)",
                        (id_prestamo, item['id_articulo'], item.get('cantidad', 1))
                    )

                conexion.commit()
                conexion.close()
                return jsonify({'status': 'ok', 'message': 'Solicitud enviada exitosamente.'})

            else:
                sql = """
                    SELECT p.id_prestamo as id, 
                           DATE_FORMAT(p.fecha_solicitud, '%%Y-%%m-%%d %%H:%%i') as fecha,
                           a.sku, a.nombre, dp.cantidad
                    FROM prestamos p
                    INNER JOIN detalle_prestamos dp ON p.id_prestamo = dp.id_prestamo
                    INNER JOIN articulos a ON dp.id_articulo = a.id_articulo
                    WHERE p.estado = 'Pendiente'
                    ORDER BY p.fecha_solicitud DESC
                """
                cursor.execute(sql)
                filas = cursor.fetchall()

                solicitudes_dict = {}
                for f in filas:
                    id_sol = f['id']
                    if id_sol not in solicitudes_dict:
                        solicitudes_dict[id_sol] = {'id': id_sol, 'fecha': f['fecha'], 'materiales': []}
                    solicitudes_dict[id_sol]['materiales'].append({
                        'sku': f['sku'],
                        'nombre': f['nombre'],
                        'cantidad': f['cantidad']
                    })

                resultado = list(solicitudes_dict.values())
                conexion.close()
                return jsonify(resultado)
    except Exception as e:
        print("Error en /api/solicitudes:", str(e))
        return jsonify([])

@app.route('/api/pedidos/<accion>/<int:id_prestamo>', methods=['POST'])
def cambiar_estado_pedido(accion, id_prestamo):
    estados = {'aprobar': 'Aprobado', 'entregar': 'Entregado'}
    nuevo_estado = estados.get(accion)
    if not nuevo_estado:
        return jsonify({'status': 'error', 'message': 'Acción inválida'}), 400

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "UPDATE prestamos SET estado = %s WHERE id_prestamo = %s"
            cursor.execute(sql, (nuevo_estado, id_prestamo))
            conexion.commit()
        conexion.close()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/pedidos/rechazar/<int:id_prestamo>', methods=['POST'])
def rechazar_pedido(id_prestamo):
    datos = request.get_json() or {}
    motivo = datos.get('motivo', '').strip()

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "UPDATE prestamos SET estado = 'Rechazado', motivo_rechazo = %s WHERE id_prestamo = %s"
            cursor.execute(sql, (motivo, id_prestamo))
            conexion.commit()
        conexion.close()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/pedidos/historial', methods=['GET'])
def obtener_historial_pedidos():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    p.id_prestamo,
                    DATE_FORMAT(p.fecha_solicitud, '%%Y-%%m-%%d %%H:%%i') as fecha_solicitud,
                    p.estado,
                    IFNULL(p.motivo_rechazo, '-') as motivo_rechazo,
                    GROUP_CONCAT(CONCAT('[', a.sku, '] ', a.nombre, ' (x', dp.cantidad, ')') SEPARATOR ', ') as detalles
                FROM prestamos p
                INNER JOIN detalle_prestamos dp ON p.id_prestamo = dp.id_prestamo
                INNER JOIN articulos a ON dp.id_articulo = a.id_articulo
                GROUP BY p.id_prestamo
                ORDER BY p.fecha_solicitud DESC
            """
            cursor.execute(sql)
            historial = cursor.fetchall()
        conexion.close()
        return jsonify(historial)
    except Exception as e:
        print("Error en /api/pedidos/historial:", str(e))
        return jsonify([])

@app.route('/api/articulos', methods=['GET', 'POST', 'DELETE'])
def gestionar_articulos():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            if request.method == 'GET':
                sql = """
                    SELECT 
                        a.id_articulo, 
                        a.sku, 
                        a.nombre, 
                        IFNULL(SUM(i.cantidad_total - i.cantidad_prestada), 0) AS stock
                    FROM articulos a
                    LEFT JOIN inventario_stock i ON a.id_articulo = i.id_articulo
                    GROUP BY a.id_articulo, a.sku, a.nombre
                """
                cursor.execute(sql)
                articulos = cursor.fetchall()
                conexion.close()
                return jsonify(articulos)

            elif request.method == 'POST':
                datos = request.get_json() or {}
                sku = datos.get('sku')
                nombre = datos.get('nombre')
                stock = int(datos.get('stock', 0))
                
                sql_art = "INSERT INTO articulos (sku, nombre) VALUES (%s, %s)"
                cursor.execute(sql_art, (sku, nombre))
                id_nuevo_art = cursor.lastrowid

                sql_stock = "INSERT INTO inventario_stock (id_articulo, id_ubicacion, cantidad_total) VALUES (%s, 1, %s)"
                cursor.execute(sql_stock, (id_nuevo_art, stock))

                conexion.commit()
                conexion.close()
                return jsonify({'status': 'ok'})

            elif request.method == 'DELETE':
                id_art = request.args.get('id')
                cursor.execute("DELETE FROM inventario_stock WHERE id_articulo = %s", (id_art,))
                cursor.execute("DELETE FROM articulos WHERE id_articulo = %s", (id_art,))
                conexion.commit()
                conexion.close()
                return jsonify({'status': 'ok'})
    except Exception as e:
        print("Error en /api/articulos:", str(e))
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, port=5000)