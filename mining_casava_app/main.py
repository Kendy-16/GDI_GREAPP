"""Punto de entrada del aplicativo: python main.py  (o MiningCasavaGRE.exe)"""
import logging
import tkinter as tk
from tkinter import messagebox

from src import config, errores


def _nitidez():
    """En Windows evita que el texto se vea borroso con zoom de pantalla (125 %, 150 %)."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def _aviso(titulo, texto):
    raiz = tk.Tk()
    raiz.withdraw()
    messagebox.showerror(titulo, texto)
    raiz.destroy()


def main():
    errores.configurar_log(str(config.raiz() / "logs"))
    logging.info("Aplicación iniciada")
    _nitidez()
    try:
        from src.ui.app import App
        app = App()
    except Exception as exc:                      # error al abrir la ventana
        errores.registrar_error("inicio", exc)
        _aviso("Mining Casava", "No se pudo iniciar el aplicativo.\n\n" + errores.traducir(exc))
        return
    errores.instalar_manejador(app)               # un error en un boton ya no cierra la ventana
    app.mainloop()
    logging.info("Aplicación cerrada")


if __name__ == "__main__":
    main()