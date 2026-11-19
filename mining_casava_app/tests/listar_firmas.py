"""Lista los procedimientos y sus parámetros (tests/listar_firmas.py).

Sirve para comprobar que los nombres que usa src/servicios coinciden con A03
y para la tabla de los 26 procedimientos de la presentación.
Ejecutar desde la raíz:  python tests/listar_firmas.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import db  # noqa: E402
from src.servicios.procs import consultar  # noqa: E402

con = db.conectar("u_admin")
_, filas = consultar(
    con,
    "SELECT r.ROUTINE_NAME, p.ORDINAL_POSITION, p.PARAMETER_MODE, p.PARAMETER_NAME "
    "FROM information_schema.ROUTINES r LEFT JOIN information_schema.PARAMETERS p "
    "ON p.SPECIFIC_SCHEMA = r.ROUTINE_SCHEMA AND p.SPECIFIC_NAME = r.SPECIFIC_NAME "
    "WHERE r.ROUTINE_SCHEMA = DATABASE() AND r.ROUTINE_TYPE = 'PROCEDURE' "
    "ORDER BY r.ROUTINE_NAME, p.ORDINAL_POSITION",
)
procs = {}
for nombre, _pos, modo, par in filas:
    procs.setdefault(nombre, []).append(f"{modo} {par}" if par else "")
os.makedirs("evidencias/pruebas", exist_ok=True)
with open("evidencias/pruebas/procedimientos.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["Procedimiento", "Parámetros"])
    for n, ps in procs.items():
        w.writerow([n, ", ".join(p for p in ps if p)])
        print(f"{n}({', '.join(p for p in ps if p)})")
print(f"\n{len(procs)} procedimientos")
con.close()
