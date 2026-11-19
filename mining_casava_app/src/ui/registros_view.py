"""Pantalla Registros: pestañas Guías + 5 maestras (src/ui/registros_view.py)."""
import tkinter as tk
from tkinter import messagebox, ttk

from src.errores import ErrorServicio, registrar_error, traducir
from src.servicios import maestras
from src.servicios.procs import emparejar
from src.ui.guia_form import GuiasView
from src.ui.widgets import Tabla, etiqueta


class PestanaMaestra(ttk.Frame):
    def __init__(self, parent, con, usuario, editable, maestra):
        super().__init__(parent, padding=8)
        self.con, self.usuario, self.editable, self.m = con, usuario, editable, maestra
        self.editando = False
        izq = ttk.Frame(self)
        izq.pack(side="left", fill="both", expand=True)
        der = ttk.LabelFrame(self, text=maestra, padding=14)
        der.pack(side="right", fill="y", padx=(8, 0))

        barra = ttk.Frame(izq)
        barra.pack(fill="x", pady=(0, 6))
        ttk.Label(barra, text="Buscar:").pack(side="left")
        self.busca = tk.StringVar()
        ent = ttk.Entry(barra, textvariable=self.busca, width=28)
        ent.pack(side="left", padx=4)
        ent.bind("<Return>", lambda _e: self.refrescar())
        ttk.Button(barra, text="Buscar", style="Primario.TButton", command=self.refrescar).pack(side="left", padx=4)
        self.tabla = Tabla(izq)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.al_seleccionar(self._on_select)

        try:
            self.campos, self.solo_alta = maestras.campos(con, maestra)
        except ErrorServicio as err:
            ttk.Label(der, text=str(err), style="Error.TLabel", wraplength=260).pack()
            return
        self.vars, self.entradas = {}, {}
        for n in self.campos:
            ttk.Label(der, text=etiqueta(n, self.m), style="Campo.TLabel").pack(anchor="w")
            self.vars[n] = tk.StringVar()
            ent = ttk.Entry(der, textvariable=self.vars[n], width=32)
            ent.pack(fill="x", pady=(2, 10))
            self.entradas[n] = ent
        fila = ttk.Frame(der)
        fila.pack(pady=8)
        estado = "normal" if editable else "disabled"
        ttk.Button(fila, text="Nuevo", command=self.nuevo, state=estado).pack(side="left", padx=2)
        ttk.Button(fila, text="Guardar", style="Primario.TButton", command=self.guardar, state=estado).pack(side="left", padx=2)
        ttk.Button(fila, text="Eliminar", style="Peligro.TButton", command=self.eliminar, state=estado).pack(side="left", padx=2)
        if not editable:
            ttk.Label(der, text="Solo consulta", style="Sub.TLabel").pack()
        self.nuevo()
        self.refrescar()

    # ---- estado del formulario
    def _estado_campos(self):
        for i, n in enumerate(self.campos):
            if not self.editable:
                ok = False
            elif self.editando:
                ok = i != 0                      # la clave no se cambia al editar
            else:
                ok = n in self.solo_alta         # en el alta solo los campos del alta
            self.entradas[n].configure(state="normal" if ok else "readonly")

    def nuevo(self):
        self.editando = False
        for v in self.vars.values():
            v.set("")
        self.tabla.tree.selection_remove(self.tabla.tree.selection())
        self._estado_campos()

    def refrescar(self):
        try:
            cols, filas = maestras.listar(self.con, self.m, self.busca.get().strip())
        except ErrorServicio as err:
            messagebox.showerror("Mining Casava", str(err), parent=self)
            return
        self.tabla.cargar(cols, filas)

    def _on_select(self):
        fila = self.tabla.seleccion()
        if not fila:
            return
        cols, vals = list(fila.keys()), list(fila.values())
        m = emparejar(self.campos, cols)
        self.editando = True
        for n, var in self.vars.items():
            v = vals[m[n]] if n in m else None
            var.set("" if v is None else str(v))
        self._estado_campos()

    # ---- operaciones
    def _valores(self):
        return {n: v.get().strip() or None for n, v in self.vars.items()}

    def guardar(self):
        val = self._valores()
        clave = self.campos[0]
        if self.editando and not val[clave]:
            messagebox.showwarning("Mining Casava", "Seleccione un registro de la lista.", parent=self)
            return
        try:
            if self.editando:
                maestras.modificar(self.con, self.usuario, self.m, val)
                msg = f"{self.m} modificado."
            else:
                salidas = maestras.registrar(self.con, self.usuario, self.m, val)
                extra = f" (id {list(salidas.values())[0]})" if salidas else ""
                msg = f"{self.m} registrado{extra}."
        except ErrorServicio as err:
            messagebox.showerror("No se pudo guardar", str(err), parent=self)
            return
        except Exception as err:  # noqa: BLE001
            registrar_error("guardar " + self.m, err)
            messagebox.showerror("No se pudo guardar", traducir(err), parent=self)
            return
        messagebox.showinfo("Mining Casava", msg, parent=self)
        self.refrescar()
        self.nuevo()

    def eliminar(self):
        if not self.editando:
            messagebox.showwarning("Mining Casava", "Seleccione un registro de la lista.", parent=self)
            return
        val = self._valores()
        if not messagebox.askyesno("Confirmar baja", f"¿Eliminar {self.m.lower()} {val[self.campos[0]]}?", parent=self):
            return
        try:
            maestras.eliminar(self.con, self.usuario, self.m, val)
        except ErrorServicio as err:                      # p. ej. "está en uso"
            messagebox.showerror("No se pudo eliminar", str(err), parent=self)
            return
        messagebox.showinfo("Mining Casava", f"{self.m} eliminado.", parent=self)
        self.refrescar()
        self.nuevo()


class RegistrosView(ttk.Frame):
    """Uso: RegistrosView(contenedor, con, usuario, rol).pack(fill='both', expand=True)"""

    def __init__(self, parent, con, usuario, rol):
        super().__init__(parent, padding=8)
        editable = rol in ("GESTOR", "ADMINISTRADOR")
        ttk.Label(self, text="Registros", style="Titulo.TLabel").pack(anchor="w", pady=(0, 8))
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        nb.add(GuiasView(nb, con, usuario, editable), text="Guías")
        for nombre in maestras.MAESTRAS:
            nb.add(PestanaMaestra(nb, con, usuario, editable, nombre), text=nombre)