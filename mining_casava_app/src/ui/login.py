"""Pantalla de inicio de sesion. El rol lo determina la clave, no un selector."""
import tkinter as tk
from tkinter import ttk

from .. import auth, config
from ..db import DBError
from . import estilos


class LoginFrame(ttk.Frame):
    def __init__(self, master, al_ingresar):
        super().__init__(master)
        self.al_ingresar = al_ingresar

        tarjeta = tk.Frame(self, bg=estilos.MENTA, highlightbackground=estilos.LINEA,
                           highlightthickness=1, padx=44, pady=34)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(tarjeta, text="Guías de Remisión Electrónica", style="TarjetaTitulo.TLabel").pack()
        ttk.Label(tarjeta, text="Inversiones Mining Casava E.I.R.L.", style="TarjetaSub.TLabel").pack(pady=(2, 20))

        ttk.Label(tarjeta, text="Usuario", style="TarjetaCampo.TLabel").pack(anchor="w")
        self.usuario = ttk.Entry(tarjeta, width=34)
        self.usuario.pack(fill="x", pady=(2, 12))

        ttk.Label(tarjeta, text="Clave", style="TarjetaCampo.TLabel").pack(anchor="w")
        self.clave = ttk.Entry(tarjeta, width=34, show="•")
        self.clave.pack(fill="x", pady=(2, 18))

        self.boton = ttk.Button(tarjeta, text="Ingresar", style="Primario.TButton", command=self.ingresar)
        self.boton.pack(fill="x")

        self.mensaje = ttk.Label(tarjeta, text="", style="TarjetaError.TLabel", wraplength=300, justify="center")
        self.mensaje.pack(pady=(12, 0))

        self.usuario.focus()
        self.usuario.bind("<Return>", lambda e: self.clave.focus())
        self.clave.bind("<Return>", lambda e: self.ingresar())

    def ingresar(self):
        self.boton.state(["disabled"])
        self.mensaje.config(text="")
        self.update_idletasks()
        try:
            sesion = auth.iniciar_sesion(self.usuario.get(), self.clave.get())
        except (auth.AuthError, DBError, config.ConfigError) as e:
            self.mensaje.config(text=str(e))
            self.clave.delete(0, "end")
            self.boton.state(["!disabled"])
            return
        self.al_ingresar(sesion)