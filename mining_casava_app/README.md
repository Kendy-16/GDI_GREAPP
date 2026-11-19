# Mining Casava · Guías de Remisión Electrónica (GRE)

Aplicativo de escritorio desarrollado con Python y Tkinter que utiliza MySQL como sistema gestor de base de datos.

## 1. Requisitos

- Windows 10 u 11 de 64 bits.
- MySQL Server 8.0 y MySQL Workbench.
- Para ejecutar desde el código fuente: Python 3.14 y las dependencias indicadas en `requirements.txt`.

## 2. Estructura del proyecto

```text
mining_casava_app/
├── main.py
├── prueba_conexion.py
├── construir_exe.bat
├── config.ini.example
├── sql/
├── src/
├── tests/
├── evidencias/
└── README.md
```

## 3. Preparar MySQL

En MySQL Workbench, ejecuta los scripts SQL en este orden: `A01`, `A02`, `A03`, `A04`, `A05` y `A06`. Verifica que MySQL Server esté iniciado y que se haya creado la base de datos `mining_casava`.

## 4. Ejecutar desde el código fuente

Desde una terminal abierta en esta carpeta:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copia `config.ini.example` y nombra la copia `config.ini`. Abre `config.ini` y verifica host, puerto, base de datos y credenciales. Después ejecuta:

```bat
python prueba_conexion.py
python main.py
```

## 5. Ejecutar la versión .exe descargada

**No abras el ejecutable suelto que está directamente en `dist/`.** Ese archivo no tiene su configuración en la misma carpeta.

La versión preparada para distribuir está dentro de:

```text
dist\MiningCasavaGRE_v1.0\MiningCasavaGRE.exe
```

Abre la carpeta `dist`, entra en `MiningCasavaGRE_v1.0` y ejecuta el archivo `MiningCasavaGRE.exe` que está allí. En esa misma carpeta deben permanecer `config.ini` y `config.ini.example`.

Si descargas `MiningCasavaGRE_v1.0.zip` desde GitHub Releases, descomprímelo primero. Luego abre la carpeta extraída y ejecuta `MiningCasavaGRE.exe`, sin separarlo de `config.ini`.

## 6. Configuración del ejecutable

El programa busca `config.ini` junto al ejecutable. Si aparece el mensaje **«No se encontró config.ini»**, comprueba lo siguiente:

1. Estás ejecutando `dist\MiningCasavaGRE_v1.0\MiningCasavaGRE.exe`, no el `.exe` suelto de `dist`.
2. `config.ini` está en la misma carpeta que el `.exe`.
3. El nombre es exactamente `config.ini`, no `config.ini.txt`.
4. El archivo contiene los datos correctos para conectarse a tu servidor MySQL.

## 7. Pruebas

Para ejecutar las pruebas automáticas desde el código fuente:

```bat
python tests/ejecutar_pruebas.py
```

Los resultados se guardan en `evidencias/pruebas/`.

## 8. Generar el ejecutable

Ejecuta `construir_exe.bat`. El paquete distribuible se genera en `dist\MiningCasavaGRE_v1.0\` y se comprime como `dist\MiningCasavaGRE_v1.0.zip`.

Al publicar en GitHub, se recomienda adjuntar el ZIP de la carpeta `MiningCasavaGRE_v1.0` en **Releases**. Indica siempre que se debe descomprimir y ejecutar el `.exe` que está junto a `config.ini`.
