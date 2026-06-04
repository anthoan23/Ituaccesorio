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
) ENGINE=InnoDB AUTO_INCREMENT=595 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bitacora`
--

LOCK TABLES `bitacora` WRITE;
/*!40000 ALTER TABLE `bitacora` DISABLE KEYS */;
INSERT INTO `bitacora` VALUES (590,'CLIENTE',1,'Cotización Trade-in','Cotización Trade-in | Modelo: Galaxy S24 Ultra | Base: 1100 | Deducción: 0 | Estimado: 1100 | Fallas: Pantalla, Batería, Cámara, Táctil, Puerto de carga, Micrófono, Bocina, WiFi','2026-05-13 15:38:41'),(591,'CLIENTE',1,'Cotización Trade-in','Cotización Trade-in | Modelo: iPhone 15 Pro | Base: 1200 | Deducción: 0 | Estimado: 1200 | Fallas: Pantalla, Batería, Cámara, Táctil, Puerto de carga, Micrófono, Bocina, WiFi','2026-05-13 15:46:59'),(592,'CLIENTE',1,'Cotización Trade-in','Cotización Trade-in | Modelo: iPhone 15 Pro | Base: 1200 | Deducción: 0 | Estimado: 1200 | Fallas: Botón de power, LCD, Táctil, Cámara trasera, Cámara delantera, Sensor de proximidad, Caja','2026-05-13 16:00:50'),(593,'CLIENTE',1,'Cotización Trade-in','Cotización Trade-in | Modelo: iPhone 15 Pro | Base: 1200 | Deducción: 0 | Estimado: 1200 | Fallas: Botón de power, Cornetas, Táctil','2026-05-13 16:10:03'),(594,'CLIENTE',1,'Cotización Trade-in','Cotización Trade-in | Modelo: iPhone 15 Pro | Base: 1200 | Deducción: 0 | Estimado: 1200 | Fallas: Botón de power, Cornetas, Mica, Sensor de proximidad','2026-05-15 02:31:39');
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modulo`
--

LOCK TABLES `modulo` WRITE;
/*!40000 ALTER TABLE `modulo` DISABLE KEYS */;
INSERT INTO `modulo` VALUES (1,'Productos','Gestión de productos y catálogo'),(3,'Carrito','Gestión del carrito de compras'),(4,'Pedidos','Procesamiento y seguimiento de pedidos'),(5,'Pagos','Procesamiento de pagos y facturación'),(6,'Usuarios','Gestión de usuarios, credenciales y estados de cuenta'),(7,'Roles','Configuración de roles del sistema (Admin, Técnico, Ventas, etc.)'),(8,'Permisos','Asignación de permisos de lectura, escritura, modificación y borrado por módulo'),(9,'Bitácora','Auditoría del sistema y registro de acciones de los usuarios'),(10,'Reportes','Generación de estadísticas de ventas, reparaciones y movimientos técnicos'),(11,'Soporte','Gestión de tickets de soporte técnico y atención al cliente'),(13,'Inventario','Control de stock de repuestos y productos en almacén'),(14,'Clientes','Gestión de datos de contacto e historial de clientes específicos'),(15,'Trade-in','Modulo para la cotizacion y gestion del trade-in');
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
INSERT INTO `permiso` VALUES (6,1,1,0,0,0),(6,3,1,0,0,0),(6,4,1,0,0,0),(6,5,1,0,0,0),(6,15,1,0,0,0),(7,1,1,0,0,0),(7,3,1,1,1,1),(7,4,1,0,0,0),(7,5,1,0,0,0),(7,15,1,0,0,0);
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
  UNIQUE KEY `email` (`cedula`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES ('USR-001','Eduin',32014004,'Dino1234',1,1,'2026-05-10 02:51:02','/static/img/perfil/725ff8bd356d449a8bc7e9cd9e54f579.jpg','2026-05-21 03:38:50'),('USR-002','Anthoan',2323123,'Dino1234',6,1,'2026-05-17 02:04:00',NULL,'2026-05-17 02:05:11'),('USR-003','Elena',40404040,'Dino1234',5,1,'2026-05-17 02:04:49',NULL,'2026-05-17 02:05:11'),('USR-004','ClienteTest',9876543,'Dino1234',7,1,'2026-05-21 03:24:14',NULL,'2026-05-21 03:24:14'),('USR-005','Prueba',12345678,'Dino1234',7,1,'2026-06-04 01:09:43','/static/img/perfil/4bf079567cf44a8086d4cce7a324573a.png','2026-06-04 01:21:23');
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

-- Dump completed on 2026-06-03 22:05:07
