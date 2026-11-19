"""Pantalla de reportes: elegir, poner parametros, ejecutar, ver en tabla y exportar a CSV."""
import os
import tempfile
import time
import tkinter as tk
import webbrowser
from tkinter import ttk, filedialog, messagebox

from .. import reportes
from . import estilos
from ..db import DBError


class ReportesFrame(ttk.Frame):
    def __init__(self, master, sesion, grupo):
        super().__init__(master)
        self.sesion = sesion
        self.lista = reportes.disponibles(sesion.rol, grupo)
        self.columnas, self.filas = [], []
        self.entradas = []
        self._rep_usado, self._params_usados = None, []

        titulo = "Reportes" if grupo == "datos" else "Auditoría"
        ttk.Label(self, text=titulo, style="Titulo.TLabel").pack(anchor="w", pady=(0, 8))

        sel = ttk.Frame(self)
        sel.pack(fill="x")
        ttk.Label(sel, text="Reporte:").pack(side="left")
        self.combo = ttk.Combobox(sel, state="readonly", width=60,
                                  values=[r["nombre"] for r in self.lista])
        self.combo.pack(side="left", padx=8)
        self.combo.bind("<<ComboboxSelected>>", self.al_elegir)

        self.zona_params = ttk.Frame(self, padding=(0, 8))
        self.zona_params.pack(fill="x")

        acciones = ttk.Frame(self)
        acciones.pack(fill="x", pady=4)
        self.b_ejecutar = ttk.Button(acciones, text="Ejecutar", style="Primario.TButton", command=self.ejecutar)
        self.b_ejecutar.pack(side="left")
        self.b_csv = ttk.Button(acciones, text="Exportar a CSV", command=self.exportar, state="disabled")
        self.b_csv.pack(side="left", padx=8)
        self.b_imprimir = ttk.Button(acciones, text="Imprimir / PDF", command=self.imprimir, state="disabled")
        self.b_imprimir.pack(side="left")
        self.estado = ttk.Label(acciones, text="", style="Sub.TLabel")
        self.estado.pack(side="left", padx=10)

        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True, pady=(6, 0))
        self.tabla = ttk.Treeview(marco, show="headings")
        estilos.rayado(self.tabla)
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        sx = ttk.Scrollbar(marco, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        if self.lista:
            self.combo.current(0)
            self.al_elegir()

    def al_elegir(self, _evento=None):
        for w in self.zona_params.winfo_children():
            w.destroy()
        self.entradas = []
        rep = self.lista[self.combo.current()]
        for i, (etiqueta, tipo) in enumerate(rep["params"]):
            ttk.Label(self.zona_params, text=etiqueta + ":").grid(row=i, column=0, sticky="w", pady=2)
            e = ttk.Entry(self.zona_params, width=30)
            e.grid(row=i, column=1, padx=8, pady=2, sticky="w")
            if tipo == "fecha":
                ttk.Label(self.zona_params, text="AAAA-MM-DD", style="Sub.TLabel").grid(row=i, column=2, sticky="w")
            self.entradas.append(e)
        if self.entradas:
            self.entradas[0].focus()

    def ejecutar(self):
        rep = self.lista[self.combo.current()]
        t0 = time.perf_counter()
        try:
            self.columnas, self.filas = reportes.ejecutar(
                self.sesion, rep, [e.get() for e in self.entradas])
        except (reportes.ParamError, DBError) as err:
            messagebox.showwarning("Reporte", str(err))
            return
        self._rep_usado = rep
        self._params_usados = [
            "%s: %s" % (etiq, e.get().strip())
            for (etiq, _t), e in zip(rep["params"], self.entradas) if e.get().strip()]
        self._mostrar()
        ms = (time.perf_counter() - t0) * 1000
        self.estado.config(text="%d filas · %.0f ms" % (len(self.filas), ms))
        self.b_csv.config(state="normal" if self.filas else "disabled")
        self.b_imprimir.config(state="normal" if self.filas else "disabled")

    def _mostrar(self):
        self.tabla.delete(*self.tabla.get_children())
        self.tabla["columns"] = self.columnas
        for c in self.columnas:
            self.tabla.heading(c, text=c)
            self.tabla.column(c, width=max(90, len(c) * 11), stretch=False)
        for i, f in enumerate(self.filas):
            self.tabla.insert("", "end", values=f, tags=("par",) if i % 2 else ())

    def exportar(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if ruta:
            reportes.exportar_csv(ruta, self.columnas, self.filas)
            messagebox.showinfo("Exportar", "Archivo guardado:\n%s" % ruta)

    def imprimir(self):
        """Genera una pagina imprimible y la abre en el navegador (Ctrl+P o Guardar como PDF)."""
        if not self.filas or self._rep_usado is None:
            return
        pagina = reportes.html_imprimible(
            self._rep_usado["nombre"], self._params_usados, self.columnas, self.filas,
            getattr(self.sesion, "usuario", None) or self.sesion.nombre, self.sesion.rol)
        try:
            ruta = os.path.join(tempfile.gettempdir(), "reporte_mining_casava_%d.html" % int(time.time()))
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(pagina)
            webbrowser.open("file:///" + ruta.replace("\\", "/"))
        except Exception as err:  # noqa: BLE001
            messagebox.showerror("Imprimir", "No se pudo preparar la impresión:\n%s" % err)