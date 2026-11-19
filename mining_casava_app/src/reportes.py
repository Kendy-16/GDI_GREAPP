"""Catalogo de reportes: cada uno llama a un procedimiento almacenado (script A05).

Tipos de parametro:  serie | ruc | fecha | entero | texto
Un campo vacio se envia como NULL (= sin filtro).
"""
import csv
from datetime import datetime
from html import escape

from mysql.connector import Error

from .db import DBError, mensaje_error

TODOS = ("EXTERNO", "EMPLEADO", "GESTOR", "ADMINISTRADOR")
DESDE_EMPLEADO = ("EMPLEADO", "GESTOR", "ADMINISTRADOR")
SOLO_ADMIN = ("ADMINISTRADOR",)

D = ("Desde", "fecha")
H = ("Hasta", "fecha")

CATALOGO = [
    dict(id=1,  grupo="datos", nombre="01 · Guía completa por serie (JOIN)", proc="sp_rpt_01",
         params=[("Serie (ej. EG07-00000100)", "serie")], roles=TODOS),
    dict(id=2,  grupo="datos", nombre="02 · Guías por rango de fechas", proc="sp_rpt_02",
         params=[D, H], roles=DESDE_EMPLEADO),
    dict(id=3,  grupo="datos", nombre="03 · Guías por remitente (JOIN)", proc="sp_rpt_03",
         params=[("RUC remitente (vacío = todos)", "ruc")], roles=DESDE_EMPLEADO),
    dict(id=4,  grupo="datos", nombre="04 · Ítems de una guía con su producto (JOIN)", proc="sp_rpt_04",
         params=[("Serie", "serie")], roles=DESDE_EMPLEADO),
    dict(id=5,  grupo="datos", nombre="05 · Vehículo y conductor de cada guía (JOIN)", proc="sp_rpt_05",
         params=[D, H], roles=DESDE_EMPLEADO),
    dict(id=6,  grupo="datos", nombre="06 · Productos más transportados (JOIN)", proc="sp_rpt_06",
         params=[("Cuántos mostrar (ej. 10)", "entero")], roles=DESDE_EMPLEADO),
    dict(id=7,  grupo="datos", nombre="07 · Guías por mes", proc="sp_rpt_07",
         params=[("Año (ej. 2026; vacío = todos)", "entero")], roles=TODOS),
    dict(id=8,  grupo="datos", nombre="08 · Guías por tipo, modalidad y motivo", proc="sp_rpt_08",
         params=[D, H], roles=DESDE_EMPLEADO),
    dict(id=9,  grupo="datos", nombre="09 · Peso transportado por destinatario (JOIN)", proc="sp_rpt_09",
         params=[D, H], roles=DESDE_EMPLEADO),
    dict(id=10, grupo="datos", nombre="10 · Viajes por conductor y vehículo (JOIN)", proc="sp_rpt_10",
         params=[D, H], roles=DESDE_EMPLEADO),
    dict(id=11, grupo="datos", nombre="11 · Guías con transbordo o retorno vacío (JOIN)", proc="sp_rpt_11",
         params=[D, H], roles=DESDE_EMPLEADO),
    dict(id=12, grupo="datos", nombre="12 · Guías de compra con proveedor y documento (JOIN)", proc="sp_rpt_12",
         params=[D, H], roles=DESDE_EMPLEADO),
    dict(id=101, grupo="auditoria", nombre="Auditoría de ingresos", proc="sp_adm_aud_accesos",
         params=[D, H, ("Usuario (vacío = todos)", "texto")], roles=SOLO_ADMIN),
    dict(id=102, grupo="auditoria", nombre="Trazabilidad de cambios en los datos", proc="sp_adm_aud_cambios",
         params=[D, H, ("Tabla (ej. EMPRESA)", "texto"), ("Operación (INSERT/UPDATE/DELETE)", "texto")],
         roles=SOLO_ADMIN),
]


class ParamError(Exception):
    pass


def disponibles(rol, grupo="datos"):
    return [r for r in CATALOGO if r["grupo"] == grupo and rol in r["roles"]]


