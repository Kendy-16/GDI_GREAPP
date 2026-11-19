/* =====================================================================
   APLICATIVO - SCRIPT A05: REPORTES (12) + CONSULTAS DE AUDITORIA (2)
   Base: mining_casava - ejecutar DESPUES de A02. Solo lee datos.

   Los reportes parten de las 10 consultas del script 03 (serie, rango de
   series, fechas, remitente, items, vehiculo y conductor, productos, dia y
   mes) mejoradas con parametros y completadas hasta 12. Cada reporte es un
   procedimiento almacenado; un parametro NULL significa "sin filtro".

   Reporte  Nombre                                        JOIN      Rol minimo
   -------  --------------------------------------------  --------  ----------
   01       Guia completa por serie                       SI (4)    EXTERNO
   02       Guias por rango de fechas                     no        EMPLEADO
   03       Guias por remitente                           SI (2)    EMPLEADO
   04       Items de una guia con su producto             SI        EMPLEADO
   05       Vehiculo y conductor de cada guia             SI (3)    EMPLEADO
   06       Productos mas transportados                   SI        EMPLEADO
   07       Guias por mes                                 no        EXTERNO
   08       Guias por tipo, modalidad y motivo            no        EMPLEADO
   09       Peso transportado por destinatario            SI        EMPLEADO
   10       Viajes por conductor y vehiculo               SI (3)    EMPLEADO
   11       Guias con transbordo o retorno vacio          SI (2)    EMPLEADO
   12       Guias de compra con proveedor y documento     SI (2)    EMPLEADO
   Auditoria de ingresos y de cambios de datos                      ADMINISTRADOR

   9 de los 12 reportes usan JOIN (el enunciado pide al menos 6).

   EJECUCION EN WORKBENCH: usa DELIMITER $$ (ya incluido); ejecutar completo.
   ===================================================================== */

USE mining_casava;

DELIMITER $$

-- REPORTE 1 (JOIN). Guia completa por serie - disponible para EXTERNOS
DROP PROCEDURE IF EXISTS sp_rpt_01$$
CREATE PROCEDURE sp_rpt_01(IN p_serie VARCHAR(13))
BEGIN
    SELECT g.Serie_numero, g.Tipo_guia, g.Fecha, g.Hora, g.Motivo_traslado, g.Modalidad_traslado,
           rem.Razon_Social  AS remitente,
           dest.Razon_Social AS destinatario,
           tr.Razon_Social   AS transportista,
           g.Punto_partida, g.Punto_llegada,
           g.Peso_bruto_total_carga AS peso, g.Unidad_medida_peso_bruto AS unidad,
           IF(d.Transbordo_programado, 'SI', 'NO') AS transbordo,
           (SELECT COUNT(*) FROM BIEN_TRANSPORTADO b WHERE b.Serie_numero = g.Serie_numero) AS items
    FROM GUIA_DE_REMISION g
    JOIN EMPRESA rem  ON rem.RUC  = g.RUC_Remitente
    JOIN EMPRESA dest ON dest.RUC = g.RUC_Destinatario
    LEFT JOIN EMPRESA tr ON tr.RUC = g.RUC_Transportista
    LEFT JOIN DETALLE_GUIA d ON d.Serie_numero = g.Serie_numero
    WHERE g.Serie_numero = p_serie;
END$$

