"""Widgets comunes (src/ui/widgets.py)."""
import tkinter as tk
from tkinter import ttk


ETIQUETAS = {
    "ruc_rem": "RUC remitente", "ruc_dest": "RUC destinatario", "ruc_transp": "RUC transportista",
    "ruc_pagador": "RUC pagador flete", "ruc_prov": "RUC proveedor", "ruc": "RUC",
    "ruc_transportista": "RUC transportista", "numero_registro_mtc": "Nro registro MTC",
    "fecha_inicio": "Fecha inicio traslado", "fecha_entrega": "Fecha entrega", "obs": "Observaciones",
    "partida": "Punto de partida", "llegada": "Punto de llegada", "veh_vacio": "Vehículo vacío (0/1)",
    "transbordo": "Transbordo (0/1)", "envases": "Envases (0/1)", "m1l": "M1L (0/1)",
    "subcontratado": "Subcontratado (0/1)", "nro_tuce": "Nro TUCE", "nro_licencia": "Nro licencia",
    "sunat": "Código SUNAT", "gtin": "GTIN", "id": "Id", "serie": "Serie (XXXX-00000000)",
}


def etiqueta(nombre):
    return ETIQUETAS.get(nombre, nombre.replace("_", " ").capitalize())


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
        self.columnas, self._filas = [], []

    def cargar(self, columnas, filas):
        self.columnas = list(columnas)
        self._filas = [tuple(f) for f in filas]
        self.tree["columns"] = self.columnas
        for c in self.columnas:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, minwidth=60, stretch=False)
        self.tree.delete(*self.tree.get_children())
        for i, f in enumerate(self._filas):
            self.tree.insert("", "end", iid=str(i), values=["" if v is None else str(v) for v in f])

    def indice(self):
        s = self.tree.selection()
        return int(s[0]) if s else None

    def seleccion(self):
        i = self.indice()
        return None if i is None else dict(zip(self.columnas, self._filas[i]))

    def al_seleccionar(self, fn):
        self.tree.bind("<<TreeviewSelect>>", lambda _e: fn())