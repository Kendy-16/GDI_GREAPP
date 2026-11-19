/* =====================================================================
   MODELO FISICO (3) - SCRIPT 01: CREACION
   Guia de Remision Electronica (GRE) - Inversiones Mining Casava E.I.R.L.
   Gestor: MySQL 8.0.46 (InnoDB) - Cliente: MySQL Workbench

   Como ejecutarlo en Workbench (para sacar las capturas por partes):
   selecciona UNA seccion, pulsa el rayo (Ctrl+Shift+Enter) y captura.

   Nota sobre nombres: se quitaron las tildes de tablas y columnas del
   diccionario (Serie_número -> Serie_numero, Nro_ítem -> Nro_item,
   Tipo_guía -> Tipo_guia) para evitar problemas de codificacion.
   Los valores de texto tambien van sin tilde ('Publico', no 'Público').
   ===================================================================== */


/* =====================================================================
   SECCION 0. ENTORNO
   ===================================================================== */
SELECT VERSION() AS version_mysql;
SHOW VARIABLES LIKE 'innodb_page_size';        -- debe dar 16384 (bloque de 16 KB)
SHOW VARIABLES LIKE 'default_storage_engine';  -- debe dar InnoDB


/* =====================================================================
   SECCION 1. CREACION DE LA BASE DE DATOS
   ===================================================================== */
DROP DATABASE IF EXISTS mining_casava;

CREATE DATABASE mining_casava
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE mining_casava;

SHOW DATABASES LIKE 'mining_casava';


/* =====================================================================
   SECCION 2. CREACION DE TABLAS (orden de dependencia)
   Primero las que no dependen de nadie, al final las hijas de la guia.
   ===================================================================== */

-- 2.1 EMPRESA ---------------------------------------------------------
CREATE TABLE EMPRESA (
    RUC          VARCHAR(11)  NOT NULL,
    Razon_Social VARCHAR(150) NOT NULL,
    CONSTRAINT pk_empresa PRIMARY KEY (RUC),
    CONSTRAINT ck_empresa_ruc   CHECK (REGEXP_LIKE(RUC, '^[0-9]{11}$')),
    -- mayusculas: se compara contra UPPER usando collation binaria
    CONSTRAINT ck_empresa_razon CHECK ((Razon_Social COLLATE utf8mb4_bin) = UPPER(Razon_Social))
) ENGINE=InnoDB;

-- 2.2 TRANSPORTISTA (1:1 con EMPRESA) -----------------------------------
CREATE TABLE TRANSPORTISTA (
    RUC_Transportista   VARCHAR(11) NOT NULL,
    Numero_registro_MTC VARCHAR(20) NOT NULL,
    CONSTRAINT pk_transportista PRIMARY KEY (RUC_Transportista),
    CONSTRAINT fk_transportista_empresa
        FOREIGN KEY (RUC_Transportista) REFERENCES EMPRESA (RUC),
    CONSTRAINT ck_transportista_mtc CHECK (REGEXP_LIKE(Numero_registro_MTC, '^[A-Za-z0-9]+$'))
) ENGINE=InnoDB;

-- 2.3 VEHICULO ----------------------------------------------------------
CREATE TABLE VEHICULO (
    Placa    VARCHAR(6)  NOT NULL,
    Nro_TUCE VARCHAR(20) NULL,          -- obligatorio si modalidad = Publico (regla de aplicacion)
    CONSTRAINT pk_vehiculo PRIMARY KEY (Placa),
    CONSTRAINT ck_vehiculo_placa CHECK (REGEXP_LIKE(Placa, '^[A-Z0-9]{6}$', 'c'))
) ENGINE=InnoDB;

-- 2.4 CONDUCTOR ---------------------------------------------------------
CREATE TABLE CONDUCTOR (
    DNI          VARCHAR(8)   NOT NULL,
    Nombre       VARCHAR(100) NOT NULL,
    Nro_Licencia VARCHAR(15)  NOT NULL,
    CONSTRAINT pk_conductor PRIMARY KEY (DNI),
    CONSTRAINT uq_conductor_licencia UNIQUE (Nro_Licencia),
    CONSTRAINT ck_conductor_dni    CHECK (REGEXP_LIKE(DNI, '^[0-9]{8}$')),
    CONSTRAINT ck_conductor_nombre CHECK ((Nombre COLLATE utf8mb4_bin) = UPPER(Nombre))
) ENGINE=InnoDB;

