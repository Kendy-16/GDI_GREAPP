"""Menu principal: las opciones visibles cambian segun el rol."""
import tkinter as tk
from tkinter import messagebox, ttk

from .. import db
from ..auth import NOMBRE_ROL
from ..errores import traducir
from . import estilos
from .inicio import InicioView
from .registros_view import RegistrosView
from .reportes_view import ReportesFrame
from .usuarios_view import UsuariosView

# opcion -> roles que la ven
OPCIONES = [
    ("inicio",    "Inicio",    ("EXTERNO", "EMPLEADO", "GESTOR", "ADMINISTRADOR")),
    ("reportes",  "Reportes",  ("EXTERNO", "EMPLEADO", "GESTOR", "ADMINISTRADOR")),
    ("registros", "Registros", ("GESTOR", "ADMINISTRADOR")),
    ("usuarios",  "Usuarios",  ("ADMINISTRADOR",)),
    ("auditoria", "Auditoría", ("ADMINISTRADOR",)),
]

DESCRIPCION_ROL = {
    "EXTERNO": "Solo 2 reportes genéricos",
    "EMPLEADO": "Consulta de todo lo registrado",
    "GESTOR": "Alta, cambio y baja de registros",
    "ADMINISTRADOR": "Todos los permisos",
}

# cuenta de MySQL de cada rol (script A06)
CUENTAS = {
    "EXTERNO": "u_externo",
    "EMPLEADO": "u_empleado",
    "GESTOR": "u_gestor",
    "ADMINISTRADOR": "u_admin",
}


class MenuFrame(ttk.Frame):
    def __init__(self, master, sesion, cerrar_sesion):
        super().__init__(master)
        self.sesion = sesion
        self._conexion = None
        self.botones = {}

        barra = tk.Frame(self, bg=estilos.VERDE_OSCURO)
        barra.pack(fill="x")
        tk.Label(barra, text="Mining Casava · GRE", bg=estilos.VERDE_OSCURO, fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=14, pady=8)
        tk.Label(barra, text="%s  ·  %s" % (sesion.nombre, NOMBRE_ROL[sesion.rol]),
                 bg=estilos.VERDE_OSCURO, fg="#CFEFE0").pack(side="right", padx=14)

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)

        lateral = ttk.Frame(cuerpo, padding=10)
        lateral.pack(side="left", fill="y")
        for clave, texto, roles in OPCIONES:
            if sesion.rol in roles:
                if clave == "reportes":
                    texto = "Reportes (%d)" % (2 if sesion.rol == "EXTERNO" else 12)
                b = ttk.Button(lateral, text=texto, width=26, style="Menu.TButton",
                               command=lambda c=clave: self.abrir(c))
                b.pack(pady=3, fill="x")
                self.botones[clave] = b
        ttk.Separator(lateral).pack(fill="x", pady=10)
        ttk.Button(lateral, text="Cerrar sesión", command=cerrar_sesion).pack(pady=3, fill="x")

        self.contenido = ttk.Frame(cuerpo, padding=16)
        self.contenido.pack(side="left", fill="both", expand=True)
        self.abrir("inicio")

    def destroy(self):
        if self._conexion is not None:
            try:
                self._conexion.close()
            except Exception:
                pass
            self._conexion = None
        super().destroy()

    def _vaciar(self):
        for w in self.contenido.winfo_children():
            w.destroy()

    def _con(self):
        """Conexión con la cuenta MySQL del rol (u_gestor, u_admin...)."""
        if self._conexion is None:
            self._conexion = db.conectar(CUENTAS[self.sesion.rol])
        return self._conexion

    def _con_cifras(self):
        """Conexión para las cifras del panel; None si no se puede conectar."""
        try:
            return self._con()
        except Exception:  # noqa: BLE001
            return None

    def _usuario(self):
        """Usuario de login (para la auditoría); si la sesión no lo guarda, el nombre."""
        return getattr(self.sesion, "usuario", None) or self.sesion.nombre

    def _vista(self, fabrica):
        try:
            fabrica().pack(fill="both", expand=True)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Mining Casava", traducir(e), parent=self)

    def abrir(self, clave):
        self._vaciar()
        for k, b in self.botones.items():
            b.configure(style="MenuActivo.TButton" if k == clave else "Menu.TButton")
        if clave == "inicio":
            opciones = [(c, t) for c, t, roles in OPCIONES
                        if c != "inicio" and self.sesion.rol in roles]
            self._vista(lambda: InicioView(
                self.contenido, self.sesion, opciones, self.abrir, self._con_cifras()))
        elif clave == "reportes":
            ReportesFrame(self.contenido, self.sesion, "datos").pack(fill="both", expand=True)
        elif clave == "auditoria":
            ReportesFrame(self.contenido, self.sesion, "auditoria").pack(fill="both", expand=True)
        elif clave == "registros":
            self._vista(lambda: RegistrosView(self.contenido, self._con(), self._usuario(), self.sesion.rol))
        elif clave == "usuarios":
            self._vista(lambda: UsuariosView(self.contenido, self._con(), self._usuario()))