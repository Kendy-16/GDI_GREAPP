/* =====================================================================
   APLICATIVO - SCRIPT A03: PROCEDIMIENTOS ALMACENADOS
   Base: mining_casava - ejecutar DESPUES de A02.

   Toda alta, cambio y baja del aplicativo pasa por estos procedimientos;
   la aplicacion nunca escribe con INSERT/UPDATE/DELETE sueltos.

   Contenido:
     Sesion ............ sp_login, sp_cerrar_sesion
     Usuarios (admin) .. sp_adm_usuario_crear, sp_adm_usuario_estado, sp_adm_usuario_clave
     Guia (con hijas) .. sp_guia_registrar, sp_guia_modificar, sp_guia_eliminar
                         (internos: sp_int_bienes, sp_int_traslados, sp_int_documentos)
     Maestras .......... sp_empresa_*, sp_transportista_*, sp_vehiculo_*,
                         sp_conductor_*, sp_producto_*  (registrar, modificar, eliminar)

   Las listas de la guia (bienes, traslados, documentos) se envian como JSON:
     p_bienes      '[{"item":1,"producto":4,"normalizado":0,"cantidad":850.00}]'
     p_traslados   '[{"placa":"CBM500","dni":"52477647"}]'
     p_documentos  '[{"nro":"F251-216195","tipo":"Factura"}]'   (o NULL)
   En sp_guia_modificar, una lista NULL significa "no tocar esa tabla hija".

   Cada operacion de guia es UNA transaccion: si algo falla, se deshace todo.

   EJECUCION EN WORKBENCH: el script usa DELIMITER $$ (ya incluido). Se ejecuta
   completo con el rayo (Ctrl+Shift+Enter).
   ===================================================================== */

USE mining_casava;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_login$$
CREATE PROCEDURE sp_login(    IN  p_usuario   VARCHAR(30),
    IN  p_clave     VARCHAR(100),
    IN  p_equipo    VARCHAR(100),
    OUT p_resultado VARCHAR(10),
    OUT p_rol       VARCHAR(15),
    OUT p_nombre    VARCHAR(100),
    OUT p_id        INT)
BEGIN
    DECLARE v_id INT DEFAULT NULL;
    DECLARE v_estado VARCHAR(10) DEFAULT NULL;
    DECLARE v_rol VARCHAR(15) DEFAULT NULL;
    DECLARE v_nombre VARCHAR(100) DEFAULT NULL;
    DECLARE v_ok INT DEFAULT 0;
    DECLARE v_intentos INT DEFAULT 0;

    SET p_resultado = 'FALLO'; SET p_rol = NULL; SET p_nombre = NULL; SET p_id = NULL;

    SELECT Id_usuario, Estado, Rol, Nombre_completo, Intentos_fallidos,
           (Clave_hash = SHA2(CONCAT(Salt, p_clave), 256))
      INTO v_id, v_estado, v_rol, v_nombre, v_intentos, v_ok
      FROM USUARIO_APP WHERE Usuario = p_usuario LIMIT 1;

    IF v_id IS NULL THEN
        -- usuario inexistente: no se revela si existe o no
        INSERT INTO AUDITORIA_ACCESO (Usuario_intentado, Id_usuario, Resultado, Equipo, Detalle)
        VALUES (p_usuario, NULL, 'FALLO', p_equipo, 'Usuario inexistente');
    ELSEIF v_estado <> 'ACTIVO' THEN
        SET p_resultado = 'BLOQUEADO';
        INSERT INTO AUDITORIA_ACCESO (Usuario_intentado, Id_usuario, Resultado, Equipo, Detalle)
        VALUES (p_usuario, v_id, 'BLOQUEADO', p_equipo, CONCAT('Cuenta en estado ', v_estado));
    ELSEIF v_ok = 1 THEN
        UPDATE USUARIO_APP SET Intentos_fallidos = 0, Ultimo_acceso = NOW() WHERE Id_usuario = v_id;
        SET p_resultado = 'EXITO'; SET p_rol = v_rol; SET p_nombre = v_nombre; SET p_id = v_id;
        INSERT INTO AUDITORIA_ACCESO (Usuario_intentado, Id_usuario, Resultado, Equipo, Detalle)
        VALUES (p_usuario, v_id, 'EXITO', p_equipo, CONCAT('Ingreso como ', v_rol));
    ELSE
        SET v_intentos = v_intentos + 1;
        UPDATE USUARIO_APP SET Intentos_fallidos = v_intentos WHERE Id_usuario = v_id;
        INSERT INTO AUDITORIA_ACCESO (Usuario_intentado, Id_usuario, Resultado, Equipo, Detalle)
        VALUES (p_usuario, v_id, 'FALLO', p_equipo, CONCAT('Clave incorrecta (intento ', v_intentos, ' de 5)'));
        IF v_intentos >= 5 THEN
            UPDATE USUARIO_APP SET Estado = 'BLOQUEADO' WHERE Id_usuario = v_id;
            SET p_resultado = 'BLOQUEADO';
        END IF;
    END IF;