-- 2.5 PRODUCTO ----------------------------------------------------------
CREATE TABLE PRODUCTO (
    Id_producto          INT          NOT NULL AUTO_INCREMENT,
    Codigo_GTIN          VARCHAR(14)  NULL,
    Codigo_productoSUNAT VARCHAR(10)  NULL,
    Descripcion          VARCHAR(250) NOT NULL,
    Partida_arancelaria  VARCHAR(10)  NULL,
    Unidad_de_medida     VARCHAR(20)  NOT NULL,
    CONSTRAINT pk_producto PRIMARY KEY (Id_producto),
    CONSTRAINT ck_producto_gtin     CHECK (Codigo_GTIN IS NULL OR REGEXP_LIKE(Codigo_GTIN, '^[0-9]{1,14}$')),
    CONSTRAINT ck_producto_partida  CHECK (Partida_arancelaria IS NULL OR REGEXP_LIKE(Partida_arancelaria, '^[0-9]{10}$'))
) ENGINE=InnoDB;

-- 2.6 GUIA_DE_REMISION (la tabla mas grande) ----------------------------
CREATE TABLE GUIA_DE_REMISION (
    Serie_numero             VARCHAR(13)   NOT NULL,
    Tipo_guia                VARCHAR(13)   NOT NULL,
    Fecha                    DATE          NOT NULL,
    Hora                     TIME          NOT NULL,
    Motivo_traslado          VARCHAR(50)   NOT NULL,
    Fecha_inicio_traslado    DATE          NOT NULL,
    Observaciones            VARCHAR(250)  NULL,
    Punto_partida            VARCHAR(200)  NOT NULL,
    Punto_llegada            VARCHAR(200)  NOT NULL,
    Peso_bruto_total_carga   DECIMAL(12,3) NOT NULL,
    Unidad_medida_peso_bruto VARCHAR(3)    NOT NULL,
    Modalidad_traslado       VARCHAR(7)    NULL,
    RUC_Remitente            VARCHAR(11)   NOT NULL,
    RUC_Destinatario         VARCHAR(11)   NOT NULL,
    RUC_Transportista        VARCHAR(11)   NULL,
    RUC_PagadorFlete         VARCHAR(11)   NULL,
    RUC_Proveedor            VARCHAR(11)   NULL,
    Fecha_entrega_bienes_transportista DATE NULL,

    CONSTRAINT pk_guia PRIMARY KEY (Serie_numero),

    CONSTRAINT fk_guia_remitente     FOREIGN KEY (RUC_Remitente)     REFERENCES EMPRESA (RUC),
    CONSTRAINT fk_guia_destinatario  FOREIGN KEY (RUC_Destinatario)  REFERENCES EMPRESA (RUC),
    CONSTRAINT fk_guia_transportista FOREIGN KEY (RUC_Transportista) REFERENCES TRANSPORTISTA (RUC_Transportista),
    CONSTRAINT fk_guia_pagadorflete  FOREIGN KEY (RUC_PagadorFlete)  REFERENCES EMPRESA (RUC),
    CONSTRAINT fk_guia_proveedor     FOREIGN KEY (RUC_Proveedor)     REFERENCES EMPRESA (RUC),

    -- reglas de dominio
    CONSTRAINT ck_guia_serie   CHECK (REGEXP_LIKE(Serie_numero, '^[A-Z0-9]{4}-[0-9]{8}$', 'c')),
    CONSTRAINT ck_guia_tipo    CHECK (Tipo_guia IN ('Remitente', 'Transportista')),
    CONSTRAINT ck_guia_peso    CHECK (Peso_bruto_total_carga > 0),
    CONSTRAINT ck_guia_unidad  CHECK (Unidad_medida_peso_bruto IN ('TNE', 'KGM')),
    CONSTRAINT ck_guia_modal   CHECK (Modalidad_traslado IS NULL OR Modalidad_traslado IN ('Publico', 'Privado')),

    -- reglas condicionales del diccionario
    -- modalidad obligatoria si Tipo_guia = Remitente
    CONSTRAINT ck_guia_modalidad_oblig
        CHECK (Tipo_guia <> 'Remitente' OR Modalidad_traslado IS NOT NULL),
    -- si la modalidad es Publico: transportista y fecha de entrega obligatorios
    CONSTRAINT ck_guia_publico
        CHECK (Modalidad_traslado IS NULL OR Modalidad_traslado <> 'Publico'
               OR (RUC_Transportista IS NOT NULL AND Fecha_entrega_bienes_transportista IS NOT NULL)),
    -- si el motivo es Compra: proveedor obligatorio
    CONSTRAINT ck_guia_compra
        CHECK (Motivo_traslado <> 'Compra' OR RUC_Proveedor IS NOT NULL)
) ENGINE=InnoDB;

