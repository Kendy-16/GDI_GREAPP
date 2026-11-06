# Mining Casava · Guías de Remisión Electrónica (GRE)

Aplicativo de escritorio que consume la base de datos MySQL `mining_casava`.
Sin frameworks: **Python + Tkinter** (interfaz) y **mysql-connector-python** (conector).

## Requisitos
- Windows 10/11 (también corre en Linux/macOS)
- MySQL Server 8.0 y MySQL Workbench
- Python 3.10 o superior (con Tkinter, que viene incluido en el instalador oficial)

## Estructura
```
main.py                 punto de entrada de la aplicación
prueba_conexion.py      comprueba la conexión y las cuentas de cada rol
config.ini.example      plantilla de configuración (copiar como config.ini)
requirements.txt        dependencias
sql/                    scripts A01 a A06 (ver orden abajo)
src/
  config.py             lee config.ini
  db.py                 abre conexiones a MySQL y traduce errores
  auth.py               login y cierre de sesión (doble conexión por rol)
  reportes.py           catálogo de reportes y ejecución de procedimientos
  ui/                   ventanas Tkinter: app, login, menú por rol, reportes
docs/                   memoria descriptiva y manuales
evidencias/             capturas de pruebas y trazabilidad
```

## Puesta en marcha
1. **Base de datos:** en Workbench ejecutar, en este orden, los scripts de `sql/`:
   `A01` → `A02` → `A03` → `A04` → `A05` → `A06`
   (A02 carga los datos; A06 crea los roles y las cuentas; los triggers de A04 van después de A02 a propósito).
2. **Configuración:** copiar `config.ini.example` como `config.ini` y revisar host, puerto y claves.
3. **Entorno de Python** (en la terminal de VS Code, dentro de la carpeta del proyecto):
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Probar la conexión:** `python prueba_conexion.py`
5. **Abrir la aplicación:** `python main.py`

## Usuarios de prueba (creados por A02)
| Usuario | Clave | Rol |
|---|---|---|
| externo1 | Ext#2026 | Externo: reportes 01 y 07 |
| empleado1 | Emp#2026 | Empleado: consulta de todo |
| gestor1 | Ges#2026 | Gestor: alta, cambio y baja de registros |
| admin | Adm#2026 | Administrador: todos los permisos y auditoría |

## Cómo se conecta
1. La app abre una conexión con la cuenta `app_login`, que solo puede ejecutar `sp_login`.
2. `sp_login` valida usuario y clave (hash SHA-256 con sal) y devuelve el rol; deja el intento en `AUDITORIA_ACCESO`.
3. La app se reconecta con la cuenta de MySQL de ese rol (`u_externo`, `u_empleado`, `u_gestor` o `u_admin`).
4. Fija `@usuario_app` para que los triggers registren quién hizo cada cambio en `AUDITORIA_CAMBIOS`.

## Generar el ejecutable
```
pip install -r requirements-dev.txt
pyinstaller --onefile --windowed --name MiningCasavaGRE main.py
```
El `.exe` queda en `dist/`. Debe llevar al lado su archivo `config.ini`.

## Estado
| Módulo | Estado |
|---|---|
| Scripts SQL A01–A06 | Hechos |
| Conexión, login por rol, cierre de sesión | Hecho |
| Reportes 1–12 y auditoría (con exportar a CSV) | Hecho |
| Alta, cambio y baja de guías y maestras (pantallas) | Pendiente |
| Gestión de usuarios (pantalla) | Pendiente |
| Ejecutable y manual de usuario | Pendiente |

> Todos los datos son ficticios. `config.ini` no se sube a GitHub (está en `.gitignore`).
