"""Widgets comunes (src/ui/widgets.py)."""
import tkinter as tk
from tkinter import ttk

from . import estilos


ETIQUETAS = {
    "razon_social": "Razón social", "fecha": "Fecha (AAAA-MM-DD)", "hora": "Hora (HH:MM:SS)",
    "tipo": "Tipo", "motivo": "Motivo", "modalidad": "Modalidad", "peso": "Peso", "unidad": "Unidad",
    "ruc_rem": "Remitente (RUC)", "ruc_dest": "Destinatario (RUC)", "ruc_transp": "RUC transportista",
    "ruc_pagador": "RUC pagador flete", "ruc_prov": "RUC proveedor", "ruc": "RUC",
    "ruc_transportista": "RUC transportista", "numero_registro_mtc": "Nro registro MTC",
    "fecha_inicio": "Fecha inicio traslado", "fecha_entrega": "Fecha entrega", "obs": "Observaciones",
    "partida": "Punto de partida", "llegada": "Punto de llegada", "veh_vacio": "Vehículo vacío (0/1)",
    "transbordo": "Transbordo (0/1)", "envases": "Envases (0/1)", "m1l": "M1L (0/1)",
    "subcontratado": "Subcontratado (0/1)", "nro_tuce": "Nro TUCE", "nro_licencia": "Nro licencia",
    "dni": "DNI", "placa": "Placa", "descripcion": "Descripción", "sunat": "Código SUNAT", "gtin": "GTIN", "id": "Id", "serie": "Serie (XXXX-00000000)",
}


# en Producto, "partida" es la partida arancelaria (no el punto de partida de la guía)
ESPECIFICAS = {"Producto": {"partida": "Partida arancelaria", "unidad": "Unidad de medida"}}


def etiqueta(nombre, contexto=None):
    if contexto in ESPECIFICAS and nombre in ESPECIFICAS[contexto]:
        return ESPECIFICAS[contexto][nombre]
    return ETIQUETAS.get(nombre, nombre.replace("_", " ").capitalize())


HEADERS = {"razon_social": "Razón social", "numero_registro_mtc": "Nro registro MTC",
           "ruc_transportista": "RUC transportista", "nro_tuce": "Nro TUCE", "nro_licencia": "Nro licencia"}


def _titulo(c):
    return HEADERS.get(str(c).lower(), str(c).replace("_", " "))


class Tabla(ttk.Frame):
    """Treeview con barras. Guarda las filas aparte para no perder ceros (DNI 0123...)."""

    def __init__(self, parent, height=10):
        super().__init__(parent)
        self.tree = ttk.Treeview(self, show="headings", height=height, selectmode="browse")
        ys = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        xs = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        estilos.rayado(self.tree)
        self.columnas, self._filas = [], []

    def cargar(self, columnas, filas):
        self.columnas = list(columnas)
        self._filas = [tuple(f) for f in filas]
        self.tree["columns"] = self.columnas
        for i, c in enumerate(self.columnas):
            self.tree.heading(c, text=_titulo(c))
            largo = max([len(_titulo(c))] + [len(str(f[i])) for f in self._filas[:200] if f[i] is not None])
            self.tree.column(c, width=min(max(90, largo * 8 + 24), 340), minwidth=60, stretch=False)
        self.tree.delete(*self.tree.get_children())
        for i, f in enumerate(self._filas):
            self.tree.insert("", "end", iid=str(i), values=["" if v is None else str(v) for v in f],
                             tags=("par",) if i % 2 else ())

    def indice(self):
        s = self.tree.selection()
        return int(s[0]) if s else None

    def seleccion(self):
        i = self.indice()
        return None if i is None else dict(zip(self.columnas, self._filas[i]))

    def al_seleccionar(self, fn):
        self.tree.bind("<<TreeviewSelect>>", lambda _e: fn())