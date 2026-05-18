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
  `usuario_id` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `modulo_id` int NOT NULL,
  `accion` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `fecha_hora` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `modulo_id` (`modulo_id`),
  CONSTRAINT `bitacora_ibfk_2` FOREIGN KEY (`modulo_id`) REFERENCES `modulo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=595 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modulo`
--

LOCK TABLES `modulo` WRITE;
/*!40000 ALTER TABLE `modulo` DISABLE KEYS */;
INSERT INTO `modulo` VALUES (1,'Productos','Gestión de productos y catálogo'),(2,'Categorías','Gestión de categorías de productos'),(3,'Carrito','Gestión del carrito de compras'),(4,'Pedidos','Procesamiento y seguimiento de pedidos'),(5,'Pagos','Procesamiento de pagos y facturación'),(15,'Trade-in','Modulo para la cotizacion y gestion del trade-in');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permiso`
--

LOCK TABLES `permiso` WRITE;
/*!40000 ALTER TABLE `permiso` DISABLE KEYS */;
INSERT INTO `permiso` VALUES (1,3,1,0,0,0);
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
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'Admin','none'),(5,'Tecnico','none'),(6,'Ventas','rol para los empleados de ventas');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `cedula` int NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `rol_id` int NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `foto_perfil` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ultima_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`cedula`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES ('USR-001','Eduin',32014004,'Dino1234',1,1,'2026-05-10 02:51:02',NULL,'2026-05-17 02:05:11'),('USR-002','Anthoan',2323123,'Dino1234',6,1,'2026-05-17 02:04:00',NULL,'2026-05-17 02:05:11'),('USR-003','Elena',40404040,'Dino1234',5,1,'2026-05-17 02:04:49',NULL,'2026-05-17 02:05:11'),('USR-004','antonio',313131313,'Dino1234',6,1,'2026-05-17 02:13:43',NULL,'2026-05-17 02:16:03');
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
    IN p_nombre VARCHAR(50),
    IN p_cedula INT,
    IN p_password VARCHAR(255),
    IN p_rol_id INT,
    IN p_foto_perfil VARCHAR(100)
)
BEGIN
    DECLARE v_count INT;
    DECLARE v_nuevo_id VARCHAR(20);
    DECLARE v_prefijo VARCHAR(5) DEFAULT 'USR-';
    
    -- Obtener el siguiente número secuencial
    -- Contamos cuántos usuarios hay para generar el siguiente (puedes usar una tabla de secuencias si prefieres)
    SELECT COUNT(*) + 1 INTO v_count FROM usuario;
    
    -- Formatear el ID (Ejemplo: USR-0001, USR-0002...)
    SET v_nuevo_id = CONCAT(v_prefijo, LPAD(v_count, 3, '0'));
    
    -- Insertar el nuevo registro
    INSERT INTO usuario (id, nombre, cedula, password, rol_id, activo, foto_perfil)
    VALUES (v_nuevo_id, p_nombre, p_cedula, p_password, p_rol_id, 1, p_foto_perfil);
    
    -- Retornar el ID creado para el backend
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

-- Dump completed on 2026-05-16 22:17:18
