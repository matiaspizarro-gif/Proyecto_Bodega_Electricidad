"""Genera docs/02-casos-de-uso.png. Ejecutar: python3 casos_de_uso.py"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch

fig, ax = plt.subplots(figsize=(15, 10), dpi=120)
ax.set_xlim(0, 15); ax.set_ylim(0, 10); ax.axis("off")
AZUL = "#007bff"

def actor(x, y, nombre):
    ax.add_patch(plt.Circle((x, y + 0.75), 0.18, fill=False, lw=2))
    ax.plot([x, x], [y + 0.57, y], color="k", lw=2)
    ax.plot([x - 0.35, x + 0.35], [y + 0.38, y + 0.38], color="k", lw=2)
    ax.plot([x, x - 0.3], [y, y - 0.5], color="k", lw=2)
    ax.plot([x, x + 0.3], [y, y - 0.5], color="k", lw=2)
    ax.text(x, y - 0.8, nombre, ha="center", va="top", fontsize=13, weight="bold")

ax.text(7.5, 9.6, "Diagrama de Casos de Uso — Sistema de Solicitudes de Bodega de Electricidad",
        ha="center", fontsize=16, weight="bold")
ax.add_patch(FancyBboxPatch((2.3, 0.4), 10.4, 8.7, boxstyle="round,pad=0.05,rounding_size=0.3",
                            fill=False, ec=AZUL, lw=2))
ax.text(7.5, 8.8, "Sistema Pañol (Flask + MySQL)", ha="center", color=AZUL, fontsize=13, weight="bold")

W, H = 3.0, 0.85
cu = {
    # columna izquierda: solo Profesor
    "CU01": (4.0, 8.0, "CU-01 Registrarse"),
    "CU05": (4.0, 6.9, "CU-05 Enviar solicitud\nde materiales"),
    "CU04": (4.0, 5.8, "CU-04 Buscar artículo"),
    # columna central: ambos actores
    "CU02": (7.5, 5.0, "CU-02 Iniciar sesión"),
    "CU03": (7.5, 3.9, "CU-03 Cerrar sesión"),
    "CU06": (7.5, 2.8, "CU-06 Chatear\n(mensajes)"),
    # columna derecha: solo Encargado
    "CU07": (11.0, 8.0, "CU-07 Revisar solicitudes\npendientes"),
    "CU09": (11.0, 6.9, "CU-09 Rechazar con\nmotivo"),
    "CU08": (11.0, 5.8, "CU-08 Aprobar / marcar\nentregada"),
    "CU10": (11.0, 2.2, "CU-10 Consultar\nhistorial"),
    "CU11": (11.0, 1.1, "CU-11 Gestionar inventario\n(listar, agregar, eliminar)"),
}
for k, (x, y, t) in cu.items():
    ax.add_patch(Ellipse((x, y), W, H, fc="#eaf3ff", ec=AZUL, lw=1.5, zorder=2))
    ax.text(x, y, t, ha="center", va="center", fontsize=10.5, zorder=3)

PX, PY = 0.9, 4.0
EX, EY = 14.1, 4.0
actor(PX, PY, "Profesor")
actor(EX, EY, "Encargado\nde bodega")

def linea(a, b):
    ax.plot([a[0], b[0]], [a[1], b[1]], color="#555", lw=1.1, zorder=1)

for k in ["CU01", "CU02", "CU03", "CU04", "CU05", "CU06"]:
    x, y, _ = cu[k]
    linea((PX + 0.4, PY + 0.4), (x - W / 2 + 0.05, y))
for k in ["CU02", "CU03", "CU06", "CU07", "CU08", "CU09", "CU10", "CU11"]:
    x, y, _ = cu[k]
    linea((EX - 0.4, EY + 0.4), (x + W / 2 - 0.05, y))

def relacion(origen, destino, texto):
    (x1, y1, _), (x2, y2, _) = cu[origen], cu[destino]
    ax.annotate("", xy=(x2, y2 + (H / 2 if y2 < y1 else -H / 2)),
                xytext=(x1, y1 + (-H / 2 if y2 < y1 else H / 2)),
                arrowprops=dict(arrowstyle="->", ls="--", color="#333", lw=1.2), zorder=1)
    ax.text(x1 + 0.12, (y1 + y2) / 2 - 0.05, texto, fontsize=10, style="italic", color="#333")

relacion("CU05", "CU04", "«include»")
relacion("CU09", "CU07", "«extend»")
ax.text(2.6, 0.55, "Nota: CU-02, CU-03 y CU-06 los usan ambos actores.", fontsize=9.5, color="#555")
fig.savefig("../02-casos-de-uso.png", bbox_inches="tight", facecolor="white")
