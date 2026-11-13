"""Pantalla Usuarios, solo administrador (src/ui/usuarios_view.py)."""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from src.errores import ErrorServicio, registrar_error, traducir
from src.servicios import usuarios
from src.ui.widgets import Tabla


class UsuariosView(ttk.Frame):
    """Uso: UsuariosView(contenedor, con, usuario_admin).pack(fill='both', expand=True)"""

    def __init__(self, parent, con, admin):
        super().__init__(parent, padding=8)
        self.con, self.admin = con, admin
        ttk.Label(self, text="Usuarios", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 6))
        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)
        self.tabla = Tabla(cuerpo, height=14)
        self.tabla.pack(side="left", fill="both", expand=True)
        self.tabla.al_seleccionar(self._on_select)
        der = ttk.LabelFrame(cuerpo, text="Datos", padding=8)
        der.pack(side="right", fill="y", padx=(8, 0))
        self.v = {k: tk.StringVar() for k in ("usuario", "nombre", "clave")}
        self.rol, self.estado = tk.StringVar(value=usuarios.ROLES[0]), tk.StringVar(value="ACTIVO")
        for k, t, show in (("usuario", "Usuario", ""), ("nombre", "Nombre", ""), ("clave", "Clave (mín. 8)", "*")):
            ttk.Label(der, text=t).pack(anchor="w")
            ttk.Entry(der, textvariable=self.v[k], show=show, width=30).pack(pady=(0, 6))
        ttk.Label(der, text="Rol").pack(anchor="w")
        ttk.Combobox(der, textvariable=self.rol, values=usuarios.ROLES, state="readonly", width=28).pack(pady=(0, 6))
        ttk.Button(der, text="Crear usuario", command=self.crear).pack(fill="x", pady=2)
        ttk.Separator(der).pack(fill="x", pady=8)
        ttk.Label(der, text="Estado").pack(anchor="w")
        ttk.Combobox(der, textvariable=self.estado, values=usuarios.ESTADOS, state="readonly", width=28).pack(pady=(0, 6))
        ttk.Button(der, text="Cambiar estado (bloquear / desbloquear)", command=self.estado_).pack(fill="x", pady=2)
        ttk.Button(der, text="Cambiar clave", command=self.clave).pack(fill="x", pady=2)
        self.refrescar()

    def refrescar(self):
        try:
            cols, filas = usuarios.listar(self.con)
        except ErrorServicio as err:
            messagebox.showerror("Mining Casava", str(err), parent=self)
            return
        self.tabla.cargar(cols, filas)

    def _on_select(self):
        fila = self.tabla.seleccion() or {}
        low = {c.lower(): v for c, v in fila.items()}
        if "usuario" in low:
            self.v["usuario"].set(low["usuario"])
        for k in ("estado",):
            if low.get(k) in usuarios.ESTADOS:
                self.estado.set(low[k])

    def _hacer(self, accion, ok):
        try:
            accion()
        except ErrorServicio as err:
            messagebox.showerror("No se pudo completar", str(err), parent=self)
            return
        except Exception as err:  # noqa: BLE001
            registrar_error("usuarios", err)
            messagebox.showerror("No se pudo completar", traducir(err), parent=self)
            return
        messagebox.showinfo("Mining Casava", ok, parent=self)
        self.v["clave"].set("")
        self.refrescar()

    def crear(self):
        self._hacer(lambda: usuarios.crear(self.con, self.admin, self.v["usuario"].get(), self.v["nombre"].get(),
                                           self.v["clave"].get(), self.rol.get()), "Usuario creado.")

    def estado_(self):
        self._hacer(lambda: usuarios.cambiar_estado(self.con, self.admin, self.v["usuario"].get().strip(),
                                                    self.estado.get()), "Estado actualizado.")

    def clave(self):
        u = self.v["usuario"].get().strip()
        if not u:
            messagebox.showwarning("Mining Casava", "Seleccione un usuario.", parent=self)
            return
        nueva = simpledialog.askstring("Cambiar clave", f"Nueva clave para {u} (mín. 8 caracteres):", show="*", parent=self)
        if nueva:
            self._hacer(lambda: usuarios.cambiar_clave(self.con, self.admin, u, nueva), "Clave cambiada.")