-- REPORTE 2. Guias por rango de fechas (usa idx_guia_fecha)
DROP PROCEDURE IF EXISTS sp_rpt_02$$
CREATE PROCEDURE sp_rpt_02(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT Serie_numero, Tipo_guia, Fecha, Hora, Motivo_traslado, Modalidad_traslado,
           Peso_bruto_total_carga AS peso, Unidad_medida_peso_bruto AS unidad
    FROM GUIA_DE_REMISION
    WHERE Fecha BETWEEN p_desde AND p_hasta
    ORDER BY Fecha, Hora;
END$$

-- REPORTE 3 (JOIN). Guias por remitente (usa idx_guia_ruc_remitente; RUC NULL = todos)
DROP PROCEDURE IF EXISTS sp_rpt_03$$
CREATE PROCEDURE sp_rpt_03(IN p_ruc VARCHAR(11))
BEGIN
    SELECT g.Serie_numero, g.Fecha, g.Motivo_traslado,
           rem.Razon_Social AS remitente, dest.Razon_Social AS destinatario,
           g.Peso_bruto_total_carga AS peso, g.Unidad_medida_peso_bruto AS unidad
    FROM GUIA_DE_REMISION g
    JOIN EMPRESA rem  ON rem.RUC  = g.RUC_Remitente
    JOIN EMPRESA dest ON dest.RUC = g.RUC_Destinatario
    WHERE p_ruc IS NULL OR g.RUC_Remitente = p_ruc
    ORDER BY g.Fecha, g.Hora;
END$$

-- REPORTE 4 (JOIN). Items de una guia con su producto (PK compuesta de BIEN_TRANSPORTADO)
DROP PROCEDURE IF EXISTS sp_rpt_04$$
CREATE PROCEDURE sp_rpt_04(IN p_serie VARCHAR(13))
BEGIN
    SELECT b.Serie_numero, b.Nro_item, p.Descripcion, b.Cantidad, p.Unidad_de_medida,
           IF(b.Bien_normalizado, 'SI', 'NO') AS bien_normalizado
    FROM BIEN_TRANSPORTADO b
    JOIN PRODUCTO p ON p.Id_producto = b.Id_producto
    WHERE b.Serie_numero = p_serie
    ORDER BY b.Nro_item;
END$$

-- REPORTE 5 (JOIN). Vehiculo y conductor de cada guia
DROP PROCEDURE IF EXISTS sp_rpt_05$$
CREATE PROCEDURE sp_rpt_05(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT t.Serie_numero, g.Fecha, v.Placa, v.Nro_TUCE, c.DNI, c.Nombre AS conductor, c.Nro_Licencia
    FROM TRASLADO t
    JOIN GUIA_DE_REMISION g ON g.Serie_numero = t.Serie_numero
    JOIN VEHICULO  v ON v.Placa = t.Placa
    JOIN CONDUCTOR c ON c.DNI   = t.DNI
    WHERE g.Fecha BETWEEN p_desde AND p_hasta
    ORDER BY g.Fecha, t.Serie_numero;
END$$

-- REPORTE 6 (JOIN). Productos mas transportados (usa idx_bien_id_producto)
DROP PROCEDURE IF EXISTS sp_rpt_06$$
CREATE PROCEDURE sp_rpt_06(IN p_top INT)
BEGIN
    SET p_top = COALESCE(p_top, 10);
    SELECT p.Id_producto, p.Descripcion, p.Unidad_de_medida,
           COUNT(*) AS veces_transportado,
           COUNT(DISTINCT b.Serie_numero) AS guias,
           SUM(b.Cantidad) AS cantidad_total
    FROM BIEN_TRANSPORTADO b
    JOIN PRODUCTO p ON p.Id_producto = b.Id_producto
    GROUP BY p.Id_producto, p.Descripcion, p.Unidad_de_medida
    ORDER BY veces_transportado DESC
    LIMIT p_top;
END$$

-- REPORTE 7. Guias por mes - disponible para EXTERNOS
DROP PROCEDURE IF EXISTS sp_rpt_07$$
CREATE PROCEDURE sp_rpt_07(IN p_anio INT)
BEGIN
    SELECT DATE_FORMAT(Fecha, '%Y-%m') AS mes,
           COUNT(*) AS guias,
           SUM(Tipo_guia = 'Remitente')     AS remitente,
           SUM(Tipo_guia = 'Transportista') AS transportista,
           ROUND(SUM(CASE Unidad_medida_peso_bruto WHEN 'TNE' THEN Peso_bruto_total_carga * 1000
                          ELSE Peso_bruto_total_carga END) / 1000, 2) AS toneladas
    FROM GUIA_DE_REMISION
    WHERE p_anio IS NULL OR YEAR(Fecha) = p_anio
    GROUP BY DATE_FORMAT(Fecha, '%Y-%m')
    ORDER BY mes;
END$$

-- REPORTE 8. Guias por tipo, modalidad y motivo
DROP PROCEDURE IF EXISTS sp_rpt_08$$
CREATE PROCEDURE sp_rpt_08(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT Tipo_guia, COALESCE(Modalidad_traslado, 'No aplica') AS modalidad,
           Motivo_traslado, COUNT(*) AS guias
    FROM GUIA_DE_REMISION
    WHERE Fecha BETWEEN p_desde AND p_hasta
    GROUP BY Tipo_guia, Modalidad_traslado, Motivo_traslado
    ORDER BY Tipo_guia, guias DESC;
END$$

-- REPORTE 9 (JOIN). Peso transportado por destinatario (en toneladas, TNE y KGM unificados)
DROP PROCEDURE IF EXISTS sp_rpt_09$$
CREATE PROCEDURE sp_rpt_09(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT dest.RUC, dest.Razon_Social AS destinatario,
           COUNT(*) AS guias,
           ROUND(SUM(CASE g.Unidad_medida_peso_bruto WHEN 'TNE' THEN g.Peso_bruto_total_carga * 1000 ELSE g.Peso_bruto_total_carga END) / 1000, 2) AS toneladas
    FROM GUIA_DE_REMISION g
    JOIN EMPRESA dest ON dest.RUC = g.RUC_Destinatario
    WHERE g.Fecha BETWEEN p_desde AND p_hasta
    GROUP BY dest.RUC, dest.Razon_Social
    ORDER BY toneladas DESC;
END$$

-- REPORTE 10 (JOIN). Viajes por conductor y vehiculo
DROP PROCEDURE IF EXISTS sp_rpt_10$$
CREATE PROCEDURE sp_rpt_10(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT c.DNI, c.Nombre AS conductor, v.Placa,
           COUNT(*) AS viajes,
           MIN(g.Fecha) AS primer_viaje, MAX(g.Fecha) AS ultimo_viaje
    FROM TRASLADO t
    JOIN GUIA_DE_REMISION g ON g.Serie_numero = t.Serie_numero
    JOIN CONDUCTOR c ON c.DNI   = t.DNI
    JOIN VEHICULO  v ON v.Placa = t.Placa
    WHERE g.Fecha BETWEEN p_desde AND p_hasta
    GROUP BY c.DNI, c.Nombre, v.Placa
    ORDER BY viajes DESC, c.Nombre;
END$$

-- REPORTE 11 (JOIN). Guias con transbordo, retorno de vehiculo vacio o de envases vacios
DROP PROCEDURE IF EXISTS sp_rpt_11$$
CREATE PROCEDURE sp_rpt_11(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT g.Serie_numero, g.Tipo_guia, g.Fecha, rem.Razon_Social AS remitente,
           IF(d.Transbordo_programado, 'SI', 'NO')    AS transbordo,
           IF(d.Vehiculo_vacio_retorno = 1, 'SI', 'NO') AS vehiculo_vacio_retorno,
           IF(d.Envases_vacios_retorno, 'SI', 'NO')   AS envases_vacios_retorno
    FROM GUIA_DE_REMISION g
    JOIN DETALLE_GUIA d ON d.Serie_numero = g.Serie_numero
    JOIN EMPRESA rem    ON rem.RUC = g.RUC_Remitente
    WHERE g.Fecha BETWEEN p_desde AND p_hasta
      AND (d.Transbordo_programado = 1 OR d.Vehiculo_vacio_retorno = 1 OR d.Envases_vacios_retorno = 1)
    ORDER BY g.Fecha, g.Hora;
END$$

-- REPORTE 12 (JOIN). Guias de compra con su proveedor y documento (LEFT JOIN: muestra tambien las que no tienen documento)
DROP PROCEDURE IF EXISTS sp_rpt_12$$
CREATE PROCEDURE sp_rpt_12(IN p_desde DATE, IN p_hasta DATE)
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT g.Serie_numero, g.Fecha, prov.Razon_Social AS proveedor,
           doc.Tipo_Documento, doc.Nro_Documento,
           g.Peso_bruto_total_carga AS peso, g.Unidad_medida_peso_bruto AS unidad
    FROM GUIA_DE_REMISION g
    JOIN EMPRESA prov ON prov.RUC = g.RUC_Proveedor
    LEFT JOIN DOCUMENTO_RELACIONADO doc ON doc.Serie_numero = g.Serie_numero
    WHERE g.Motivo_traslado = 'Compra' AND g.Fecha BETWEEN p_desde AND p_hasta
    ORDER BY g.Fecha, g.Hora;
END$$

-- AUDITORIA DE INGRESOS (solo ADMINISTRADOR)
DROP PROCEDURE IF EXISTS sp_adm_aud_accesos$$
CREATE PROCEDURE sp_adm_aud_accesos(IN p_desde DATE, IN p_hasta DATE, IN p_usuario VARCHAR(30))
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT Id_acceso, Fecha_hora, Usuario_intentado, Resultado, Equipo, Detalle
    FROM AUDITORIA_ACCESO
    WHERE DATE(Fecha_hora) BETWEEN p_desde AND p_hasta
      AND (p_usuario IS NULL OR Usuario_intentado = p_usuario)
    ORDER BY Id_acceso DESC;
END$$

-- TRAZABILIDAD DE DATOS (solo ADMINISTRADOR)
DROP PROCEDURE IF EXISTS sp_adm_aud_cambios$$
CREATE PROCEDURE sp_adm_aud_cambios(IN p_desde DATE, IN p_hasta DATE, IN p_tabla VARCHAR(30), IN p_operacion VARCHAR(6))
BEGIN
    SET p_desde = COALESCE(p_desde, '1900-01-01');
    SET p_hasta = COALESCE(p_hasta, '2999-12-31');
    SELECT Id_cambio, Fecha_hora, Usuario_app, Operacion, Tabla_afectada, Clave_registro,
           Valores_antes, Valores_despues
    FROM AUDITORIA_CAMBIOS
    WHERE DATE(Fecha_hora) BETWEEN p_desde AND p_hasta
      AND (p_tabla IS NULL OR Tabla_afectada = p_tabla)
      AND (p_operacion IS NULL OR Operacion = p_operacion)
    ORDER BY Id_cambio DESC;
END$$

DELIMITER ;

/* ---------- PRUEBAS (una por una, con captura) ---------- */
CALL sp_rpt_01('EG07-00000100');
CALL sp_rpt_02('2026-09-01', '2026-09-07');
CALL sp_rpt_03('20158813998');
CALL sp_rpt_04('EG07-00000100');
CALL sp_rpt_05('2026-10-01', '2026-10-03');
CALL sp_rpt_06(5);
CALL sp_rpt_07(2026);
CALL sp_rpt_08(NULL, NULL);
CALL sp_rpt_09('2026-07-01', '2026-10-31');
CALL sp_rpt_10('2026-10-01', '2026-10-31');
CALL sp_rpt_11('2026-07-01', '2026-10-31');
CALL sp_rpt_12('2026-07-01', '2026-10-31');
CALL sp_adm_aud_accesos(NULL, NULL, NULL);
CALL sp_adm_aud_cambios(NULL, NULL, NULL, NULL);