END$$

DROP PROCEDURE IF EXISTS sp_cerrar_sesion$$
CREATE PROCEDURE sp_cerrar_sesion(    IN p_usuario VARCHAR(30),
    IN p_equipo  VARCHAR(100))
BEGIN
    INSERT INTO AUDITORIA_ACCESO (Usuario_intentado, Id_usuario, Resultado, Equipo, Detalle)
    SELECT p_usuario, (SELECT Id_usuario FROM USUARIO_APP WHERE Usuario = p_usuario LIMIT 1),
           'CIERRE', p_equipo, 'Cierre de sesion';
END$$

DROP PROCEDURE IF EXISTS sp_adm_usuario_crear$$
CREATE PROCEDURE sp_adm_usuario_crear(    IN p_usuario VARCHAR(30),
    IN p_nombre  VARCHAR(100),
    IN p_clave   VARCHAR(100),
    IN p_rol     VARCHAR(15))
BEGIN
    DECLARE v_salt CHAR(16);
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un usuario con ese nombre';
    IF CHAR_LENGTH(p_clave) < 8 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La clave debe tener al menos 8 caracteres';
    END IF;
    SET v_salt = SUBSTRING(SHA2(CONCAT(UUID(), RAND()), 256), 1, 16);
    INSERT INTO USUARIO_APP (Usuario, Nombre_completo, Salt, Clave_hash, Rol)
    VALUES (p_usuario, p_nombre, v_salt, SHA2(CONCAT(v_salt, p_clave), 256), p_rol);
END$$

DROP PROCEDURE IF EXISTS sp_adm_usuario_estado$$
CREATE PROCEDURE sp_adm_usuario_estado(    IN p_usuario VARCHAR(30),
    IN p_estado  VARCHAR(10))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM USUARIO_APP WHERE Usuario = p_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario no existe';
    END IF;
    UPDATE USUARIO_APP SET Estado = p_estado, Intentos_fallidos = 0 WHERE Usuario = p_usuario;
END$$

DROP PROCEDURE IF EXISTS sp_adm_usuario_clave$$
CREATE PROCEDURE sp_adm_usuario_clave(    IN p_usuario VARCHAR(30),
    IN p_clave_nueva VARCHAR(100))
BEGIN
    DECLARE v_salt CHAR(16);
    IF NOT EXISTS (SELECT 1 FROM USUARIO_APP WHERE Usuario = p_usuario) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario no existe';
    END IF;
    IF CHAR_LENGTH(p_clave_nueva) < 8 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La clave debe tener al menos 8 caracteres';
    END IF;
    SET v_salt = SUBSTRING(SHA2(CONCAT(UUID(), RAND()), 256), 1, 16);
    UPDATE USUARIO_APP
       SET Salt = v_salt, Clave_hash = SHA2(CONCAT(v_salt, p_clave_nueva), 256),
           Fecha_cambio_clave = NOW(), Intentos_fallidos = 0
     WHERE Usuario = p_usuario;
END$$

