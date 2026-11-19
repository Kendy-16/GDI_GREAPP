# Mining Casava GRE · Guías de Remisión Electrónica

Aplicativo de escritorio para gestionar las Guías de Remisión Electrónica de **Inversiones Mining Casava E.I.R.L.**

## IMPORTANTE: cómo abrir el ejecutable descargado

Si descargaste el repositorio como ZIP desde GitHub, **no ejecutes el archivo `MiningCasavaGRE.exe` que aparece directamente dentro de `mining_casava_app/dist/`**. Ese es un ejecutable suelto y no tiene al lado su archivo de configuración.

Para abrir la versión empaquetada correctamente:

1. Descomprime el ZIP del repositorio.
2. Abre `GDI_GREAPP-main/mining_casava_app/dist/`.
3. Entra en la carpeta `MiningCasavaGRE_v1.0/`.
4. Comprueba que dentro estén `MiningCasavaGRE.exe` y `config.ini`.
5. Ejecuta **ese** `MiningCasavaGRE.exe`.

La ruta completa será:

```text
GDI_GREAPP-main
└── mining_casava_app
    └── dist
        └── MiningCasavaGRE_v1.0
            ├── MiningCasavaGRE.exe   <-- EJECUTAR ESTE
            ├── config.ini            <-- debe estar junto al .exe
            ├── config.ini.example
            └── LEEME.txt
```

También puedes descargar `MiningCasavaGRE_v1.0.zip` desde la sección **Releases** de GitHub. En ese caso, descomprime ese ZIP y ejecuta el `.exe` que queda junto a `config.ini`.

> Regla importante: el archivo `config.ini` debe permanecer en la misma carpeta que `MiningCasavaGRE.exe`. No muevas el `.exe` por separado.

## Requisitos previos

- Windows 10 u 11 de 64 bits.
- MySQL Server 8.0 instalado y en ejecución.
- Base de datos `mining_casava` creada y configurada mediante los scripts SQL A01–A06, en ese orden.

## Preparar la base de datos

Abre MySQL Workbench y ejecuta los scripts `A01` → `A02` → `A03` → `A04` → `A05` → `A06`. Los scripts se encuentran en el repositorio y en `mining_casava_app/sql/`.

## Configuración

El paquete del ejecutable incluye `config.ini` y `config.ini.example`. Antes de iniciar, abre `config.ini` y verifica el host, puerto, nombre de base de datos y las credenciales de las cuentas MySQL. Los valores deben corresponder con la instalación local y con los usuarios creados por los scripts SQL.

Si por alguna razón falta `config.ini`, haz una copia de `config.ini.example`, renómbrala exactamente como `config.ini` y completa los datos de conexión. Asegúrate de que Windows no haya agregado la extensión `.txt`.

## Ejecutar desde el código fuente

Consulta [`mining_casava_app/README.md`](mining_casava_app/README.md) para instalar dependencias, configurar Python, probar la conexión y ejecutar `main.py`.

## Contenido del repositorio

- `mining_casava_app/`: código fuente, configuración de ejemplo, scripts SQL, pruebas y documentación.
- `backups/`: respaldos de la base de datos.
- `A01`–`A06`: scripts SQL de creación y configuración.

## Funcionalidades principales

- Gestión de guías, ítems, traslados y documentos relacionados.
- Gestión de empresa, transportista, vehículo, conductor, producto y usuarios.
- Reportes con filtros y exportación a CSV.
- Acceso diferenciado según el rol de usuario.
- Auditoría de accesos y cambios.
