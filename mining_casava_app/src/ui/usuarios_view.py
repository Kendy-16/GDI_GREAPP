"""Pantalla Usuarios, solo administrador (src/ui/usuarios_view.py)."""
import tkinter as tk
from tkinter import messagebox, ttk

from src.errores import ErrorServicio, registrar_error, traducir
from src.servicios import usuarios
from src.ui.widgets import Tabla


class UsuariosView(ttk.Frame):
    """Lista a la izquierda; formulario Usuario, Nombre, Clave y Rol a la derecha."""

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
        self.rol = tk.StringVar(value=usuarios.ROLES[0])
        for k, t, show in (("usuario", "Usuario", ""), ("nombre", "Nombre", ""), ("clave", "Clave (mín. 8 caracteres)", "*")):
            ttk.Label(der, text=t).pack(anchor="w")
            ttk.Entry(der, textvariable=self.v[k], show=show, width=30).pack(pady=(0, 6))
        ttk.Label(der, text="Rol").pack(anchor="w")
        ttk.Combobox(der, textvariable=self.rol, values=usuarios.ROLES, state="readonly", width=28).pack(pady=(0, 10))
        for texto, cmd in (("Crear usuario", self.crear), ("Bloquear", self.bloquear),
                           ("Desbloquear", self.desbloquear), ("Cambiar clave", self.clave)):
            ttk.Button(der, text=texto, command=cmd).pack(fill="x", pady=2)
        self.refrescar()

    def refrescar(self):
        try:
            cols, filas = usuarios.listar(self.con)
        except ErrorServicio as err:
            messagebox.showerror("Mining Casava", str(err), parent=self)
            return
        self.tabla.cargar(cols, filas)

    def _on_select(self):
        fila = {c.lower(): v for c, v in (self.tabla.seleccion() or {}).items()}
        if "usuario" in fila:
            self.v["usuario"].set(fila["usuario"])
        if "nombre" in fila:
            self.v["nombre"].set(fila["nombre"] or "")
        if fila.get("rol") in usuarios.ROLES:
            self.rol.set(fila["rol"])
        self.v["clave"].set("")

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

    def _usuario(self):
        u = self.v["usuario"].get().strip()
        if not u:
            raise ErrorServicio("Seleccione o escriba el usuario.")
        return u

    def crear(self):
        self._hacer(lambda: usuarios.crear(self.con, self.admin, self.v["usuario"].get(), self.v["nombre"].get(),
                                           self.v["clave"].get(), self.rol.get()), "Usuario creado.")

    def bloquear(self):
        self._hacer(lambda: usuarios.cambiar_estado(self.con, self.admin, self._usuario(), "BLOQUEADO"),
                    "Usuario bloqueado.")

    def desbloquear(self):
        self._hacer(lambda: usuarios.cambiar_estado(self.con, self.admin, self._usuario(), "ACTIVO"),
                    "Usuario desbloqueado.")

    def clave(self):
        self._hacer(lambda: usuarios.cambiar_clave(self.con, self.admin, self._usuario(), self.v["clave"].get()),
                    "Clave cambiada.")