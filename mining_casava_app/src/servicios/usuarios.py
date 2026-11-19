"""Gestión de usuarios, solo administrador (src/servicios/usuarios.py).

Usa sp_adm_usuario_crear, sp_adm_usuario_estado y sp_adm_usuario_clave.
"""
from src.errores import ErrorServicio
from src.servicios.procs import consultar, emparejar, llamar

ROLES = ["EXTERNO", "EMPLEADO", "GESTOR", "ADMINISTRADOR"]
ESTADOS = ["ACTIVO", "INACTIVO", "BLOQUEADO"]


def listar(con):
    """Solo Usuario, Nombre, Rol y Estado (nunca el hash ni la sal)."""
    cols, filas = consultar(con, "SELECT * FROM USUARIO_APP ORDER BY 1")
    m = emparejar(["usuario", "nombre", "rol", "estado"], cols)
    usar = [(k, t) for k, t in (("usuario", "Usuario"), ("nombre", "Nombre"), ("rol", "Rol"), ("estado", "Estado")) if k in m]
    return [t for _, t in usar], [tuple(f[m[k]] for k, _ in usar) for f in filas]


def _valores(usuario, nombre="", clave="", rol="", estado=""):
    return {
        "usuario": usuario, "nombre": nombre, "nombre_completo": nombre,
        "clave": clave, "nueva_clave": clave, "clave_nueva": clave, "password": clave,
        "rol": rol, "estado": estado, "nuevo_estado": estado,
    }


def crear(con, admin, usuario, nombre, clave, rol):
    if not usuario.strip():
        raise ErrorServicio("Escriba el usuario.")
    if len(clave) < 8:
        raise ErrorServicio("La clave debe tener al menos 8 caracteres.")
    if rol not in ROLES:
        raise ErrorServicio("Elija un rol.")
    llamar(con, "sp_adm_usuario_crear", _valores(usuario.strip(), nombre.strip(), clave, rol), admin)


def cambiar_estado(con, admin, usuario, estado):
    if estado not in ESTADOS:
        raise ErrorServicio("Estado no válido: use ACTIVO, INACTIVO o BLOQUEADO.")
    llamar(con, "sp_adm_usuario_estado", _valores(usuario, estado=estado), admin)


def cambiar_clave(con, admin, usuario, clave):
    if len(clave) < 8:
        raise ErrorServicio("La clave debe tener al menos 8 caracteres.")
    llamar(con, "sp_adm_usuario_clave", _valores(usuario, clave=clave), admin)