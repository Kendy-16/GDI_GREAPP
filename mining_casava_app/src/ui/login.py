"""Pantalla de inicio de sesion. El rol lo determina la clave, no un selector."""
import tkinter as tk
from tkinter import ttk

from .. import auth, config
from ..db import DBError


class LoginFrame(ttk.Frame):
    def __init__(self, master, al_ingresar):
        super().__init__(master)
        self.al_ingresar = al_ingresar

        tarjeta = ttk.Frame(self, padding=30, relief="groove")
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(tarjeta, text="Guías de Remisión Electrónica",
                  font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 4))
        ttk.Label(tarjeta, text="Inversiones Mining Casava E.I.R.L.",
                  foreground="#555").grid(row=1, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(tarjeta, text="Usuario").grid(row=2, column=0, sticky="w", pady=4)
        self.usuario = ttk.Entry(tarjeta, width=28)
        self.usuario.grid(row=2, column=1, pady=4)

        ttk.Label(tarjeta, text="Clave").grid(row=3, column=0, sticky="w", pady=4)
        self.clave = ttk.Entry(tarjeta, width=28, show="•")
        self.clave.grid(row=3, column=1, pady=4)

        self.boton = ttk.Button(tarjeta, text="Ingresar", command=self.ingresar)
        self.boton.grid(row=4, column=0, columnspan=2, pady=(16, 6), sticky="ew")

        self.mensaje = ttk.Label(tarjeta, text="", foreground="#b00020", wraplength=300, justify="center")
        self.mensaje.grid(row=5, column=0, columnspan=2)

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
