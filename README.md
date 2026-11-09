# Sistema de Gestión de Préstamos - Bodega de Electricidad

Sistema web desarrollado en Flask y MySQL para la gestión de inventario, solicitudes de materiales y comunicación directa entre docentes y el encargado de pañol/bodega del área de electricidad.

## Requisitos del Sistema
- Python 3.8+
- MySQL Server / MariaDB (vía XAMPP o standalone en el puerto `3307`)
- Git

## Estructura del Proyecto

```text
Proyecto_Bodega_Electricidad/
├── README.md
├── .env.example
├── .gitignore
├── server.py
├── db.py
├── static/
│   ├── app.js
│   └── styles.css
├── templates/
│   ├── login.html
│   ├── index.html
│   └── encargado.html
└── docs/
    ├── 01-diagrama-ER.png
    ├── 02-casos-de-uso.png
    ├── 03-arquitectura-y-despliegue.png
    ├── 04-casos-de-uso-descritos.md
    ├── 05-casos-de-prueba.md
    └── 06-checklist-seguridad.md

    Instalación y Configuración Local
Clonar el repositorio:

Bash
git clone [https://github.com/matiaspizarro-gif/Proyecto_Bodega_Electricidad.git](https://github.com/matiaspizarro-gif/Proyecto_Bodega_Electricidad.git)
cd Proyecto_Bodega_Electricidad
Instalar dependencias:

Bash
pip install flask pymysql mysql-connector-python
Configurar base de datos:

Importar el archivo SQL de la base de datos bodega_electricidad_prestamos en MySQL (Puerto 3307).

Variables de entorno:

Crear un archivo .env tomando como referencia .env.example.

Ejecutar el servidor:

Bash
python server.py
Acceder desde el navegador a http://localhost:5000.

Funcionalidades Principales
Autenticación y Registro: Inicio de sesión para encargado (admin) y registro/login para profesores con RUT y contraseña.

Solicitud de Materiales: Buscador dinámico de artículos con stock disponible en tiempo real.

Gestión FIFO de Pedidos: Panel para el encargado de bodega con opciones de aprobar, entregar o rechazar solicitudes.

Chat Multiprofesor: Canal de mensajería interna entre los docentes y la bodega.

Control de Inventario (CRUD): Administración de artículos y stock.