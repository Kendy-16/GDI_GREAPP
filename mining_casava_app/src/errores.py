"""Errores claros, log y manejador global (src/errores.py)."""
import logging
import os
import re
from tkinter import messagebox

import mysql.connector
from . import config

class ErrorServicio(Exception):
    """Error que se puede mostrar tal cual al usuario."""


class ErrorFirma(ErrorServicio):
    """El procedimiento o sus parámetros no coinciden con lo que espera el código."""


MENSAJES = {
    1062: "Ya existe un registro con esa clave.",
    1451: "No se puede eliminar: el registro está en uso.",
    1452: "Un dato relacionado no existe (revise empresa, producto, vehículo o conductor).",
    3819: "Un dato no cumple una regla de validación.",
    1370: "Su rol no tiene permiso para ejecutar esta operación.",
    1142: "Su rol no tiene permiso sobre esta tabla u operación.",
    1045: "Usuario o clave de MySQL incorrectos (revise config.ini).",
    2003: "No se pudo conectar con MySQL (¿está encendido el servicio?).",
}


def traducir(exc):
    """Convierte cualquier excepción en un mensaje para el usuario."""
    if isinstance(exc, ErrorServicio):
        return str(exc)
    if isinstance(exc, mysql.connector.Error):
        n = getattr(exc, "errno", None)
        msg = getattr(exc, "msg", None) or str(exc)
        if n == 1644:                       # SIGNAL de procedimientos y triggers
            return msg
        if n == 3819:
            m = re.search(r"'([^']+)'", msg)
            return MENSAJES[3819] + (f" (regla {m.group(1)})." if m else "")
        if n == 1062:
            m = re.search(r"'([^']+)'", msg)
            return MENSAJES[1062] + (f" Valor: {m.group(1)}." if m else "")
        if n in (1142, 1370):                # permiso: se agrega qué se rechazó
            return MENSAJES[n] + "\n(" + msg + ")"
        if n in MENSAJES:
            return MENSAJES[n]
        return f"Error de base de datos ({n}): {msg}"
    return f"Error inesperado: {exc}"


def configurar_log(carpeta=None):
    """Llamar una vez al iniciar. Nunca se registran claves.

    Por defecto el log va en <carpeta del programa>/logs (junto al .exe si esta empaquetado)."""
    carpeta = carpeta or str(config.raiz() / "logs")
    os.makedirs(carpeta, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(carpeta, "app.log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


def registrar_error(contexto, exc):
    logging.error("%s: %s: %s", contexto, type(exc).__name__, exc)


def instalar_manejador(root):
    """Evita que la ventana se cierre por un error inesperado en un botón."""
    def _cb(exc, val, tb):
        logging.error("Error no controlado", exc_info=(exc, val, tb))
        messagebox.showerror(
            "Mining Casava",
            "Ocurrió un error inesperado y se guardó en logs/app.log.\n\n" + traducir(val),
        )
    root.report_callback_exception = _cb