"""Listado de guías y formulario completo (src/ui/guia_form.py)."""
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from src.errores import ErrorServicio, registrar_error, traducir
from src.servicios import guias
from src.ui import estilos
from src.ui.widgets import Tabla, etiqueta

FLAGS = ("transbordo", "envases", "m1l", "veh_vacio", "subcontratado")
# orden del mockup 4
FILA1 = ("serie", "tipo", "fecha", "hora")
FILA2 = ("motivo", "modalidad", "ruc_rem", "ruc_dest")
FILA3 = ("partida", "llegada", "peso")


class GuiasView(ttk.Frame):
    """Mockup 3: filtros, tabla (Serie, Fecha, Tipo, Motivo, Remitente, Peso) y botones."""

    def __init__(self, parent, con, usuario, editable):
        super().__init__(parent, padding=8)
        self.con, self.usuario = con, usuario
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        self.v = {k: tk.StringVar() for k in ("serie", "desde", "hasta", "ruc")}
        for i, (k, t) in enumerate([("serie", "Serie"), ("desde", "Desde (AAAA-MM-DD)"),
                                    ("hasta", "Hasta (AAAA-MM-DD)"), ("ruc", "Remitente (RUC)")]):
            ttk.Label(barra, text=t, style="Campo.TLabel").grid(row=0, column=i, sticky="w", padx=4)
            ttk.Entry(barra, textvariable=self.v[k], width=18).grid(row=1, column=i, padx=4)
        ttk.Button(barra, text="Buscar", style="Primario.TButton", command=self.buscar).grid(row=1, column=4, padx=6)
        self.tabla = Tabla(self, height=14)
        self.tabla.pack(fill="both", expand=True, pady=8)
        acc = ttk.Frame(self)
        acc.pack(fill="x")
        est = "normal" if editable else "disabled"
        ttk.Button(acc, text="Nueva guía", style="Primario.TButton", command=self.nueva, state=est).pack(side="left", padx=2)
        ttk.Button(acc, text="Editar", command=self.editar, state=est).pack(side="left", padx=2)
        ttk.Button(acc, text="Eliminar", style="Peligro.TButton", command=self.eliminar, state=est).pack(side="left", padx=2)
        ttk.Button(acc, text="Duplicar", command=self.duplicar, state=est).pack(side="left", padx=2)
        self.info = ttk.Label(acc, text="")
        self.info.pack(side="right")
        self.buscar()

    def buscar(self):
        try:
            cols, filas = guias.listar(self.con, *(self.v[k].get().strip() for k in ("serie", "desde", "hasta", "ruc")))
        except ErrorServicio as err:
            messagebox.showerror("Mining Casava", str(err), parent=self)
            return
        self.tabla.cargar(cols, filas)
        self.info.configure(text=f"{len(filas)} guía(s)")

    def _serie_sel(self):
        fila = self.tabla.seleccion()
        if not fila:
            messagebox.showwarning("Mining Casava", "Seleccione una guía de la lista.", parent=self)
            return None
        return fila.get("Serie") or list(fila.values())[0]

    def nueva(self):
        GuiaForm(self, self.con, self.usuario, None, self.buscar)

    def editar(self):
        s = self._serie_sel()
        if s:
            GuiaForm(self, self.con, self.usuario, s, self.buscar)

    def duplicar(self):
        s = self._serie_sel()
        if s:
            GuiaForm(self, self.con, self.usuario, None, self.buscar, copiar_de=s)

    def eliminar(self):
        s = self._serie_sel()
        if not s:
            return
        try:
            texto = guias.resumen_baja(self.con, s)
            if not messagebox.askyesno("Confirmar baja", texto + "\n\n¿Continuar?", parent=self):
                return
            guias.eliminar(self.con, self.usuario, s)
        except ErrorServicio as err:
            messagebox.showerror("No se pudo eliminar", str(err), parent=self)
            return
        messagebox.showinfo("Mining Casava", f"Guía {s} eliminada.", parent=self)
        self.buscar()


