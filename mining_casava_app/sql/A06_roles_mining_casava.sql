/* =====================================================================
   APLICATIVO - SCRIPT A06: ROLES Y PERMISOS DE MYSQL
   Base: mining_casava - ejecutar AL FINAL (despues de A03, A04 y A05),
   con un usuario administrador de MySQL (root).

   Hay 4 roles de aplicacion y, ademas, una cuenta tecnica solo para el login.
   La aplicacion funciona asi:
     1. Se conecta como  app_login  (solo puede ejecutar sp_login).
     2. sp_login valida usuario y clave y devuelve el ROL de la persona.
     3. La aplicacion se RECONECTA con la cuenta de MySQL de ese rol
        (u_externo, u_empleado, u_gestor o u_admin).
   Asi los permisos los hace cumplir el propio MySQL, no solo la interfaz.

   Rol MySQL        Cuenta        Que puede hacer
   ---------------  ------------  ----------------------------------------------
   rol_externo      u_externo     Reportes 01 y 07
   rol_empleado     u_empleado    SELECT en las 10 tablas + los 12 reportes
   rol_gestor       u_gestor      Lo del empleado + procedimientos de alta, cambio
                                  y baja (solo REGISTROS, ningun DDL)
   rol_admin        u_admin       ALL PRIVILEGES sobre mining_casava + gestion de
                                  usuarios + auditoria

   Los procedimientos se ejecutan con los privilegios de su creador (DEFINER),
   por eso los roles solo necesitan EXECUTE: ningun rol, salvo el
   administrador, puede hacer INSERT/UPDATE/DELETE directo sobre las tablas.

   CAMBIAR las claves de ejemplo antes de entregar el proyecto en produccion.
   ===================================================================== */

-- Limpieza para poder repetir el script
DROP USER IF EXISTS 'app_login'@'localhost';
DROP USER IF EXISTS 'u_externo'@'localhost';
DROP USER IF EXISTS 'u_empleado'@'localhost';
DROP USER IF EXISTS 'u_gestor'@'localhost';
DROP USER IF EXISTS 'u_admin'@'localhost';
DROP ROLE IF EXISTS rol_externo, rol_empleado, rol_gestor, rol_admin;

CREATE ROLE rol_externo, rol_empleado, rol_gestor, rol_admin;

/* ---------- ROL EXTERNO: dos reportes genericos ---------- */
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_01 TO rol_externo;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_07 TO rol_externo;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_cerrar_sesion TO rol_externo;

/* ---------- ROL EMPLEADO: consulta todo lo registrado ---------- */
GRANT SELECT ON mining_casava.EMPRESA TO rol_empleado;
GRANT SELECT ON mining_casava.TRANSPORTISTA TO rol_empleado;
GRANT SELECT ON mining_casava.VEHICULO TO rol_empleado;
GRANT SELECT ON mining_casava.CONDUCTOR TO rol_empleado;
GRANT SELECT ON mining_casava.PRODUCTO TO rol_empleado;
GRANT SELECT ON mining_casava.GUIA_DE_REMISION TO rol_empleado;
GRANT SELECT ON mining_casava.DETALLE_GUIA TO rol_empleado;
GRANT SELECT ON mining_casava.DOCUMENTO_RELACIONADO TO rol_empleado;
GRANT SELECT ON mining_casava.TRASLADO TO rol_empleado;
GRANT SELECT ON mining_casava.BIEN_TRANSPORTADO TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_01 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_02 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_03 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_04 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_05 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_06 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_07 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_08 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_09 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_10 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_11 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_rpt_12 TO rol_empleado;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_cerrar_sesion TO rol_empleado;

