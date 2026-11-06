"""Menu principal: las opciones visibles cambian segun el rol."""
import tkinter as tk
from tkinter import ttk

from ..auth import NOMBRE_ROL
from .reportes_view import ReportesFrame

# opcion -> roles que la ven
OPCIONES = [
    ("inicio",    "Inicio",                    ("EXTERNO", "EMPLEADO", "GESTOR", "ADMINISTRADOR")),
    ("reportes",  "Reportes",                  ("EXTERNO", "EMPLEADO", "GESTOR", "ADMINISTRADOR")),
    ("registros", "Registros (alta/cambio/baja)", ("GESTOR", "ADMINISTRADOR")),
    ("usuarios",  "Usuarios",                  ("ADMINISTRADOR",)),
    ("auditoria", "Auditoría",                 ("ADMINISTRADOR",)),
]

DESCRIPCION_ROL = {
    "EXTERNO": "Puede consultar un conjunto reducido de reportes genéricos.",
    "EMPLEADO": "Puede consultar toda la información registrada.",
    "GESTOR": "Puede insertar, modificar y eliminar registros (no estructuras).",
    "ADMINISTRADOR": "Tiene todos los permisos, incluida la auditoría.",
}


class MenuFrame(ttk.Frame):
    def __init__(self, master, sesion, cerrar_sesion):
        super().__init__(master)
        self.sesion = sesion

        barra = tk.Frame(self, bg="#1f3b57")
        barra.pack(fill="x")
        tk.Label(barra, text="Mining Casava · GRE", bg="#1f3b57", fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=14, pady=8)
        tk.Label(barra, text="%s  ·  %s" % (sesion.nombre, NOMBRE_ROL[sesion.rol]),
                 bg="#1f3b57", fg="#cfe0f1").pack(side="right", padx=14)

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)

        lateral = ttk.Frame(cuerpo, padding=10)
        lateral.pack(side="left", fill="y")
        for clave, texto, roles in OPCIONES:
            if sesion.rol in roles:
                ttk.Button(lateral, text=texto, width=28,
                           command=lambda c=clave: self.abrir(c)).pack(pady=3)
        ttk.Separator(lateral).pack(fill="x", pady=10)
        ttk.Button(lateral, text="Cerrar sesión", command=cerrar_sesion).pack(pady=3, fill="x")

        self.contenido = ttk.Frame(cuerpo, padding=12)
        self.contenido.pack(side="left", fill="both", expand=True)
        self.abrir("inicio")

    def _vaciar(self):
        for w in self.contenido.winfo_children():
            w.destroy()

    def abrir(self, clave):
        self._vaciar()
        if clave == "inicio":
            ttk.Label(self.contenido, text="Bienvenido, %s" % self.sesion.nombre.title(),
                      font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(10, 4))
            ttk.Label(self.contenido, text="Rol: %s" % NOMBRE_ROL[self.sesion.rol]).pack(anchor="w")
            ttk.Label(self.contenido, text=DESCRIPCION_ROL[self.sesion.rol],
                      foreground="#555").pack(anchor="w", pady=6)
        elif clave == "reportes":
            ReportesFrame(self.contenido, self.sesion, "datos").pack(fill="both", expand=True)
        elif clave == "auditoria":
            ReportesFrame(self.contenido, self.sesion, "auditoria").pack(fill="both", expand=True)
        else:
            titulo = dict((c, t) for c, t, _ in OPCIONES)[clave]
            ttk.Label(self.contenido, text=titulo, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(10, 4))
            ttk.Label(self.contenido, text="Módulo en desarrollo.\n"
                      "Usará los procedimientos sp_*_registrar, sp_*_modificar y sp_*_eliminar.",
                      foreground="#555", justify="left").pack(anchor="w")