class GuiaForm(tk.Toplevel):
    """Mockup 4: cabecera, ítems, traslados y documentos. Guardar = una transacción en MySQL."""

    def __init__(self, parent, con, usuario, serie=None, al_guardar=None, copiar_de=None):
        super().__init__(parent)
        self.con, self.usuario, self.serie, self.al_guardar = con, usuario, serie, al_guardar
        self._copia = copiar_de
        titulo = "Editar guía" if serie else ("Nueva guía (copia de %s)" % copiar_de if copiar_de else "Nueva guía de remisión")
        self.title(titulo)
        estilos.centrar(self, 1020, 780)        # no pasa del tamaño de la pantalla
        try:
            accion = "modificar" if serie else "registrar"
            self.campos = guias.campos_cabecera(con, accion)
            self.datos = guias.obtener(con, serie or copiar_de) if (serie or copiar_de) else None
            self.cat = guias.catalogos(con)
        except ErrorServicio as err:
            messagebox.showerror("Mining Casava", str(err), parent=parent)
            self.destroy()
            return
        self._d = self.datos or {"cab": {}, "bienes": [], "traslados": [], "documentos": []}
        self.bienes, self.traslados, self.documentos = self._d["bienes"], self._d["traslados"], self._d["documentos"]

        pie = ttk.Frame(self)                                   # primero, para que siempre se vea
        pie.pack(side="bottom", fill="x", padx=8, pady=8)
        ttk.Button(pie, text="Guardar", style="Primario.TButton", command=self.guardar).pack(side="left", padx=4)
        ttk.Button(pie, text="Cancelar", command=self.destroy).pack(side="left", padx=4)

        self.vars = {}
        marco = ttk.LabelFrame(self, text=titulo, padding=8)
        marco.pack(fill="x", padx=8, pady=(6, 3))
        for c in range(4):
            marco.columnconfigure(c, weight=1)
        for fila, grupo in ((0, FILA1), (2, FILA2)):
            for col, n in enumerate([x for x in grupo if x in self.campos]):
                self._campo(marco, n, fila, col)
        col = 0
        for n, span in (("partida", 2), ("llegada", 1), ("peso", 1)):
            if n in self.campos:
                self._campo(marco, n, 4, col, span)
                col += span
        resto = [n for n in self.campos if n not in FILA1 + FILA2 + FILA3]
        if resto:
            m2 = ttk.LabelFrame(self, text="Datos del traslado", padding=8)
            m2.pack(fill="x", padx=8, pady=3)
            for c in range(4):
                m2.columnconfigure(c, weight=1)
            for i, n in enumerate(resto):
                r, c = divmod(i, 4)
                self._campo(m2, n, r * 2, c)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=3)
        self._tab_bienes(nb)
        self._tab_traslados(nb)
        self._tab_documentos(nb)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

    # ---- cabecera
    def _inicial(self, n):
        val = self._d["cab"].get(n)
        if self._copia and "serie" in n:
            val = None
        if val is None and not self.serie and not self._copia:
            if n in FLAGS:
                val = "0"
            elif n in ("fecha", "fecha_inicio"):
                val = date.today().isoformat()
        return "" if val is None else str(val)

    def _campo(self, padre, n, fila, col, span=1):
        ttk.Label(padre, text=etiqueta(n), style="Campo.TLabel").grid(row=fila, column=col, columnspan=span, sticky="w", padx=4)
        v = tk.StringVar(value=self._inicial(n))
        self.vars[n] = v
        if n in FLAGS:
            w = ttk.Combobox(padre, textvariable=v, values=["0", "1"])
        elif "ruc" in n:
            w = ttk.Combobox(padre, textvariable=v, values=self.cat["rucs"])
        elif n in self.cat["opciones"]:
            w = ttk.Combobox(padre, textvariable=v, values=self.cat["opciones"][n])
        else:
            w = ttk.Entry(padre, textvariable=v)
        if self.serie and "serie" in n:
            w.configure(state="readonly")
        w.grid(row=fila + 1, column=col, columnspan=span, sticky="ew", padx=4, pady=(0, 4))

    # ---- pestañas de listas hijas
    def _tab_bienes(self, nb):
        f = ttk.Frame(nb, padding=6)
        nb.add(f, text="Ítems")
        fila = ttk.Frame(f)
        fila.pack(fill="x")
        self.b_prod, self.b_cant, self.b_norm = tk.StringVar(), tk.StringVar(), tk.IntVar()
        ttk.Label(fila, text="Producto").pack(side="left")
        ttk.Combobox(fila, textvariable=self.b_prod, values=self.cat["productos"], width=40).pack(side="left", padx=4)
        ttk.Label(fila, text="Cantidad").pack(side="left")
        ttk.Entry(fila, textvariable=self.b_cant, width=10).pack(side="left", padx=4)
        ttk.Checkbutton(fila, text="Normalizado", variable=self.b_norm).pack(side="left", padx=4)
        ttk.Button(fila, text="Agregar", command=self._add_bien).pack(side="left", padx=2)
        ttk.Button(fila, text="Quitar", command=self._del_bien).pack(side="left", padx=2)
        self.t_bienes = Tabla(f, height=6)
        self.t_bienes.pack(fill="both", expand=True, pady=6)
        self._pintar_bienes()

    def _add_bien(self):
        try:
            pid = int(self.b_prod.get().split("·")[0].strip())
            cant = float(self.b_cant.get().replace(",", "."))
            if cant <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ítem", "Elija un producto y una cantidad mayor a 0.", parent=self)
            return
        self.bienes.append({"item": len(self.bienes) + 1, "producto": pid,
                            "normalizado": self.b_norm.get(), "cantidad": cant})
        self.b_cant.set("")
        self._pintar_bienes()

    def _del_bien(self):
        i = self.t_bienes.indice()
        if i is not None:
            self.bienes.pop(i)
            for n, b in enumerate(self.bienes, 1):
                b["item"] = n
            self._pintar_bienes()

    def _pintar_bienes(self):
        self.t_bienes.cargar(["Nro", "Producto", "Cantidad", "Normalizado"],
                             [(b["item"], b["producto"], b["cantidad"], b["normalizado"]) for b in self.bienes])

    def _tab_traslados(self, nb):
        f = ttk.Frame(nb, padding=6)
        nb.add(f, text="Traslados")
        fila = ttk.Frame(f)
        fila.pack(fill="x")
        self.t_placa, self.t_dni = tk.StringVar(), tk.StringVar()
        ttk.Label(fila, text="Vehículo (placa)").pack(side="left")
        ttk.Combobox(fila, textvariable=self.t_placa, values=self.cat["placas"], width=14).pack(side="left", padx=4)
        ttk.Label(fila, text="Conductor (DNI)").pack(side="left")
        ttk.Combobox(fila, textvariable=self.t_dni, values=self.cat["dnis"], width=14).pack(side="left", padx=4)
        ttk.Button(fila, text="Agregar", command=self._add_tras).pack(side="left", padx=2)
        ttk.Button(fila, text="Quitar", command=self._del_tras).pack(side="left", padx=2)
        self.t_tras = Tabla(f, height=6)
        self.t_tras.pack(fill="both", expand=True, pady=6)
        self._pintar_tras()

    def _add_tras(self):
        p, d = self.t_placa.get().strip(), self.t_dni.get().strip()
        if not p or not d:
            messagebox.showwarning("Traslado", "Indique placa y DNI.", parent=self)
            return
        self.traslados.append({"placa": p, "dni": d})
        self._pintar_tras()

    def _del_tras(self):
        i = self.t_tras.indice()
        if i is not None:
            self.traslados.pop(i)
            self._pintar_tras()

    def _pintar_tras(self):
        self.t_tras.cargar(["Placa", "DNI"], [(t["placa"], t["dni"]) for t in self.traslados])

    def _tab_documentos(self, nb):
        f = ttk.Frame(nb, padding=6)
        nb.add(f, text="Documentos")
        fila = ttk.Frame(f)
        fila.pack(fill="x")
        self.d_nro, self.d_tipo = tk.StringVar(), tk.StringVar(value="Factura")
        ttk.Label(fila, text="Nro").pack(side="left")
        ttk.Entry(fila, textvariable=self.d_nro, width=18).pack(side="left", padx=4)
        ttk.Label(fila, text="Tipo").pack(side="left")
        ttk.Combobox(fila, textvariable=self.d_tipo, values=["Factura", "Boleta", "Orden de compra", "Otro"],
                     width=16).pack(side="left", padx=4)
        ttk.Button(fila, text="Agregar", command=self._add_doc).pack(side="left", padx=2)
        ttk.Button(fila, text="Quitar", command=self._del_doc).pack(side="left", padx=2)
        self.t_docs = Tabla(f, height=6)
        self.t_docs.pack(fill="both", expand=True, pady=6)
        self._pintar_docs()

    def _add_doc(self):
        n, t = self.d_nro.get().strip(), self.d_tipo.get().strip()
        if not n:
            messagebox.showwarning("Documento", "Indique el número del documento.", parent=self)
            return
        self.documentos.append({"nro": n, "tipo": t})
        self.d_nro.set("")
        self._pintar_docs()

    def _del_doc(self):
        i = self.t_docs.indice()
        if i is not None:
            self.documentos.pop(i)
            self._pintar_docs()

    def _pintar_docs(self):
        self.t_docs.cargar(["Nro", "Tipo"], [(d["nro"], d["tipo"]) for d in self.documentos])

    # ---- guardar
    def guardar(self):
        cab = {n: (v.get().strip() or None) for n, v in self.vars.items()}
        try:
            f = guias.modificar if self.serie else guias.registrar
            f(self.con, self.usuario, cab, self.bienes, self.traslados, self.documentos)
        except ErrorServicio as err:
            messagebox.showerror("No se pudo guardar la guía", str(err), parent=self)
            return
        except Exception as err:  # noqa: BLE001
            registrar_error("guardar guía", err)
            messagebox.showerror("No se pudo guardar la guía", traducir(err), parent=self)
            return
        messagebox.showinfo("Mining Casava", "Guía guardada completa.", parent=self)
        if self.al_guardar:
            self.al_guardar()
        self.destroy()