/* ---------- ROL GESTOR: empleado + insertar, modificar y eliminar registros ---------- */
GRANT rol_empleado TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_guia_registrar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_guia_modificar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_guia_eliminar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_empresa_registrar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_empresa_modificar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_empresa_eliminar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_transportista_registrar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_transportista_modificar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_transportista_eliminar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_vehiculo_registrar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_vehiculo_modificar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_vehiculo_eliminar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_conductor_registrar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_conductor_modificar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_conductor_eliminar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_producto_registrar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_producto_modificar TO rol_gestor;
GRANT EXECUTE ON PROCEDURE mining_casava.sp_producto_eliminar TO rol_gestor;

/* ---------- ROL ADMINISTRADOR: todos los permisos ---------- */
GRANT ALL PRIVILEGES ON mining_casava.* TO rol_admin;

/* ---------- CUENTAS DE MYSQL (una por rol + la del login) ---------- */
CREATE USER 'app_login'@'localhost'  IDENTIFIED BY 'AppLogin#2026';
CREATE USER 'u_externo'@'localhost'  IDENTIFIED BY 'Externo#2026';
CREATE USER 'u_empleado'@'localhost' IDENTIFIED BY 'Empleado#2026';
CREATE USER 'u_gestor'@'localhost'   IDENTIFIED BY 'Gestor#2026';
CREATE USER 'u_admin'@'localhost'    IDENTIFIED BY 'Admin#2026';

GRANT EXECUTE ON PROCEDURE mining_casava.sp_login TO 'app_login'@'localhost';

GRANT rol_externo  TO 'u_externo'@'localhost';
GRANT rol_empleado TO 'u_empleado'@'localhost';
GRANT rol_gestor   TO 'u_gestor'@'localhost';
GRANT rol_admin    TO 'u_admin'@'localhost';

-- Que el rol quede activo apenas la cuenta se conecta
SET DEFAULT ROLE rol_externo  TO 'u_externo'@'localhost';
SET DEFAULT ROLE rol_empleado TO 'u_empleado'@'localhost';
SET DEFAULT ROLE rol_gestor   TO 'u_gestor'@'localhost';
SET DEFAULT ROLE rol_admin    TO 'u_admin'@'localhost';

FLUSH PRIVILEGES;

/* ---------- VERIFICACION (capturas) ---------- */
SHOW GRANTS FOR 'app_login'@'localhost';
SHOW GRANTS FOR 'u_externo'@'localhost' USING rol_externo;
SHOW GRANTS FOR 'u_empleado'@'localhost' USING rol_empleado;
SHOW GRANTS FOR 'u_gestor'@'localhost' USING rol_gestor, rol_empleado;
SHOW GRANTS FOR 'u_admin'@'localhost' USING rol_admin;

SELECT User AS cuenta, Host FROM mysql.user
WHERE User IN ('app_login','u_externo','u_empleado','u_gestor','u_admin');

/* ---------- PRUEBAS DE ACCESO POR ROL ----------
   Abrir una conexion nueva en Workbench con cada cuenta y probar:

   -- Como u_externo:
   CALL mining_casava.sp_rpt_01('EG07-00000100');      -- funciona
   CALL mining_casava.sp_rpt_02(NULL, NULL);           -- ERROR 1370: sin permiso
   SELECT * FROM mining_casava.EMPRESA;                -- ERROR 1142: sin permiso

   -- Como u_empleado:
   SELECT COUNT(*) FROM mining_casava.GUIA_DE_REMISION;     -- funciona
   CALL mining_casava.sp_empresa_registrar('20999999991','PRUEBA S.A.C.');  -- ERROR: sin permiso

   -- Como u_gestor:
   CALL mining_casava.sp_empresa_registrar('20999999991','PRUEBA S.A.C.');  -- funciona
   DROP TABLE mining_casava.EMPRESA;                   -- ERROR: sin permiso (no toca estructuras)
   DELETE FROM mining_casava.EMPRESA;                  -- ERROR: solo por procedimientos

   -- Como u_admin: todo funciona, incluidas sp_adm_aud_accesos y sp_adm_usuario_crear.
*/
