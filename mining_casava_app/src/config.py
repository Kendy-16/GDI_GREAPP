"""Lectura de config.ini (servidor, base y claves de las cuentas de MySQL)."""
import configparser
import sys
from pathlib import Path


def raiz():
    """Carpeta base: junto al .exe si esta empaquetado; la raiz del proyecto si no."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


RUTA_CONFIG = raiz() / "config.ini"


class ConfigError(Exception):
    pass


def cargar():
    if not RUTA_CONFIG.exists():
        raise ConfigError(
            "No se encontró config.ini en:\n%s\n"
            "Copie config.ini.example como config.ini y complete los datos." % RUTA_CONFIG)
    cp = configparser.ConfigParser(interpolation=None)   # None: permite '%' en las claves
    cp.read(RUTA_CONFIG, encoding="utf-8")
    try:
        return {
            "host": cp.get("mysql", "host"),
            "port": cp.getint("mysql", "port"),
            "database": cp.get("mysql", "database"),
            "cuentas": dict(cp.items("cuentas")),
        }
    except (configparser.Error, ValueError) as e:
        raise ConfigError("config.ini incompleto o con formato incorrecto: %s" % e)