-- 2.7 DETALLE_GUIA (1:1 con la guia) --------------------------------------
CREATE TABLE DETALLE_GUIA (
    Serie_numero             VARCHAR(13) NOT NULL,
    Transbordo_programado    BOOLEAN     NOT NULL DEFAULT FALSE,
    Envases_vacios_retorno   BOOLEAN     NOT NULL DEFAULT FALSE,
    Traslado_cat_M1_L        BOOLEAN     NOT NULL DEFAULT FALSE,   -- solo guia Remitente
    Vehiculo_vacio_retorno   BOOLEAN     NULL     DEFAULT FALSE,   -- solo guia Transportista
    Transporte_Subcontratado BOOLEAN     NULL     DEFAULT FALSE,   -- solo guia Transportista
    CONSTRAINT pk_detalle PRIMARY KEY (Serie_numero),
    CONSTRAINT fk_detalle_guia FOREIGN KEY (Serie_numero) REFERENCES GUIA_DE_REMISION (Serie_numero)
) ENGINE=InnoDB;

-- 2.8 DOCUMENTO_RELACIONADO ----------------------------------------------
CREATE TABLE DOCUMENTO_RELACIONADO (
    Serie_numero   VARCHAR(13) NOT NULL,
    Nro_Documento  VARCHAR(20) NOT NULL,
    Tipo_Documento VARCHAR(20) NOT NULL,
    CONSTRAINT pk_documento PRIMARY KEY (Serie_numero, Nro_Documento),
    CONSTRAINT fk_documento_guia FOREIGN KEY (Serie_numero) REFERENCES GUIA_DE_REMISION (Serie_numero),
    CONSTRAINT ck_documento_tipo CHECK (Tipo_Documento IN ('Factura', 'Boleta')),
    CONSTRAINT ck_documento_nro  CHECK (REGEXP_LIKE(Nro_Documento, '^[A-Z0-9]{4}-[0-9]{1,8}$', 'c'))
) ENGINE=InnoDB;

-- 2.9 TRASLADO (guia + vehiculo + conductor) -----------------------------
CREATE TABLE TRASLADO (
    Serie_numero VARCHAR(13) NOT NULL,
    Placa        VARCHAR(6)  NOT NULL,
    DNI          VARCHAR(8)  NOT NULL,
    CONSTRAINT pk_traslado PRIMARY KEY (Serie_numero, Placa, DNI),
    CONSTRAINT fk_traslado_guia      FOREIGN KEY (Serie_numero) REFERENCES GUIA_DE_REMISION (Serie_numero),
    CONSTRAINT fk_traslado_vehiculo  FOREIGN KEY (Placa)        REFERENCES VEHICULO (Placa),
    CONSTRAINT fk_traslado_conductor FOREIGN KEY (DNI)          REFERENCES CONDUCTOR (DNI)
) ENGINE=InnoDB;

-- 2.10 BIEN_TRANSPORTADO ---------------------------------------------------
CREATE TABLE BIEN_TRANSPORTADO (
    Serie_numero    VARCHAR(13)   NOT NULL,
    Nro_item        INT           NOT NULL,
    Id_producto     INT           NOT NULL,
    Bien_normalizado BOOLEAN      NOT NULL DEFAULT FALSE,
    Cantidad        DECIMAL(12,2) NOT NULL,
    CONSTRAINT pk_bien PRIMARY KEY (Serie_numero, Nro_item),
    CONSTRAINT fk_bien_guia     FOREIGN KEY (Serie_numero) REFERENCES GUIA_DE_REMISION (Serie_numero),
    CONSTRAINT fk_bien_producto FOREIGN KEY (Id_producto)  REFERENCES PRODUCTO (Id_producto),
    CONSTRAINT ck_bien_item     CHECK (Nro_item >= 1),
    CONSTRAINT ck_bien_cantidad CHECK (Cantidad > 0)
) ENGINE=InnoDB;

