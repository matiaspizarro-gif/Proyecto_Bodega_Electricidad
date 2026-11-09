# Casos de Prueba

Todos los datos son **ficticios** (provienen de `db/schema.sql`). Antes de probar, deja la BD en su estado inicial: `docker compose down -v && docker compose up --build`.

Las columnas **Resultado obtenido** y **Estado** se completan al ejecutar cada prueba (✅ Pasa / ❌ Falla). Las pruebas marcadas con ⚠️ verifican una limitación conocida: hoy **deberían fallar**, y sirven para demostrar el defecto y comprobar su corrección.

| ID | CU | Descripción | Datos de entrada | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|
| CP-01 | CU-01 | Registro válido | RUT `33333333-3`, Carla Ficticia, `carla.ficticia@ejemplo.cl`, clave `Prueba123` | Mensaje "Profesor registrado con éxito" y vuelve a la pestaña de inicio de sesión | | |
| CP-02 | CU-01 | Registro con RUT duplicado | RUT `11111111-1`, otro correo | "El RUT o Correo ya se encuentra registrado." | | |
| CP-03 | CU-01 | Registro con correo duplicado | Otro RUT, `ana.prueba@ejemplo.cl` | Mismo mensaje que CP-02 | | |
| CP-04 | CU-02 | Login de profesor con correo | `ana.prueba@ejemplo.cl` / `Prueba123` | Redirige a `/` y muestra "Profesor: Ana Prueba" | | |
| CP-05 | CU-02 | Login de profesor con RUT | `22222222-2` / `Prueba123` | Redirige a `/` | | |
| CP-06 | CU-02 | Login con clave incorrecta | `ana.prueba@ejemplo.cl` / `xxx` | "Usuario o contraseña incorrectos" | | |
| CP-07 | CU-02 | Login de encargado | `admin` / `admin123` | Redirige a `/encargado` | | |
| CP-08 | CU-03 | Cerrar sesión | Profesor logueado → "Cerrar Sesión" → abrir `/` | Redirige a `/login` | | |
| CP-09 | CU-02 | Acceso sin sesión | Abrir `/encargado` en una ventana privada | Redirige a `/login` | | |
| CP-10 | CU-02 | Profesor intenta entrar al panel del encargado | Logueado como Ana, abrir `/encargado` | Redirige a `/login` | | |
| CP-11 | CU-04 | Búsqueda por nombre | Escribir `multi` | Aparece "[ART-0001] Multímetro digital (Stock: 12)" (10−2 en bodega principal + 4 en San Fernando) | | |
| CP-12 | CU-04 | Búsqueda por SKU | Escribir `art-0003` | Aparece "Interruptor termomagnético 16A" | | |
| CP-13 | CU-04 | Búsqueda de 1 carácter | Escribir `m` | No aparece la lista | | |
| CP-14 | CU-04 | Búsqueda sin resultados | Escribir `zzzz` | "Sin resultados" | | |
| CP-15 | CU-05 | Agregar el mismo artículo dos veces | Agregar ART-0001 dos veces | Alerta "Este artículo ya está en tu lista." | | |
| CP-16 | CU-05 | Enviar solicitud vacía | Presionar "Enviar Solicitud" sin artículos | Alerta "Selecciona al menos un artículo antes de enviar." | | |
| CP-17 | CU-05 | Enviar solicitud válida | ART-0001 y ART-0004 | "¡Solicitud enviada con éxito!" y aparece en Pendientes del encargado con los 2 artículos | | |
| CP-18 ⚠️ | CU-05 | La solicitud identifica al profesor | Enviar solicitud como Ana y revisarla como encargado | El encargado ve que la solicitó Ana Prueba | | |
| CP-19 ⚠️ | CU-05 | Elegir la cantidad | Intentar pedir 3 unidades de ART-0005 | Se puede indicar la cantidad 3 | | |
| CP-20 | CU-07 | Pendientes vacío | BD recién creada | "No hay solicitudes pendientes en este momento." | | |
| CP-21 ⚠️ | CU-07 | Orden de llegada (FIFO) | Enviar las solicitudes A y luego B | A aparece antes que B | | |
| CP-22 | CU-08 | Aprobar solicitud | "Aprobar" en la solicitud de CP-17 | Desaparece de Pendientes; en Historial aparece "Aprobado" | | |
| CP-23 ⚠️ | CU-08 | Entregar una solicitud ya aprobada | Buscar la solicitud de CP-22 para marcarla como entregada | Existe una forma de pasarla a "Entregado" | | |
| CP-24 ⚠️ | CU-08 | Entregar descuenta stock | Marcar como entregada una solicitud con ART-0002 y buscar `cable` | El stock baja de 25 a 24 | | |
| CP-25 | CU-09 | Rechazar con motivo | "Rechazar" con el motivo `Sin stock para esa fecha` | Historial: "Rechazado" con ese motivo | | |
| CP-26 | CU-09 | Cancelar el rechazo | "Rechazar" → Cancelar | La solicitud sigue en Pendientes | | |
| CP-27 | CU-10 | Historial | Después de CP-22 y CP-25 | Se ven ambas solicitudes con su estado y sus artículos | | |
| CP-28 | CU-11 | Agregar artículo | SKU `ART-0006`, nombre `Tester de voltaje`, stock 8 | Aparece en la tabla con stock 8 y se puede encontrar en el buscador del profesor | | |
| CP-29 | CU-11 | Agregar sin nombre | Solo el SKU `ART-0007` | Alerta "Completa al menos el SKU y el Nombre." | | |
| CP-30 ⚠️ | CU-11 | Agregar con SKU duplicado | SKU `ART-0001` | Se muestra un error y no se crea un duplicado | | |
| CP-31 | CU-11 | Eliminar artículo sin uso | Eliminar ART-0006 | Desaparece de la tabla | | |
| CP-32 ⚠️ | CU-11 | Eliminar artículo usado en una solicitud | Eliminar ART-0001 después de CP-17 | Mensaje claro de que no se puede eliminar | | |
| CP-33 | CU-06 | Profesor envía mensaje | Ana escribe `¿Hay multímetros disponibles?` | Aparece en su chat y en el chat del encargado con Ana | | |
| CP-34 | CU-06 | Encargado responde | Seleccionar a Ana y escribir `Sí, quedan varios.` | Ana lo ve en menos de 3 segundos, sin recargar | | |
| CP-35 | CU-06 | Chats separados | Bruno inicia sesión | Bruno no ve los mensajes de Ana | | |
| CP-36 | CU-06 | Encargado sin profesor seleccionado | Escribir un mensaje sin elegir profesor | Alerta "Selecciona un profesor antes de enviar un mensaje." | | |

