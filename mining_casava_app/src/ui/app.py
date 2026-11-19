"""Ventana principal: administra el paso entre Login y Menu."""
import logging
import tkinter as tk

from .. import auth
from . import estilos
from .login import LoginFrame
from .menu import MenuFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mining Casava · Guías de Remisión Electrónica")
        estilos.aplicar(self)
        estilos.centrar(self, 1100, 700)
        self.minsize(900, 580)
        self.sesion = None
        self.protocol("WM_DELETE_WINDOW", self.salir)
        self.mostrar_login()

    def _limpiar(self):
        for w in self.winfo_children():
            w.destroy()

    def mostrar_login(self):
        self._limpiar()
        LoginFrame(self, self.al_ingresar).pack(fill="both", expand=True)

    def al_ingresar(self, sesion):
        self.sesion = sesion
        logging.info("Ingreso: %s (%s)", sesion.usuario, sesion.rol)
        self._limpiar()
        MenuFrame(self, sesion, self.cerrar_sesion).pack(fill="both", expand=True)

    def cerrar_sesion(self):
        if self.sesion:
            logging.info("Cierre de sesión: %s", self.sesion.usuario)
            auth.cerrar_sesion(self.sesion)
            self.sesion = None
        self.mostrar_login()

    def salir(self):
        if self.sesion:
            auth.cerrar_sesion(self.sesion)
        self.destroy()