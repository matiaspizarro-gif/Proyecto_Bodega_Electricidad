# Checklist de Seguridad

Revisión del código actual (`server.py`, `templates/`, `static/app.js`). Estado: ✅ Cumple · ⚠️ Parcial · ❌ No cumple.

## 1. Configuración y secretos

| # | Control | Estado | Evidencia / Acción |
|---|---|---|---|
| 1.1 | Credenciales de BD fuera del código | ✅ | Se leen de variables de entorno (`.env`). Los valores por defecto de `server.py` son solo para desarrollo local. |
| 1.2 | `.env` fuera del repositorio | ✅ | Está en `.gitignore` y `.dockerignore`. Solo se sube `.env.example`, sin valores reales. |
| 1.3 | `SECRET_KEY` de Flask segura | ⚠️ | Se lee de `SECRET_KEY`, pero si no se define usa un valor fijo. **Acción:** generar una con `secrets.token_hex(32)` en `.env`. |
| 1.4 | Modo debug apagado | ✅ | `FLASK_DEBUG=0` por defecto. El debugger de Werkzeug permite ejecutar código si queda activo. |
| 1.5 | No usar `root` para la aplicación | ❌ | La app se conecta como `root`. **Acción:** crear un usuario MySQL con permisos solo sobre `bodega_electricidad_prestamos`. |
| 1.6 | Datos de prueba ficticios | ✅ | `db/schema.sql` usa RUT, nombres y correos inventados. |

## 2. Autenticación

| # | Control | Estado | Evidencia / Acción |
|---|---|---|---|
| 2.1 | Contraseñas con hash | ❌ | `profesores.password` se guarda y compara en texto plano. **Acción:** usar `werkzeug.security.generate_password_hash` / `check_password_hash` (Werkzeug ya está instalado). |
| 2.2 | Sin credenciales fijas en el código | ❌ | El encargado es `admin` / `admin123` dentro de `server.py`. **Acción:** guardarlo en la BD con hash, o como mínimo leerlo desde `.env`. |
| 2.3 | Política mínima de contraseña | ❌ | Se acepta cualquier clave. **Acción:** exigir un largo mínimo (por ejemplo, 8 caracteres) en el registro. |
| 2.4 | Límite de intentos de login | ❌ | No existe. **Acción:** bloqueo temporal después de N intentos fallidos. |
| 2.5 | Mensaje de error genérico | ✅ | "Usuario o contraseña incorrectos" no revela cuál de los dos falló. |
| 2.6 | Cierre de sesión | ✅ | `/api/logout` borra la sesión. |
| 2.7 | Validar RUT y dominio del correo | ❌ | No se valida el dígito verificador del RUT ni el dominio institucional del correo. Cualquier persona puede crear una cuenta de profesor. |

## 3. Autorización (control de acceso)

| # | Control | Estado | Evidencia / Acción |
|---|---|---|---|
| 3.1 | Páginas protegidas por rol | ✅ | `/` y `/encargado` revisan `session['rol']`. |
| 3.2 | API protegida por sesión | ❌ | Las rutas `/api/*` **no revisan la sesión**. Sin iniciar sesión se puede borrar artículos, aprobar o rechazar pedidos y listar profesores con sus correos (probado: `DELETE /api/articulos` sin sesión llega a la BD). **Acción:** decorador `@requiere_rol('encargado')` en las rutas de administración. |
| 3.3 | El profesor solo ve sus mensajes | ❌ | `GET /api/mensajes?id_profesor=X` devuelve el chat de cualquier profesor (IDOR). **Acción:** si el rol es profesor, ignorar el parámetro y usar `session['usuario_id']`. |
| 3.4 | El remitente lo define el servidor | ❌ | `remitente` e `id_profesor` vienen del navegador, por lo que un profesor puede escribir como "Encargado" o en el chat de otro. **Acción:** asignarlos según `session['rol']`. |
| 3.5 | La solicitud toma el profesor de la sesión | ⚠️ | Se usa `session.get('usuario_id') or datos.get('id_profesor')`, pero el valor no se guarda (no existe la columna). |

