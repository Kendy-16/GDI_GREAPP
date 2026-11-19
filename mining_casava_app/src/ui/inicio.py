"""Pantalla de inicio tipo panel: bienvenida, cifras y accesos rápidos (src/ui/inicio.py)."""
import tkinter as tk
from tkinter import ttk

from .. import config
from ..servicios.procs import consultar
from . import estilos

DESCRIPCION = {
    "reportes": "Consulta los reportes y expórtalos a CSV",
    "registros": "Altas, cambios y bajas de guías y maestras",
    "usuarios": "Crear usuarios, bloquear y cambiar clave",
    "auditoria": "Quién ingresó y qué cambió",
}
ICONO = {"reportes": "▥", "registros": "✎", "usuarios": "☺", "auditoria": "⌚"}


def _norm(clave):
    return str(clave).lower().replace("í", "i").replace("é", "e")


class InicioView(ttk.Frame):
    """opciones: lista de (clave, texto) sin 'inicio' ni 'cerrar sesión'.
    abrir: función que abre una opción (la misma de los botones laterales).
    con: conexión opcional para mostrar cifras (si falta o no hay permiso, no se muestran)."""

    def __init__(self, master, sesion, opciones, abrir, con=None):
        super().__init__(master)
        self._logo = None
        nombre = getattr(sesion, "nombre", None) or getattr(sesion, "usuario", "")
        rol = str(getattr(sesion, "rol", "")).capitalize()

        # --- banda de bienvenida
        banda = tk.Frame(self, bg=estilos.MENTA, highlightbackground=estilos.LINEA,
                         highlightthickness=1, padx=24, pady=18)
        banda.pack(fill="x")
        txt = tk.Frame(banda, bg=estilos.MENTA)
        txt.pack(side="left", fill="x", expand=True)
        ttk.Label(txt, text=f"Bienvenido, {nombre}", style="TarjetaTitulo.TLabel").pack(anchor="w")
        ttk.Label(txt, text=f"Rol: {rol}  ·  Inversiones Mining Casava E.I.R.L.",
                  style="TarjetaSub.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Label(txt, text="Elija una opción para comenzar.", style="TarjetaSub.TLabel").pack(anchor="w", pady=(2, 0))
        self._poner_logo(banda)

        # --- cifras (solo si hay conexión y permiso de lectura)
        cifras = self._cifras(con) if con else []
        if cifras:
            fila = ttk.Frame(self)
            fila.pack(fill="x", pady=(16, 0))
            for i, (valor, titulo) in enumerate(cifras):
                fila.columnconfigure(i, weight=1, uniform="cifra")
                c = tk.Frame(fila, bg=estilos.BLANCO, highlightbackground=estilos.LINEA,
                             highlightthickness=1, padx=12, pady=10)
                c.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0))
                tk.Label(c, text=str(valor), bg=estilos.BLANCO, fg=estilos.VERDE,
                         font=(estilos.FUENTE, 22, "bold")).pack()
                tk.Label(c, text=titulo, bg=estilos.BLANCO, fg=estilos.GRIS,
                         font=(estilos.FUENTE, 9)).pack()

        # --- accesos rápidos
        ttk.Label(self, text="Accesos rápidos", style="Titulo.TLabel").pack(anchor="w", pady=(20, 8))
        rejilla = ttk.Frame(self)
        rejilla.pack(fill="x")
        columnas = 3
        for i, (clave, texto) in enumerate(opciones):
            rejilla.columnconfigure(i % columnas, weight=1, uniform="acceso")
            self._tarjeta(rejilla, clave, texto, abrir).grid(
                row=i // columnas, column=i % columnas, sticky="nsew", padx=6, pady=6)

    def _poner_logo(self, banda):
        """Si existe assets/logo.png lo muestra a la derecha (PNG de unos 160 px de alto)."""
        ruta = config.raiz() / "assets" / "logo.png"
        try:
            self._logo = tk.PhotoImage(file=str(ruta))
        except Exception:
            return
        tk.Label(banda, image=self._logo, bg=estilos.MENTA).pack(side="right")

    @staticmethod
    def _cifras(con):
        res = []
        for titulo, tabla in (("Guías", "GUIA_DE_REMISION"), ("Empresas", "EMPRESA"),
                              ("Vehículos", "VEHICULO"), ("Conductores", "CONDUCTOR")):
            try:
                _, filas = consultar(con, f"SELECT COUNT(*) FROM {tabla}")
                res.append((filas[0][0], titulo))
            except Exception:
                return []          # sin permiso (p. ej. externo): no se muestran cifras
        return res

    def _tarjeta(self, padre, clave, texto, abrir):
        k = _norm(clave)
        t = tk.Frame(padre, bg=estilos.MENTA, highlightbackground=estilos.LINEA, highlightthickness=1,
                     padx=16, pady=14, cursor="hand2")
        cv = tk.Canvas(t, width=46, height=46, bg=estilos.MENTA, highlightthickness=0)
        cv.create_oval(2, 2, 44, 44, fill=estilos.VERDE_OSCURO, outline="")
        cv.create_text(23, 23, text=ICONO.get(k, "●"), fill="white", font=(estilos.FUENTE, 16))
        cv.pack(anchor="w")
        l1 = tk.Label(t, text=texto, bg=estilos.MENTA, fg=estilos.VERDE_OSCURO,
                      font=(estilos.FUENTE, 12, "bold"), anchor="w")
        l1.pack(anchor="w", pady=(8, 2))
        l2 = tk.Label(t, text=DESCRIPCION.get(k, ""), bg=estilos.MENTA, fg=estilos.GRIS,
                      font=(estilos.FUENTE, 9), wraplength=190, justify="left", anchor="w")
        l2.pack(anchor="w")
        for w in (t, cv, l1, l2):
            w.bind("<Button-1>", lambda e, c=clave: abrir(c))
            w.bind("<Enter>", lambda e, f=t: f.configure(highlightbackground=estilos.VERDE, highlightthickness=2))
            w.bind("<Leave>", lambda e, f=t: f.configure(highlightbackground=estilos.LINEA, highlightthickness=1))
        return t