DROP PROCEDURE IF EXISTS sp_int_bienes$$
CREATE PROCEDURE sp_int_bienes(IN p_serie VARCHAR(13), IN p_bienes JSON)
BEGIN
    IF p_bienes IS NULL OR JSON_LENGTH(p_bienes) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La guia debe tener al menos un bien transportado';
    END IF;
    INSERT INTO BIEN_TRANSPORTADO (Serie_numero, Nro_item, Id_producto, Bien_normalizado, Cantidad)
    SELECT p_serie, jt.nro_item, jt.id_producto, jt.normalizado, jt.cantidad
      FROM JSON_TABLE(p_bienes, '$[*]' COLUMNS (
            nro_item    INT           PATH '$.item',
            id_producto INT           PATH '$.producto',
            normalizado TINYINT       PATH '$.normalizado' DEFAULT '0' ON EMPTY,
            cantidad    DECIMAL(12,2) PATH '$.cantidad')) AS jt;
END$$

DROP PROCEDURE IF EXISTS sp_int_traslados$$
CREATE PROCEDURE sp_int_traslados(IN p_serie VARCHAR(13), IN p_traslados JSON)
BEGIN
    IF p_traslados IS NULL OR JSON_LENGTH(p_traslados) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La guia debe tener al menos un vehiculo y conductor';
    END IF;
    INSERT INTO TRASLADO (Serie_numero, Placa, DNI)
    SELECT p_serie, jt.placa, jt.dni
      FROM JSON_TABLE(p_traslados, '$[*]' COLUMNS (
            placa VARCHAR(6) PATH '$.placa',
            dni   VARCHAR(8) PATH '$.dni')) AS jt;
END$$

DROP PROCEDURE IF EXISTS sp_int_documentos$$
CREATE PROCEDURE sp_int_documentos(IN p_serie VARCHAR(13), IN p_documentos JSON)
BEGIN
    IF p_documentos IS NOT NULL AND JSON_LENGTH(p_documentos) > 0 THEN
        INSERT INTO DOCUMENTO_RELACIONADO (Serie_numero, Nro_Documento, Tipo_Documento)
        SELECT p_serie, jt.nro, jt.tipo
          FROM JSON_TABLE(p_documentos, '$[*]' COLUMNS (
                nro  VARCHAR(20) PATH '$.nro',
                tipo VARCHAR(20) PATH '$.tipo')) AS jt;
    END IF;
END$$

DROP PROCEDURE IF EXISTS sp_guia_registrar$$
CREATE PROCEDURE sp_guia_registrar(    IN p_serie VARCHAR(13), IN p_tipo VARCHAR(13), IN p_fecha DATE, IN p_hora TIME,
    IN p_motivo VARCHAR(50), IN p_fecha_inicio DATE, IN p_obs VARCHAR(250),
    IN p_partida VARCHAR(200), IN p_llegada VARCHAR(200),
    IN p_peso DECIMAL(12,3), IN p_unidad VARCHAR(3), IN p_modalidad VARCHAR(7),
    IN p_ruc_rem VARCHAR(11), IN p_ruc_dest VARCHAR(11), IN p_ruc_transp VARCHAR(11),
    IN p_ruc_pagador VARCHAR(11), IN p_ruc_prov VARCHAR(11), IN p_fecha_entrega DATE,
    IN p_transbordo TINYINT, IN p_envases TINYINT, IN p_m1l TINYINT,
    IN p_veh_vacio TINYINT, IN p_subcontratado TINYINT,
    IN p_bienes JSON, IN p_traslados JSON, IN p_documentos JSON)
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        BEGIN ROLLBACK; SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con esa clave'; END;
    DECLARE EXIT HANDLER FOR 1452
        BEGIN ROLLBACK; SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Una referencia (empresa, vehiculo, conductor o producto) no existe'; END;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        BEGIN ROLLBACK; RESIGNAL; END;

    START TRANSACTION;
    INSERT INTO GUIA_DE_REMISION (Serie_numero, Tipo_guia, Fecha, Hora, Motivo_traslado, Fecha_inicio_traslado,
        Observaciones, Punto_partida, Punto_llegada, Peso_bruto_total_carga, Unidad_medida_peso_bruto,
        Modalidad_traslado, RUC_Remitente, RUC_Destinatario, RUC_Transportista, RUC_PagadorFlete,
        RUC_Proveedor, Fecha_entrega_bienes_transportista)
    VALUES (p_serie, p_tipo, p_fecha, p_hora, p_motivo, p_fecha_inicio, p_obs, p_partida, p_llegada,
        p_peso, p_unidad, p_modalidad, p_ruc_rem, p_ruc_dest, p_ruc_transp, p_ruc_pagador,
        p_ruc_prov, p_fecha_entrega);

    INSERT INTO DETALLE_GUIA (Serie_numero, Transbordo_programado, Envases_vacios_retorno, Traslado_cat_M1_L,
        Vehiculo_vacio_retorno, Transporte_Subcontratado)
    VALUES (p_serie, COALESCE(p_transbordo, 0), COALESCE(p_envases, 0), COALESCE(p_m1l, 0),
        p_veh_vacio, p_subcontratado);

    CALL sp_int_bienes(p_serie, p_bienes);
    CALL sp_int_traslados(p_serie, p_traslados);
    CALL sp_int_documentos(p_serie, p_documentos);
    COMMIT;
