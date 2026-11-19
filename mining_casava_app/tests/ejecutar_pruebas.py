"""Corre las pruebas y guarda la evidencia (tests/ejecutar_pruebas.py).

Genera en evidencias/pruebas/: resultado_<fecha>.txt y casos_<fecha>.csv
(ID, descripción, resultado, detalle), listo para la tabla del informe.
Ejecutar desde la raíz:  python tests/ejecutar_pruebas.py
"""
import csv
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import test_crud  # noqa: E402


class Resultado(unittest.TextTestResult):
    filas = []

    def _add(self, t, estado, detalle=""):
        self.filas.append((t.id().split(".")[-1], t.shortDescription() or "", estado, detalle))

    def addSuccess(self, t):
        super().addSuccess(t)
        self._add(t, "OK")

    def addFailure(self, t, err):
        super().addFailure(t, err)
        self._add(t, "FALLO", str(err[1]))

    def addError(self, t, err):
        super().addError(t, err)
        self._add(t, "ERROR", str(err[1]))

    def addSkip(self, t, reason):
        super().addSkip(t, reason)
        self._add(t, "OMITIDA", reason)


if __name__ == "__main__":
    os.makedirs("evidencias/pruebas", exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"evidencias/pruebas/resultado_{sello}.txt", "w", encoding="utf-8") as fh:
        runner = unittest.TextTestRunner(stream=fh, verbosity=2, resultclass=Resultado)
        res = runner.run(unittest.defaultTestLoader.loadTestsFromModule(test_crud))
    with open(f"evidencias/pruebas/casos_{sello}.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["ID", "Descripción", "Resultado", "Detalle"])
        w.writerows(sorted(Resultado.filas))
    for f in sorted(Resultado.filas):
        print(f[0], f[2], "-", f[1])
    print(f"\n{res.testsRun} pruebas · {len(res.failures)} fallos · {len(res.errors)} errores")
