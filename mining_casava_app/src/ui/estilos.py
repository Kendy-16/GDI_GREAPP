"""Estilos de la aplicación: paleta institucional (verde), Arial y botones uniformes."""
from tkinter import font as tkfont, ttk

VERDE_OSCURO = "#00402F"
VERDE = "#00BF72"
MENTA = "#E6F6EE"
LINEA = "#9EE0C0"
TEXTO = "#1B3A2F"
GRIS = "#4A6B5E"
AMBAR = "#C0762B"
ROJO = "#B00020"
BLANCO = "#FFFFFF"
FUENTE = "Arial"


def aplicar(root):
    """Llamar una vez, justo después de crear la ventana principal."""
    root.configure(bg=BLANCO)
    root.option_add("*Toplevel*background", BLANCO)          # ventanas secundarias en blanco
    root.option_add("*TCombobox*Listbox.background", BLANCO)
    root.option_add("*TCombobox*Listbox.foreground", TEXTO)
    root.option_add("*TCombobox*Listbox.selectBackground", VERDE)
    root.option_add("*TCombobox*Listbox.selectForeground", BLANCO)
    root.option_add("*TCombobox*Listbox.font", (FUENTE, 10))
    for nombre in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont", "TkCaptionFont"):
        try:
            tkfont.nametofont(nombre).configure(family=FUENTE, size=10)
        except Exception:
            pass

    st = ttk.Style(root)
    st.theme_use("clam")
    st.configure(".", background=BLANCO, foreground=TEXTO, font=(FUENTE, 10), bordercolor=LINEA,
                 lightcolor=BLANCO, darkcolor=BLANCO, troughcolor=MENTA, focuscolor=VERDE)

    # --- marcos y etiquetas
    st.configure("TFrame", background=BLANCO)
    st.configure("TLabel", background=BLANCO, foreground=TEXTO)
    st.configure("Titulo.TLabel", font=(FUENTE, 16, "bold"), foreground=VERDE_OSCURO)
    st.configure("Sub.TLabel", foreground=GRIS)
    st.configure("Error.TLabel", foreground=ROJO)
    st.configure("Campo.TLabel", foreground=GRIS, font=(FUENTE, 9))
    # variantes para la tarjeta menta del login
    st.configure("TarjetaTitulo.TLabel", background=MENTA, foreground=VERDE_OSCURO, font=(FUENTE, 15, "bold"))
    st.configure("TarjetaSub.TLabel", background=MENTA, foreground=GRIS)
    st.configure("TarjetaCampo.TLabel", background=MENTA, foreground=GRIS, font=(FUENTE, 9))
    st.configure("TarjetaError.TLabel", background=MENTA, foreground=ROJO)
    st.configure("TLabelframe", background=BLANCO, bordercolor=LINEA)
    st.configure("TLabelframe.Label", background=BLANCO, foreground=VERDE_OSCURO, font=(FUENTE, 10, "bold"))
    st.configure("TSeparator", background=LINEA)
    st.configure("TCheckbutton", background=BLANCO)

    # --- botones: gris (normal), verde (acción principal), rojo (eliminar)
    for nombre, color, hover in (("TButton", GRIS, "#3A574B"), ("Primario.TButton", VERDE, "#00A862"),
                                 ("Peligro.TButton", ROJO, "#8E0019")):
        st.configure(nombre, background=color, foreground=BLANCO, font=(FUENTE, 10, "bold"), padding=(14, 7),
                     borderwidth=1, relief="flat", bordercolor=color, lightcolor=color, darkcolor=color)
        st.map(nombre, background=[("disabled", "#C9D6D0"), ("pressed", hover), ("active", hover)],
               foreground=[("disabled", "#F4F8F6")], bordercolor=[("disabled", "#C9D6D0")],
               lightcolor=[("disabled", "#C9D6D0")], darkcolor=[("disabled", "#C9D6D0")])
    st.configure("Menu.TButton", background=MENTA, foreground=VERDE_OSCURO, anchor="w", padding=(12, 8),
                 font=(FUENTE, 10), bordercolor=LINEA, lightcolor=MENTA, darkcolor=MENTA)
    st.map("Menu.TButton", background=[("active", LINEA)])
    st.configure("MenuActivo.TButton", background=VERDE_OSCURO, foreground=BLANCO, anchor="w", padding=(12, 8),
                 font=(FUENTE, 10, "bold"), bordercolor=VERDE_OSCURO, lightcolor=VERDE_OSCURO, darkcolor=VERDE_OSCURO)
    st.map("MenuActivo.TButton", background=[("active", VERDE_OSCURO)])

    # --- campos
    campo = dict(fieldbackground=BLANCO, foreground=TEXTO, bordercolor=LINEA, lightcolor=LINEA,
                 darkcolor=LINEA, padding=5)
    st.configure("TEntry", **campo)
    st.configure("TCombobox", arrowcolor=VERDE_OSCURO, background=MENTA, **campo)
    st.map("TEntry", bordercolor=[("focus", VERDE)], lightcolor=[("focus", VERDE)],
           fieldbackground=[("readonly", MENTA), ("disabled", MENTA)])
    st.map("TCombobox", fieldbackground=[("readonly", BLANCO), ("disabled", MENTA)],
           bordercolor=[("focus", VERDE)], lightcolor=[("focus", VERDE)],
           selectbackground=[("readonly", BLANCO)], selectforeground=[("readonly", TEXTO)])

    # --- tablas y pestañas
    alto = max(26, int(26 * root.winfo_fpixels("1i") / 96))          # fila proporcional al zoom de Windows
    st.configure("Treeview", background=BLANCO, fieldbackground=BLANCO, foreground=TEXTO, rowheight=alto,
                 bordercolor=LINEA)
    st.configure("Treeview.Heading", background=VERDE_OSCURO, foreground=BLANCO, font=(FUENTE, 10, "bold"),
                 padding=6, relief="flat")
    st.map("Treeview.Heading", background=[("active", "#0A5A42")])
    st.map("Treeview", background=[("selected", VERDE)], foreground=[("selected", BLANCO)])
    st.configure("TNotebook", background=BLANCO, borderwidth=0, tabmargins=(0, 4, 0, 0))
    st.configure("TNotebook.Tab", background=MENTA, foreground=VERDE_OSCURO, padding=(16, 7), bordercolor=LINEA)
    st.map("TNotebook.Tab", background=[("selected", VERDE_OSCURO)], foreground=[("selected", BLANCO)])
    st.configure("TScrollbar", background=LINEA, troughcolor=MENTA, bordercolor=MENTA, arrowcolor=VERDE_OSCURO)


def rayado(tree):
    """Filas alternadas en blanco y menta (usar tags=('par',) en las filas pares)."""
    tree.tag_configure("par", background=MENTA)


def centrar(ventana, ancho, alto):
    """Centra la ventana y la limita al tamaño de la pantalla (para que no queden botones fuera)."""
    ventana.update_idletasks()
    sw, sh = ventana.winfo_screenwidth(), ventana.winfo_screenheight()
    ancho, alto = min(ancho, sw - 40), min(alto, sh - 90)
    ventana.geometry("%dx%d+%d+%d" % (ancho, alto, (sw - ancho) // 2, max(0, (sh - alto) // 2 - 20)))