END$$

DROP PROCEDURE IF EXISTS sp_guia_modificar$$
CREATE PROCEDURE sp_guia_modificar(    IN p_serie VARCHAR(13), IN p_tipo VARCHAR(13), IN p_fecha DATE, IN p_hora TIME,
    IN p_motivo VARCHAR(50), IN p_fecha_inicio DATE, IN p_obs VARCHAR(250),
    IN p_partida VARCHAR(200), IN p_llegada VARCHAR(200),
    IN p_peso DECIMAL(12,3), IN p_unidad VARCHAR(3), IN p_modalidad VARCHAR(7),
    IN p_ruc_rem VARCHAR(11), IN p_ruc_dest VARCHAR(11), IN p_ruc_transp VARCHAR(11),
    IN p_ruc_pagador VARCHAR(11), IN p_ruc_prov VARCHAR(11), IN p_fecha_entrega DATE,
    IN p_transbordo TINYINT, IN p_envases TINYINT, IN p_m1l TINYINT,
    IN p_veh_vacio TINYINT, IN p_subcontratado TINYINT,
    IN p_bienes JSON, IN p_traslados JSON, IN p_documentos JSON)
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        BEGIN ROLLBACK; SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con esa clave'; END;
    DECLARE EXIT HANDLER FOR 1452
        BEGIN ROLLBACK; SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Una referencia (empresa, vehiculo, conductor o producto) no existe'; END;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        BEGIN ROLLBACK; RESIGNAL; END;

    IF NOT EXISTS (SELECT 1 FROM GUIA_DE_REMISION WHERE Serie_numero = p_serie) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La guia no existe';
    END IF;

    START TRANSACTION;
    UPDATE GUIA_DE_REMISION
       SET Tipo_guia = p_tipo, Fecha = p_fecha, Hora = p_hora, Motivo_traslado = p_motivo,
           Fecha_inicio_traslado = p_fecha_inicio, Observaciones = p_obs,
           Punto_partida = p_partida, Punto_llegada = p_llegada,
           Peso_bruto_total_carga = p_peso, Unidad_medida_peso_bruto = p_unidad,
           Modalidad_traslado = p_modalidad, RUC_Remitente = p_ruc_rem, RUC_Destinatario = p_ruc_dest,
           RUC_Transportista = p_ruc_transp, RUC_PagadorFlete = p_ruc_pagador, RUC_Proveedor = p_ruc_prov,
           Fecha_entrega_bienes_transportista = p_fecha_entrega
     WHERE Serie_numero = p_serie;

    INSERT INTO DETALLE_GUIA (Serie_numero, Transbordo_programado, Envases_vacios_retorno, Traslado_cat_M1_L,
        Vehiculo_vacio_retorno, Transporte_Subcontratado)
    VALUES (p_serie, COALESCE(p_transbordo, 0), COALESCE(p_envases, 0), COALESCE(p_m1l, 0),
        p_veh_vacio, p_subcontratado)
    ON DUPLICATE KEY UPDATE
        Transbordo_programado = COALESCE(p_transbordo, 0), Envases_vacios_retorno = COALESCE(p_envases, 0),
        Traslado_cat_M1_L = COALESCE(p_m1l, 0), Vehiculo_vacio_retorno = p_veh_vacio,
        Transporte_Subcontratado = p_subcontratado;

    -- Las listas hijas: NULL = no tocar; con valor = reemplazar por la nueva lista
    IF p_bienes IS NOT NULL THEN
        DELETE FROM BIEN_TRANSPORTADO WHERE Serie_numero = p_serie;
        CALL sp_int_bienes(p_serie, p_bienes);
    END IF;
    IF p_traslados IS NOT NULL THEN
        DELETE FROM TRASLADO WHERE Serie_numero = p_serie;
        CALL sp_int_traslados(p_serie, p_traslados);
    END IF;
    IF p_documentos IS NOT NULL THEN
        DELETE FROM DOCUMENTO_RELACIONADO WHERE Serie_numero = p_serie;
        CALL sp_int_documentos(p_serie, p_documentos);
    END IF;
    COMMIT;