def _convertir(valor, tipo, etiqueta):
    valor = (valor or "").strip()
    if valor == "":
        return None
    try:
        if tipo == "fecha":
            datetime.strptime(valor, "%Y-%m-%d")
            return valor
        if tipo == "entero":
            return int(valor)
    except ValueError:
        if tipo == "fecha":
            raise ParamError("'%s': use el formato AAAA-MM-DD (ej. 2026-09-30)." % etiqueta)
        raise ParamError("'%s': debe ser un número entero." % etiqueta)
    if tipo in ("serie", "ruc", "texto"):
        return valor.upper() if tipo != "texto" else valor
    return valor


def ejecutar(sesion, reporte, valores):
    """Devuelve (columnas, filas). 'valores' = lista de textos, uno por parametro."""
    args = [_convertir(v, t, e) for v, (e, t) in zip(valores, reporte["params"])]
    # los reportes que piden una serie la necesitan obligatoriamente
    for a, (e, t) in zip(args, reporte["params"]):
        if t == "serie" and a is None:
            raise ParamError("Ingrese la serie de la guía.")
    try:
        cur = sesion.conexion.cursor()
        cur.callproc(reporte["proc"], args)
        columnas, filas = [], []
        for res in cur.stored_results():
            columnas = [d[0] for d in res.description]
            filas = res.fetchall()
            break
        cur.close()
    except Error as e:
        raise DBError(mensaje_error(e))
    return columnas, [[_texto(c) for c in f] for f in filas]


def _texto(v):
    if v is None:
        return ""
    if isinstance(v, (bytes, bytearray)):
        return v.decode("utf-8", errors="replace")
    return str(v)


def exportar_csv(ruta, columnas, filas):
    # utf-8-sig: Excel abre bien las tildes
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(columnas)
        w.writerows(filas)


_CSS = """
body{font-family:Arial,Helvetica,sans-serif;color:#1b2b24;margin:24px}
.cab{border-bottom:3px solid #00402F;padding-bottom:8px;margin-bottom:12px}
.cab h1{margin:0;font-size:18px;color:#00402F}
.cab h2{margin:4px 0 0;font-size:15px}
.meta{font-size:11px;color:#4A6B5E;margin-top:6px}
table{border-collapse:collapse;width:100%;font-size:11px}
th{background:#00402F;color:#fff;text-align:left;padding:5px 6px;border:1px solid #00402F}
td{padding:4px 6px;border:1px solid #9EE0C0;vertical-align:top}
tr:nth-child(even) td{background:#E6F6EE}
thead{display:table-header-group}
tr{page-break-inside:avoid}
.pie{margin-top:10px;font-size:11px;color:#4A6B5E}
.aviso{background:#fff3cd;border:1px solid #e0c36a;padding:6px 10px;margin-bottom:12px;font-size:12px}
@page{size:A4 landscape;margin:12mm}
@media print{.aviso{display:none}body{margin:0}}
"""


def html_imprimible(titulo, parametros, columnas, filas, usuario, rol):
    """Devuelve una pagina HTML lista para imprimir (o guardar como PDF) desde el navegador."""
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    params = " · ".join(escape(p) for p in parametros) if parametros else "sin filtros"
    cab = "".join("<th>%s</th>" % escape(str(c)) for c in columnas)
    cuerpo = "".join(
        "<tr>%s</tr>" % "".join("<td>%s</td>" % escape(str(c)) for c in f) for f in filas)
    return (
        "<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>"
        "<title>%s</title><style>%s</style></head><body>"
        "<div class='aviso'>Use <b>Ctrl+P</b> para imprimir o elija "
        "<b>Guardar como PDF</b> como destino.</div>"
        "<div class='cab'><h1>Inversiones Mining Casava E.I.R.L.</h1><h2>%s</h2>"
        "<div class='meta'>Parámetros: %s<br>Generado: %s · Usuario: %s (%s)</div></div>"
        "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>"
        "<div class='pie'>Total de filas: %d</div>"
        "<script>window.onload=function(){setTimeout(function(){window.print()},300)}</script>"
        "</body></html>"
    ) % (escape(titulo), _CSS, escape(titulo), params, ahora,
         escape(str(usuario)), escape(str(rol)), cab, cuerpo, len(filas))