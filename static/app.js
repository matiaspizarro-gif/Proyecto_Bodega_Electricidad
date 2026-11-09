document.addEventListener('DOMContentLoaded', async () => {
    // Referencias al DOM
    const inputBusqueda = document.getElementById('inputBusqueda');
    const listaSugerencias = document.getElementById('listaSugerencias');
    const listaSeleccionados = document.getElementById('listaSeleccionados');
    const btnEnviar = document.getElementById('btnEnviar');
    const infoProfesor = document.getElementById('infoProfesor');

    // Elementos del Chat
    const profChatBox = document.getElementById('profChatBox');
    const profMsgInput = document.getElementById('profMsgInput');
    const btnEnviarMsgProf = document.getElementById('btnEnviarMsgProf');

    let materialesSeleccionados = [];
    let usuarioSesion = null;

    // =============================================================
    // 1. VALIDAR SESIÓN DE USUARIO
    // =============================================================
    try {
        const res = await fetch('/api/session');
        const sesion = await res.json();

        if (sesion.activa && sesion.rol === 'profesor') {
            usuarioSesion = sesion;
            if (infoProfesor) {
                infoProfesor.innerHTML = `<strong>Profesor:</strong> ${sesion.nombre}`;
            }
            cargarMensajesProfesor();
            setInterval(cargarMensajesProfesor, 3000);
        } else {
            window.location.href = '/login';
            return;
        }
    } catch (e) {
        console.error("Error al validar la sesión:", e);
        window.location.href = '/login';
        return;
    }

    // =============================================================
    // 2. BUSCADOR DE ARTÍCULOS EN TIEMPO REAL (AUTO-COMPLETADO)
    // =============================================================
    if (inputBusqueda && listaSugerencias) {
        inputBusqueda.addEventListener('input', async (e) => {
            const texto = e.target.value.trim();

            // Ocultar la lista si hay menos de 2 caracteres
            if (texto.length < 2) {
                listaSugerencias.innerHTML = '';
                listaSugerencias.style.display = 'none';
                return;
            }

            try {
                // Petición al endpoint /api/sugerencias de server.py
                const res = await fetch(`/api/sugerencias?q=${encodeURIComponent(texto)}`);
                const datos = await res.json();

                listaSugerencias.innerHTML = '';

                if (!datos || datos.length === 0) {
                    listaSugerencias.innerHTML = '<div style="padding: 10px; color: #777; background: #fff;">Sin resultados</div>';
                    listaSugerencias.style.display = 'block';
                    return;
                }

                // Renderizar cada artículo encontrado en la BD
                datos.forEach(item => {
                    const div = document.createElement('div');
                    div.style.cssText = 'padding: 10px; cursor: pointer; border-bottom: 1px solid #eee; background: #fff; color: #333;';
                    
                    const stock = item.stock !== undefined ? item.stock : '0';
                    div.innerHTML = `<strong>[${item.sku}]</strong> ${item.nombre} <small style="color: #666;">(Stock: ${stock})</small>`;

                    div.onmouseover = () => div.style.background = '#f0f0f0';
                    div.onmouseout = () => div.style.background = '#fff';

                    // Seleccionar un artículo al hacer clic
                    div.addEventListener('click', () => {
                        const yaExiste = materialesSeleccionados.some(m => m.id_articulo === item.id_articulo);
                        if (!yaExiste) {
                            materialesSeleccionados.push({
                                id_articulo: item.id_articulo,
                                sku: item.sku,
                                nombre: item.nombre,
                                cantidad: 1
                            });
                            actualizarLista();
                        } else {
                            alert("Este artículo ya está en tu lista.");
                        }
                        
                        inputBusqueda.value = '';
                        listaSugerencias.innerHTML = '';
                        listaSugerencias.style.display = 'none';
                    });

                    listaSugerencias.appendChild(div);
                });

                listaSugerencias.style.display = 'block';

            } catch (err) {
                console.error("Error al obtener sugerencias:", err);
            }
        });

        // Ocultar la caja de sugerencias si el usuario hace clic fuera de ella
        document.addEventListener('click', (e) => {
            if (!inputBusqueda.contains(e.target) && !listaSugerencias.contains(e.target)) {
                listaSugerencias.innerHTML = '';
                listaSugerencias.style.display = 'none';
            }
        });
    }

    // =============================================================
    // 3. CARRITO DE SELECCIONADOS
    // =============================================================
    function actualizarLista() {
        if (!listaSeleccionados) return;
        listaSeleccionados.innerHTML = '';

        if (materialesSeleccionados.length === 0) {
            listaSeleccionados.innerHTML = '<li style="color: #888; padding: 5px;">No has agregado ningún material aún.</li>';
            return;
        }

        materialesSeleccionados.forEach((item, index) => {
            const li = document.createElement('li');
            li.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; background: #fff; padding: 8px; border: 1px solid #ddd; border-radius: 4px;';
            li.innerHTML = `
                <span><strong>[${item.sku}]</strong> ${item.nombre}</span>
                <button type="button" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer;" onclick="eliminarMaterial(${index})">Quitar</button>
            `;
            listaSeleccionados.appendChild(li);
        });
    }

    window.eliminarMaterial = function(index) {
        materialesSeleccionados.splice(index, 1);
        actualizarLista();
    };

    // =============================================================
    // 4. ENVÍO DE LA SOLICITUD
    // =============================================================
    if (btnEnviar) {
        btnEnviar.addEventListener('click', async (e) => {
            e.preventDefault();

            if (materialesSeleccionados.length === 0) {
                alert("Selecciona al menos un artículo antes de enviar.");
                return;
            }

            try {
                const res = await fetch('/api/solicitudes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        items: materialesSeleccionados,
                        id_profesor: usuarioSesion.id
                    })
                });

                const respuesta = await res.json();

                if (respuesta.status === 'ok') {
                    alert("¡Solicitud enviada con éxito!");
                    materialesSeleccionados = [];
                    actualizarLista();
                } else {
                    alert("Error: " + (respuesta.message || "No se pudo procesar."));
                }
            } catch (err) {
                console.error("Error al enviar solicitud:", err);
                alert("No se pudo conectar con el servidor.");
            }
        });
    }

    // =============================================================
    // 5. CHAT DEL PROFESOR
    // =============================================================
    async function cargarMensajesProfesor() {
        if (!profChatBox) return;

        try {
            const res = await fetch('/api/mensajes');
            const msgs = await res.json();
            
            if (!msgs || msgs.length === 0) {
                profChatBox.innerHTML = '<p style="color: #888; font-style: italic; text-align: center;">No tienes mensajes previos con el encargado.</p>';
                return;
            }

            const estaAlFinal = (profChatBox.scrollHeight - profChatBox.scrollTop) <= (profChatBox.clientHeight + 50);

            profChatBox.innerHTML = msgs.map(m => {
                const esProfesor = m.remitente === 'Profesor';
                const claseCss = esProfesor ? 'msg-profesor' : 'msg-encargado';
                return `
                    <div class="${claseCss}">
                        <div style="font-size: 11px; font-weight: bold; color: #555;">${m.remitente} • ${m.fecha}</div>
                        <div style="font-size: 14px; margin-top: 2px;">${m.mensaje}</div>
                    </div>
                `;
            }).join('');

            if (estaAlFinal) {
                profChatBox.scrollTop = profChatBox.scrollHeight;
            }
        } catch (err) {
            console.error("Error al cargar mensajes:", err);
        }
    }

    async function enviarMensajeProfesor() {
        if (!profMsgInput) return;
        const texto = profMsgInput.value.trim();

        if (!texto) return;

        try {
            const res = await fetch('/api/mensajes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mensaje: texto,
                    remitente: 'Profesor',
                    id_profesor: usuarioSesion.id
                })
            });

            const resp = await res.json();

            if (resp.status === 'ok') {
                profMsgInput.value = '';
                cargarMensajesProfesor();
            }
        } catch (err) {
            console.error("Error al enviar mensaje:", err);
        }
    }

    if (btnEnviarMsgProf) {
        btnEnviarMsgProf.addEventListener('click', enviarMensajeProfesor);
    }

    if (profMsgInput) {
        profMsgInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                enviarMensajeProfesor();
            }
        });
    }

    actualizarLista();
});