END$$

DROP PROCEDURE IF EXISTS sp_guia_eliminar$$
CREATE PROCEDURE sp_guia_eliminar(IN p_serie VARCHAR(13))
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        BEGIN ROLLBACK; RESIGNAL; END;
    IF NOT EXISTS (SELECT 1 FROM GUIA_DE_REMISION WHERE Serie_numero = p_serie) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La guia no existe';
    END IF;
    START TRANSACTION;
    -- primero las hijas (claves foraneas), al final la cabecera
    DELETE FROM DOCUMENTO_RELACIONADO WHERE Serie_numero = p_serie;
    DELETE FROM BIEN_TRANSPORTADO     WHERE Serie_numero = p_serie;
    DELETE FROM TRASLADO              WHERE Serie_numero = p_serie;
    DELETE FROM DETALLE_GUIA          WHERE Serie_numero = p_serie;
    DELETE FROM GUIA_DE_REMISION      WHERE Serie_numero = p_serie;
    COMMIT;
END$$

DROP PROCEDURE IF EXISTS sp_empresa_registrar$$
CREATE PROCEDURE sp_empresa_registrar(IN p_ruc VARCHAR(11), IN p_razon_social VARCHAR(150))
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con esa clave o valor unico';
    INSERT INTO EMPRESA (RUC, Razon_Social)
    VALUES (p_ruc, p_razon_social);
END$$

DROP PROCEDURE IF EXISTS sp_empresa_modificar$$
CREATE PROCEDURE sp_empresa_modificar(IN p_ruc VARCHAR(11), IN p_razon_social VARCHAR(150))
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con ese valor unico';
    IF NOT EXISTS (SELECT 1 FROM EMPRESA WHERE RUC = p_ruc) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El registro no existe';
    END IF;
    UPDATE EMPRESA SET Razon_Social = p_razon_social WHERE RUC = p_ruc;
END$$

DROP PROCEDURE IF EXISTS sp_empresa_eliminar$$
CREATE PROCEDURE sp_empresa_eliminar(IN p_ruc VARCHAR(11))
BEGIN
    DECLARE EXIT HANDLER FOR 1451
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar: el registro esta siendo usado por otras tablas';
    IF NOT EXISTS (SELECT 1 FROM EMPRESA WHERE RUC = p_ruc) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El registro no existe';
    END IF;
    DELETE FROM EMPRESA WHERE RUC = p_ruc;
END$$

DROP PROCEDURE IF EXISTS sp_transportista_registrar$$
CREATE PROCEDURE sp_transportista_registrar(IN p_ruc_transportista VARCHAR(11), IN p_numero_registro_mtc VARCHAR(20))
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con esa clave o valor unico';
    DECLARE EXIT HANDLER FOR 1452
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La empresa (RUC) no existe: registrela primero';
    INSERT INTO TRANSPORTISTA (RUC_Transportista, Numero_registro_MTC)
    VALUES (p_ruc_transportista, p_numero_registro_mtc);
END$$

