# Casos de Uso Descritos

Actores:

- **Profesor:** docente que solicita materiales a la bodega.
- **Encargado de bodega:** administra las solicitudes y el inventario, y responde los mensajes.

Diagrama: `02-casos-de-uso.png`.

---

## CU-01 Registrarse

| Campo | Descripción |
|---|---|
| Actor | Profesor |
| Precondición | El profesor no tiene cuenta. |
| Flujo principal | 1. Abre `/login` y elige la pestaña "Crear Cuenta Profesor". 2. Ingresa RUT, nombre, apellido (opcional), correo y contraseña. 3. Presiona "Registrarse". 4. El sistema verifica que el RUT y el correo no existan. 5. Guarda el profesor y muestra "Profesor registrado con éxito". 6. Vuelve a la pestaña de inicio de sesión. |
| Flujos alternativos | 4a. El RUT o el correo ya existen: muestra "El RUT o Correo ya se encuentra registrado." 2a. Falta un campo obligatorio: el navegador no deja enviar (el servidor también responde 400). |
| Postcondición | Existe un nuevo registro en `profesores`. |

## CU-02 Iniciar sesión

| Campo | Descripción |
|---|---|
| Actores | Profesor, Encargado |
| Precondición | El usuario tiene credenciales. |
| Flujo principal | 1. Ingresa usuario (RUT, correo o `admin`) y contraseña. 2. El sistema valida las credenciales. 3. Crea la sesión con el rol y redirige: Profesor → `/`, Encargado → `/encargado`. |
| Flujo alternativo | 2a. Credenciales incorrectas: muestra "Usuario o contraseña incorrectos" (HTTP 401). |
| Postcondición | Sesión activa con `usuario_id`, `nombre` y `rol`. |

## CU-03 Cerrar sesión

| Campo | Descripción |
|---|---|
| Actores | Profesor, Encargado |
| Flujo principal | 1. Presiona "Cerrar Sesión". 2. El sistema borra la sesión. 3. Redirige a `/login`. |
| Postcondición | Las páginas protegidas vuelven a redirigir a `/login`. |

## CU-04 Buscar artículo

| Campo | Descripción |
|---|---|
| Actor | Profesor |
| Precondición | Sesión de profesor activa. |
| Flujo principal | 1. Escribe al menos 2 caracteres en "Buscar Artículo". 2. El sistema busca por nombre o SKU (sin distinguir mayúsculas) y muestra hasta 10 resultados con su stock disponible (`cantidad_total - cantidad_prestada`). |
| Flujos alternativos | 1a. Menos de 2 caracteres: la lista se oculta. 2a. Sin coincidencias: muestra "Sin resultados". |

## CU-05 Enviar solicitud de materiales

| Campo | Descripción |
|---|---|
| Actor | Profesor |
| Precondición | Sesión de profesor activa. |
| Flujo principal | 1. Busca artículos (**incluye CU-04**) y hace clic en cada uno para agregarlo a "Materiales Seleccionados". 2. Puede quitar artículos con "Quitar". 3. Presiona "Enviar Solicitud". 4. El sistema crea un `prestamo` en estado `Pendiente` y un `detalle_prestamos` por artículo. 5. Muestra "¡Solicitud enviada con éxito!" y vacía la lista. |
| Flujos alternativos | 1a. El artículo ya está en la lista: muestra "Este artículo ya está en tu lista." 3a. La lista está vacía: muestra "Selecciona al menos un artículo antes de enviar." |
| Postcondición | La solicitud aparece en "Solicitudes Pendientes" del encargado. |
| Limitaciones actuales | La cantidad siempre es 1. No se valida el stock. No se guarda el profesor que hizo la solicitud. |

## CU-06 Chatear

| Campo | Descripción |
|---|---|
| Actores | Profesor, Encargado |
| Precondición | Sesión activa. El encargado debe elegir un profesor en el selector. |
| Flujo principal | 1. Escribe el mensaje y presiona "Enviar" o Enter. 2. El sistema guarda el mensaje con el remitente y el profesor de la conversación. 3. Ambos chats se actualizan cada 3 segundos. |
| Flujos alternativos | 1a. Mensaje vacío: no se envía. 1b. El encargado no eligió profesor: muestra "Selecciona un profesor antes de enviar un mensaje." |

## CU-07 Revisar solicitudes pendientes

| Campo | Descripción |
|---|---|
| Actor | Encargado |
| Precondición | Sesión de encargado activa. |
| Flujo principal | 1. Abre la pestaña "Solicitudes Pendientes" (o presiona "Actualizar Lista"). 2. El sistema muestra cada solicitud `Pendiente` con número, fecha y artículos (SKU, nombre, cantidad). |
| Flujo alternativo | 2a. No hay pendientes: muestra "No hay solicitudes pendientes en este momento." |
| Extensión | Desde aquí puede rechazar (**CU-09 extiende CU-07**). |

## CU-08 Aprobar / marcar entregada

| Campo | Descripción |
|---|---|
| Actor | Encargado |
| Precondición | Hay una solicitud en estado `Pendiente`. |
| Flujo principal | 1. Presiona "Aprobar" o "Marcar Entregado". 2. El sistema cambia el estado a `Aprobado` o `Entregado`. 3. La solicitud deja de aparecer en Pendientes. |
| Limitación actual | Una solicitud `Aprobado` ya no aparece en ninguna lista con botones, así que no se puede pasar a `Entregado`. Entregar no descuenta stock. |

## CU-09 Rechazar solicitud con motivo

| Campo | Descripción |
|---|---|
| Actor | Encargado |
| Precondición | Hay una solicitud `Pendiente`. |
| Flujo principal | 1. Presiona "Rechazar". 2. Escribe el motivo en el cuadro de diálogo. 3. El sistema cambia el estado a `Rechazado` y guarda `motivo_rechazo`. |
| Flujo alternativo | 2a. Cancela o deja el motivo vacío: no se hace nada. |

## CU-10 Consultar historial

| Campo | Descripción |
|---|---|
| Actor | Encargado |
| Flujo principal | 1. Abre "Historial de Pedidos". 2. El sistema muestra todas las solicitudes (número, fecha, estado, artículos y motivo de rechazo), de la más nueva a la más antigua. |

## CU-11 Gestionar inventario

| Campo | Descripción |
|---|---|
| Actor | Encargado |
| Precondición | Sesión de encargado activa. |
| Flujo principal (listar) | 1. Abre "CRUD Inventario". 2. El sistema lista los artículos con su stock total. |
| Flujo principal (agregar) | 1. Ingresa SKU, nombre y stock inicial. 2. Presiona "Guardar Artículo". 3. El sistema crea el artículo y su stock en la ubicación 1 (Bodega principal). |
| Flujo principal (eliminar) | 1. Presiona "Eliminar" y confirma. 2. El sistema borra el stock y el artículo. |
| Flujos alternativos | Agregar sin SKU o nombre: muestra "Completa al menos el SKU y el Nombre." Eliminar un artículo que ya está en una solicitud: la BD lo impide por la llave foránea y la interfaz no muestra el error. |
| Limitación actual | No existe la opción de editar un artículo (la "U" del CRUD). |
