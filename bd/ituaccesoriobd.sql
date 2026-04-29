-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: ituaccesorio
-- ------------------------------------------------------
-- Server version	8.4.0

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
-- Table structure for table `capacitacion`
--

DROP TABLE IF EXISTS `capacitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `capacitacion` (
  `ID_especialidad` int NOT NULL,
  `ID_em` int NOT NULL,
  PRIMARY KEY (`ID_especialidad`,`ID_em`),
  KEY `ID_em` (`ID_em`),
  CONSTRAINT `capacitacion_ibfk_1` FOREIGN KEY (`ID_especialidad`) REFERENCES `especialidad` (`ID_especialidad`),
  CONSTRAINT `capacitacion_ibfk_2` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `capacitacion`
--

LOCK TABLES `capacitacion` WRITE;
/*!40000 ALTER TABLE `capacitacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `capacitacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `caracteistica`
--

DROP TABLE IF EXISTS `caracteistica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `caracteistica` (
  `ID_producto` int NOT NULL,
  `Capacida` varchar(10) DEFAULT NULL,
  `Color` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`ID_producto`),
  CONSTRAINT `caracteistica_ibfk_stock` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `caracteistica`
--

LOCK TABLES `caracteistica` WRITE;
/*!40000 ALTER TABLE `caracteistica` DISABLE KEYS */;
/*!40000 ALTER TABLE `caracteistica` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cargo`
--

DROP TABLE IF EXISTS `cargo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cargo` (
  `ID_cargo` int NOT NULL AUTO_INCREMENT,
  `N_cargo` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_cargo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cargo`
--

LOCK TABLES `cargo` WRITE;
/*!40000 ALTER TABLE `cargo` DISABLE KEYS */;
/*!40000 ALTER TABLE `cargo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clase_producto`
--

DROP TABLE IF EXISTS `clase_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clase_producto` (
  `ID_clase` int NOT NULL AUTO_INCREMENT,
  `N_Clase` varchar(30) DEFAULT NULL,
  `Num_i` int DEFAULT NULL,
  PRIMARY KEY (`ID_clase`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clase_producto`
--

LOCK TABLES `clase_producto` WRITE;
/*!40000 ALTER TABLE `clase_producto` DISABLE KEYS */;
/*!40000 ALTER TABLE `clase_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `ID_c` int NOT NULL,
  `Nombre_c` varchar(40) DEFAULT NULL,
  `Apellido_c` varchar(40) DEFAULT NULL,
  `Celular_c` varchar(15) DEFAULT NULL,
  `Correo_c` varchar(30) DEFAULT NULL,
  `Direccion_c` varchar(60) DEFAULT NULL,
  `Tipo_c` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID_c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` (`ID_c`,`Nombre_c`,`Apellido_c`,`Celular_c`,`Correo_c`,`Direccion_c`,`Tipo_c`) VALUES
  (1,'María','González','04141234567','maria.g@example.com','Calle 1, Ciudad','Regular'),
  (2,'Juan','Pérez','04141234568','juan.p@example.com','Av. 2, Ciudad','Premium'),
  (3,'Ana','Rodríguez','04141234569','ana.r@example.com','Calle 3, Ciudad','Regular'),
  (4,'Luis','Martínez','04141234570','luis.m@example.com','Av. 4, Ciudad','Mayorista'),
  (5,'Carla','Fernández','04141234571','carla.f@example.com','Calle 5, Ciudad','Regular');
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credito`
--

DROP TABLE IF EXISTS `credito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credito` (
  `ID_credito` int NOT NULL AUTO_INCREMENT,
  `ID_orden` int DEFAULT NULL,
  `Dias_c` int DEFAULT NULL,
  PRIMARY KEY (`ID_credito`),
  KEY `ID_orden` (`ID_orden`),
  CONSTRAINT `credito_ibfk_1` FOREIGN KEY (`ID_orden`) REFERENCES `orden_compra` (`ID_orden_c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credito`
--

LOCK TABLES `credito` WRITE;
/*!40000 ALTER TABLE `credito` DISABLE KEYS */;
/*!40000 ALTER TABLE `credito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleado`
--

DROP TABLE IF EXISTS `empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado` (
  `ID_em` int NOT NULL,
  `Nombre_em` varchar(40) DEFAULT NULL,
  `Apellido_em` varchar(40) DEFAULT NULL,
  `Celular_em` varchar(15) DEFAULT NULL,
  `Correo_em` varchar(30) DEFAULT NULL,
  `Direccion_em` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ID_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleado_cargo`
--

DROP TABLE IF EXISTS `empleado_cargo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado_cargo` (
  `ID_cargo` int NOT NULL,
  `ID_em` int NOT NULL,
  `A_cargo` int DEFAULT NULL,
  PRIMARY KEY (`ID_cargo`,`ID_em`),
  KEY `ID_em` (`ID_em`),
  CONSTRAINT `empleado_cargo_ibfk_1` FOREIGN KEY (`ID_cargo`) REFERENCES `cargo` (`ID_cargo`),
  CONSTRAINT `empleado_cargo_ibfk_2` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado_cargo`
--

LOCK TABLES `empleado_cargo` WRITE;
/*!40000 ALTER TABLE `empleado_cargo` DISABLE KEYS */;
/*!40000 ALTER TABLE `empleado_cargo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entrega`
--

DROP TABLE IF EXISTS `entrega`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entrega` (
  `ID_p` int NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  `Estado` int DEFAULT NULL,
  `Direccion_e` varchar(60) DEFAULT NULL,
  `Fecha_e` varchar(10) DEFAULT NULL,
  `Hora_e` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ID_p`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `entrega_ibfk_1` FOREIGN KEY (`ID_p`) REFERENCES `personal_delivery` (`ID_p`),
  CONSTRAINT `entrega_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entrega`
--

LOCK TABLES `entrega` WRITE;
/*!40000 ALTER TABLE `entrega` DISABLE KEYS */;
/*!40000 ALTER TABLE `entrega` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entrega_p`
--

DROP TABLE IF EXISTS `entrega_p`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entrega_p` (
  `ID_entrega` int NOT NULL AUTO_INCREMENT,
  `ID_em` int DEFAULT NULL,
  `ID_orden_c` int DEFAULT NULL,
  `ID_producto` int DEFAULT NULL,
  `Catidad_e` int DEFAULT NULL,
  `Fecha_e` varchar(10) DEFAULT NULL,
  `Hora_e` varchar(10) DEFAULT NULL,
  `Factura` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID_entrega`),
  KEY `ID_em` (`ID_em`),
  KEY `ID_orden_c` (`ID_orden_c`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `entrega_p_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`),
  CONSTRAINT `entrega_p_ibfk_2` FOREIGN KEY (`ID_orden_c`) REFERENCES `orden_compra` (`ID_orden_c`),
  CONSTRAINT `entrega_p_ibfk_3` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entrega_p`
--

LOCK TABLES `entrega_p` WRITE;
/*!40000 ALTER TABLE `entrega_p` DISABLE KEYS */;
/*!40000 ALTER TABLE `entrega_p` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `especialidad`
--

DROP TABLE IF EXISTS `especialidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `especialidad` (
  `ID_especialidad` int NOT NULL AUTO_INCREMENT,
  `N_especialidad` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `especialidad`
--

LOCK TABLES `especialidad` WRITE;
/*!40000 ALTER TABLE `especialidad` DISABLE KEYS */;
/*!40000 ALTER TABLE `especialidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencia_e`
--

DROP TABLE IF EXISTS `evidencia_e`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencia_e` (
  `ID_evidencia_e` int NOT NULL AUTO_INCREMENT,
  `ID_orden` int DEFAULT NULL,
  `Foto_e` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_evidencia_e`),
  KEY `ID_orden` (`ID_orden`),
  CONSTRAINT `evidencia_e_ibfk_1` FOREIGN KEY (`ID_orden`) REFERENCES `orden_e` (`ID_orden_e`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia_e`
--

LOCK TABLES `evidencia_e` WRITE;
/*!40000 ALTER TABLE `evidencia_e` DISABLE KEYS */;
/*!40000 ALTER TABLE `evidencia_e` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencia_r`
--

DROP TABLE IF EXISTS `evidencia_r`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencia_r` (
  `ID_evidencia_r` int NOT NULL AUTO_INCREMENT,
  `ID_test` int DEFAULT NULL,
  `Foto_r` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_evidencia_r`),
  KEY `ID_test` (`ID_test`),
  CONSTRAINT `evidencia_r_ibfk_1` FOREIGN KEY (`ID_test`) REFERENCES `test` (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia_r`
--

LOCK TABLES `evidencia_r` WRITE;
/*!40000 ALTER TABLE `evidencia_r` DISABLE KEYS */;
/*!40000 ALTER TABLE `evidencia_r` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencia_t`
--

DROP TABLE IF EXISTS `evidencia_t`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencia_t` (
  `ID_Foto_s` int NOT NULL AUTO_INCREMENT,
  `ID_producto` int DEFAULT NULL,
  `Foto_s` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_Foto_s`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `evidencia_t_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia_t`
--

LOCK TABLES `evidencia_t` WRITE;
/*!40000 ALTER TABLE `evidencia_t` DISABLE KEYS */;
/*!40000 ALTER TABLE `evidencia_t` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencia_t_tradein`
--

DROP TABLE IF EXISTS `evidencia_t_tradein`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencia_t_tradein` (
  `ID_evidencia_t` int NOT NULL AUTO_INCREMENT,
  `ID_Tradein` int DEFAULT NULL,
  `Foto_t` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_evidencia_t`),
  KEY `ID_Tradein` (`ID_Tradein`),
  CONSTRAINT `evidencia_t_tradein_ibfk_1` FOREIGN KEY (`ID_Tradein`) REFERENCES `tradein` (`ID_Tradein`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia_t_tradein`
--

LOCK TABLES `evidencia_t_tradein` WRITE;
/*!40000 ALTER TABLE `evidencia_t_tradein` DISABLE KEYS */;
/*!40000 ALTER TABLE `evidencia_t_tradein` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interaccion`
--

DROP TABLE IF EXISTS `interaccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interaccion` (
  `ID_em` int NOT NULL,
  `ID_orden` int NOT NULL,
  `Accion` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_em`,`ID_orden`),
  KEY `ID_orden` (`ID_orden`),
  CONSTRAINT `interaccion_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`),
  CONSTRAINT `interaccion_ibfk_2` FOREIGN KEY (`ID_orden`) REFERENCES `orden_e` (`ID_orden_e`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interaccion`
--

LOCK TABLES `interaccion` WRITE;
/*!40000 ALTER TABLE `interaccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `interaccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lista_carrito`
--

DROP TABLE IF EXISTS `lista_carrito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lista_carrito` (
  `ID_carrito` int NOT NULL AUTO_INCREMENT,
  `ID_producto` int DEFAULT NULL,
  `ID_c` int DEFAULT NULL,
  `Cantidad` int DEFAULT NULL,
  `Estado_c` int DEFAULT NULL,
  PRIMARY KEY (`ID_carrito`),
  KEY `ID_producto` (`ID_producto`),
  KEY `ID_c` (`ID_c`),
  CONSTRAINT `lista_carrito_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`),
  CONSTRAINT `lista_carrito_ibfk_2` FOREIGN KEY (`ID_c`) REFERENCES `cliente` (`ID_c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lista_carrito`
--

LOCK TABLES `lista_carrito` WRITE;
/*!40000 ALTER TABLE `lista_carrito` DISABLE KEYS */;
/*!40000 ALTER TABLE `lista_carrito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lista_compra`
--

DROP TABLE IF EXISTS `lista_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lista_compra` (
  `ID_producto` int NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  `Cantidad` int DEFAULT NULL,
  PRIMARY KEY (`ID_producto`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `lista_compra_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`),
  CONSTRAINT `lista_compra_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lista_compra`
--

LOCK TABLES `lista_compra` WRITE;
/*!40000 ALTER TABLE `lista_compra` DISABLE KEYS */;
/*!40000 ALTER TABLE `lista_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marca_producto`
--

DROP TABLE IF EXISTS `marca_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `marca_producto` (
  `ID_marca` int NOT NULL AUTO_INCREMENT,
  `ID_clase` int DEFAULT NULL,
  `N_marca` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_marca`),
  KEY `ID_clase` (`ID_clase`),
  CONSTRAINT `marca_producto_ibfk_1` FOREIGN KEY (`ID_clase`) REFERENCES `clase_producto` (`ID_clase`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marca_producto`
--

LOCK TABLES `marca_producto` WRITE;
/*!40000 ALTER TABLE `marca_producto` DISABLE KEYS */;
/*!40000 ALTER TABLE `marca_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modelo_producto`
--

DROP TABLE IF EXISTS `modelo_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modelo_producto` (
  `ID_modelo` int NOT NULL AUTO_INCREMENT,
  `ID_marca` int DEFAULT NULL,
  `N_modelo` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_modelo`),
  KEY `modelo_producto_fk_marca` (`ID_marca`),
  CONSTRAINT `modelo_producto_fk_marca` FOREIGN KEY (`ID_marca`) REFERENCES `marca_producto` (`ID_marca`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modelo_producto`
--

LOCK TABLES `modelo_producto` WRITE;
/*!40000 ALTER TABLE `modelo_producto` DISABLE KEYS */;
/*!40000 ALTER TABLE `modelo_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orden_compra`
--

DROP TABLE IF EXISTS `orden_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden_compra` (
  `ID_orden_c` int NOT NULL AUTO_INCREMENT,
  `ID_em` int DEFAULT NULL,
  `ID_provedor` int DEFAULT NULL,
  `Fecha_o` varchar(10) DEFAULT NULL,
  `Costo_venta` int DEFAULT NULL,
  PRIMARY KEY (`ID_orden_c`),
  KEY `ID_em` (`ID_em`),
  KEY `ID_provedor` (`ID_provedor`),
  CONSTRAINT `orden_compra_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`),
  CONSTRAINT `orden_compra_ibfk_2` FOREIGN KEY (`ID_provedor`) REFERENCES `provedor` (`ID_provedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orden_compra`
--

LOCK TABLES `orden_compra` WRITE;
/*!40000 ALTER TABLE `orden_compra` DISABLE KEYS */;
/*!40000 ALTER TABLE `orden_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orden_e`
--

DROP TABLE IF EXISTS `orden_e`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orden_e` (
  `ID_orden_e` int NOT NULL AUTO_INCREMENT,
  `ID_modelo` int DEFAULT NULL,
  `ID_c` int DEFAULT NULL,
  `Estado_o` varchar(20) DEFAULT NULL,
  `Des_cliente` varchar(300) DEFAULT NULL,
  `Patron` int DEFAULT NULL,
  `Clave` varchar(60) DEFAULT NULL,
  `Costo_reparacion` int DEFAULT NULL,
  PRIMARY KEY (`ID_orden_e`),
  KEY `ID_modelo` (`ID_modelo`),
  KEY `ID_c` (`ID_c`),
  CONSTRAINT `orden_e_ibfk_1` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`),
  CONSTRAINT `orden_e_ibfk_2` FOREIGN KEY (`ID_c`) REFERENCES `cliente` (`ID_c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orden_e`
--

LOCK TABLES `orden_e` WRITE;
/*!40000 ALTER TABLE `orden_e` DISABLE KEYS */;
/*!40000 ALTER TABLE `orden_e` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pago_carrito`
--

DROP TABLE IF EXISTS `pago_carrito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pago_carrito` (
  `ID_carrito` int NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_carrito`,`ID_factura`),
  KEY `pago_carrito_fk_factura` (`ID_factura`),
  CONSTRAINT `pago_carrito_fk_carrito` FOREIGN KEY (`ID_carrito`) REFERENCES `lista_carrito` (`ID_carrito`),
  CONSTRAINT `pago_carrito_fk_factura` FOREIGN KEY (`ID_factura`) REFERENCES `venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pago_carrito`
--

LOCK TABLES `pago_carrito` WRITE;
/*!40000 ALTER TABLE `pago_carrito` DISABLE KEYS */;
/*!40000 ALTER TABLE `pago_carrito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pago_orden`
--

DROP TABLE IF EXISTS `pago_orden`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pago_orden` (
  `ID_orden_e` int NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_orden_e`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `pago_orden_ibfk_1` FOREIGN KEY (`ID_orden_e`) REFERENCES `orden_e` (`ID_orden_e`),
  CONSTRAINT `pago_orden_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pago_orden`
--

LOCK TABLES `pago_orden` WRITE;
/*!40000 ALTER TABLE `pago_orden` DISABLE KEYS */;
/*!40000 ALTER TABLE `pago_orden` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `personal_delivery`
--

DROP TABLE IF EXISTS `personal_delivery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `personal_delivery` (
  `ID_p` int NOT NULL,
  `Nombre_p` varchar(40) DEFAULT NULL,
  `Apellido_p` varchar(40) DEFAULT NULL,
  `Celular_p` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`ID_p`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `personal_delivery`
--

LOCK TABLES `personal_delivery` WRITE;
/*!40000 ALTER TABLE `personal_delivery` DISABLE KEYS */;
/*!40000 ALTER TABLE `personal_delivery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos_orden`
--

DROP TABLE IF EXISTS `productos_orden`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos_orden` (
  `ID_orden_c` int NOT NULL,
  `ID_modelo` int NOT NULL,
  `Catidad_p` int DEFAULT NULL,
  PRIMARY KEY (`ID_orden_c`,`ID_modelo`),
  KEY `ID_modelo` (`ID_modelo`),
  CONSTRAINT `productos_orden_ibfk_1` FOREIGN KEY (`ID_orden_c`) REFERENCES `orden_compra` (`ID_orden_c`),
  CONSTRAINT `productos_orden_ibfk_2` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos_orden`
--

LOCK TABLES `productos_orden` WRITE;
/*!40000 ALTER TABLE `productos_orden` DISABLE KEYS */;
/*!40000 ALTER TABLE `productos_orden` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provedor`
--

DROP TABLE IF EXISTS `provedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `provedor` (
  `ID_provedor` int NOT NULL,
  `N_provedor` varchar(40) DEFAULT NULL,
  `Tipo_provedor` varchar(20) DEFAULT NULL,
  `Celular_pr` varchar(15) DEFAULT NULL,
  `Correo_pr` varchar(30) DEFAULT NULL,
  `Direccion_pr` varchar(60) DEFAULT NULL,
  `Limite_credito` int DEFAULT NULL,
  PRIMARY KEY (`ID_provedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provedor`
--

LOCK TABLES `provedor` WRITE;
/*!40000 ALTER TABLE `provedor` DISABLE KEYS */;
/*!40000 ALTER TABLE `provedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provedores_productos`
--

DROP TABLE IF EXISTS `provedores_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `provedores_productos` (
  `ID_provedor` int NOT NULL,
  `ID_modelo` int NOT NULL,
  `Costo` int DEFAULT NULL,
  PRIMARY KEY (`ID_provedor`,`ID_modelo`),
  KEY `ID_modelo` (`ID_modelo`),
  CONSTRAINT `provedores_productos_ibfk_1` FOREIGN KEY (`ID_provedor`) REFERENCES `provedor` (`ID_provedor`),
  CONSTRAINT `provedores_productos_ibfk_2` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provedores_productos`
--

LOCK TABLES `provedores_productos` WRITE;
/*!40000 ALTER TABLE `provedores_productos` DISABLE KEYS */;
/*!40000 ALTER TABLE `provedores_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repuestos_u`
--

DROP TABLE IF EXISTS `repuestos_u`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repuestos_u` (
  `ID_producto` int NOT NULL,
  `ID_orden` int NOT NULL,
  `Cantidad` int DEFAULT NULL,
  PRIMARY KEY (`ID_producto`,`ID_orden`),
  KEY `ID_orden` (`ID_orden`),
  CONSTRAINT `repuestos_u_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`),
  CONSTRAINT `repuestos_u_ibfk_2` FOREIGN KEY (`ID_orden`) REFERENCES `orden_e` (`ID_orden_e`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repuestos_u`
--

LOCK TABLES `repuestos_u` WRITE;
/*!40000 ALTER TABLE `repuestos_u` DISABLE KEYS */;
/*!40000 ALTER TABLE `repuestos_u` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `revision_orden`
--

DROP TABLE IF EXISTS `revision_orden`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `revision_orden` (
  `ID_test` int NOT NULL,
  `ID_orden` int NOT NULL,
  PRIMARY KEY (`ID_test`,`ID_orden`),
  KEY `revision_orden_fk_orden` (`ID_orden`),
  CONSTRAINT `revision_orden_fk_orden` FOREIGN KEY (`ID_orden`) REFERENCES `orden_e` (`ID_orden_e`),
  CONSTRAINT `revision_orden_fk_test` FOREIGN KEY (`ID_test`) REFERENCES `test` (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `revision_orden`
--

LOCK TABLES `revision_orden` WRITE;
/*!40000 ALTER TABLE `revision_orden` DISABLE KEYS */;
/*!40000 ALTER TABLE `revision_orden` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `revision_test`
--

DROP TABLE IF EXISTS `revision_test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `revision_test` (
  `ID_test` int NOT NULL,
  `ID_Tradein` int NOT NULL,
  PRIMARY KEY (`ID_test`,`ID_Tradein`),
  KEY `ID_Tradein` (`ID_Tradein`),
  CONSTRAINT `revision_test_ibfk_1` FOREIGN KEY (`ID_test`) REFERENCES `test` (`ID_test`),
  CONSTRAINT `revision_test_ibfk_2` FOREIGN KEY (`ID_Tradein`) REFERENCES `tradein` (`ID_Tradein`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `revision_test`
--

LOCK TABLES `revision_test` WRITE;
/*!40000 ALTER TABLE `revision_test` DISABLE KEYS */;
/*!40000 ALTER TABLE `revision_test` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock`
--

DROP TABLE IF EXISTS `stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock` (
  `ID_producto` int NOT NULL AUTO_INCREMENT,
  `ID_modelo` int DEFAULT NULL,
  `Existencia` int DEFAULT NULL,
  `Costo_venta` int DEFAULT NULL,
  PRIMARY KEY (`ID_producto`),
  KEY `ID_modelo` (`ID_modelo`),
  CONSTRAINT `stock_ibfk_1` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock`
--

LOCK TABLES `stock` WRITE;
/*!40000 ALTER TABLE `stock` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test`
--

DROP TABLE IF EXISTS `test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test` (
  `ID_test` int NOT NULL AUTO_INCREMENT,
  `ID_em` int DEFAULT NULL,
  `Num_test` int DEFAULT NULL,
  `Btn_power` int DEFAULT NULL,
  `Btn_vol` int DEFAULT NULL,
  `Cornetas` int DEFAULT NULL,
  `Mica` int DEFAULT NULL,
  `LCD` int DEFAULT NULL,
  `Tactil` int DEFAULT NULL,
  `Wifi` int DEFAULT NULL,
  `Puerto_carga` int DEFAULT NULL,
  `Cam_pos` int DEFAULT NULL,
  `Cam_del` int DEFAULT NULL,
  `Microfono` int DEFAULT NULL,
  `Flash` int DEFAULT NULL,
  `Btn_sil` int DEFAULT NULL,
  `Auricular` int DEFAULT NULL,
  `Señal` int DEFAULT NULL,
  `Sensor_proximidad` int DEFAULT NULL,
  `Face_id` int DEFAULT NULL,
  `Bluetooth` int DEFAULT NULL,
  `Observaciones` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID_test`),
  KEY `ID_em` (`ID_em`),
  CONSTRAINT `test_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test`
--

LOCK TABLES `test` WRITE;
/*!40000 ALTER TABLE `test` DISABLE KEYS */;
/*!40000 ALTER TABLE `test` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tradein`
--

DROP TABLE IF EXISTS `tradein`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tradein` (
  `ID_Tradein` int NOT NULL AUTO_INCREMENT,
  `ID_em` int DEFAULT NULL,
  `ID_c` int DEFAULT NULL,
  `ID_producto` int DEFAULT NULL,
  `Cotizacion` int DEFAULT NULL,
  `Fecha_t` varchar(10) DEFAULT NULL,
  `Color` varchar(20) DEFAULT NULL,
  `N_utilizado` int DEFAULT NULL,
  `Liberacion` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID_Tradein`),
  KEY `ID_em` (`ID_em`),
  KEY `ID_c` (`ID_c`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `tradein_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`),
  CONSTRAINT `tradein_ibfk_2` FOREIGN KEY (`ID_c`) REFERENCES `cliente` (`ID_c`),
  CONSTRAINT `tradein_ibfk_3` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tradein`
--

LOCK TABLES `tradein` WRITE;
/*!40000 ALTER TABLE `tradein` DISABLE KEYS */;
/*!40000 ALTER TABLE `tradein` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta`
--

DROP TABLE IF EXISTS `venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venta` (
  `ID_factura` varchar(20) NOT NULL,
  `ID_em` int DEFAULT NULL,
  `ID_c` int DEFAULT NULL,
  `Costo_total` int DEFAULT NULL,
  `Fecha_v` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ID_factura`),
  KEY `ID_em` (`ID_em`),
  KEY `ID_c` (`ID_c`),
  CONSTRAINT `venta_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`),
  CONSTRAINT `venta_ibfk_2` FOREIGN KEY (`ID_c`) REFERENCES `cliente` (`ID_c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta`
--

LOCK TABLES `venta` WRITE;
/*!40000 ALTER TABLE `venta` DISABLE KEYS */;
/*!40000 ALTER TABLE `venta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-28 18:02:48