DROP PROCEDURE IF EXISTS sp_transportista_modificar$$
CREATE PROCEDURE sp_transportista_modificar(IN p_ruc_transportista VARCHAR(11), IN p_numero_registro_mtc VARCHAR(20))
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con ese valor unico';
    IF NOT EXISTS (SELECT 1 FROM TRANSPORTISTA WHERE RUC_Transportista = p_ruc_transportista) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El registro no existe';
    END IF;
    UPDATE TRANSPORTISTA SET Numero_registro_MTC = p_numero_registro_mtc WHERE RUC_Transportista = p_ruc_transportista;
END$$

DROP PROCEDURE IF EXISTS sp_transportista_eliminar$$
CREATE PROCEDURE sp_transportista_eliminar(IN p_ruc_transportista VARCHAR(11))
BEGIN
    DECLARE EXIT HANDLER FOR 1451
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar: el registro esta siendo usado por otras tablas';
    IF NOT EXISTS (SELECT 1 FROM TRANSPORTISTA WHERE RUC_Transportista = p_ruc_transportista) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El registro no existe';
    END IF;
    DELETE FROM TRANSPORTISTA WHERE RUC_Transportista = p_ruc_transportista;
END$$

DROP PROCEDURE IF EXISTS sp_vehiculo_registrar$$
CREATE PROCEDURE sp_vehiculo_registrar(IN p_placa VARCHAR(6), IN p_nro_tuce VARCHAR(20))
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con esa clave o valor unico';
    INSERT INTO VEHICULO (Placa, Nro_TUCE)
    VALUES (p_placa, p_nro_tuce);
END$$

DROP PROCEDURE IF EXISTS sp_vehiculo_modificar$$
CREATE PROCEDURE sp_vehiculo_modificar(IN p_placa VARCHAR(6), IN p_nro_tuce VARCHAR(20))
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con ese valor unico';
    IF NOT EXISTS (SELECT 1 FROM VEHICULO WHERE Placa = p_placa) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El registro no existe';
    END IF;
    UPDATE VEHICULO SET Nro_TUCE = p_nro_tuce WHERE Placa = p_placa;
END$$

DROP PROCEDURE IF EXISTS sp_vehiculo_eliminar$$
CREATE PROCEDURE sp_vehiculo_eliminar(IN p_placa VARCHAR(6))
BEGIN
    DECLARE EXIT HANDLER FOR 1451
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar: el registro esta siendo usado por otras tablas';
    IF NOT EXISTS (SELECT 1 FROM VEHICULO WHERE Placa = p_placa) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El registro no existe';
    END IF;
    DELETE FROM VEHICULO WHERE Placa = p_placa;
END$$

DROP PROCEDURE IF EXISTS sp_conductor_registrar$$
CREATE PROCEDURE sp_conductor_registrar(IN p_dni VARCHAR(8), IN p_nombre VARCHAR(100), IN p_nro_licencia VARCHAR(15))
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con esa clave o valor unico';
    INSERT INTO CONDUCTOR (DNI, Nombre, Nro_Licencia)
    VALUES (p_dni, p_nombre, p_nro_licencia);
END$$

DROP PROCEDURE IF EXISTS sp_conductor_modificar$$
CREATE PROCEDURE sp_conductor_modificar(IN p_dni VARCHAR(8), IN p_nombre VARCHAR(100), IN p_nro_licencia VARCHAR(15))
BEGIN
    DECLARE EXIT HANDLER FOR 1062
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un registro con ese valor unico';
    IF NOT EXISTS (SELECT 1 FROM CONDUCTOR WHERE DNI = p_dni) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El registro no existe';
    END IF;
    UPDATE CONDUCTOR SET Nombre = p_nombre, Nro_Licencia = p_nro_licencia WHERE DNI = p_dni;
END$$

DROP PROCEDURE IF EXISTS sp_conductor_eliminar$$
CREATE PROCEDURE sp_conductor_eliminar(IN p_dni VARCHAR(8))
BEGIN
    DECLARE EXIT HANDLER FOR 1451
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar: el registro esta siendo usado por otras tablas';
    IF NOT EXISTS (SELECT 1 FROM CONDUCTOR WHERE DNI = p_dni) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El registro no existe';
    END IF;
    DELETE FROM CONDUCTOR WHERE DNI = p_dni;
