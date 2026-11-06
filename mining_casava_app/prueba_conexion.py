"""Prueba de conexion a la base de datos (evidencia para el informe).

Ejecutar:  python prueba_conexion.py
Opcional:  python prueba_conexion.py --usuario admin --clave "Adm#2026"

Comprueba, en orden: config.ini, conexion con la cuenta tecnica de login,
sp_login, conexion con cada cuenta de rol y lectura de las tablas.
"""
import argparse
import socket
import sys

from mysql.connector import Error

from src import config, db

TABLAS = ["EMPRESA", "TRANSPORTISTA", "VEHICULO", "CONDUCTOR", "PRODUCTO", "GUIA_DE_REMISION",
          "DETALLE_GUIA", "BIEN_TRANSPORTADO", "TRASLADO", "DOCUMENTO_RELACIONADO"]
CUENTAS = [("u_externo", "EXTERNO"), ("u_empleado", "EMPLEADO"), ("u_gestor", "GESTOR"), ("u_admin", "ADMINISTRADOR")]


def paso(n, texto):
    print("\n[%d] %s" % (n, texto))


def ok(texto):
    print("    OK    " + texto)


def falla(texto):
    print("    FALLO " + texto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--usuario", default="admin")
    ap.add_argument("--clave", default="Adm#2026")
    a = ap.parse_args()
    errores = 0

    paso(1, "Leer config.ini")
    try:
        cfg = config.cargar()
        ok("servidor %s:%s · base '%s' · %d cuentas" % (cfg["host"], cfg["port"], cfg["database"], len(cfg["cuentas"])))
    except config.ConfigError as e:
        falla(str(e)); sys.exit(1)

    paso(2, "Conectar con la cuenta técnica 'app_login'")
    try:
        cx = db.conectar("app_login")
        cur = cx.cursor()
        cur.execute("SELECT VERSION(), DATABASE(), CURRENT_USER()")
        v, bd, u = cur.fetchone()
        ok("MySQL %s · base %s · cuenta %s" % (v, bd, u))
        cur.close(); cx.close()
    except db.DBError as e:
        falla(str(e)); sys.exit(1)

    paso(3, "Llamar al procedimiento sp_login con el usuario '%s'" % a.usuario)
    try:
        cx = db.conectar("app_login")
        cur = cx.cursor()
        r = cur.callproc("sp_login", (a.usuario, a.clave, socket.gethostname(), "", "", "", 0))
        ok("resultado = %s · rol = %s · nombre = %s" % (r[3], r[4], r[5]))
        if r[3] != "EXITO":
            errores += 1
        cur.close(); cx.close()
    except (db.DBError, Error) as e:
        falla(str(e)); errores += 1

    paso(4, "Conectar con la cuenta de cada rol")
    for cuenta, rol in CUENTAS:
        try:
            cx = db.conectar(cuenta)
            cur = cx.cursor()
            cur.execute("SELECT CURRENT_USER(), CURRENT_ROLE()")
            u, r = cur.fetchone()
            ok("%-11s rol activo: %s" % (cuenta, r))
            cur.close(); cx.close()
        except db.DBError as e:
            falla("%s: %s" % (cuenta, e)); errores += 1

    paso(5, "Leer las tablas con la cuenta u_empleado (filas por tabla)")
    try:
        cx = db.conectar("u_empleado")
        cur = cx.cursor()
        for t in TABLAS:
            cur.execute("SELECT COUNT(*) FROM %s" % t)
            ok("%-22s %6d filas" % (t, cur.fetchone()[0]))
        cur.close(); cx.close()
    except (db.DBError, Error) as e:
        falla(str(e)); errores += 1

    print("\n" + ("PRUEBA COMPLETA: todo en orden." if errores == 0 else "PRUEBA CON %d ERROR(ES)." % errores))
    sys.exit(0 if errores == 0 else 1)


if __name__ == "__main__":
    main()
