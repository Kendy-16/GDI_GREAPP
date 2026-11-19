"""Llamadas genéricas a procedimientos (src/servicios/procs.py).

Lee la firma real del procedimiento en information_schema, de modo que el
código no depende de adivinar el orden de los parámetros: se pasan los datos
por NOMBRE (sin el prefijo p_) y aquí se ordenan.
"""
import json
from decimal import Decimal

from src.errores import ErrorFirma, ErrorServicio, traducir

_CACHE = {}


def _f(*ins, out=()):
    return [("IN", n) for n in ins] + [("OUT", n) for n in out]


_GUIA = ("serie", "tipo", "fecha", "hora", "motivo", "fecha_inicio", "obs", "partida", "llegada",
         "peso", "unidad", "modalidad", "ruc_rem", "ruc_dest", "ruc_transp", "ruc_pagador",
         "ruc_prov", "fecha_entrega", "transbordo", "envases", "m1l", "veh_vacio",
         "subcontratado", "bienes", "traslados", "documentos")

# Firmas reales de A03 (salida de tests/listar_firmas.py). Se usan antes que information_schema,
# porque MySQL no le muestra al gestor la definición de algunos procedimientos.
FIRMAS = {
    "sp_adm_usuario_clave": _f("usuario", "clave_nueva"),
    "sp_adm_usuario_crear": _f("usuario", "nombre", "clave", "rol"),
    "sp_adm_usuario_estado": _f("usuario", "estado"),
    "sp_conductor_eliminar": _f("dni"),
    "sp_conductor_modificar": _f("dni", "nombre", "nro_licencia"),
    "sp_conductor_registrar": _f("dni", "nombre", "nro_licencia"),
    "sp_empresa_eliminar": _f("ruc"),
    "sp_empresa_modificar": _f("ruc", "razon_social"),
    "sp_empresa_registrar": _f("ruc", "razon_social"),
    "sp_guia_eliminar": _f("serie"),
    "sp_guia_modificar": _f(*_GUIA),
    "sp_guia_registrar": _f(*_GUIA),
    "sp_producto_eliminar": _f("id"),
    "sp_producto_modificar": _f("id", "gtin", "sunat", "descripcion", "partida", "unidad"),
    "sp_producto_registrar": _f("gtin", "sunat", "descripcion", "partida", "unidad", out=("id",)),
    "sp_transportista_eliminar": _f("ruc_transportista"),
    "sp_transportista_modificar": _f("ruc_transportista", "numero_registro_mtc"),
    "sp_transportista_registrar": _f("ruc_transportista", "numero_registro_mtc"),
    "sp_vehiculo_eliminar": _f("placa"),
    "sp_vehiculo_modificar": _f("placa", "nro_tuce"),
    "sp_vehiculo_registrar": _f("placa", "nro_tuce"),
}


def _txt(x):
    if isinstance(x, (bytes, bytearray)):
        return x.decode("utf-8", "replace")
    return x


def norm(nombre):
    n = _txt(nombre).lower()
    for pref in ("p_", "in_", "i_"):
        if n.startswith(pref):
            return n[len(pref):]
    return n


def _json_default(o):
    return float(o) if isinstance(o, Decimal) else str(o)


def consultar(con, sql, params=()):
    """Ejecuta una consulta. Devuelve (columnas, filas)."""
    cur = con.cursor()
    try:
        cur.execute(sql, params)
        if cur.description:
            cols = [d[0] for d in cur.description]
            filas = [tuple(_txt(x) for x in f) for f in cur.fetchall()]
        else:
            cols, filas = [], []
    except Exception as e:
        raise ErrorServicio(traducir(e)) from e
    finally:
        cur.close()
    return cols, filas


def firma(con, nombre):
    """Lista de (modo, nombre_normalizado) del procedimiento."""
    if nombre in FIRMAS:
        return FIRMAS[nombre]
    if nombre in _CACHE:
        return _CACHE[nombre]
    _, filas = consultar(
        con,
        "SELECT PARAMETER_MODE, PARAMETER_NAME FROM information_schema.PARAMETERS "
        "WHERE SPECIFIC_SCHEMA = DATABASE() AND SPECIFIC_NAME = %s "
        "AND ORDINAL_POSITION > 0 ORDER BY ORDINAL_POSITION",
        (nombre,),
    )
    if not filas:
        raise ErrorFirma(
            f"No encuentro el procedimiento {nombre}. Revise el nombre en "
            f"src/servicios o ejecute tests/listar_firmas.py."
        )
    _CACHE[nombre] = [(_txt(m), norm(n)) for m, n in filas]
    return _CACHE[nombre]


def llamar(con, nombre, valores, usuario=None):
    """CALL nombre(...). Devuelve (salidas: dict, filas_resultado: list).

    `valores` usa los nombres de parámetro sin prefijo (ruc, razon_social...).
    Las listas y diccionarios se envían como JSON.
    """
    sig = firma(con, nombre)
    faltan = [n for modo, n in sig if modo != "OUT" and n not in valores]
    if faltan:
        raise ErrorFirma(
            f"{nombre} espera estos datos que no se enviaron: {', '.join(faltan)}."
        )
    args = []
    for modo, n in sig:
        if modo == "OUT":
            args.append(None)
            continue
        v = valores[n]
        if isinstance(v, (list, dict)):
            v = json.dumps(v, ensure_ascii=False, default=_json_default)
        elif isinstance(v, str) and not v.strip():
            v = None
        args.append(v)
    cur = con.cursor()
    try:
        if usuario:
            cur.execute("SET @usuario_app = %s", (usuario,))   # para los triggers de auditoría
        res = cur.callproc(nombre, args)
        filas = []
        for r in cur.stored_results():
            filas.extend(r.fetchall())
    except Exception as e:
        raise ErrorServicio(traducir(e)) from e
    finally:
        cur.close()
    salidas = {n: _txt(res[i]) for i, (m, n) in enumerate(sig) if m in ("OUT", "INOUT")}
    return salidas, filas


# parámetro -> palabras que identifican su columna en la tabla
ALIAS = {
    "id": ["id_producto", "id"],
    "serie": ["serie_numero", "serie"],
    "ruc_rem": ["ruc_remitente", "remitente"],
    "ruc_dest": ["ruc_destinatario", "destinatario"],
    "ruc_transp": ["ruc_transportista", "transportista"],
    "ruc_pagador": ["ruc_pagadorflete", "pagador"],
    "ruc_prov": ["ruc_proveedor", "proveedor"],
    "fecha_inicio": ["fecha_inicio", "inicio"],
    "fecha_entrega": ["fecha_entrega", "entrega"],
    "obs": ["observ", "obs"],
    "envases": ["envase"],
    "m1l": ["m1l", "m1"],
    "veh_vacio": ["vacio"],
    "subcontratado": ["subcontrat"],
}


def emparejar(params, columnas):
    """Devuelve {parametro: indice_de_columna} comparando nombres de forma flexible."""
    low = [str(c).lower() for c in columnas]
    usadas, res = set(), {}
    for p in params:
        cands = ALIAS.get(p, [p])
        idx = None
        for a in cands:                                   # 1) nombre exacto
            if a in low and low.index(a) not in usadas:
                idx = low.index(a)
                break
        if idx is None:                                   # 2) la columna contiene la palabra
            for a in cands:
                for i, c in enumerate(low):
                    if i not in usadas and a in c:
                        idx = i
                        break
                if idx is not None:
                    break
        if idx is not None:
            usadas.add(idx)
            res[p] = idx
    return res