END$$

DROP PROCEDURE IF EXISTS sp_producto_registrar$$
CREATE PROCEDURE sp_producto_registrar(    IN p_gtin VARCHAR(14), IN p_sunat VARCHAR(10), IN p_descripcion VARCHAR(250),
    IN p_partida VARCHAR(10), IN p_unidad VARCHAR(20), OUT p_id INT)
BEGIN
    INSERT INTO PRODUCTO (Codigo_GTIN, Codigo_productoSUNAT, Descripcion, Partida_arancelaria, Unidad_de_medida)
    VALUES (p_gtin, p_sunat, p_descripcion, p_partida, p_unidad);
    SET p_id = LAST_INSERT_ID();
END$$

DROP PROCEDURE IF EXISTS sp_producto_modificar$$
CREATE PROCEDURE sp_producto_modificar(    IN p_id INT, IN p_gtin VARCHAR(14), IN p_sunat VARCHAR(10), IN p_descripcion VARCHAR(250),
    IN p_partida VARCHAR(10), IN p_unidad VARCHAR(20))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM PRODUCTO WHERE Id_producto = p_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto no existe';
    END IF;
    UPDATE PRODUCTO
       SET Codigo_GTIN = p_gtin, Codigo_productoSUNAT = p_sunat, Descripcion = p_descripcion,
           Partida_arancelaria = p_partida, Unidad_de_medida = p_unidad
     WHERE Id_producto = p_id;
END$$

DROP PROCEDURE IF EXISTS sp_producto_eliminar$$
CREATE PROCEDURE sp_producto_eliminar(IN p_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR 1451
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar: el producto esta en guias registradas';
    IF NOT EXISTS (SELECT 1 FROM PRODUCTO WHERE Id_producto = p_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El producto no existe';
    END IF;
    DELETE FROM PRODUCTO WHERE Id_producto = p_id;
END$$

DELIMITER ;

/* ---------- VERIFICACION ---------- */
SELECT ROUTINE_NAME AS procedimiento
FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA = 'mining_casava' AND ROUTINE_TYPE = 'PROCEDURE'
ORDER BY ROUTINE_NAME;

/* ---------- PRUEBAS RAPIDAS (opcionales, una por una) ----------

-- Login correcto (ver los 4 valores de salida)
CALL sp_login('gestor1', 'Ges#2026', 'LAPTOP-PRUEBA', @res, @rol, @nom, @id);
SELECT @res AS resultado, @rol AS rol, @nom AS nombre, @id AS id;

-- Login incorrecto
CALL sp_login('gestor1', 'mala-clave', 'LAPTOP-PRUEBA', @res, @rol, @nom, @id);
SELECT @res AS resultado;
SELECT * FROM AUDITORIA_ACCESO ORDER BY Id_acceso DESC LIMIT 5;

-- Registrar una guia completa (Remitente, privada, venta, 1 bien, 1 traslado)
SET @usuario_app = 'gestor1';
CALL sp_guia_registrar('EG07-00009001', 'Remitente', '2026-11-02', '09:30:00', 'Venta', '2026-11-02',
     NULL, 'PLANTA DE BENEFICIO SAN JOSE, KM 24 CARRETERA AREQUIPA - LA JOYA, DISTRITO DE LA JOYA, AREQUIPA',
     'TERMINAL PORTUARIO DE MATARANI, MUELLE SUR S/N, DISTRITO DE ISLAY, PROVINCIA DE ISLAY, AREQUIPA',
     850.000, 'KGM', 'Privado', '20158813998', '20662836016', NULL, NULL, NULL, NULL,
     0, 0, 0, NULL, NULL,
     '[{"item":1,"producto":4,"normalizado":0,"cantidad":850.00}]',
     '[{"placa":"CBM500","dni":"52477647"}]', NULL);

-- Eliminarla
CALL sp_guia_eliminar('EG07-00009001');
*/
