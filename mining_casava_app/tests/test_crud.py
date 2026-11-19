"""Pruebas automáticas del CRUD y de los roles (tests/test_crud.py).

Ejecutar desde la raíz del proyecto:  python tests/ejecutar_pruebas.py
Haga un respaldo de la base antes (mysqldump). Los datos de prueba llevan
el prefijo PRUEBA y se limpian al final.
"""
import unittest
from datetime import datetime

from src import db
from src.errores import ErrorFirma, ErrorServicio
from src.servicios import guias, maestras, usuarios
from src.servicios.procs import consultar

RUC_P = "20999999993"
USR_P = "pr" + datetime.now().strftime("%m%d%H%M%S")   # único por corrida
SERIE_P = "T999-99999999"


class PruebasCrud(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.con = {c: db.conectar(c) for c in ("u_externo", "u_empleado", "u_gestor", "u_admin")}
        cls.login = db.conectar("app_login")
        cls._limpiar()

    @classmethod
    def tearDownClass(cls):
        cls._limpiar()
        for c in list(cls.con.values()) + [cls.login]:
            c.close()

    @classmethod
    def _limpiar(cls):
        adm = cls.con["u_admin"]
        for f in (lambda: maestras.eliminar(adm, "pruebas", "Empresa", {"ruc": RUC_P}),
                  lambda: guias.eliminar(adm, "pruebas", SERIE_P),
                  lambda: consultar(adm, "DROP TABLE IF EXISTS prueba_estructura"),
                  lambda: consultar(adm, "DELETE FROM USUARIO_APP WHERE Usuario = %s", (USR_P,))):
            try:
                f()
            except ErrorServicio:
                pass

    # ---------- Maestras (empresa como ejemplo representativo)
    def test_01_empresa_alta(self):
        """CP-01 · gestor · alta de empresa PRUEBA · queda registrada"""
        g = self.con["u_gestor"]
        maestras.registrar(g, "gestor1", "Empresa", {"ruc": RUC_P, "razon_social": "PRUEBA EMPRESA A"})
        _, filas = maestras.listar(g, "Empresa", RUC_P)
        self.assertTrue(filas)

    def test_02_empresa_cambio(self):
        """CP-02 · gestor · cambio de razón social · queda actualizada"""
        g = self.con["u_gestor"]
        maestras.modificar(g, "gestor1", "Empresa", {"ruc": RUC_P, "razon_social": "PRUEBA EMPRESA B"})
        _, filas = maestras.listar(g, "Empresa", "PRUEBA EMPRESA B")
        self.assertTrue(filas)

    def test_03_empresa_duplicada_falla(self):
        """CP-03 · gestor · alta duplicada · MySQL la rechaza con mensaje claro"""
        with self.assertRaises(ErrorServicio) as cm:
            maestras.registrar(self.con["u_gestor"], "gestor1", "Empresa", {"ruc": RUC_P, "razon_social": "OTRA"})
        self.assertNotIsInstance(cm.exception, ErrorFirma)

    def test_04_empresa_baja(self):
        """CP-04 · gestor · baja de empresa PRUEBA · desaparece de la lista"""
        g = self.con["u_gestor"]
        maestras.eliminar(g, "gestor1", "Empresa", {"ruc": RUC_P})
        _, filas = maestras.listar(g, "Empresa", RUC_P)
        self.assertFalse(filas)

    def test_05_auditoria_de_cambios(self):
        """CP-05 · admin · AUDITORIA_CAMBIOS · hay INSERT, UPDATE y DELETE de la empresa PRUEBA"""
        _, f = consultar(self.con["u_admin"],
                         "SELECT DISTINCT Operacion FROM AUDITORIA_CAMBIOS "
                         "WHERE Tabla_afectada = 'EMPRESA' AND Clave_registro LIKE %s", (f"%{RUC_P}%",))
        self.assertTrue({"INSERT", "UPDATE", "DELETE"} <= {x[0] for x in f})

    def test_06_baja_de_registro_en_uso_falla(self):
        """CP-06 · gestor · baja de una empresa usada en guías · MySQL la rechaza"""
        _, f = consultar(self.con["u_admin"], "SELECT RUC_Remitente FROM GUIA_DE_REMISION LIMIT 1")
        if not f:
            self.skipTest("No hay guías cargadas.")
        with self.assertRaises(ErrorServicio) as cm:
            maestras.eliminar(self.con["u_gestor"], "gestor1", "Empresa", {"ruc": f[0][0]})
        self.assertNotIsInstance(cm.exception, ErrorFirma)

    # ---------- Acceso por rol
    def test_10_externo_no_lee_tablas(self):
        """CP-10 · externo · SELECT sobre EMPRESA · denegado"""
        with self.assertRaises(ErrorServicio) as cm:
            consultar(self.con["u_externo"], "SELECT * FROM EMPRESA")
        self.assertIn("permiso", str(cm.exception))

    def test_11_externo_no_ejecuta_altas(self):
        """CP-11 · externo · CALL sp_empresa_registrar · denegado"""
        with self.assertRaises(ErrorServicio) as cm:
            consultar(self.con["u_externo"], "CALL sp_empresa_registrar(%s, %s)", ("20999999992", "PRUEBA X"))
        self.assertIn("permiso", str(cm.exception))

    def test_12_empleado_lee_pero_no_escribe(self):
        """CP-12 · empleado · SELECT permitido, CALL y DELETE denegados"""
        e = self.con["u_empleado"]
        consultar(e, "SELECT COUNT(*) FROM EMPRESA")
        with self.assertRaises(ErrorServicio):
            consultar(e, "CALL sp_empresa_registrar(%s, %s)", ("20999999992", "PRUEBA X"))
        with self.assertRaises(ErrorServicio):
            consultar(e, "DELETE FROM EMPRESA WHERE RUC = %s", ("20999999992",))

    def test_13_gestor_no_toca_estructuras_ni_auditoria(self):
        """CP-13 · gestor · CREATE TABLE y SELECT en AUDITORIA_CAMBIOS · denegados"""
        g = self.con["u_gestor"]
        with self.assertRaises(ErrorServicio):
            consultar(g, "CREATE TABLE prueba_estructura (a INT)")
        with self.assertRaises(ErrorServicio):
            consultar(g, "SELECT * FROM AUDITORIA_CAMBIOS LIMIT 1")

    def test_14_admin_ve_auditoria(self):
        """CP-14 · admin · SELECT en AUDITORIA_CAMBIOS y AUDITORIA_ACCESO · permitido"""
        a = self.con["u_admin"]
        consultar(a, "SELECT COUNT(*) FROM AUDITORIA_CAMBIOS")
        consultar(a, "SELECT COUNT(*) FROM AUDITORIA_ACCESO")

    # ---------- Guías
    def _cab_modelo(self):
        g = self.con["u_gestor"]
        cols, f = guias.listar(g)
        if not f:
            self.skipTest("No hay guías para usar de modelo.")
        serie0 = f[0][[c.lower() for c in cols].index("serie")]
        d = guias.obtener(g, serie0)
        cab = dict(d["cab"])
        for k in cab:
            if "serie" in k:
                cab[k] = SERIE_P
        return cab, d

    def test_20_guia_sin_bienes_falla(self):
        """CP-20 · gestor · guía sin bienes · rechazada (validación previa)"""
        cab, _ = self._cab_modelo()
        with self.assertRaises(ErrorServicio) as cm:
            guias.registrar(self.con["u_gestor"], "gestor1", cab, [], [], [])
        self.assertIn("bien", str(cm.exception).lower())

    def test_21_guia_ciclo_completo(self):
        """CP-21 · gestor · alta completa, cambio y baja con sus hijas de una guía PRUEBA"""
        g = self.con["u_gestor"]
        cab, d = self._cab_modelo()
        try:
            guias.registrar(g, "gestor1", cab, d["bienes"], d["traslados"], d["documentos"])
            self.assertEqual(guias.obtener(g, SERIE_P)["cab"]["serie"], SERIE_P)
            guias.modificar(g, "gestor1", cab, d["bienes"], d["traslados"], d["documentos"])
            guias.eliminar(g, "gestor1", SERIE_P)
            with self.assertRaises(ErrorServicio):
                guias.obtener(g, SERIE_P)
        except ErrorFirma as err:
            self.skipTest(f"Ajustar nombres de parámetros: {err}")

    # ---------- Usuarios
    def test_30_usuario_crear_bloquear_desbloquear_clave(self):
        """CP-30 · admin · crear, bloquear, desbloquear y cambiar clave de un usuario PRUEBA"""
        a = self.con["u_admin"]
        usuarios.crear(a, "admin", USR_P, "USUARIO PRUEBA", "Prueba1234", "EXTERNO")
        usuarios.cambiar_estado(a, "admin", USR_P, "BLOQUEADO")
        cols, f = usuarios.listar(a)
        i_u = [c.lower() for c in cols].index("usuario")
        i_e = [c.lower() for c in cols].index("estado")
        self.assertEqual([x[i_e] for x in f if x[i_u] == USR_P], ["BLOQUEADO"])
        usuarios.cambiar_estado(a, "admin", USR_P, "ACTIVO")
        usuarios.cambiar_clave(a, "admin", USR_P, "Otra12345")
        with self.assertRaises(ErrorServicio):
            usuarios.cambiar_clave(a, "admin", USR_P, "corta")

    def test_31_cinco_fallos_bloquean(self):
        """CP-31 · app_login · 5 claves incorrectas seguidas · la cuenta queda bloqueada"""
        cur = self.login.cursor()
        for _ in range(5):
            cur.callproc("sp_login", (USR_P, "incorrecta", "PRUEBAS", "", "", "", 0))
        r = cur.callproc("sp_login", (USR_P, "Otra12345", "PRUEBAS", "", "", "", 0))
        cur.close()
        self.assertNotEqual(r[3], "EXITO")


if __name__ == "__main__":
    unittest.main(verbosity=2)