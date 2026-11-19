/* =====================================================================
   APLICATIVO - SCRIPT A04: TRIGGERS
   Base: mining_casava - ejecutar DESPUES de A02 y A03.
   (Los triggers van despues de cargar los datos para que la carga inicial
    no llene AUDITORIA_CAMBIOS.)

   PARTE 1. TRAZABILIDAD: 33 triggers (11 tablas x INSERT, UPDATE, DELETE).
   Cada uno escribe en AUDITORIA_CAMBIOS: tabla, operacion, clave del
   registro, valores ANTES y DESPUES (JSON), usuario de la aplicacion y
   usuario de MySQL. Como el borrado es fisico, el trigger DELETE guarda
   la fila completa que se elimino.
     - El usuario de la aplicacion llega por la variable de sesion @usuario_app,
       que la app fija con  SET @usuario_app = '<usuario>'  al iniciar sesion.
       Si no existe, se registra 'SIN_SESION'.
     - En USUARIO_APP nunca se guarda Salt ni Clave_hash.
     - El trigger UPDATE solo registra si algun valor cambio de verdad.

   PARTE 2. VALIDACIONES Y SEGURIDAD: reglas que el modelo dejo como
   "regla de aplicacion" y proteccion de las tablas de auditoria.

   EJECUCION EN WORKBENCH: usa DELIMITER $$ (ya incluido); ejecutar completo.
   ===================================================================== */

USE mining_casava;

DELIMITER $$

/* ===================== PARTE 1. TRAZABILIDAD ===================== */

