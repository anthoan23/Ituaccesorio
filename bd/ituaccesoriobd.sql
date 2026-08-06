-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: ituaccesoriobd
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
-- Table structure for table `Abastece`
--

DROP TABLE IF EXISTS `Abastece`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Abastece` (
  `ID_entrega_inventario` varchar(10) NOT NULL,
  `ID_inventario` varchar(10) NOT NULL,
  `Cantidad_entregada` int NOT NULL,
  PRIMARY KEY (`ID_entrega_inventario`,`ID_inventario`),
  KEY `ID_existencia` (`ID_inventario`),
  CONSTRAINT `Abastece_ibfk_1` FOREIGN KEY (`ID_entrega_inventario`) REFERENCES `Entrega_inventario` (`ID_entrega_inventario`) ON DELETE CASCADE,
  CONSTRAINT `Abastece_ibfk_2` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Abastece`
--

LOCK TABLES `Abastece` WRITE;
/*!40000 ALTER TABLE `Abastece` DISABLE KEYS */;
INSERT INTO `Abastece` VALUES ('ENT0000001','1',10),('ENT0000002','3',5),('ENT0000003','2',20),('ENT0000004','4',8),('ENT0000005','8',30);
/*!40000 ALTER TABLE `Abastece` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Capacitacion`
--

DROP TABLE IF EXISTS `Capacitacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Capacitacion` (
  `ID_empleado` int NOT NULL,
  `ID_especialidad` varchar(10) NOT NULL,
  `Nivel_Capacitacion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID_empleado`,`ID_especialidad`),
  KEY `ID_especialidad` (`ID_especialidad`),
  CONSTRAINT `Capacitacion_ibfk_1` FOREIGN KEY (`ID_empleado`) REFERENCES `Empleado` (`ID_empleado`),
  CONSTRAINT `Capacitacion_ibfk_2` FOREIGN KEY (`ID_especialidad`) REFERENCES `Especialidad` (`ID_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Capacitacion`
--

LOCK TABLES `Capacitacion` WRITE;
/*!40000 ALTER TABLE `Capacitacion` DISABLE KEYS */;
INSERT INTO `Capacitacion` VALUES (12345543,'ESP0000004','Intermedio'),(20123456,'ESP0000004','Avanzado'),(20234567,'ESP0000005','Intermedio'),(20345678,'ESP0000006','BÃ¡sico'),(20456789,'ESP0000007','Avanzado'),(20567890,'ESP0000008','Avanzado'),(30124556,'ESP0000005','BÃ¡sico'),(1111111111,'ESP0000001',NULL),(1111111111,'ESP0000002',NULL),(1111111111,'ESP0000003',NULL);
/*!40000 ALTER TABLE `Capacitacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Cargo`
--

DROP TABLE IF EXISTS `Cargo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cargo` (
  `ID_cargo` varchar(10) NOT NULL,
  `Nombre_cargo` varchar(30) NOT NULL,
  `Descripcion_cargo` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`ID_cargo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cargo`
--

LOCK TABLES `Cargo` WRITE;
/*!40000 ALTER TABLE `Cargo` DISABLE KEYS */;
INSERT INTO `Cargo` VALUES ('CRG0000001','Prueba-1','Esta es la descripciÃ³n detallada para la prueba'),('CRG0000002','Prueba-2','Esta es la descripciÃ³n detallada para la prueba 2'),('CRG0000003','Prueba-3','Esta es la descripciÃ³n detallada para la prueba 3'),('CRG0000004','Prueba-4','Esta es la descripciÃ³n detallada para la prueba 4'),('CRG0000005','Prueba-5','Esta es la descripciÃ³n detallada para la prueba 5'),('CRG0000006','TÃ©cnico','Encargado de las revisiones y reparaciones'),('CRG0000007','Vendedor','Encargado de ventas y atenciÃ³n al cliente'),('CRG0000008','Almacenista','Encargado del control de inventario'),('CRG0000009','Delivery','Encargado de entregas a domicilio'),('CRG0000010','Administrador','Administrador del sistema'),('CRG0000011','Soporte TÃ©cnico','Soporte tÃ©cnico especializado');
/*!40000 ALTER TABLE `Cargo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Categoria`
--

DROP TABLE IF EXISTS `Categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Categoria` (
  `ID_categoria` int NOT NULL AUTO_INCREMENT,
  `Nombre_categoria` varchar(30) NOT NULL,
  PRIMARY KEY (`ID_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Categoria`
--

LOCK TABLES `Categoria` WRITE;
/*!40000 ALTER TABLE `Categoria` DISABLE KEYS */;
INSERT INTO `Categoria` VALUES (2,'t');
/*!40000 ALTER TABLE `Categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Clase_producto`
--

DROP TABLE IF EXISTS `Clase_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Clase_producto` (
  `ID_Clase` varchar(10) NOT NULL,
  `Nombre_Clase` varchar(30) NOT NULL,
  PRIMARY KEY (`ID_Clase`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Clase_producto`
--

LOCK TABLES `Clase_producto` WRITE;
/*!40000 ALTER TABLE `Clase_producto` DISABLE KEYS */;
INSERT INTO `Clase_producto` VALUES ('1','Telefono'),('2','Pantalla'),('3','Tablet'),('4','Cargador'),('5','Funda'),('6','AudÃ­fonos'),('7','Repuesto');
/*!40000 ALTER TABLE `Clase_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Cliente`
--

DROP TABLE IF EXISTS `Cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cliente` (
  `ID_cliente` varchar(10) NOT NULL,
  `Direccion_cliente` varchar(40) DEFAULT NULL,
  `Celular_cliente` varchar(15) DEFAULT NULL,
  `Correo_cliente` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cliente`
--

LOCK TABLES `Cliente` WRITE;
/*!40000 ALTER TABLE `Cliente` DISABLE KEYS */;
INSERT INTO `Cliente` VALUES ('1','Barquisimeto','04145675567','ejemplo@gmail.com'),('22345678','Caracas','04121234567','cliente1@gmail.com'),('30548845','Barquisimeto','04142342121','ejemplotest@gmail.com'),('31143265','Rio claro','04246667263','prueba@gmail.com'),('33456789','Maracaibo','04241234567','cliente2@gmail.com'),('44567890','Valencia','04161234567','cliente3@gmail.com'),('55678901','San CristÃ³bal','04181234567','cliente4@gmail.com'),('66789012','Puerto La Cruz','04261234567','cliente5@gmail.com'),('91754623','Barquisimeto','04243124554','ejemplo@gmail.com');
/*!40000 ALTER TABLE `Cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Cliente_juridico`
--

DROP TABLE IF EXISTS `Cliente_juridico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cliente_juridico` (
  `ID_cliente` varchar(10) NOT NULL,
  `Razon_social` varchar(60) NOT NULL,
  `Rif_cliente` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`),
  CONSTRAINT `Cliente_juridico_ibfk_1` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cliente_juridico`
--

LOCK TABLES `Cliente_juridico` WRITE;
/*!40000 ALTER TABLE `Cliente_juridico` DISABLE KEYS */;
INSERT INTO `Cliente_juridico` VALUES ('1','Tech Solutions C.A.','J-12345678-0'),('30548845','Comercializadora Digital S.A.','J-87654321-5'),('31143265','Importaciones Globales C.A.','J-11223344-1');
/*!40000 ALTER TABLE `Cliente_juridico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Credito`
--

DROP TABLE IF EXISTS `Credito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Credito` (
  `ID_credito` varchar(10) NOT NULL,
  `ID_orden_compra` varchar(10) DEFAULT NULL,
  `Dias_credito` int DEFAULT NULL,
  `Monto_credito` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_credito`),
  KEY `ID_orden_compra` (`ID_orden_compra`),
  CONSTRAINT `Credito_ibfk_1` FOREIGN KEY (`ID_orden_compra`) REFERENCES `Orden_compra` (`ID_orden_compra`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Credito`
--

LOCK TABLES `Credito` WRITE;
/*!40000 ALTER TABLE `Credito` DISABLE KEYS */;
INSERT INTO `Credito` VALUES ('CRE000001','OC0000002',30,15000.00),('CRE000002','OC0000003',15,8000.00),('CRE000003','OC0000004',45,25000.00),('CRE000004','OC0000001',0,0.00),('CRE000005','OC0000005',20,5000.00);
/*!40000 ALTER TABLE `Credito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Detalle_orden`
--

DROP TABLE IF EXISTS `Detalle_orden`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Detalle_orden` (
  `ID_orden_compra` varchar(10) NOT NULL,
  `ID_producto` varchar(10) NOT NULL,
  `Cantidad_producto` int DEFAULT NULL,
  PRIMARY KEY (`ID_orden_compra`,`ID_producto`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `Detalle_orden_ibfk_1` FOREIGN KEY (`ID_orden_compra`) REFERENCES `Orden_compra` (`ID_orden_compra`),
  CONSTRAINT `Detalle_orden_ibfk_2` FOREIGN KEY (`ID_producto`) REFERENCES `Producto` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Detalle_orden`
--

LOCK TABLES `Detalle_orden` WRITE;
/*!40000 ALTER TABLE `Detalle_orden` DISABLE KEYS */;
INSERT INTO `Detalle_orden` VALUES ('OC0000001','1',10),('OC0000001','3',5),('OC0000002','2',20),('OC0000002','4',8),('OC0000003','5',15),('OC0000003','7',50),('OC0000004','6',10),('OC0000004','9',20),('OC0000005','10',25),('OC0000005','8',30);
/*!40000 ALTER TABLE `Detalle_orden` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Detalle_venta`
--

DROP TABLE IF EXISTS `Detalle_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Detalle_venta` (
  `ID_inventario` varchar(10) NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  `Cantidad_articulo` int DEFAULT NULL,
  PRIMARY KEY (`ID_inventario`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `Detalle_venta_ibfk_1` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`),
  CONSTRAINT `Detalle_venta_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `Venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Detalle_venta`
--

LOCK TABLES `Detalle_venta` WRITE;
/*!40000 ALTER TABLE `Detalle_venta` DISABLE KEYS */;
INSERT INTO `Detalle_venta` VALUES ('1','FAC-202606-080A3A',1),('1','FAC-202606-111111',1),('1','FAC-202606-6993F3',1),('1','FAC-202606-8D8B04',1),('1','FAC-202606-B1475D',1),('1','FAC-202606-DA0967',4),('1','FAC-202606-EB6A95',2),('1','FAC-202606-FDD009',2),('10','FAC-202606-333333',2),('2','FAC-202606-222222',2),('3','FAC-202606-111111',1),('4','FAC-202606-333333',1),('5','FAC-202606-444444',1),('6','FAC-202606-555555',1),('7','FAC-202606-666666',3),('8','FAC-202606-777777',2),('9','FAC-202606-222222',1);
/*!40000 ALTER TABLE `Detalle_venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Empleado`
--

DROP TABLE IF EXISTS `Empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Empleado` (
  `ID_empleado` int NOT NULL,
  `ID_cargo` varchar(10) DEFAULT NULL,
  `Nombre_empleado` varchar(40) NOT NULL,
  `Apellido_empleado` varchar(40) NOT NULL,
  `Celular_empleado` varchar(15) DEFAULT NULL,
  `Correo_empleado` varchar(120) DEFAULT NULL,
  `Direccion_empleado` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ID_empleado`),
  KEY `ID_cargo` (`ID_cargo`),
  CONSTRAINT `Empleado_ibfk_1` FOREIGN KEY (`ID_cargo`) REFERENCES `Cargo` (`ID_cargo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Empleado`
--

LOCK TABLES `Empleado` WRITE;
/*!40000 ALTER TABLE `Empleado` DISABLE KEYS */;
INSERT INTO `Empleado` VALUES (12345543,'CRG0000001','Anthonio','Alvarez','0415458632','Anthonio@gmail.com','mucho mas lejos'),(12345678,'CRG0000004','empleado','gonzalez','1234567899','ejemplo@gmail.com','Barquisimeto'),(20123456,'CRG0000007','Laura','SÃ¡nchez','04121234568','laura.sanchez@itu.com','Caracas'),(20234567,'CRG0000008','Carlos','Mendoza','04161234569','carlos.mendoza@itu.com','Barquisimeto'),(20345678,'CRG0000009','Roberto','GarcÃ­a','04141234570','roberto.garcia@itu.com','Cabudare'),(20456789,'CRG0000010','Daniela','Rojas','04241234571','daniela.rojas@itu.com','Lara'),(20567890,'CRG0000011','Fernando','LÃ³pez','04121234572','fernando.lopez@itu.com','Barquisimeto'),(30124556,'CRG0000005','Maria','Gonzalez','04125684514','Maria@gmail.com','Lejos'),(30548845,'CRG0000005','Manuel','Prado','041563555555','Manuel@gmail.com','ssssssssssssss'),(31111554,'CRG0000004','Pedro','Perez','0412564782','Jose2@gmail.com','Al infinito y mas alla ss'),(31111555,'CRG0000005','Jose','Gomez','0412564789','Jose@gmail.com','Al infinito y mas alla '),(32014004,'CRG0000006','Eduin','Meneses','04141233212','Prueba@gmail.com','Barquisimeto'),(1111111111,'CRG0000006','Tomas','Colina','0415478998','Tomas@gmail.com','mas lejos');
/*!40000 ALTER TABLE `Empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Entrega`
--

DROP TABLE IF EXISTS `Entrega`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Entrega` (
  `ID_entrega` varchar(10) NOT NULL,
  `ID_factura` varchar(20) DEFAULT NULL,
  `Cedula_delivery` varchar(15) DEFAULT NULL,
  `Estado_entrega` int DEFAULT NULL,
  `Direccion_entrega` varchar(60) DEFAULT NULL,
  `Fecha_entrega` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_entrega`),
  KEY `ID_factura` (`ID_factura`),
  KEY `Cedula_delivery` (`Cedula_delivery`),
  CONSTRAINT `Entrega_ibfk_1` FOREIGN KEY (`ID_factura`) REFERENCES `Venta` (`ID_factura`),
  CONSTRAINT `Entrega_ibfk_2` FOREIGN KEY (`Cedula_delivery`) REFERENCES `Personal_delivery` (`Cedula_delivery`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Entrega`
--

LOCK TABLES `Entrega` WRITE;
/*!40000 ALTER TABLE `Entrega` DISABLE KEYS */;
INSERT INTO `Entrega` VALUES ('ENT000001','FAC-202606-111111','25000001',1,'Caracas - Av. Principal','2026-06-03 14:00:00'),('ENT000002','FAC-202606-222222','25000002',1,'Maracaibo - Calle 5','2026-06-03 11:30:00'),('ENT000003','FAC-202606-333333','25000003',0,'Valencia - Urb. Las Acacias',NULL),('ENT000004','FAC-202606-444444','25000001',1,'San CristÃ³bal - Centro','2026-06-06 16:00:00'),('ENT000005','FAC-202606-555555','25000004',0,'Puerto La Cruz - Paseo ColÃ³n',NULL);
/*!40000 ALTER TABLE `Entrega` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Entrega_inventario`
--

DROP TABLE IF EXISTS `Entrega_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Entrega_inventario` (
  `ID_entrega_inventario` varchar(10) NOT NULL,
  `ID_empleado` int DEFAULT NULL,
  `ID_orden_compra` varchar(10) DEFAULT NULL,
  `Fecha_entrega_inventario` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_entrega_inventario`),
  KEY `ID_empleado` (`ID_empleado`),
  KEY `ID_orden_compra` (`ID_orden_compra`),
  CONSTRAINT `Entrega_inventario_ibfk_1` FOREIGN KEY (`ID_empleado`) REFERENCES `Empleado` (`ID_empleado`),
  CONSTRAINT `Entrega_inventario_ibfk_2` FOREIGN KEY (`ID_orden_compra`) REFERENCES `Orden_compra` (`ID_orden_compra`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Entrega_inventario`
--

LOCK TABLES `Entrega_inventario` WRITE;
/*!40000 ALTER TABLE `Entrega_inventario` DISABLE KEYS */;
INSERT INTO `Entrega_inventario` VALUES ('ENT0000001',20234567,'OC0000001','2026-06-02 15:00:00'),('ENT0000002',20234567,'OC0000001','2026-06-02 15:00:00'),('ENT0000003',20234567,'OC0000002','2026-06-03 14:30:00'),('ENT0000004',20234567,'OC0000002','2026-06-03 14:30:00'),('ENT0000005',20234567,'OC0000005','2026-06-07 10:00:00');
/*!40000 ALTER TABLE `Entrega_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Equipo`
--

DROP TABLE IF EXISTS `Equipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Equipo` (
  `ID_equipo` varchar(16) NOT NULL,
  `ID_producto` varchar(10) DEFAULT NULL,
  `Color` varchar(20) DEFAULT NULL,
  `Capacidad` varchar(20) DEFAULT NULL,
  `Clave` int DEFAULT NULL,
  `Patron` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ID_equipo`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `Equipo_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `Producto` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Equipo`
--

LOCK TABLES `Equipo` WRITE;
/*!40000 ALTER TABLE `Equipo` DISABLE KEYS */;
INSERT INTO `Equipo` VALUES ('EQ0000001','1','Negro','128GB',1234,'PATRON123'),('EQ0000002','3','Azul','256GB',NULL,NULL),('EQ0000003','4','Blanco','512GB',NULL,NULL),('EQ0000004','1','Rojo','64GB',1111,'PATRON456'),('EQ0000005','3','Verde','128GB',NULL,NULL);
/*!40000 ALTER TABLE `Equipo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Especialidad`
--

DROP TABLE IF EXISTS `Especialidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Especialidad` (
  `ID_especialidad` varchar(10) NOT NULL,
  `Nombre_especialidad` varchar(30) NOT NULL,
  `Descripcion_especialidad` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`ID_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Especialidad`
--

LOCK TABLES `Especialidad` WRITE;
/*!40000 ALTER TABLE `Especialidad` DISABLE KEYS */;
INSERT INTO `Especialidad` VALUES ('ESP0000001','Prueba-1','Esta es la descripciÃ³n detallada para la prueba 1'),('ESP0000002','Prueba-2','Esta es la descripciÃ³n detallada para la prueba  2'),('ESP0000003','Prueba-3','Esta es la descripciÃ³n detallada para la prueba 3'),('ESP0000004','ReparaciÃ³n iOS','Especialista en reparaciÃ³n de dispositivos Apple'),('ESP0000005','ReparaciÃ³n Android','Especialista en reparaciÃ³n de dispositivos Android'),('ESP0000006','Cambio de Pantalla','Especialista en cambio de pantallas'),('ESP0000007','ReparaciÃ³n Placa','Especialista en reparaciÃ³n de placas madre'),('ESP0000008','Software','Especialista en problemas de software'),('ESP0000009','Prueba Uno','dddddd'),('ESP0000010','Rdfdf','DFDFD');
/*!40000 ALTER TABLE `Especialidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Existencias_productos`
--

DROP TABLE IF EXISTS `Existencias_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Existencias_productos` (
  `ID_inventario` varchar(10) NOT NULL,
  `ID_producto` varchar(10) DEFAULT NULL,
  `Existencia` int DEFAULT NULL,
  `Costo_venta` decimal(10,2) DEFAULT NULL,
  `ID_categoria` int DEFAULT NULL,
  PRIMARY KEY (`ID_inventario`),
  KEY `ID_producto` (`ID_producto`),
  KEY `fk_existencias_categoria` (`ID_categoria`),
  CONSTRAINT `Existencias_productos_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `Producto` (`ID_producto`),
  CONSTRAINT `fk_existencias_categoria` FOREIGN KEY (`ID_categoria`) REFERENCES `Categoria` (`ID_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Existencias_productos`
--

LOCK TABLES `Existencias_productos` WRITE;
/*!40000 ALTER TABLE `Existencias_productos` DISABLE KEYS */;
INSERT INTO `Existencias_productos` VALUES ('1','1',10,800.00,2),('10','10',14,80.00,2),('2','2',0,350.00,2),('3','3',8,950.00,NULL),('4','4',12,850.00,NULL),('5','5',17,400.00,NULL),('6','6',5,450.00,NULL),('7','7',30,25.00,NULL),('8','8',25,15.00,NULL),('9','9',10,120.00,NULL);
/*!40000 ALTER TABLE `Existencias_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Fotos_inventario`
--

DROP TABLE IF EXISTS `Fotos_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Fotos_inventario` (
  `ID_foto_inventario` varchar(10) NOT NULL,
  `ID_inventario` varchar(10) DEFAULT NULL,
  `Foto_inventario` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_foto_inventario`),
  KEY `ID_inventario` (`ID_inventario`),
  CONSTRAINT `Fotos_inventario_ibfk_1` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Fotos_inventario`
--

LOCK TABLES `Fotos_inventario` WRITE;
/*!40000 ALTER TABLE `Fotos_inventario` DISABLE KEYS */;
INSERT INTO `Fotos_inventario` VALUES ('1','1','/static/img/evidencias/inventario/1f33501ad0a140d59f4fd2bfe24a9459.jpeg'),('2','2','/static/img/evidencias/inventario/foto_2.jpeg'),('3','3','/static/img/evidencias/inventario/foto_3.jpeg'),('4','4','/static/img/evidencias/inventario/foto_4.jpeg'),('5','5','/static/img/evidencias/inventario/foto_5.jpeg'),('6','6','/static/img/evidencias/inventario/foto_6.jpeg');
/*!40000 ALTER TABLE `Fotos_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Fotos_orden_servicio`
--

DROP TABLE IF EXISTS `Fotos_orden_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Fotos_orden_servicio` (
  `ID_foto_orden_servicio` varchar(10) NOT NULL,
  `ID_orden_servicio` varchar(10) DEFAULT NULL,
  `Foto_orden_servicio` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_foto_orden_servicio`),
  KEY `ID_orden_servicio` (`ID_orden_servicio`),
  CONSTRAINT `Fotos_orden_servicio_ibfk_1` FOREIGN KEY (`ID_orden_servicio`) REFERENCES `Orden_servicio` (`ID_orden_servicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Fotos_orden_servicio`
--

LOCK TABLES `Fotos_orden_servicio` WRITE;
/*!40000 ALTER TABLE `Fotos_orden_servicio` DISABLE KEYS */;
INSERT INTO `Fotos_orden_servicio` VALUES ('FOS000001','OS0000001','/static/img/evidencias/orden_servicio/os1_1.jpeg'),('FOS000002','OS0000001','/static/img/evidencias/orden_servicio/os1_2.jpeg'),('FOS000003','OS0000002','/static/img/evidencias/orden_servicio/os2_1.jpeg'),('FOS000004','OS0000003','/static/img/evidencias/orden_servicio/os3_1.jpeg'),('FOS000005','OS0000005','/static/img/evidencias/orden_servicio/os5_1.jpeg'),('FOS000006','OS0000025','/static/img/evidencias/taller/OS0000025/54a0a2acb2e64b5abbfd322e9d6ea48e.jpg');
/*!40000 ALTER TABLE `Fotos_orden_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Fotos_trade_in`
--

DROP TABLE IF EXISTS `Fotos_trade_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Fotos_trade_in` (
  `ID_foto_trade_in` varchar(10) NOT NULL,
  `ID_Trade_in` varchar(10) DEFAULT NULL,
  `Foto_trade_in` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_foto_trade_in`),
  KEY `ID_Trade_in` (`ID_Trade_in`),
  CONSTRAINT `Fotos_trade_in_ibfk_1` FOREIGN KEY (`ID_Trade_in`) REFERENCES `Trade_in` (`ID_Trade_in`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Fotos_trade_in`
--

LOCK TABLES `Fotos_trade_in` WRITE;
/*!40000 ALTER TABLE `Fotos_trade_in` DISABLE KEYS */;
INSERT INTO `Fotos_trade_in` VALUES ('FTI000001','TRD000001','/static/img/evidencias/trade_in/trd1_1.jpeg'),('FTI000002','TRD000001','/static/img/evidencias/trade_in/trd1_2.jpeg'),('FTI000003','TRD000002','/static/img/evidencias/trade_in/trd2_1.jpeg'),('FTI000004','TRD000003','/static/img/evidencias/trade_in/trd3_1.jpeg'),('FTI000005','TRD000005','/static/img/evidencias/trade_in/trd5_1.jpeg');
/*!40000 ALTER TABLE `Fotos_trade_in` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Interaccion`
--

DROP TABLE IF EXISTS `Interaccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Interaccion` (
  `ID_interaccion` varchar(10) NOT NULL,
  `ID_orden_servicio` varchar(10) DEFAULT NULL,
  `ID_empleado` int DEFAULT NULL,
  `Accion` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_interaccion`),
  KEY `ID_orden_servicio` (`ID_orden_servicio`),
  KEY `ID_empleado` (`ID_empleado`),
  CONSTRAINT `Interaccion_ibfk_1` FOREIGN KEY (`ID_orden_servicio`) REFERENCES `Orden_servicio` (`ID_orden_servicio`),
  CONSTRAINT `Interaccion_ibfk_2` FOREIGN KEY (`ID_empleado`) REFERENCES `Empleado` (`ID_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Interaccion`
--

LOCK TABLES `Interaccion` WRITE;
/*!40000 ALTER TABLE `Interaccion` DISABLE KEYS */;
INSERT INTO `Interaccion` VALUES ('INT000001','OS0000001',32014004,'RevisiÃ³n'),('INT000002','OS0000001',32014004,'En proceso'),('INT000003','OS0000002',32014004,'En proceso'),('INT000004','OS0000003',20567890,'Pendiente de repuesto'),('INT000005','OS0000004',20567890,'Limpieza realizada'),('INT0000050','OS0000020',32014004,'Pendiente'),('INT0000051','OS0000021',32014004,'Pendiente'),('INT0000052','OS0000022',32014004,'Pendiente'),('INT0000053','OS0000023',32014004,'Pendiente'),('INT0000054','OS0000024',32014004,'Pendiente'),('INT0000055','OS0000025',32014004,'Pendiente'),('INT0000056','OS0000026',32014004,'Pendiente'),('INT0000057','OS0000027',32014004,'Pendiente'),('INT0000058','OS0000027',32014004,'En proceso'),('INT0000059','OS0000028',32014004,'Pendiente'),('INT0000060','OS0000028',32014004,'En proceso'),('INT0000061','OS0000029',32014004,'Pendiente'),('INT0000062','OS0000029',32014004,'En proceso'),('INT0000063','OS0000030',32014004,'Pendiente'),('INT0000064','OS0000030',32014004,'En proceso'),('INT0000065','OS0000031',32014004,'Pendiente'),('INT0000066','OS0000031',32014004,'En proceso'),('INT0000067','OS0000032',32014004,'Pendiente'),('INT0000068','OS0000032',32014004,'En proceso'),('INT0000069','OS0000033',32014004,'Pendiente'),('INT0000070','OS0000033',32014004,'En proceso'),('INT0000071','OS0000034',32014004,'Pendiente'),('INT0000072','OS0000034',32014004,'En proceso'),('INT000008','OS0000001',32014004,'RevisiÃ³n'),('INT000009','OS0000001',32014004,'RevisiÃ³n'),('INT000010','OS0000005',32014004,'RevisiÃ³n'),('INT000011','OS0000001',32014004,'RevisiÃ³n'),('INT000012','OS0000001',32014004,'RevisiÃ³n'),('INT000013','OS0000004',32014004,'En proceso'),('INT000014','OS0000006',32014004,'En proceso'),('INT000015','OS0000005',32014004,'En proceso'),('INT000016','OS0000006',32014004,'En proceso'),('INT000017','OS0000002',32014004,'En proceso'),('INT000018','OS0000002',32014004,'Reparada'),('INT000019','OS0000001',32014004,'En proceso'),('INT000020','OS0000006',32014004,'En proceso'),('INT000021','OS0000001',32014004,'En proceso'),('INT000022','OS0000005',32014004,'Reparada'),('INT000023','OS0000002',32014004,'RevisiÃ³n'),('INT000024','OS0000002',32014004,'RevisiÃ³n'),('INT000025','OS0000002',32014004,'RevisiÃ³n'),('INT000026','OS0000001',32014004,'En proceso'),('INT000027','OS0000001',32014004,'Reparada'),('INT000028','OS0000001',32014004,'RevisiÃ³n'),('INT000029','OS0000004',32014004,'Reparada'),('INT000030','OS0000004',32014004,'RevisiÃ³n'),('INT000031','OS0000034',32014004,'Reparada'),('INT000032','OS0000025',32014004,'Reparada'),('INT000033','OS0000023',32014004,'Asignada'),('INT000034','OS0000033',32014004,'En proceso'),('INT000035','OS0000027',32014004,'En proceso'),('INT000036','OS0000026',32014004,'En proceso'),('INT000037','OS0000025',32014004,'RevisiÃ³n'),('INT000038','OS0000033',32014004,'Asignada');
/*!40000 ALTER TABLE `Interaccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Lista_compra`
--

DROP TABLE IF EXISTS `Lista_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Lista_compra` (
  `ID_lista_compra` varchar(10) NOT NULL,
  `ID_inventario` varchar(10) DEFAULT NULL,
  `ID_cliente` varchar(10) DEFAULT NULL,
  `Cantidad_producto` int DEFAULT NULL,
  `Estado_lista_compra` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_lista_compra`),
  KEY `ID_inventario` (`ID_inventario`),
  KEY `ID_cliente` (`ID_cliente`),
  CONSTRAINT `Lista_compra_ibfk_1` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`),
  CONSTRAINT `Lista_compra_ibfk_2` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Lista_compra`
--

LOCK TABLES `Lista_compra` WRITE;
/*!40000 ALTER TABLE `Lista_compra` DISABLE KEYS */;
INSERT INTO `Lista_compra` VALUES ('LST000001','1','22345678',1,'Pendiente'),('LST000002','3','33456789',1,'Pendiente'),('LST000003','2','44567890',2,'Pendiente'),('LST000004','4','55678901',1,'Completada'),('LST000005','5','66789012',1,'Pendiente'),('LST000006','7','30548845',3,'Pendiente');
/*!40000 ALTER TABLE `Lista_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Marca_producto`
--

DROP TABLE IF EXISTS `Marca_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Marca_producto` (
  `ID_marca` varchar(10) NOT NULL,
  `Nombre_marca` varchar(30) NOT NULL,
  PRIMARY KEY (`ID_marca`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Marca_producto`
--

LOCK TABLES `Marca_producto` WRITE;
/*!40000 ALTER TABLE `Marca_producto` DISABLE KEYS */;
INSERT INTO `Marca_producto` VALUES ('1','Iphone'),('2','Iphone'),('3','Samsung'),('4','Xiaomi'),('5','Motorola'),('6','Huawei'),('7','LG');
/*!40000 ALTER TABLE `Marca_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Metodo_pago`
--

DROP TABLE IF EXISTS `Metodo_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Metodo_pago` (
  `ID_factura` varchar(20) NOT NULL,
  `Moneda` varchar(10) DEFAULT NULL,
  `Fecha_pago` datetime DEFAULT NULL,
  `Capture` varchar(255) DEFAULT NULL,
  `Estado_pago` varchar(10) DEFAULT NULL,
  `Metodo` varchar(30) DEFAULT NULL,
  `Referencia` varchar(100) DEFAULT NULL,
  `Monto` decimal(12,2) DEFAULT NULL,
  `Aprobado_por` varchar(20) DEFAULT NULL,
  `Fecha_aprobacion` datetime DEFAULT NULL,
  `Motivo_rechazo` varchar(255) DEFAULT NULL,
  `Fecha_rechazo` datetime DEFAULT NULL,
  `Rechazado_por` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ID_factura`),
  KEY `idx_estado_pago` (`Estado_pago`),
  KEY `idx_factura` (`ID_factura`),
  CONSTRAINT `Metodo_pago_ibfk_1` FOREIGN KEY (`ID_factura`) REFERENCES `Venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Metodo_pago`
--

LOCK TABLES `Metodo_pago` WRITE;
/*!40000 ALTER TABLE `Metodo_pago` DISABLE KEYS */;
INSERT INTO `Metodo_pago` VALUES ('FAC-202606-080A3A','USDT','2026-06-07 22:32:41','/static/img/capturas/capture_37ea939d175d47c39ebbd80720b44bc8.png','aprobado','binance','123321',607010.00,'32014004','2026-06-07 22:32:42',NULL,NULL,NULL),('FAC-202606-111111','VES','2026-06-01 11:00:00','/static/img/capturas/capture_001.png','aprobado','pago_movil','REF001',950.00,'32014004','2026-06-01 11:05:00',NULL,NULL,NULL),('FAC-202606-222222','USD','2026-06-02 12:00:00','/static/img/capturas/capture_002.png','aprobado','binance','REF002',120.00,'32014004','2026-06-02 12:10:00',NULL,NULL,NULL),('FAC-202606-333333','USDT','2026-06-03 10:00:00','/static/img/capturas/capture_003.png','aprobado','binance','REF003',1050.00,'32014004','2026-06-03 10:15:00',NULL,NULL,NULL),('FAC-202606-444444','VES','2026-06-04 15:00:00','/static/img/capturas/capture_004.png','pendiente','pago_movil','REF004',400.00,NULL,NULL,NULL,NULL,NULL),('FAC-202606-555555','USD','2026-06-05 17:00:00','/static/img/capturas/capture_005.png','aprobado','zelle','REF005',450.00,'32014004','2026-06-05 17:30:00',NULL,NULL,NULL),('FAC-202606-666666','VES','2026-06-06 13:00:00','/static/img/capturas/capture_006.png','rechazado','pago_movil','REF006',75.00,NULL,NULL,'Monto incorrecto','2026-06-06 14:00:00','32014004'),('FAC-202606-777777','USDT','2026-06-07 16:00:00','/static/img/capturas/capture_007.png','aprobado','binance','REF007',30.00,'32014004','2026-06-07 16:30:00',NULL,NULL,NULL);
/*!40000 ALTER TABLE `Metodo_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Orden_compra`
--

DROP TABLE IF EXISTS `Orden_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Orden_compra` (
  `ID_orden_compra` varchar(10) NOT NULL,
  `ID_empleado` int DEFAULT NULL,
  `ID_proveedor` int DEFAULT NULL,
  `Estado_orden_compra` varchar(20) DEFAULT NULL,
  `Fecha_orden_compra` datetime DEFAULT NULL,
  `Factura_compra` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_orden_compra`),
  KEY `ID_empleado` (`ID_empleado`),
  KEY `ID_proveedor` (`ID_proveedor`),
  CONSTRAINT `Orden_compra_ibfk_1` FOREIGN KEY (`ID_empleado`) REFERENCES `Empleado` (`ID_empleado`),
  CONSTRAINT `Orden_compra_ibfk_2` FOREIGN KEY (`ID_proveedor`) REFERENCES `Proveedor` (`ID_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Orden_compra`
--

LOCK TABLES `Orden_compra` WRITE;
/*!40000 ALTER TABLE `Orden_compra` DISABLE KEYS */;
INSERT INTO `Orden_compra` VALUES ('OC0000001',20123456,1,'Completada','2026-06-01 10:00:00','FAC-PROV-001'),('OC0000002',20123456,2,'Completada','2026-06-02 11:30:00','FAC-PROV-002'),('OC0000003',20234567,3,'En proceso','2026-06-03 09:15:00','FAC-PROV-003'),('OC0000004',20234567,4,'Pendiente','2026-06-05 14:45:00','FAC-PROV-004'),('OC0000005',20123456,5,'Completada','2026-06-06 08:20:00','FAC-PROV-005');
/*!40000 ALTER TABLE `Orden_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Orden_servicio`
--

DROP TABLE IF EXISTS `Orden_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Orden_servicio` (
  `ID_orden_servicio` varchar(10) NOT NULL,
  `ID_equipo` varchar(16) DEFAULT NULL,
  `ID_cliente` varchar(10) DEFAULT NULL,
  `Estado_orden_servicio` varchar(20) DEFAULT NULL,
  `Descripcion_reparacion` varchar(300) DEFAULT NULL,
  `Costo_reparacion` decimal(10,2) DEFAULT NULL,
  `Nota_orden_servicio` varchar(300) DEFAULT NULL,
  `Fecha_entrada` datetime DEFAULT NULL,
  `Fecha_salida` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_orden_servicio`),
  KEY `ID_cliente` (`ID_cliente`),
  KEY `ID_equipo` (`ID_equipo`),
  CONSTRAINT `Orden_servicio_ibfk_1` FOREIGN KEY (`ID_equipo`) REFERENCES `Equipo` (`ID_equipo`),
  CONSTRAINT `Orden_servicio_ibfk_2` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Orden_servicio`
--

LOCK TABLES `Orden_servicio` WRITE;
/*!40000 ALTER TABLE `Orden_servicio` DISABLE KEYS */;
INSERT INTO `Orden_servicio` VALUES ('OS0000001','EQ0000001','22345678','Reparada','Mandigo',250.00,'Entrega programada','2026-06-01 09:00:00','2026-06-11 20:23:26'),('OS0000002','EQ0000002','22345678','Reparada','holaaaaaaaa',80.00,NULL,'2026-06-02 10:30:00','2026-06-11 18:36:07'),('OS0000003','EQ0000003','44567890','Asignada','Problema de carga',45.00,NULL,'2026-06-03 14:00:00',NULL),('OS0000004','EQ0000004','55678901','Reparada','hhhhhhhhhh',35.00,'Entrega realizada','2026-06-04 08:00:00','2026-06-24 12:00:37'),('OS0000005','EQ0000005','66789012','Reparada','mandigo',60.00,'Dejo el cargador','2026-06-06 11:00:00','2026-06-11 20:25:24'),('OS0000006','EQ0000005','30548845','En proceso','DiagnÃ³stico',0.00,'Equipo sin evaluar','2026-06-07 09:30:00',NULL),('OS0000020','EQ0000001','22345678','Pendiente',NULL,0.00,'Pendiente revisiÃ³n de pantalla','2026-06-24 11:45:27',NULL),('OS0000021','EQ0000002','22345678','Pendiente',NULL,0.00,'Revisar puerto de carga','2026-06-24 11:45:27',NULL),('OS0000022','EQ0000003','44567890','Pendiente',NULL,0.00,'Falla crÃ­tica de encendido','2026-06-24 11:45:27',NULL),('OS0000023','EQ0000004','55678901','Asignada',NULL,0.00,'BaterÃ­a inflada','2026-06-24 11:45:27',NULL),('OS0000024','EQ0000005','66789012','Pendiente',NULL,0.00,'Mantenimiento preventivo completo','2026-06-24 11:45:27',NULL),('OS0000025','EQ0000001','44567890','Reparada','ssssssssssssss',0.00,'Falla de software / bucle de inicio','2026-06-24 11:45:27','2026-06-24 17:30:25'),('OS0000026','EQ0000002','55678901','En proceso',NULL,0.00,'Cambiar cristal trasero roto','2026-06-24 11:45:27',NULL),('OS0000027','EQ0000001','22345678','En proceso','Evaluando circuitos en tarjeta principal',50.00,NULL,'2026-06-24 11:45:27',NULL),('OS0000028','EQ0000002','22345678','En proceso','Desensamblando mÃ³dulo de pantalla daÃ±ado',85.00,NULL,'2026-06-24 11:45:27',NULL),('OS0000029','EQ0000003','44567890','En proceso','Soldando nuevo pin de carga tipo C',30.00,NULL,'2026-06-24 11:45:27',NULL),('OS0000030','EQ0000004','55678901','En proceso','Limpieza por ultrasonido debido a humedad',40.00,NULL,'2026-06-24 11:45:27',NULL),('OS0000031','EQ0000005','66789012','En proceso','Reinstalando sistema operativo y firmware',25.00,NULL,'2026-06-24 11:45:27',NULL),('OS0000032','EQ0000001','33456789','En proceso','Removiendo corto circuito en etapa de potencia',60.00,NULL,'2026-06-24 11:45:27',NULL),('OS0000033','EQ0000002','44567890','Asignada','Removiendo pegamento viejo para cambio de baterÃ­a',45.00,NULL,'2026-06-24 11:45:27',NULL),('OS0000034','EQ0000003','55678901','Reparada','lklklklkllklkljj',20.00,NULL,'2026-06-24 11:45:27','2026-06-24 12:02:10');
/*!40000 ALTER TABLE `Orden_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Pago_servicio`
--

DROP TABLE IF EXISTS `Pago_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Pago_servicio` (
  `ID_orden_servicio` varchar(10) NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_orden_servicio`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `Pago_servicio_ibfk_1` FOREIGN KEY (`ID_orden_servicio`) REFERENCES `Orden_servicio` (`ID_orden_servicio`),
  CONSTRAINT `Pago_servicio_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `Venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Pago_servicio`
--

LOCK TABLES `Pago_servicio` WRITE;
/*!40000 ALTER TABLE `Pago_servicio` DISABLE KEYS */;
INSERT INTO `Pago_servicio` VALUES ('OS0000001','FAC-202606-111111'),('OS0000004','FAC-202606-444444');
/*!40000 ALTER TABLE `Pago_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Persona_natural`
--

DROP TABLE IF EXISTS `Persona_natural`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Persona_natural` (
  `ID_cliente` varchar(10) NOT NULL,
  `Apellido_cliente` varchar(40) NOT NULL,
  `Nombre_cliente` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`),
  CONSTRAINT `Persona_natural_ibfk_1` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Persona_natural`
--

LOCK TABLES `Persona_natural` WRITE;
/*!40000 ALTER TABLE `Persona_natural` DISABLE KEYS */;
INSERT INTO `Persona_natural` VALUES ('1','Sinforoza','Petra'),('22345678','GonzÃ¡lez','Carlos'),('30548845','Test','Cliente'),('31143265','Rodriguez','Manuel'),('33456789','RodrÃ­guez','Ana'),('44567890','PÃ©rez','Luis'),('55678901','DÃ­az','MarÃ­a'),('66789012','FernÃ¡ndez','JosÃ©'),('91754623','Test','Prueba');
/*!40000 ALTER TABLE `Persona_natural` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Personal_delivery`
--

DROP TABLE IF EXISTS `Personal_delivery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Personal_delivery` (
  `Cedula_delivery` varchar(15) NOT NULL,
  `Nombre_delivery` varchar(40) NOT NULL,
  `Apellido_delivery` varchar(40) NOT NULL,
  PRIMARY KEY (`Cedula_delivery`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Personal_delivery`
--

LOCK TABLES `Personal_delivery` WRITE;
/*!40000 ALTER TABLE `Personal_delivery` DISABLE KEYS */;
INSERT INTO `Personal_delivery` VALUES ('25000001','Pedro','RamÃ­rez'),('25000002','MarÃ­a','Torres'),('25000003','Juan','Castillo'),('25000004','Luisa','Morales'),('25000005','AndrÃ©s','Vargas');
/*!40000 ALTER TABLE `Personal_delivery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Producto`
--

DROP TABLE IF EXISTS `Producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Producto` (
  `ID_producto` varchar(10) NOT NULL,
  `ID_Clase` varchar(10) DEFAULT NULL,
  `ID_marca` varchar(10) DEFAULT NULL,
  `Nombre_producto` varchar(30) NOT NULL,
  `Descripcion` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID_producto`),
  KEY `ID_Clase` (`ID_Clase`),
  KEY `ID_marca` (`ID_marca`),
  CONSTRAINT `Producto_ibfk_1` FOREIGN KEY (`ID_Clase`) REFERENCES `Clase_producto` (`ID_Clase`),
  CONSTRAINT `Producto_ibfk_2` FOREIGN KEY (`ID_marca`) REFERENCES `Marca_producto` (`ID_marca`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Producto`
--

LOCK TABLES `Producto` WRITE;
/*!40000 ALTER TABLE `Producto` DISABLE KEYS */;
INSERT INTO `Producto` VALUES ('1','1','1','Iphone 15','Iphone 15'),('10','7','4','BaterÃ­a Xiaomi','BaterÃ­a original Xiaomi'),('11','1','5','Prueba Juan','Prueba Juan'),('2','2','2','Pantalla Generica Iphone 15','Pantalla generica para iphone 15'),('3','1','3','Samsung S24','Smartphone Samsung S24 256GB'),('4','1','4','Xiaomi 13 Pro','Xiaomi 13 Pro 512GB'),('5','2','3','Pantalla S24','Pantalla original Samsung S24'),('6','3','5','Moto Tab','Tablet Motorola 10 pulgadas'),('7','4','2','Cargador 20W','Cargador rÃ¡pido 20W USB-C'),('8','5','1','Funda iPhone','Funda protectora para iPhone'),('9','6','6','FreeBuds Pro','AudÃ­fonos Huawei FreeBuds Pro');
/*!40000 ALTER TABLE `Producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Proveedor`
--

DROP TABLE IF EXISTS `Proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Proveedor` (
  `ID_proveedor` int NOT NULL,
  `Nombre_proveedor` varchar(40) NOT NULL,
  `Tipo_proveedor` varchar(20) DEFAULT NULL,
  `Celular_proveedor` varchar(15) DEFAULT NULL,
  `Correo_proveedor` varchar(120) DEFAULT NULL,
  `Direccion_proveedor` varchar(60) DEFAULT NULL,
  `Limite_credito` decimal(10,2) DEFAULT NULL,
  `Rif_proveedor` varchar(15) DEFAULT NULL COMMENT 'RIF del proveedor (ej: J-12345678-9)',
  PRIMARY KEY (`ID_proveedor`),
  UNIQUE KEY `Rif_proveedor` (`Rif_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Proveedor`
--

LOCK TABLES `Proveedor` WRITE;
/*!40000 ALTER TABLE `Proveedor` DISABLE KEYS */;
INSERT INTO `Proveedor` VALUES (1,'Distribuidora Tech Sa','Nacional','04121234501','ventas@distritech.com','Caracas',50000.00,'J-12456897-9'),(2,'Importaciones Digitales C.A.','Importador','04141234501','contacto@importdigital.com','Maracaibo',75000.00,NULL),(3,'Repuestos Express','Minorista','04241234502','info@repuestosexpress.com','Valencia',25000.00,NULL),(4,'Global Parts','Mayorista','04161234503','sales@globalparts.com','Barquisimeto',100000.00,NULL),(5,'Suministros MÃ³viles','Distribuidor','04181234504','ventas@suministrosmoviles.com','San CristÃ³bal',30000.00,NULL),(6,'Prueba Juan','Nacional','04120754888','correo@correo.com','prueba juan',5000.00,'J-12345672-9');
/*!40000 ALTER TABLE `Proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Repuestos_usados`
--

DROP TABLE IF EXISTS `Repuestos_usados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Repuestos_usados` (
  `ID_orden_servicio` varchar(10) NOT NULL,
  `ID_inventario` varchar(10) NOT NULL,
  `Cantidad_usada` int NOT NULL,
  PRIMARY KEY (`ID_orden_servicio`,`ID_inventario`),
  KEY `ID_inventario` (`ID_inventario`),
  CONSTRAINT `Repuestos_usados_ibfk_1` FOREIGN KEY (`ID_orden_servicio`) REFERENCES `Orden_servicio` (`ID_orden_servicio`),
  CONSTRAINT `Repuestos_usados_ibfk_2` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Repuestos_usados`
--

LOCK TABLES `Repuestos_usados` WRITE;
/*!40000 ALTER TABLE `Repuestos_usados` DISABLE KEYS */;
INSERT INTO `Repuestos_usados` VALUES ('OS0000001','10',1),('OS0000001','2',1),('OS0000002','10',3),('OS0000003','7',1),('OS0000004','2',12),('OS0000005','5',3),('OS0000025','10',1),('OS0000034','2',3);
/*!40000 ALTER TABLE `Repuestos_usados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Suministra`
--

DROP TABLE IF EXISTS `Suministra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Suministra` (
  `ID_proveedor` int NOT NULL,
  `ID_producto` varchar(10) NOT NULL,
  `Costo_producto` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_proveedor`,`ID_producto`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `Suministra_ibfk_1` FOREIGN KEY (`ID_proveedor`) REFERENCES `Proveedor` (`ID_proveedor`),
  CONSTRAINT `Suministra_ibfk_2` FOREIGN KEY (`ID_producto`) REFERENCES `Producto` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Suministra`
--

LOCK TABLES `Suministra` WRITE;
/*!40000 ALTER TABLE `Suministra` DISABLE KEYS */;
INSERT INTO `Suministra` VALUES (1,'1',650.00),(1,'3',800.00),(2,'2',280.00),(2,'4',700.00),(3,'5',320.00),(3,'7',18.00),(4,'6',380.00),(4,'9',95.00),(5,'10',65.00),(5,'8',10.00),(6,'3',250.00);
/*!40000 ALTER TABLE `Suministra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Test`
--

DROP TABLE IF EXISTS `Test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Test` (
  `ID_test` varchar(10) NOT NULL,
  `Numero_test` int DEFAULT NULL,
  `Nombre_test` varchar(30) NOT NULL,
  `Resultado_test` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Test`
--

LOCK TABLES `Test` WRITE;
/*!40000 ALTER TABLE `Test` DISABLE KEYS */;
INSERT INTO `Test` VALUES ('TST000001',1,'Prueba de BaterÃ­a','Funciona'),('TST000002',1,'Prueba de Pantalla','No funciona'),('TST000003',1,'Prueba de CÃ¡mara','SIn revisar'),('TST000004',4,'Prueba de Botones','Todos los botones funcionales'),('TST000005',5,'Prueba de Audio','Audio y micrÃ³fono operativos'),('TST000006',1,'Descripsion','la pantalla se mojo por dentro '),('TST000007',1,'Descripsion2','pruebaaaaaassssssssssssssssssssssssssssssss'),('TST000008',1,'BotÃ³n power','Funciona'),('TST000009',1,'Pantalla','No funciona'),('TST000010',2,'BotÃ³n de power','Funciona'),('TST000011',2,'LCD','Funciona'),('TST000012',2,'Botones inferiores','Funciona'),('TST000013',3,'BotÃ³n de power','Funciona'),('TST000014',3,'Cornetas','Funciona'),('TST000015',3,'Mica','Funciona'),('TST000016',3,'LCD','Funciona'),('TST000017',3,'TÃ¡ctil','Funciona'),('TST000018',3,'Botones laterales','Funciona'),('TST000019',3,'Botones inferiores','Funciona'),('TST000020',3,'Puerto de carga','Funciona'),('TST000021',3,'WiFi','Funciona'),('TST000022',3,'CÃ¡mara trasera','Funciona'),('TST000023',3,'CÃ¡mara delantera','Funciona'),('TST000024',3,'Flash','Funciona'),('TST000025',3,'SeÃ±al auricular','Funciona'),('TST000026',3,'MicrÃ³fono','Funciona'),('TST000027',3,'Sensor de proximidad','Funciona'),('TST000028',3,'Face ID','Funciona'),('TST000029',3,'Bluetooth','Funciona'),('TST000030',3,'Caja','Funciona'),('TST000031',3,'Cargador','Funciona'),('TST000032',3,'Cable','Funciona'),('TST000033',3,'AudÃ­fonos','Funciona'),('TST000034',3,'Manuales','Funciona'),('TST000035',1,'Manuales','Funciona'),('TST000036',4,'Observaciones','ddddddddddddddddddddddddddddd'),('TST000037',5,'Observaciones','ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss'),('TST000038',1,'Btn power','Funciona'),('TST000039',1,'Cornetas','Funciona'),('TST000040',1,'Mica','Funciona'),('TST000041',1,'LCD','Funciona'),('TST000042',1,'Tactil','Funciona'),('TST000043',1,'Btn vol','Funciona'),('TST000044',1,'Btn sil','Funciona'),('TST000045',1,'Puerto carga','Funciona'),('TST000046',1,'Wifi','Funciona'),('TST000047',1,'Cam pos','Funciona'),('TST000048',1,'Flash','Funciona'),('TST000049',1,'Senal','Funciona'),('TST000050',1,'Sensor proximidad','Funciona'),('TST000051',1,'Face id','Funciona'),('TST000052',1,'Bluetooth','Funciona'),('TST000053',1,'Caja','Funciona'),('TST000054',1,'Cargador','Funciona'),('TST000055',1,'Cable','Funciona'),('TST000056',1,'Auricular','Funciona'),('TST000057',1,'Manuales','Funciona'),('TST000058',1,'Observaciones','ssssssssssssssssssssssssssssssssss'),('TST000059',2,'Btn power','No funciona'),('TST000060',2,'Cornetas','No funciona'),('TST000061',2,'Mica','No funciona'),('TST000062',2,'LCD','No funciona'),('TST000063',2,'Tactil','No funciona'),('TST000064',2,'Btn vol','No funciona'),('TST000065',2,'Btn sil','No funciona'),('TST000066',2,'Puerto carga','No funciona'),('TST000067',2,'Wifi','No funciona'),('TST000068',2,'Cam pos','No funciona'),('TST000069',2,'Cam del','No funciona'),('TST000070',2,'Flash','No funciona'),('TST000071',2,'Senal','No funciona'),('TST000072',2,'Microfono','No funciona'),('TST000073',2,'Sensor proximidad','No funciona'),('TST000074',2,'Face id','No funciona'),('TST000075',2,'Bluetooth','No funciona'),('TST000076',2,'Caja','No funciona'),('TST000077',2,'Cargador','No funciona'),('TST000078',2,'Cable','No funciona'),('TST000079',2,'Auricular','No funciona'),('TST000080',2,'Manuales','No funciona'),('TST000081',2,'Observaciones','ssssssssssssssssssssss'),('TST000082',3,'Tactil','Funciona'),('TST000083',3,'Btn sil','Funciona'),('TST000084',6,'Btn power','Funciona'),('TST000085',6,'Cornetas','Funciona'),('TST000086',6,'Mica','Funciona'),('TST000087',6,'LCD','Funciona'),('TST000088',6,'Tactil','Funciona'),('TST000089',6,'Btn vol','Funciona'),('TST000090',6,'Btn sil','Funciona'),('TST000091',6,'Puerto carga','Funciona'),('TST000092',6,'Wifi','Funciona'),('TST000093',6,'Cam pos','Funciona'),('TST000094',6,'Cam del','Funciona'),('TST000095',6,'Flash','Funciona'),('TST000096',6,'Senal','Funciona'),('TST000097',6,'Microfono','Funciona'),('TST000098',6,'Sensor proximidad','Funciona'),('TST000099',6,'Face id','Funciona'),('TST000100',6,'Bluetooth','Funciona'),('TST000101',6,'Caja','Funciona'),('TST000102',6,'Cargador','Funciona'),('TST000103',6,'Cable','Funciona'),('TST000104',6,'Auricular','Funciona'),('TST000105',6,'Manuales','Funciona'),('TST000106',6,'Observaciones','dsdsdsdsdsdsdsdsd'),('TST000107',1,'Btn power','Funciona'),('TST000108',1,'Observaciones','dddddddddddd'),('TST000109',1,'Btn power','Funciona'),('TST000110',1,'Cornetas','Funciona'),('TST000111',1,'Mica','Funciona'),('TST000112',1,'LCD','Funciona'),('TST000113',1,'Tactil','Funciona'),('TST000114',1,'Btn vol','Funciona'),('TST000115',1,'Btn sil','Funciona'),('TST000116',1,'Puerto carga','Funciona'),('TST000117',1,'Wifi','Funciona'),('TST000118',1,'Cam pos','Funciona'),('TST000119',1,'Cam del','Funciona'),('TST000120',1,'Flash','Funciona'),('TST000121',1,'Senal','Funciona'),('TST000122',1,'Microfono','Funciona'),('TST000123',1,'Sensor proximidad','Funciona'),('TST000124',1,'Face id','Funciona'),('TST000125',1,'Bluetooth','Funciona'),('TST000126',1,'Caja','Funciona'),('TST000127',1,'Cargador','Funciona'),('TST000128',1,'Cable','Funciona'),('TST000129',1,'Auricular','Funciona'),('TST000130',1,'Manuales','Funciona'),('TST000131',1,'Observaciones','sssssssssssssssssssssssss');
/*!40000 ALTER TABLE `Test` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Test_realizados_interaccion`
--

DROP TABLE IF EXISTS `Test_realizados_interaccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Test_realizados_interaccion` (
  `ID_interaccion` varchar(10) NOT NULL,
  `ID_test` varchar(10) NOT NULL,
  PRIMARY KEY (`ID_interaccion`,`ID_test`),
  KEY `ID_test` (`ID_test`),
  CONSTRAINT `Test_realizados_interaccion_ibfk_1` FOREIGN KEY (`ID_interaccion`) REFERENCES `Interaccion` (`ID_interaccion`),
  CONSTRAINT `Test_realizados_interaccion_ibfk_2` FOREIGN KEY (`ID_test`) REFERENCES `Test` (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Test_realizados_interaccion`
--

LOCK TABLES `Test_realizados_interaccion` WRITE;
/*!40000 ALTER TABLE `Test_realizados_interaccion` DISABLE KEYS */;
INSERT INTO `Test_realizados_interaccion` VALUES ('INT000001','TST000001'),('INT000001','TST000002'),('INT000001','TST000003'),('INT000003','TST000004'),('INT000005','TST000005'),('INT000001','TST000006'),('INT000001','TST000007'),('INT000007','TST000008'),('INT000007','TST000009'),('INT000008','TST000010'),('INT000008','TST000011'),('INT000008','TST000012'),('INT000009','TST000013'),('INT000009','TST000014'),('INT000009','TST000015'),('INT000009','TST000016'),('INT000009','TST000017'),('INT000009','TST000018'),('INT000009','TST000019'),('INT000009','TST000020'),('INT000009','TST000021'),('INT000009','TST000022'),('INT000009','TST000023'),('INT000009','TST000024'),('INT000009','TST000025'),('INT000009','TST000026'),('INT000009','TST000027'),('INT000009','TST000028'),('INT000009','TST000029'),('INT000009','TST000030'),('INT000009','TST000031'),('INT000009','TST000032'),('INT000009','TST000033'),('INT000009','TST000034'),('INT000010','TST000035'),('INT000011','TST000036'),('INT000012','TST000037'),('INT000023','TST000038'),('INT000023','TST000039'),('INT000023','TST000040'),('INT000023','TST000041'),('INT000023','TST000042'),('INT000023','TST000043'),('INT000023','TST000044'),('INT000023','TST000045'),('INT000023','TST000046'),('INT000023','TST000047'),('INT000023','TST000048'),('INT000023','TST000049'),('INT000023','TST000050'),('INT000023','TST000051'),('INT000023','TST000052'),('INT000023','TST000053'),('INT000023','TST000054'),('INT000023','TST000055'),('INT000023','TST000056'),('INT000023','TST000057'),('INT000023','TST000058'),('INT000024','TST000059'),('INT000024','TST000060'),('INT000024','TST000061'),('INT000024','TST000062'),('INT000024','TST000063'),('INT000024','TST000064'),('INT000024','TST000065'),('INT000024','TST000066'),('INT000024','TST000067'),('INT000024','TST000068'),('INT000024','TST000069'),('INT000024','TST000070'),('INT000024','TST000071'),('INT000024','TST000072'),('INT000024','TST000073'),('INT000024','TST000074'),('INT000024','TST000075'),('INT000024','TST000076'),('INT000024','TST000077'),('INT000024','TST000078'),('INT000024','TST000079'),('INT000024','TST000080'),('INT000024','TST000081'),('INT000025','TST000082'),('INT000025','TST000083'),('INT000028','TST000084'),('INT000028','TST000085'),('INT000028','TST000086'),('INT000028','TST000087'),('INT000028','TST000088'),('INT000028','TST000089'),('INT000028','TST000090'),('INT000028','TST000091'),('INT000028','TST000092'),('INT000028','TST000093'),('INT000028','TST000094'),('INT000028','TST000095'),('INT000028','TST000096'),('INT000028','TST000097'),('INT000028','TST000098'),('INT000028','TST000099'),('INT000028','TST000100'),('INT000028','TST000101'),('INT000028','TST000102'),('INT000028','TST000103'),('INT000028','TST000104'),('INT000028','TST000105'),('INT000028','TST000106'),('INT000030','TST000107'),('INT000030','TST000108'),('INT000037','TST000109'),('INT000037','TST000110'),('INT000037','TST000111'),('INT000037','TST000112'),('INT000037','TST000113'),('INT000037','TST000114'),('INT000037','TST000115'),('INT000037','TST000116'),('INT000037','TST000117'),('INT000037','TST000118'),('INT000037','TST000119'),('INT000037','TST000120'),('INT000037','TST000121'),('INT000037','TST000122'),('INT000037','TST000123'),('INT000037','TST000124'),('INT000037','TST000125'),('INT000037','TST000126'),('INT000037','TST000127'),('INT000037','TST000128'),('INT000037','TST000129'),('INT000037','TST000130'),('INT000037','TST000131');
/*!40000 ALTER TABLE `Test_realizados_interaccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Test_realizados_trade_in`
--

DROP TABLE IF EXISTS `Test_realizados_trade_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Test_realizados_trade_in` (
  `ID_Trade_in` varchar(10) NOT NULL,
  `ID_test` varchar(10) NOT NULL,
  PRIMARY KEY (`ID_Trade_in`,`ID_test`),
  KEY `ID_test` (`ID_test`),
  CONSTRAINT `Test_realizados_trade_in_ibfk_1` FOREIGN KEY (`ID_Trade_in`) REFERENCES `Trade_in` (`ID_Trade_in`),
  CONSTRAINT `Test_realizados_trade_in_ibfk_2` FOREIGN KEY (`ID_test`) REFERENCES `Test` (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Test_realizados_trade_in`
--

LOCK TABLES `Test_realizados_trade_in` WRITE;
/*!40000 ALTER TABLE `Test_realizados_trade_in` DISABLE KEYS */;
INSERT INTO `Test_realizados_trade_in` VALUES ('TRD000001','TST000001'),('TRD000002','TST000001'),('TRD000001','TST000002'),('TRD000003','TST000002'),('TRD000004','TST000004');
/*!40000 ALTER TABLE `Test_realizados_trade_in` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Trade_in`
--

DROP TABLE IF EXISTS `Trade_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Trade_in` (
  `ID_Trade_in` varchar(10) NOT NULL,
  `ID_empleado` int DEFAULT NULL,
  `ID_cliente` varchar(10) DEFAULT NULL,
  `ID_inventario` varchar(10) DEFAULT NULL,
  `ID_equipo` varchar(10) DEFAULT NULL,
  `Numero_utilizado` int DEFAULT NULL,
  `Fecha_realizado` datetime DEFAULT NULL,
  `cotizacion` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_Trade_in`),
  KEY `ID_empleado` (`ID_empleado`),
  KEY `ID_cliente` (`ID_cliente`),
  KEY `ID_inventario` (`ID_inventario`),
  KEY `ID_equipo` (`ID_equipo`),
  CONSTRAINT `Trade_in_ibfk_1` FOREIGN KEY (`ID_empleado`) REFERENCES `Empleado` (`ID_empleado`),
  CONSTRAINT `Trade_in_ibfk_2` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`),
  CONSTRAINT `Trade_in_ibfk_3` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`),
  CONSTRAINT `Trade_in_ibfk_4` FOREIGN KEY (`ID_equipo`) REFERENCES `Equipo` (`ID_equipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Trade_in`
--

LOCK TABLES `Trade_in` WRITE;
/*!40000 ALTER TABLE `Trade_in` DISABLE KEYS */;
INSERT INTO `Trade_in` VALUES ('TRD000001',20123456,'22345678','1','EQ0000001',1,'2026-06-01 09:00:00',500.00),('TRD000002',20234567,'33456789','3','EQ0000002',1,'2026-06-02 10:30:00',650.00),('TRD000003',20123456,'44567890','4','EQ0000003',0,'2026-06-03 14:00:00',550.00),('TRD000004',20345678,'55678901','1','EQ0000004',1,'2026-06-04 08:15:00',400.00),('TRD000005',20234567,'66789012','2','EQ0000005',0,'2026-06-05 11:30:00',300.00);
/*!40000 ALTER TABLE `Trade_in` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Venta`
--

DROP TABLE IF EXISTS `Venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Venta` (
  `ID_factura` varchar(20) NOT NULL,
  `ID_empleado` int DEFAULT NULL,
  `ID_cliente` varchar(10) DEFAULT NULL,
  `Moneda` varchar(10) DEFAULT NULL,
  `Fecha_venta` datetime DEFAULT NULL,
  PRIMARY KEY (`ID_factura`),
  KEY `ID_empleado` (`ID_empleado`),
  KEY `ID_cliente` (`ID_cliente`),
  CONSTRAINT `Venta_ibfk_1` FOREIGN KEY (`ID_empleado`) REFERENCES `Empleado` (`ID_empleado`),
  CONSTRAINT `Venta_ibfk_2` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Venta`
--

LOCK TABLES `Venta` WRITE;
/*!40000 ALTER TABLE `Venta` DISABLE KEYS */;
INSERT INTO `Venta` VALUES ('FAC-202606-080A3A',NULL,'30548845','USDT','2026-06-07 22:25:27'),('FAC-202606-111111',20123456,'22345678','VES','2026-06-01 10:30:00'),('FAC-202606-222222',20123456,'33456789','USD','2026-06-02 11:45:00'),('FAC-202606-333333',20345678,'44567890','USDT','2026-06-03 09:20:00'),('FAC-202606-444444',20345678,'55678901','VES','2026-06-04 14:15:00'),('FAC-202606-555555',20123456,'66789012','USD','2026-06-05 16:30:00'),('FAC-202606-666666',20345678,'30548845','VES','2026-06-06 12:00:00'),('FAC-202606-6993F3',NULL,'30548845','VES','2026-06-07 21:30:03'),('FAC-202606-777777',20123456,'31143265','USDT','2026-06-07 15:45:00'),('FAC-202606-8D8B04',NULL,'30548845','VES','2026-06-07 22:17:23'),('FAC-202606-B1475D',NULL,'30548845','USD','2026-06-07 21:35:57'),('FAC-202606-DA0967',NULL,'30548845','VES','2026-06-07 20:12:28'),('FAC-202606-EB6A95',NULL,'30548845','VES','2026-06-07 20:50:37'),('FAC-202606-FDD009',NULL,'30548845','USD','2026-06-07 22:09:06');
/*!40000 ALTER TABLE `Venta` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-06 13:42:05
