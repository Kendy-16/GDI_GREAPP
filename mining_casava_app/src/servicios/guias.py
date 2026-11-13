"""Alta, cambio y baja de guías completas (src/servicios/guias.py).

sp_guia_registrar / _modificar reciben la cabecera y tres listas JSON:
  bienes:     {"item":1,"producto":3,"normalizado":0,"cantidad":10.5}
  traslados:  {"placa":"ABC123","dni":"12345678"}
  documentos: {"nro":"F001-123","tipo":"Factura"}
"""
import re
from datetime import date, datetime, timedelta
from decimal import Decimal

from src.errores import ErrorServicio
from src.servicios.procs import consultar, emparejar, firma, llamar

SERIE_RE = re.compile(r"^[A-Za-z0-9]{4}-\d{8}$")


def _es_lista(n):
    return "json" in n or "lista" in n or n in ("bienes", "traslados", "documentos")


def _plano(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (date, datetime, timedelta)):
        return str(v)
    return v


def campos_cabecera(con, accion):
    """Campos de texto del formulario (sin las listas JSON)."""
    return [n for modo, n in firma(con, f"sp_guia_{accion}") if modo != "OUT" and not _es_lista(n)]


def validar(cab, bienes, traslados):
    """Validaciones previas; MySQL vuelve a validar todo con triggers y CHECK."""
    errs = []
    for k, v in cab.items():
        if v in (None, ""):
            continue
        if "serie" in k and not SERIE_RE.match(str(v)):
            errs.append("La serie debe tener el formato XXXX-00000000.")
        if "peso" in k:
            try:
                if float(v) <= 0:
                    raise ValueError
            except ValueError:
                errs.append("El peso debe ser un número mayor a 0.")
        if "fecha" in k:
            ok = False
            for f in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
                try:
                    datetime.strptime(str(v), f)
                    ok = True
                except ValueError:
                    pass
            if not ok:
                errs.append(f"{k}: use el formato AAAA-MM-DD.")
    if not bienes:
        errs.append("La guía debe tener al menos un bien.")
    for b in bienes:
        if float(b["cantidad"]) <= 0:
            errs.append(f"El ítem {b['item']} debe tener cantidad mayor a 0.")
    if not traslados:
        errs.append("La guía debe tener al menos un traslado (vehículo y conductor).")
    return errs


def _armar(con, sp, cab, bienes, traslados, documentos):
    v = dict(cab)
    for modo, n in firma(con, sp):
        if modo == "OUT" or not _es_lista(n):
            continue
        if "bien" in n:
            v[n] = bienes
        elif "trasl" in n:
            v[n] = traslados
        elif "doc" in n:
            v[n] = documentos
    return v


def registrar(con, usuario, cab, bienes, traslados, documentos):
    errs = validar(cab, bienes, traslados)
    if errs:
        raise ErrorServicio("\n".join(dict.fromkeys(errs)))
    llamar(con, "sp_guia_registrar", _armar(con, "sp_guia_registrar", cab, bienes, traslados, documentos), usuario)


def modificar(con, usuario, cab, bienes, traslados, documentos):
    errs = validar(cab, bienes, traslados)
    if errs:
        raise ErrorServicio("\n".join(dict.fromkeys(errs)))
    llamar(con, "sp_guia_modificar", _armar(con, "sp_guia_modificar", cab, bienes, traslados, documentos), usuario)


def eliminar(con, usuario, serie):
    v = {n: serie for modo, n in firma(con, "sp_guia_eliminar") if modo != "OUT"}
    llamar(con, "sp_guia_eliminar", v, usuario)


def listar(con, serie="", desde="", hasta="", ruc=""):
    sql, p = "SELECT * FROM GUIA_DE_REMISION WHERE 1=1", []
    if serie:
        sql += " AND Serie_numero LIKE %s"
        p.append(f"%{serie}%")
    if desde:
        sql += " AND Fecha >= %s"
        p.append(desde)
    if hasta:
        sql += " AND Fecha <= %s"
        p.append(hasta)
    if ruc:
        sql += " AND RUC_Remitente LIKE %s"
        p.append(f"%{ruc}%")
    return consultar(con, sql + " ORDER BY Fecha DESC, Serie_numero DESC LIMIT 500", tuple(p))


def _hijas(con, tabla, serie, mapa):
    """Lee una tabla hija y la convierte a las claves del JSON (por palabra clave)."""
    cols, filas = consultar(con, f"SELECT * FROM {tabla} WHERE Serie_numero = %s", (serie,))
    salida = []
    for f in filas:
        d, usadas = {}, set()
        for clave, palabra in mapa:
            for i, c in enumerate(cols):
                if palabra in c.lower() and i not in usadas:
                    d[clave] = _plano(f[i])
                    usadas.add(i)
                    break
            else:
                d[clave] = None
        salida.append(d)
    return salida


def obtener(con, serie):
    cols, filas = consultar(con, "SELECT * FROM GUIA_DE_REMISION WHERE Serie_numero = %s", (serie,))
    if not filas:
        raise ErrorServicio("La guía no existe.")
    params = [n for modo, n in firma(con, "sp_guia_modificar") if modo != "OUT" and not _es_lista(n)]
    m = emparejar(params, cols)                      # ruc_rem <-> RUC_Remitente, etc.
    cab = {p: (_plano(filas[0][m[p]]) if p in m else None) for p in params}
    bienes = _hijas(con, "BIEN_TRANSPORTADO", serie,
                    [("item", "item"), ("normalizado", "normal"), ("cantidad", "cant"), ("producto", "producto")])
    traslados = _hijas(con, "TRASLADO", serie, [("placa", "placa"), ("dni", "dni")])
    documentos = _hijas(con, "DOCUMENTO_RELACIONADO", serie, [("nro", "nro"), ("tipo", "tipo")])
    return {"cab": cab, "bienes": bienes, "traslados": traslados, "documentos": documentos}


def resumen_baja(con, serie):
    """Texto para confirmar la baja: qué se borra junto con la guía."""
    partes = []
    for nombre, tabla in (("ítem(s)", "BIEN_TRANSPORTADO"), ("traslado(s)", "TRASLADO"),
                          ("documento(s)", "DOCUMENTO_RELACIONADO")):
        _, f = consultar(con, f"SELECT COUNT(*) FROM {tabla} WHERE Serie_numero = %s", (serie,))
        partes.append(f"{f[0][0]} {nombre}")
    return f"Se eliminará la guía {serie} junto con " + ", ".join(partes) + "."


def catalogos(con):
    """Listas para los desplegables del formulario."""
    _, r = consultar(con, "SELECT RUC FROM EMPRESA ORDER BY 1")
    _, p = consultar(con, "SELECT * FROM PRODUCTO ORDER BY 1")
    _, v = consultar(con, "SELECT Placa FROM VEHICULO ORDER BY 1")
    _, c = consultar(con, "SELECT DNI FROM CONDUCTOR ORDER BY 1")
    return {
        "rucs": [x[0] for x in r],
        "productos": [f"{x[0]} · {x[1]}" if len(x) > 1 else str(x[0]) for x in p],
        "placas": [x[0] for x in v],
        "dnis": [x[0] for x in c],
    }