-- EMPRESA
DROP TRIGGER IF EXISTS trg_empresa_ai$$
CREATE TRIGGER trg_empresa_ai AFTER INSERT ON EMPRESA FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('EMPRESA', 'INSERT', CONCAT_WS('|', NEW.RUC), NULL, JSON_OBJECT('RUC', NEW.RUC, 'Razon_Social', NEW.Razon_Social), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_empresa_au$$
CREATE TRIGGER trg_empresa_au AFTER UPDATE ON EMPRESA FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('RUC', OLD.RUC, 'Razon_Social', OLD.Razon_Social);
    SET v_despues = JSON_OBJECT('RUC', NEW.RUC, 'Razon_Social', NEW.Razon_Social);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('EMPRESA', 'UPDATE', CONCAT_WS('|', NEW.RUC), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_empresa_ad$$
CREATE TRIGGER trg_empresa_ad AFTER DELETE ON EMPRESA FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('EMPRESA', 'DELETE', CONCAT_WS('|', OLD.RUC), JSON_OBJECT('RUC', OLD.RUC, 'Razon_Social', OLD.Razon_Social), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- TRANSPORTISTA
DROP TRIGGER IF EXISTS trg_transportista_ai$$
CREATE TRIGGER trg_transportista_ai AFTER INSERT ON TRANSPORTISTA FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('TRANSPORTISTA', 'INSERT', CONCAT_WS('|', NEW.RUC_Transportista), NULL, JSON_OBJECT('RUC_Transportista', NEW.RUC_Transportista, 'Numero_registro_MTC', NEW.Numero_registro_MTC), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_transportista_au$$
CREATE TRIGGER trg_transportista_au AFTER UPDATE ON TRANSPORTISTA FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('RUC_Transportista', OLD.RUC_Transportista, 'Numero_registro_MTC', OLD.Numero_registro_MTC);
    SET v_despues = JSON_OBJECT('RUC_Transportista', NEW.RUC_Transportista, 'Numero_registro_MTC', NEW.Numero_registro_MTC);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('TRANSPORTISTA', 'UPDATE', CONCAT_WS('|', NEW.RUC_Transportista), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_transportista_ad$$
CREATE TRIGGER trg_transportista_ad AFTER DELETE ON TRANSPORTISTA FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('TRANSPORTISTA', 'DELETE', CONCAT_WS('|', OLD.RUC_Transportista), JSON_OBJECT('RUC_Transportista', OLD.RUC_Transportista, 'Numero_registro_MTC', OLD.Numero_registro_MTC), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- VEHICULO
DROP TRIGGER IF EXISTS trg_vehiculo_ai$$
CREATE TRIGGER trg_vehiculo_ai AFTER INSERT ON VEHICULO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('VEHICULO', 'INSERT', CONCAT_WS('|', NEW.Placa), NULL, JSON_OBJECT('Placa', NEW.Placa, 'Nro_TUCE', NEW.Nro_TUCE), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_vehiculo_au$$
CREATE TRIGGER trg_vehiculo_au AFTER UPDATE ON VEHICULO FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('Placa', OLD.Placa, 'Nro_TUCE', OLD.Nro_TUCE);
    SET v_despues = JSON_OBJECT('Placa', NEW.Placa, 'Nro_TUCE', NEW.Nro_TUCE);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('VEHICULO', 'UPDATE', CONCAT_WS('|', NEW.Placa), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_vehiculo_ad$$
CREATE TRIGGER trg_vehiculo_ad AFTER DELETE ON VEHICULO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('VEHICULO', 'DELETE', CONCAT_WS('|', OLD.Placa), JSON_OBJECT('Placa', OLD.Placa, 'Nro_TUCE', OLD.Nro_TUCE), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- CONDUCTOR
DROP TRIGGER IF EXISTS trg_conductor_ai$$
CREATE TRIGGER trg_conductor_ai AFTER INSERT ON CONDUCTOR FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('CONDUCTOR', 'INSERT', CONCAT_WS('|', NEW.DNI), NULL, JSON_OBJECT('DNI', NEW.DNI, 'Nombre', NEW.Nombre, 'Nro_Licencia', NEW.Nro_Licencia), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_conductor_au$$
CREATE TRIGGER trg_conductor_au AFTER UPDATE ON CONDUCTOR FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('DNI', OLD.DNI, 'Nombre', OLD.Nombre, 'Nro_Licencia', OLD.Nro_Licencia);
    SET v_despues = JSON_OBJECT('DNI', NEW.DNI, 'Nombre', NEW.Nombre, 'Nro_Licencia', NEW.Nro_Licencia);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('CONDUCTOR', 'UPDATE', CONCAT_WS('|', NEW.DNI), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_conductor_ad$$
CREATE TRIGGER trg_conductor_ad AFTER DELETE ON CONDUCTOR FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('CONDUCTOR', 'DELETE', CONCAT_WS('|', OLD.DNI), JSON_OBJECT('DNI', OLD.DNI, 'Nombre', OLD.Nombre, 'Nro_Licencia', OLD.Nro_Licencia), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- PRODUCTO
DROP TRIGGER IF EXISTS trg_producto_ai$$
CREATE TRIGGER trg_producto_ai AFTER INSERT ON PRODUCTO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('PRODUCTO', 'INSERT', CONCAT_WS('|', NEW.Id_producto), NULL, JSON_OBJECT('Id_producto', NEW.Id_producto, 'Codigo_GTIN', NEW.Codigo_GTIN, 'Codigo_productoSUNAT', NEW.Codigo_productoSUNAT, 'Descripcion', NEW.Descripcion, 'Partida_arancelaria', NEW.Partida_arancelaria, 'Unidad_de_medida', NEW.Unidad_de_medida), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_producto_au$$
CREATE TRIGGER trg_producto_au AFTER UPDATE ON PRODUCTO FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('Id_producto', OLD.Id_producto, 'Codigo_GTIN', OLD.Codigo_GTIN, 'Codigo_productoSUNAT', OLD.Codigo_productoSUNAT, 'Descripcion', OLD.Descripcion, 'Partida_arancelaria', OLD.Partida_arancelaria, 'Unidad_de_medida', OLD.Unidad_de_medida);
    SET v_despues = JSON_OBJECT('Id_producto', NEW.Id_producto, 'Codigo_GTIN', NEW.Codigo_GTIN, 'Codigo_productoSUNAT', NEW.Codigo_productoSUNAT, 'Descripcion', NEW.Descripcion, 'Partida_arancelaria', NEW.Partida_arancelaria, 'Unidad_de_medida', NEW.Unidad_de_medida);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('PRODUCTO', 'UPDATE', CONCAT_WS('|', NEW.Id_producto), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_producto_ad$$
CREATE TRIGGER trg_producto_ad AFTER DELETE ON PRODUCTO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('PRODUCTO', 'DELETE', CONCAT_WS('|', OLD.Id_producto), JSON_OBJECT('Id_producto', OLD.Id_producto, 'Codigo_GTIN', OLD.Codigo_GTIN, 'Codigo_productoSUNAT', OLD.Codigo_productoSUNAT, 'Descripcion', OLD.Descripcion, 'Partida_arancelaria', OLD.Partida_arancelaria, 'Unidad_de_medida', OLD.Unidad_de_medida), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- GUIA_DE_REMISION
DROP TRIGGER IF EXISTS trg_guia_de_remision_ai$$
CREATE TRIGGER trg_guia_de_remision_ai AFTER INSERT ON GUIA_DE_REMISION FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('GUIA_DE_REMISION', 'INSERT', CONCAT_WS('|', NEW.Serie_numero), NULL, JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Tipo_guia', NEW.Tipo_guia, 'Fecha', NEW.Fecha, 'Hora', NEW.Hora, 'Motivo_traslado', NEW.Motivo_traslado, 'Fecha_inicio_traslado', NEW.Fecha_inicio_traslado, 'Observaciones', NEW.Observaciones, 'Punto_partida', NEW.Punto_partida, 'Punto_llegada', NEW.Punto_llegada, 'Peso_bruto_total_carga', NEW.Peso_bruto_total_carga, 'Unidad_medida_peso_bruto', NEW.Unidad_medida_peso_bruto, 'Modalidad_traslado', NEW.Modalidad_traslado, 'RUC_Remitente', NEW.RUC_Remitente, 'RUC_Destinatario', NEW.RUC_Destinatario, 'RUC_Transportista', NEW.RUC_Transportista, 'RUC_PagadorFlete', NEW.RUC_PagadorFlete, 'RUC_Proveedor', NEW.RUC_Proveedor, 'Fecha_entrega_bienes_transportista', NEW.Fecha_entrega_bienes_transportista), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_guia_de_remision_au$$
CREATE TRIGGER trg_guia_de_remision_au AFTER UPDATE ON GUIA_DE_REMISION FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Tipo_guia', OLD.Tipo_guia, 'Fecha', OLD.Fecha, 'Hora', OLD.Hora, 'Motivo_traslado', OLD.Motivo_traslado, 'Fecha_inicio_traslado', OLD.Fecha_inicio_traslado, 'Observaciones', OLD.Observaciones, 'Punto_partida', OLD.Punto_partida, 'Punto_llegada', OLD.Punto_llegada, 'Peso_bruto_total_carga', OLD.Peso_bruto_total_carga, 'Unidad_medida_peso_bruto', OLD.Unidad_medida_peso_bruto, 'Modalidad_traslado', OLD.Modalidad_traslado, 'RUC_Remitente', OLD.RUC_Remitente, 'RUC_Destinatario', OLD.RUC_Destinatario, 'RUC_Transportista', OLD.RUC_Transportista, 'RUC_PagadorFlete', OLD.RUC_PagadorFlete, 'RUC_Proveedor', OLD.RUC_Proveedor, 'Fecha_entrega_bienes_transportista', OLD.Fecha_entrega_bienes_transportista);
    SET v_despues = JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Tipo_guia', NEW.Tipo_guia, 'Fecha', NEW.Fecha, 'Hora', NEW.Hora, 'Motivo_traslado', NEW.Motivo_traslado, 'Fecha_inicio_traslado', NEW.Fecha_inicio_traslado, 'Observaciones', NEW.Observaciones, 'Punto_partida', NEW.Punto_partida, 'Punto_llegada', NEW.Punto_llegada, 'Peso_bruto_total_carga', NEW.Peso_bruto_total_carga, 'Unidad_medida_peso_bruto', NEW.Unidad_medida_peso_bruto, 'Modalidad_traslado', NEW.Modalidad_traslado, 'RUC_Remitente', NEW.RUC_Remitente, 'RUC_Destinatario', NEW.RUC_Destinatario, 'RUC_Transportista', NEW.RUC_Transportista, 'RUC_PagadorFlete', NEW.RUC_PagadorFlete, 'RUC_Proveedor', NEW.RUC_Proveedor, 'Fecha_entrega_bienes_transportista', NEW.Fecha_entrega_bienes_transportista);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('GUIA_DE_REMISION', 'UPDATE', CONCAT_WS('|', NEW.Serie_numero), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_guia_de_remision_ad$$
CREATE TRIGGER trg_guia_de_remision_ad AFTER DELETE ON GUIA_DE_REMISION FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('GUIA_DE_REMISION', 'DELETE', CONCAT_WS('|', OLD.Serie_numero), JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Tipo_guia', OLD.Tipo_guia, 'Fecha', OLD.Fecha, 'Hora', OLD.Hora, 'Motivo_traslado', OLD.Motivo_traslado, 'Fecha_inicio_traslado', OLD.Fecha_inicio_traslado, 'Observaciones', OLD.Observaciones, 'Punto_partida', OLD.Punto_partida, 'Punto_llegada', OLD.Punto_llegada, 'Peso_bruto_total_carga', OLD.Peso_bruto_total_carga, 'Unidad_medida_peso_bruto', OLD.Unidad_medida_peso_bruto, 'Modalidad_traslado', OLD.Modalidad_traslado, 'RUC_Remitente', OLD.RUC_Remitente, 'RUC_Destinatario', OLD.RUC_Destinatario, 'RUC_Transportista', OLD.RUC_Transportista, 'RUC_PagadorFlete', OLD.RUC_PagadorFlete, 'RUC_Proveedor', OLD.RUC_Proveedor, 'Fecha_entrega_bienes_transportista', OLD.Fecha_entrega_bienes_transportista), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- DETALLE_GUIA
DROP TRIGGER IF EXISTS trg_detalle_guia_ai$$
CREATE TRIGGER trg_detalle_guia_ai AFTER INSERT ON DETALLE_GUIA FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('DETALLE_GUIA', 'INSERT', CONCAT_WS('|', NEW.Serie_numero), NULL, JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Transbordo_programado', NEW.Transbordo_programado, 'Envases_vacios_retorno', NEW.Envases_vacios_retorno, 'Traslado_cat_M1_L', NEW.Traslado_cat_M1_L, 'Vehiculo_vacio_retorno', NEW.Vehiculo_vacio_retorno, 'Transporte_Subcontratado', NEW.Transporte_Subcontratado), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_detalle_guia_au$$
CREATE TRIGGER trg_detalle_guia_au AFTER UPDATE ON DETALLE_GUIA FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Transbordo_programado', OLD.Transbordo_programado, 'Envases_vacios_retorno', OLD.Envases_vacios_retorno, 'Traslado_cat_M1_L', OLD.Traslado_cat_M1_L, 'Vehiculo_vacio_retorno', OLD.Vehiculo_vacio_retorno, 'Transporte_Subcontratado', OLD.Transporte_Subcontratado);
    SET v_despues = JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Transbordo_programado', NEW.Transbordo_programado, 'Envases_vacios_retorno', NEW.Envases_vacios_retorno, 'Traslado_cat_M1_L', NEW.Traslado_cat_M1_L, 'Vehiculo_vacio_retorno', NEW.Vehiculo_vacio_retorno, 'Transporte_Subcontratado', NEW.Transporte_Subcontratado);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('DETALLE_GUIA', 'UPDATE', CONCAT_WS('|', NEW.Serie_numero), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_detalle_guia_ad$$
CREATE TRIGGER trg_detalle_guia_ad AFTER DELETE ON DETALLE_GUIA FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('DETALLE_GUIA', 'DELETE', CONCAT_WS('|', OLD.Serie_numero), JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Transbordo_programado', OLD.Transbordo_programado, 'Envases_vacios_retorno', OLD.Envases_vacios_retorno, 'Traslado_cat_M1_L', OLD.Traslado_cat_M1_L, 'Vehiculo_vacio_retorno', OLD.Vehiculo_vacio_retorno, 'Transporte_Subcontratado', OLD.Transporte_Subcontratado), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- DOCUMENTO_RELACIONADO
DROP TRIGGER IF EXISTS trg_documento_relacionado_ai$$
CREATE TRIGGER trg_documento_relacionado_ai AFTER INSERT ON DOCUMENTO_RELACIONADO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('DOCUMENTO_RELACIONADO', 'INSERT', CONCAT_WS('|', NEW.Serie_numero, NEW.Nro_Documento), NULL, JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Nro_Documento', NEW.Nro_Documento, 'Tipo_Documento', NEW.Tipo_Documento), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_documento_relacionado_au$$
CREATE TRIGGER trg_documento_relacionado_au AFTER UPDATE ON DOCUMENTO_RELACIONADO FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Nro_Documento', OLD.Nro_Documento, 'Tipo_Documento', OLD.Tipo_Documento);
    SET v_despues = JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Nro_Documento', NEW.Nro_Documento, 'Tipo_Documento', NEW.Tipo_Documento);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('DOCUMENTO_RELACIONADO', 'UPDATE', CONCAT_WS('|', NEW.Serie_numero, NEW.Nro_Documento), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_documento_relacionado_ad$$
CREATE TRIGGER trg_documento_relacionado_ad AFTER DELETE ON DOCUMENTO_RELACIONADO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('DOCUMENTO_RELACIONADO', 'DELETE', CONCAT_WS('|', OLD.Serie_numero, OLD.Nro_Documento), JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Nro_Documento', OLD.Nro_Documento, 'Tipo_Documento', OLD.Tipo_Documento), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- TRASLADO
DROP TRIGGER IF EXISTS trg_traslado_ai$$
CREATE TRIGGER trg_traslado_ai AFTER INSERT ON TRASLADO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('TRASLADO', 'INSERT', CONCAT_WS('|', NEW.Serie_numero, NEW.Placa, NEW.DNI), NULL, JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Placa', NEW.Placa, 'DNI', NEW.DNI), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_traslado_au$$
CREATE TRIGGER trg_traslado_au AFTER UPDATE ON TRASLADO FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Placa', OLD.Placa, 'DNI', OLD.DNI);
    SET v_despues = JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Placa', NEW.Placa, 'DNI', NEW.DNI);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('TRASLADO', 'UPDATE', CONCAT_WS('|', NEW.Serie_numero, NEW.Placa, NEW.DNI), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_traslado_ad$$
CREATE TRIGGER trg_traslado_ad AFTER DELETE ON TRASLADO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('TRASLADO', 'DELETE', CONCAT_WS('|', OLD.Serie_numero, OLD.Placa, OLD.DNI), JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Placa', OLD.Placa, 'DNI', OLD.DNI), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- BIEN_TRANSPORTADO
DROP TRIGGER IF EXISTS trg_bien_transportado_ai$$
CREATE TRIGGER trg_bien_transportado_ai AFTER INSERT ON BIEN_TRANSPORTADO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('BIEN_TRANSPORTADO', 'INSERT', CONCAT_WS('|', NEW.Serie_numero, NEW.Nro_item), NULL, JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Nro_item', NEW.Nro_item, 'Id_producto', NEW.Id_producto, 'Bien_normalizado', NEW.Bien_normalizado, 'Cantidad', NEW.Cantidad), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_bien_transportado_au$$
CREATE TRIGGER trg_bien_transportado_au AFTER UPDATE ON BIEN_TRANSPORTADO FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Nro_item', OLD.Nro_item, 'Id_producto', OLD.Id_producto, 'Bien_normalizado', OLD.Bien_normalizado, 'Cantidad', OLD.Cantidad);
    SET v_despues = JSON_OBJECT('Serie_numero', NEW.Serie_numero, 'Nro_item', NEW.Nro_item, 'Id_producto', NEW.Id_producto, 'Bien_normalizado', NEW.Bien_normalizado, 'Cantidad', NEW.Cantidad);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('BIEN_TRANSPORTADO', 'UPDATE', CONCAT_WS('|', NEW.Serie_numero, NEW.Nro_item), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_bien_transportado_ad$$
CREATE TRIGGER trg_bien_transportado_ad AFTER DELETE ON BIEN_TRANSPORTADO FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('BIEN_TRANSPORTADO', 'DELETE', CONCAT_WS('|', OLD.Serie_numero, OLD.Nro_item), JSON_OBJECT('Serie_numero', OLD.Serie_numero, 'Nro_item', OLD.Nro_item, 'Id_producto', OLD.Id_producto, 'Bien_normalizado', OLD.Bien_normalizado, 'Cantidad', OLD.Cantidad), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

-- USUARIO_APP
DROP TRIGGER IF EXISTS trg_usuario_app_ai$$
CREATE TRIGGER trg_usuario_app_ai AFTER INSERT ON USUARIO_APP FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('USUARIO_APP', 'INSERT', CONCAT_WS('|', NEW.Id_usuario), NULL, JSON_OBJECT('Id_usuario', NEW.Id_usuario, 'Usuario', NEW.Usuario, 'Nombre_completo', NEW.Nombre_completo, 'Rol', NEW.Rol, 'Estado', NEW.Estado, 'Fecha_cambio_clave', NEW.Fecha_cambio_clave), COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

DROP TRIGGER IF EXISTS trg_usuario_app_au$$
CREATE TRIGGER trg_usuario_app_au AFTER UPDATE ON USUARIO_APP FOR EACH ROW
BEGIN
    DECLARE v_antes JSON; DECLARE v_despues JSON;
    SET v_antes = JSON_OBJECT('Id_usuario', OLD.Id_usuario, 'Usuario', OLD.Usuario, 'Nombre_completo', OLD.Nombre_completo, 'Rol', OLD.Rol, 'Estado', OLD.Estado, 'Fecha_cambio_clave', OLD.Fecha_cambio_clave);
    SET v_despues = JSON_OBJECT('Id_usuario', NEW.Id_usuario, 'Usuario', NEW.Usuario, 'Nombre_completo', NEW.Nombre_completo, 'Rol', NEW.Rol, 'Estado', NEW.Estado, 'Fecha_cambio_clave', NEW.Fecha_cambio_clave);
    IF NOT (v_antes <=> v_despues) THEN   -- solo si algo cambio de verdad
        INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('USUARIO_APP', 'UPDATE', CONCAT_WS('|', NEW.Id_usuario), v_antes, v_despues, COALESCE(@usuario_app, 'SIN_SESION'), USER());
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_usuario_app_ad$$
CREATE TRIGGER trg_usuario_app_ad AFTER DELETE ON USUARIO_APP FOR EACH ROW
BEGIN
    INSERT INTO AUDITORIA_CAMBIOS (Tabla_afectada, Operacion, Clave_registro, Valores_antes, Valores_despues, Usuario_app, Usuario_mysql)
    VALUES ('USUARIO_APP', 'DELETE', CONCAT_WS('|', OLD.Id_usuario), JSON_OBJECT('Id_usuario', OLD.Id_usuario, 'Usuario', OLD.Usuario, 'Nombre_completo', OLD.Nombre_completo, 'Rol', OLD.Rol, 'Estado', OLD.Estado, 'Fecha_cambio_clave', OLD.Fecha_cambio_clave), NULL, COALESCE(@usuario_app, 'SIN_SESION'), USER());
END$$

/* ===================== PARTE 2. VALIDACIONES Y SEGURIDAD ===================== */

-- Validacion 1: la fecha de inicio del traslado no puede ser anterior a la emision
DROP TRIGGER IF EXISTS trg_guia_bi_fechas$$
CREATE TRIGGER trg_guia_bi_fechas BEFORE INSERT ON GUIA_DE_REMISION FOR EACH ROW
BEGIN
    IF NEW.Fecha_inicio_traslado < NEW.Fecha THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de inicio del traslado no puede ser anterior a la fecha de emision';
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_guia_bu_fechas$$
CREATE TRIGGER trg_guia_bu_fechas BEFORE UPDATE ON GUIA_DE_REMISION FOR EACH ROW
BEGIN
    IF NEW.Fecha_inicio_traslado < NEW.Fecha THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de inicio del traslado no puede ser anterior a la fecha de emision';
    END IF;
END$$

-- Validacion 2: regla de aplicacion del modelo. Si la modalidad es Publico,
-- el vehiculo debe tener Nro_TUCE (en VEHICULO el campo es opcional)
DROP TRIGGER IF EXISTS trg_traslado_bi_tuce$$
CREATE TRIGGER trg_traslado_bi_tuce BEFORE INSERT ON TRASLADO FOR EACH ROW
BEGIN
    DECLARE v_modalidad VARCHAR(7);
    DECLARE v_tuce VARCHAR(20);
    SELECT Modalidad_traslado INTO v_modalidad FROM GUIA_DE_REMISION WHERE Serie_numero = NEW.Serie_numero;
    SELECT Nro_TUCE INTO v_tuce FROM VEHICULO WHERE Placa = NEW.Placa;
    IF v_modalidad = 'Publico' AND v_tuce IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'En transporte publico el vehiculo debe tener Nro_TUCE';
    END IF;
END$$

-- Validacion 3: la empresa propia no se puede eliminar
DROP TRIGGER IF EXISTS trg_empresa_bd_propia$$
CREATE TRIGGER trg_empresa_bd_propia BEFORE DELETE ON EMPRESA FOR EACH ROW
BEGIN
    IF OLD.RUC = '20158813998' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La empresa propia no se puede eliminar';
    END IF;
END$$

-- Seguridad: las tablas de auditoria son de solo escritura (nadie modifica ni borra el rastro)
DROP TRIGGER IF EXISTS trg_aud_cambios_bu$$
CREATE TRIGGER trg_aud_cambios_bu BEFORE UPDATE ON AUDITORIA_CAMBIOS FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La auditoria no se puede modificar';
END$$
DROP TRIGGER IF EXISTS trg_aud_cambios_bd$$
CREATE TRIGGER trg_aud_cambios_bd BEFORE DELETE ON AUDITORIA_CAMBIOS FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La auditoria no se puede eliminar';
END$$
DROP TRIGGER IF EXISTS trg_aud_acceso_bu$$
CREATE TRIGGER trg_aud_acceso_bu BEFORE UPDATE ON AUDITORIA_ACCESO FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La auditoria no se puede modificar';
END$$
DROP TRIGGER IF EXISTS trg_aud_acceso_bd$$
CREATE TRIGGER trg_aud_acceso_bd BEFORE DELETE ON AUDITORIA_ACCESO FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La auditoria no se puede eliminar';
END$$

DELIMITER ;

/* ---------- VERIFICACION (captura) ---------- */
SELECT TRIGGER_NAME AS trigger_, EVENT_MANIPULATION AS evento, EVENT_OBJECT_TABLE AS tabla,
       ACTION_TIMING AS momento
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'mining_casava'
ORDER BY EVENT_OBJECT_TABLE, ACTION_TIMING, EVENT_MANIPULATION;

SELECT COUNT(*) AS total_triggers FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = 'mining_casava';


/* ---------- PRUEBA DE TRAZABILIDAD (ejecutar por partes y capturar) ---------- */

-- 1) Simular la sesion de un gestor
SET @usuario_app = 'gestor1';

-- 2) INSERT: aparece una fila con Valores_antes = NULL
INSERT INTO EMPRESA (RUC, Razon_Social) VALUES ('20999999991', 'EMPRESA DE PRUEBA S.A.C.');

-- 3) UPDATE: aparecen los valores antes y despues
UPDATE EMPRESA SET Razon_Social = 'EMPRESA DE PRUEBA MODIFICADA S.A.C.' WHERE RUC = '20999999991';

-- 4) DELETE: aparece la fila completa que se borro
DELETE FROM EMPRESA WHERE RUC = '20999999991';

-- 5) Ver el rastro
SELECT Id_cambio, Fecha_hora, Usuario_app, Operacion, Tabla_afectada, Clave_registro,
       Valores_antes, Valores_despues
FROM AUDITORIA_CAMBIOS ORDER BY Id_cambio DESC LIMIT 10;

-- 6) La auditoria no se puede alterar (debe dar error)
UPDATE AUDITORIA_CAMBIOS SET Usuario_app = 'otro' WHERE Id_cambio = (SELECT MAX(Id_cambio) FROM (SELECT Id_cambio FROM AUDITORIA_CAMBIOS) x);

-- 7) La empresa propia no se puede borrar (debe dar error)
DELETE FROM EMPRESA WHERE RUC = '20158813998';