## Pruebas de seguridad

Detalle y corrección en `06-checklist-seguridad.md`.

| ID | Descripción | Pasos | Resultado esperado (seguro) | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| CPS-01 ⚠️ | API sin sesión | Sin iniciar sesión: `curl -X DELETE "http://127.0.0.1:5000/api/articulos?id=5"` | 401/403 y el artículo **no** se borra | | |
| CPS-02 ⚠️ | Profesor usa acciones del encargado | Logueado como Ana, en la consola del navegador: `fetch('/api/pedidos/aprobar/1',{method:'POST'})` | 403 | | |
| CPS-03 ⚠️ | Leer el chat de otro profesor | Logueado como Bruno, abrir `/api/mensajes?id_profesor=1` | 403 o solo los mensajes propios | | |
| CPS-04 ⚠️ | Suplantar al encargado | Logueado como Ana: `fetch('/api/mensajes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id_profesor:1,remitente:'Encargado',mensaje:'Hola'})})` | El remitente queda como "Profesor" | | |
| CPS-05 ⚠️ | XSS en el chat | Ana envía `<img src=x onerror=alert('XSS')>` | Se muestra como texto; no aparece ninguna alerta | | |
| CPS-06 | Inyección SQL en login | Usuario `' OR '1'='1`, cualquier clave | "Usuario o contraseña incorrectos" | | |
| CPS-07 | Inyección SQL en buscador | Escribir `%' OR 1=1 -- ` | No devuelve todo el inventario ni muestra error SQL | | |
| CPS-08 ⚠️ | Contraseñas en texto plano | Revisar la tabla `profesores` en phpMyAdmin | Las contraseñas aparecen como hash, no como texto legible | | |