-- Verificacion de la seccion 2
SHOW TABLES;
DESCRIBE GUIA_DE_REMISION;


/* =====================================================================
   SECCION 3. CREACION DE INDICES
   Correspondencia con el diseno de la Parte 1 (12 indices):

   Tipo        Tabla . campo                          Como se crea aqui
   ----------  -------------------------------------  ------------------------
   Primario    EMPRESA . RUC                          PRIMARY KEY (seccion 2)
   Primario    GUIA_DE_REMISION . Serie_numero        PRIMARY KEY (seccion 2)
   Compuesto   BIEN_TRANSPORTADO . (Serie, Nro_item)  PRIMARY KEY (seccion 2)
   Compuesto   DOCUMENTO . (Serie, Nro_Documento)     PRIMARY KEY (seccion 2)
   Compuesto   TRASLADO . (Serie, Placa, DNI)         PRIMARY KEY (seccion 2)
   Unico       VEHICULO . Placa                       PRIMARY KEY (seccion 2)
   Unico       CONDUCTOR . DNI                        PRIMARY KEY (seccion 2)
   Unico       PRODUCTO . Id_producto                 PRIMARY KEY (seccion 2)
   Unico       CONDUCTOR . Nro_Licencia               UNIQUE      (seccion 2)
   Secundario  GUIA_DE_REMISION . Fecha               CREATE INDEX (abajo)
   Secundario  GUIA_DE_REMISION . RUC_Remitente       CREATE INDEX (abajo)
   Secundario  BIEN_TRANSPORTADO . Id_producto        CREATE INDEX (abajo)

   En InnoDB la PK es la propia tabla (indice agrupado), por eso los
   primarios, compuestos y unicos-por-PK no son un indice aparte.
   Todos los indices de InnoDB son B+ tree, incluso los "unicos".
   ===================================================================== */

CREATE INDEX idx_guia_fecha          ON GUIA_DE_REMISION (Fecha);
CREATE INDEX idx_guia_ruc_remitente  ON GUIA_DE_REMISION (RUC_Remitente);
CREATE INDEX idx_bien_id_producto    ON BIEN_TRANSPORTADO (Id_producto);

-- OJO: MySQL crea solo un indice por cada clave foranea que no tenga uno
-- util. Los de RUC_Remitente e Id_producto se reemplazan al crear los de
-- arriba; los otros quedan (RUC_Destinatario, RUC_Transportista,
-- RUC_PagadorFlete, RUC_Proveedor, y Placa y DNI en TRASLADO). Se
-- veran en el listado y suman tamano: hay que tenerlos en cuenta al
-- comparar con el tamano estimado.


/* =====================================================================
   SECCION 4. VERIFICACION (capturas para la presentacion)
   ===================================================================== */

-- 4.1 Todos los indices de la base
SELECT TABLE_NAME AS tabla, INDEX_NAME AS indice,
       GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS columnas,
       IF(NON_UNIQUE = 0, 'UNICO', 'NO UNICO') AS unicidad,
       INDEX_TYPE AS estructura
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'mining_casava'
GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE, INDEX_TYPE
ORDER BY TABLE_NAME, INDEX_NAME;

-- 4.2 Claves foraneas
SELECT TABLE_NAME AS tabla, CONSTRAINT_NAME AS fk,
       COLUMN_NAME AS columna, REFERENCED_TABLE_NAME AS referencia
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'mining_casava' AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

-- 4.3 Restricciones CHECK
SELECT tc.TABLE_NAME AS tabla, cc.CONSTRAINT_NAME AS restriccion
FROM information_schema.CHECK_CONSTRAINTS cc
JOIN information_schema.TABLE_CONSTRAINTS tc
  ON tc.CONSTRAINT_SCHEMA = cc.CONSTRAINT_SCHEMA
 AND tc.CONSTRAINT_NAME   = cc.CONSTRAINT_NAME
WHERE cc.CONSTRAINT_SCHEMA = 'mining_casava'
ORDER BY tc.TABLE_NAME, cc.CONSTRAINT_NAME;