## 4. Validación de entradas y salidas

| # | Control | Estado | Evidencia / Acción |
|---|---|---|---|
| 4.1 | Consultas SQL parametrizadas | ✅ | Todas las consultas usan `%s` con parámetros, lo que previene inyección SQL. |
| 4.2 | Protección contra XSS | ❌ | `app.js` y `encargado.html` insertan mensajes, nombres y motivos con `innerHTML`. Un mensaje con `<img src=x onerror=...>` se ejecuta en el navegador del encargado (XSS almacenado). **Acción:** usar `textContent` o una función `escapeHtml()` antes de insertar texto. |
| 4.3 | Validar tipos y rangos | ❌ | No se valida que `cantidad` sea mayor que 0 ni que `stock` sea un número. `int('abc')` produce un error no controlado. |
| 4.4 | Largo máximo de campos | ⚠️ | Lo limita la BD (VARCHAR), pero no el servidor. |

## 5. Protección de sesión y transporte

| # | Control | Estado | Evidencia / Acción |
|---|---|---|---|
| 5.1 | Protección CSRF | ❌ | Las acciones POST/DELETE no usan token CSRF. **Acción:** `SESSION_COOKIE_SAMESITE='Lax'` como mínimo, o Flask-WTF/CSRF. |
| 5.2 | Cookie `HttpOnly` | ✅ | Flask la activa por defecto. |
| 5.3 | HTTPS | ❌ | Se sirve por HTTP en el puerto 5000. **Acción:** en producción, poner un proxy inverso (Nginx) con TLS y `SESSION_COOKIE_SECURE=True`. |
| 5.4 | Servidor de producción | ❌ | Se usa el servidor de desarrollo de Flask. **Acción:** usar `gunicorn` en el Dockerfile. |

## 6. Manejo de errores y registros

| # | Control | Estado | Evidencia / Acción |
|---|---|---|---|
| 6.1 | No exponer errores internos | ❌ | `/api/login` y `/api/profesores/registro` devuelven `Error de BD: <detalle>` al navegador. **Acción:** registrar el detalle en el log y responder un mensaje genérico. |
| 6.2 | Errores con el código HTTP correcto | ⚠️ | Varias rutas responden `[]` con estado 200 cuando falla la BD, por lo que la interfaz no muestra el error. |
| 6.3 | Registro de acciones administrativas | ❌ | No se registra quién aprobó, rechazó o eliminó algo. |

## 7. Infraestructura

| # | Control | Estado | Evidencia / Acción |
|---|---|---|---|
| 7.1 | Imagen base mínima | ✅ | `python:3.10-slim`. |
| 7.2 | Contenedor sin root | ❌ | El Dockerfile no define `USER`. **Acción:** `RUN useradd -m app` y `USER app`. |
| 7.3 | Puerto de MySQL expuesto | ⚠️ | `3307` queda abierto en el anfitrión. En producción, quitar `ports` del servicio `db`. |
| 7.4 | Dependencias con versión fija | ✅ | `requirements.txt` fija todas las versiones. |
| 7.5 | Código obsoleto separado | ✅ | Los PHP (con `Access-Control-Allow-Origin: *`) y `db.py` se movieron a `legacy/`; no se despliegan (`.dockerignore`). |

## Prioridad sugerida

1. **3.2** Proteger la API por rol (hoy cualquiera puede borrar el inventario).
2. **4.2** Escapar el HTML (XSS en el chat).
3. **2.1 y 2.2** Usar hash en las contraseñas y quitar `admin123` del código.
4. **3.3 y 3.4** Asignar el remitente y el profesor del chat desde la sesión.
5. **6.1** No exponer los errores de la BD.
