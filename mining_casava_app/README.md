# Mining Casava · Guías de Remisión Electrónica (GRE)

Aplicativo de escritorio que consume la base de datos MySQL `mining_casava`.
Sin frameworks: **Python + Tkinter** (interfaz) y **mysql-connector-python** (conector).

## Requisitos
- Windows 10/11 (también corre en Linux/macOS)
- MySQL Server 8.0 y MySQL Workbench
- Python 3.14 (probado) con Tkinter, incluido en el instalador oficial

## Estructura
```
main.py                 punto de entrada (inicia log y manejador de errores)
prueba_conexion.py      comprueba la conexión y las cuentas de cada rol
construir_exe.bat       genera el .exe y el paquete para GitHub
config.ini.example      plantilla de configuración (copiar como config.ini)
sql/                    scripts A01 a A06
src/
  config.py             lee config.ini
  db.py                 conexiones a MySQL
  auth.py               login y cierre de sesión (doble conexión por rol)
  errores.py            traducción de errores de MySQL, log y manejador global
  reportes.py           12 reportes, auditoría y exportación a CSV
  servicios/            guias, maestras, usuarios y procs (llamadas a procedimientos)
  ui/                   ventanas Tkinter: login, menú, registros, guía, reportes, usuarios
tests/                  15 casos automáticos y ejecutor con evidencias
evidencias/pruebas/     resultados de cada corrida (CSV y TXT)
logs/                   app.log (se crea al ejecutar; no se sube a GitHub)
```

## Puesta en marcha
1. **Base de datos:** ejecutar en Workbench `A01` → `A02` → `A03` → `A04` → `A05` → `A06`.
2. **Configuración:** copiar `config.ini.example` como `config.ini` y revisar host, puerto y claves.
3. **Entorno:**
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
| admin | Adm#2026 | Administrador: todos los permisos, usuarios y auditoría |

## Cómo se conecta
1. La app abre una conexión con `app_login`, que solo puede ejecutar `sp_login`.
2. `sp_login` valida usuario y clave (SHA-256 con sal), devuelve el rol y registra el intento en `AUDITORIA_ACCESO`. Cinco fallos seguidos bloquean la cuenta.
3. La app se reconecta con la cuenta de MySQL de ese rol (`u_externo`, `u_empleado`, `u_gestor` o `u_admin`).
4. Fija `@usuario_app` para que los triggers registren quién hizo cada cambio en `AUDITORIA_CAMBIOS`.

## Pruebas
```
python tests/ejecutar_pruebas.py
```
Corre los 15 casos (CRUD por rol, reglas de la base, permisos, usuarios y bloqueo) y guarda `casos_<fecha>.csv` y `resultado_<fecha>.txt` en `evidencias/pruebas/`.

## Generar el ejecutable
Doble clic en `construir_exe.bat` (o desde la terminal, dentro de esta carpeta). Usa PyInstaller 6.15 o superior, que es la primera versión compatible con Python 3.14.
Resultado:
- `dist\MiningCasavaGRE_v1.0\` con el `.exe`, `config.ini`, `config.ini.example` y `LEEME.txt`
- `dist\MiningCasavaGRE_v1.0.zip` para subir a GitHub como *Release*

El `.exe` necesita su `config.ini` en la misma carpeta y MySQL con los scripts ya ejecutados.

## Estado
| Componente | Estado |
|---|---|
| Base de datos (A01–A06) | Hecho |
| Backend (config, db, auth, servicios, reportes, errores) | Hecho |
| Frontend (8 pantallas) | Funcional; estética en ajuste |
| Pruebas automáticas (15/15) | Hecho |
| Ejecutable y GitHub | Hecho al publicar el Release |
| Informe, memoria y manual | En preparación |

