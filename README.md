# GDI_GREAPP · Guías de Remisión Electrónica

Aplicativo de escritorio para gestionar las guías de remisión electrónicas de **Inversiones Mining Casava E.I.R.L.**
Curso Gestión de Datos e Información · UCSM · EPIS.

- **Base de datos:** MySQL 8.0 (`mining_casava`) con procedimientos almacenados, triggers y roles.
- **Backend y frontend:** Python + Tkinter, sin frameworks (solo `mysql-connector-python`).
- **Ejecutable:** `MiningCasavaGRE.exe` generado con PyInstaller (ver *Releases*).

> Todos los datos son ficticios.

## Qué hace
- Alta, cambio y baja de guías (con ítems, traslados y documentos) y de empresa, transportista, vehículo, conductor, producto y usuarios, **solo mediante procedimientos almacenados**.
- 12 reportes (9 con JOIN) con filtros y exportación a CSV.
- 4 roles según la clave: **externo, empleado, gestor y administrador**, con permisos reales de MySQL.
- Auditoría de ingresos y trazabilidad de cada cambio (valores antes y después) mediante triggers.

## Contenido del repositorio
```
mining_casava_app/        código del aplicativo, scripts SQL, pruebas y evidencias
backups/                  respaldo de la base de datos
A01 … A06 (*.sql)         scripts de la base de datos (copia en mining_casava_app/sql/)
```

## Puesta en marcha rápida
1. Ejecutar en MySQL Workbench `A01` → `A02` → `A03` → `A04` → `A05` → `A06`.
2. Copiar `mining_casava_app/config.ini.example` como `config.ini`.
3. En `mining_casava_app/`:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```
4. O descargar el ejecutable desde **Releases** (instrucciones en el `LEEME.txt` incluido).

Detalles de uso, pruebas y generación del ejecutable: [`mining_casava_app/README.md`](mining_casava_app/README.md).

## Integrantes
Benites Castro, A. · Limache Quispe, F. · Mancilla Neyra, S. · Ramos Rios, K.
