-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: seguridad
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bitacora`
--

DROP TABLE IF EXISTS `bitacora`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bitacora` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `modulo_id` int NOT NULL,
  `accion` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `fecha_hora` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `modulo_id` (`modulo_id`),
  CONSTRAINT `bitacora_ibfk_2` FOREIGN KEY (`modulo_id`) REFERENCES `modulo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bitacora`
--

LOCK TABLES `bitacora` WRITE;
/*!40000 ALTER TABLE `bitacora` DISABLE KEYS */;
INSERT INTO `bitacora` VALUES (595,'USR-001',14,'Actualizar usuario','Se actualizó el usuario ID: USR-001 - Nuevo nombre: Eduin - Rol ID: 1','2026-06-06 20:19:35'),(596,'USR-001',14,'Actualizar usuario','Se actualizó el usuario ID: USR-001 - Nuevo nombre: Eduin - Rol ID: 1','2026-06-06 20:29:27'),(597,'USR-001',14,'Actualizar usuario','Se actualizó el usuario ID: USR-002 - Nuevo nombre: Anthoan - Rol ID: 6','2026-06-06 20:40:49'),(598,'USR-001',14,'Actualizar usuario','Se actualizó el usuario ID: USR-003 - Nuevo nombre: Elena - Rol ID: 5','2026-06-06 20:41:02'),(599,'USR-001',14,'Actualizar usuario','Se actualizó el usuario ID: USR-004 - Nuevo nombre: ClienteTest - Rol ID: 7','2026-06-06 20:41:14'),(600,'USR-001',14,'Actualizar usuario','Se actualizó el usuario ID: USR-005 - Nuevo nombre: Prueba - Rol ID: 7','2026-06-06 20:41:24');
/*!40000 ALTER TABLE `bitacora` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modulo`
--

DROP TABLE IF EXISTS `modulo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modulo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modulo`
--

LOCK TABLES `modulo` WRITE;
/*!40000 ALTER TABLE `modulo` DISABLE KEYS */;
INSERT INTO `modulo` VALUES (1,'Empleados','Gestión de empleados del sistema'),(2,'Especialidades','Gestión de especialidades técnicas'),(3,'Cargos','Gestión de cargos y posiciones'),(4,'Catálogo','Catálogo de productos para ventas'),(5,'Ventas','Gestión de ventas y facturación'),(6,'Productos','Gestión de productos del inventario'),(7,'Inventario','Control de stock y existencias'),(8,'Proveedores','Gestión de proveedores'),(9,'Trade-in','Módulo de intercambio de equipos'),(10,'Taller','Gestión de reparaciones y servicio técnico'),(11,'Órdenes de servicio','Seguimiento de órdenes de servicio'),(12,'Órdenes de compra','Gestión de compras a proveedores'),(13,'Clientes','Gestión de clientes del sistema'),(14,'Usuarios','Administración de usuarios y roles'),(15,'Bitácora','Registro de actividades del sistema'),(16,'Personal','Agrupación de módulos de personal');
/*!40000 ALTER TABLE `modulo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permiso`
--

DROP TABLE IF EXISTS `permiso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permiso` (
  `rol_id` int NOT NULL,
  `modulo_id` int NOT NULL,
  `consultar` tinyint(1) DEFAULT '1',
  `registrar` tinyint(1) DEFAULT '0',
  `modificar` tinyint(1) DEFAULT '0',
  `eliminar` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`rol_id`,`modulo_id`),
  KEY `modulo_id` (`modulo_id`),
  CONSTRAINT `permiso_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`id`) ON DELETE CASCADE,
  CONSTRAINT `permiso_ibfk_2` FOREIGN KEY (`modulo_id`) REFERENCES `modulo` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permiso`
--

LOCK TABLES `permiso` WRITE;
/*!40000 ALTER TABLE `permiso` DISABLE KEYS */;
INSERT INTO `permiso` VALUES (7,1,1,0,0,0),(7,2,1,0,0,0),(7,3,1,0,0,0),(7,4,1,1,1,1),(7,5,1,0,0,0),(7,6,1,0,0,0),(7,7,1,0,0,0),(7,8,1,0,0,0),(7,9,1,1,1,1),(7,10,1,0,0,0),(7,11,1,0,0,0),(7,12,1,0,0,0),(7,13,1,0,0,0),(7,14,1,0,0,0),(7,15,1,0,0,0),(7,16,1,0,0,0);
/*!40000 ALTER TABLE `permiso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'Admin','Administrador del sistema'),(5,'Tecnico','Rol diseñado para los técnicos del negocio'),(6,'Ventas','Rol para los empleados de ventas'),(7,'Cliente','Rol diseñado para los clientes');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `cedula` int NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `rol_id` int NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `foto_perfil` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `ultima_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES ('USR-001','Eduin',32014004,'scrypt:32768:8:1$mxwPiweA9tJ7B6Lo$729382722a55df092f3adef1a1c4517c4451d26aaf40c6d0b8357bc9b5de02de5356fdee34aa5d8cc60889a0fcf891bb36e210f673a7ca8131fadcc9fb291cc4',1,1,'2026-05-10 02:51:02','/static/img/perfil/725ff8bd356d449a8bc7e9cd9e54f579.jpg','2026-06-06 20:29:27'),('USR-002','Anthoan',12345543,'scrypt:32768:8:1$EY3xLxxGteKZdpu8$283663cbdf1749a8cfc820f7bc1355833d83ec376e186559779404adbe072a8cc4f36383549fbe6926338986adb0b6257f7a6472b6fadcdac5da52424c95c9a9',6,1,'2026-05-17 02:04:00',NULL,'2026-06-06 20:40:49'),('USR-003','Elena',30124556,'scrypt:32768:8:1$9m0ICCxI0bwFmxmk$e8a71fc275c67c8dda2704f227838c02426c980d8f0f7c9de95be5872b7a62edf7e69281b604ae361cb0f07e6078150510ba3e792e0b97f82215e5bfa1e94c53',5,1,'2026-05-17 02:04:49',NULL,'2026-06-06 20:41:02'),('USR-004','ClienteTest',30548845,'scrypt:32768:8:1$1KR2WxQrRgAhljzc$dc6695d2bf3169711ea51793e015a47738f33cf90114ab562a24409eca2b3107866c3301414a3e9d93e12c252c40faa59dd72d73abbaf94c7f3e7b19d2591c4f',7,1,'2026-05-21 03:24:14',NULL,'2026-06-06 20:41:14'),('USR-005','Prueba',31111555,'scrypt:32768:8:1$tVHhdy5aM0GpG4Ih$eea5255b05e729be54f83953b0851833a64d51f28ce5e75e55c07f8c247c50c3331dd72a97b9c40f122e5ccfc6c2073b439060771fb67f429324013016c0c475',7,1,'2026-06-04 01:09:43','/static/img/perfil/4bf079567cf44a8086d4cce7a324573a.png','2026-06-06 20:41:24');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'seguridad'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_registrar_usuario_con_prefijo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `sp_registrar_usuario_con_prefijo`(
    IN p_nombre VARCHAR(50) CHARACTER SET utf8mb4,
    IN p_cedula INT,
    IN p_password VARCHAR(255) CHARACTER SET utf8mb4,
    IN p_rol_id INT,
    IN p_foto_perfil VARCHAR(100) CHARACTER SET utf8mb4
)
BEGIN
    DECLARE v_nuevo_id VARCHAR(10) CHARACTER SET utf8mb4;
    DECLARE v_numero INT;
    DECLARE v_existe INT DEFAULT 1;
    DECLARE v_intentos INT DEFAULT 0;
    DECLARE v_max_intentos INT DEFAULT 10;
    
    -- Obtener el último número usado
    SELECT IFNULL(MAX(CAST(SUBSTRING(id, 5) AS UNSIGNED)), 0) INTO v_numero
    FROM usuario
    WHERE id LIKE 'USR-%';
    
    -- Generar ID único con prefijo USR-
    WHILE v_existe > 0 AND v_intentos < v_max_intentos DO
        SET v_intentos = v_intentos + 1;
        SET v_numero = v_numero + 1;
        SET v_nuevo_id = CONCAT('USR-', LPAD(v_numero, 3, '0'));
        
        -- Usar CAST para evitar problemas de collation (reemplaza BINARY)
        SELECT COUNT(*) INTO v_existe 
        FROM usuario 
        WHERE CAST(id AS CHAR) = CAST(v_nuevo_id AS CHAR);
    END WHILE;
    
    -- Si no se pudo generar un ID único
    IF v_intentos >= v_max_intentos THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se pudo generar un ID único para el usuario';
    END IF;
    
    -- Insertar el nuevo usuario
    INSERT INTO usuario (
        id,
        nombre,
        cedula,
        password,
        rol_id,
        activo,
        fecha_creacion,
        foto_perfil,
        ultima_actualizacion
    ) VALUES (
        v_nuevo_id,
        p_nombre,
        p_cedula,
        p_password,
        p_rol_id,
        1,
        NOW(),
        p_foto_perfil,
        NOW()
    );
    
    -- Devolver el ID generado
    SELECT v_nuevo_id AS id_generado;
    
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-06 16:44:55
