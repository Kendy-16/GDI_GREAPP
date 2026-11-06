"""Inicio y cierre de sesion.

Flujo (doble conexion):
  1. Conecta como 'app_login', que solo puede ejecutar sp_login.
  2. sp_login valida usuario y clave (hash con sal) y devuelve el ROL.
  3. Se cierra esa conexion y se abre otra con la cuenta de MySQL de ese rol.
  4. Se fija @usuario_app, que los triggers leen para la trazabilidad.
"""
import socket
from dataclasses import dataclass

from mysql.connector import Error

from .db import conectar, mensaje_error, DBError

CUENTA_POR_ROL = {
    "EXTERNO": "u_externo",
    "EMPLEADO": "u_empleado",
    "GESTOR": "u_gestor",
    "ADMINISTRADOR": "u_admin",
}

NOMBRE_ROL = {
    "EXTERNO": "Usuario externo",
    "EMPLEADO": "Empleado",
    "GESTOR": "Gestor de información",
    "ADMINISTRADOR": "Administrador",
}


class AuthError(Exception):
    pass


@dataclass
class Sesion:
    usuario: str
    nombre: str
    rol: str
    conexion: object
    equipo: str


def iniciar_sesion(usuario, clave):
    usuario = (usuario or "").strip()
    if not usuario or not clave:
        raise AuthError("Ingrese usuario y clave.")
    equipo = socket.gethostname()

    cx = conectar("app_login")
    try:
        cur = cx.cursor()
        # Los 3 ultimos parametros de sp_login son de salida (OUT): resultado, rol, nombre, id
        r = cur.callproc("sp_login", (usuario, clave, equipo, "", "", "", 0))
        resultado, rol, nombre = r[3], r[4], r[5]
        cur.close()
    except Error as e:
        raise DBError(mensaje_error(e))
    finally:
        cx.close()

    if resultado == "BLOQUEADO":
        raise AuthError("Cuenta bloqueada o inactiva. Contacte al administrador.")
    if resultado != "EXITO":
        raise AuthError("Usuario o clave incorrectos.")
    if rol not in CUENTA_POR_ROL:
        raise AuthError("El usuario tiene un rol no reconocido.")

    cx = conectar(CUENTA_POR_ROL[rol])
    try:
        cur = cx.cursor()
        cur.execute("SET @usuario_app = %s", (usuario,))
        cur.close()
    except Error as e:
        cx.close()
        raise DBError(mensaje_error(e))
    return Sesion(usuario=usuario, nombre=nombre, rol=rol, conexion=cx, equipo=equipo)


def cerrar_sesion(sesion):
    """Registra el cierre en AUDITORIA_ACCESO y cierra la conexion."""
    try:
        cur = sesion.conexion.cursor()
        cur.callproc("sp_cerrar_sesion", (sesion.usuario, sesion.equipo))
        cur.close()
    except Error:
        pass
    finally:
        try:
            sesion.conexion.close()
        except Error:
            pass
