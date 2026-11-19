"""Capa de conexion: abre conexiones a MySQL con el conector oficial (sin ORM ni framework)."""
import mysql.connector
from mysql.connector import Error

from . import config


class DBError(Exception):
    """Error de base de datos ya traducido a un mensaje entendible."""


def mensaje_error(e):
    """Traduce un error del conector a un mensaje para el usuario."""
    errno = getattr(e, "errno", None)
    if errno == 2003:
        return "No se pudo conectar con MySQL (servidor o puerto). ¿Está encendido el servicio?"
    if errno == 1045:
        return "MySQL rechazó la cuenta. Revise usuario y clave en config.ini."
    if errno == 1049:
        return "La base de datos no existe. Ejecute primero los scripts SQL."
    if errno == 1370 or errno == 1142:
        return "Su rol no tiene permiso para esta operación."
    # errores lanzados por SIGNAL en los procedimientos y triggers: el texto ya es claro
    return getattr(e, "msg", None) or str(e)


def conectar(cuenta):
    """Abre una conexion con la cuenta de MySQL indicada (app_login, u_externo, ...)."""
    cfg = config.cargar()
    if cuenta not in cfg["cuentas"]:
        raise DBError("La cuenta '%s' no está en config.ini." % cuenta)
    try:
        return mysql.connector.connect(
            host=cfg["host"], port=cfg["port"], database=cfg["database"],
            user=cuenta, password=cfg["cuentas"][cuenta],
            connection_timeout=5, autocommit=True, charset="utf8mb4")
    except Error as e:
        raise DBError(mensaje_error(e))
