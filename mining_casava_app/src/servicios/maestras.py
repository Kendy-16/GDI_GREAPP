"""Alta, cambio y baja de las 5 maestras (src/servicios/maestras.py).

Convención de nombres: sp_<maestra>_registrar / _modificar / _eliminar.
Si en A03 se llaman distinto, solo hay que cambiar el diccionario MAESTRAS.
"""
from src.servicios.procs import consultar, firma, llamar

# nombre en pantalla: (tabla, parte del nombre del procedimiento)
MAESTRAS = {
    "Empresa": ("EMPRESA", "empresa"),
    "Transportista": ("TRANSPORTISTA", "transportista"),
    "Vehículo": ("VEHICULO", "vehiculo"),
    "Conductor": ("CONDUCTOR", "conductor"),
    "Producto": ("PRODUCTO", "producto"),
}


def _sp(m, accion):
    return f"sp_{MAESTRAS[m][1]}_{accion}"


def campos(con, m):
    """(todos los campos del formulario, campos que usa el alta)."""
    mod = [n for modo, n in firma(con, _sp(m, "modificar")) if modo != "OUT"]
    reg = [n for modo, n in firma(con, _sp(m, "registrar")) if modo != "OUT"]
    return mod + [n for n in reg if n not in mod], reg


def listar(con, m, texto=""):
    cols, filas = consultar(con, f"SELECT * FROM {MAESTRAS[m][0]} LIMIT 2000")
    if texto:
        t = texto.lower()
        filas = [f for f in filas if any(t in str(x).lower() for x in f)]
    return cols, filas


def registrar(con, usuario, m, valores):
    """Devuelve los parámetros OUT (p. ej. el id nuevo de un producto)."""
    salidas, _ = llamar(con, _sp(m, "registrar"), valores, usuario)
    return salidas


def modificar(con, usuario, m, valores):
    llamar(con, _sp(m, "modificar"), valores, usuario)


def eliminar(con, usuario, m, valores):
    llamar(con, _sp(m, "eliminar"), valores, usuario)
