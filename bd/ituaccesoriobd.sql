-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
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
INSERT INTO `capacitacion` VALUES (1,1006),(2,1006),(3,1006),(5,1006),(8,1006),(1,1007),(2,1007),(4,1007),(6,1007),(9,1007),(1,1008),(3,1008),(5,1008),(7,1008),(10,1008);
/*!40000 ALTER TABLE `capacitacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `caracteristica`
--

DROP TABLE IF EXISTS `caracteristica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `caracteristica` (
  `ID_producto` int NOT NULL,
  `Capacidad` varchar(10) DEFAULT NULL,
  `Color` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`ID_producto`),
  CONSTRAINT `caracteristica_ibfk_stock` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `caracteristica`
--

LOCK TABLES `caracteristica` WRITE;
/*!40000 ALTER TABLE `caracteristica` DISABLE KEYS */;
INSERT INTO `caracteristica` VALUES (1,'512GB','Negro'),(2,'256GB','Verde'),(3,'128GB','Blanco'),(4,'1TB','Titanio'),(5,'512GB','Azul'),(6,'128GB','Morado'),(7,'256GB','Negro'),(8,'128GB','Rosa'),(9,'256GB','Azul'),(10,'128GB','Negro'),(11,'512GB','Blanco'),(12,'32GB','Negro'),(13,'10000mAh','Gris'),(14,'Universal','Negro'),(15,'256GB','Gris Espacial');
/*!40000 ALTER TABLE `caracteristica` ENABLE KEYS */;
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
  `des_cargo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID_cargo`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cargo`
--

LOCK TABLES `cargo` WRITE;
/*!40000 ALTER TABLE `cargo` DISABLE KEYS */;
INSERT INTO `cargo` VALUES (1,'Gerente General','Responsable de la gestion general de la tienda'),(2,'Supervisor de Ventas','Supervisa el equipo de ventas y cumplimiento de metas'),(3,'Vendedor','Atencion al cliente y venta de productos'),(4,'Tecnico Reparaciones','Realiza diagnosticos y reparaciones de dispositivos'),(5,'Tecnico Especialista','Especialista en reparaciones avanzadas'),(6,'Auxiliar de Almacen','Gestiona inventario y recepcion de productos'),(7,'Delivery','Realiza entregas a domicilio'),(8,'Community Manager','Gestiona redes sociales y atencion digital'),(9,'Contador','Maneja finanzas y facturacion'),(10,'Asesor Comercial','Asesora a clientes corporativos');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clase_producto`
--

LOCK TABLES `clase_producto` WRITE;
/*!40000 ALTER TABLE `clase_producto` DISABLE KEYS */;
INSERT INTO `clase_producto` VALUES (1,'Telefonos',3),(2,'Tablets',3),(3,'Accesorios de Audio',1),(4,'Cargadores',1),(5,'Fundas y Protectores',1),(6,'Cables',1),(7,'Baterias',2),(8,'Repuestos Internos',2),(9,'Herramientas',2),(10,'Smartwatches',3);
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
INSERT INTO `cliente` VALUES (1,'Maria','Gonzalez','04141234567','maria.g@example.com','Calle 1, Ciudad','Regular'),(2,'Juan','Perez','04141234568','juan.p@example.com','Av. 2, Ciudad','Premium'),(3,'Ana','Rodriguez','04141234569','ana.r@example.com','Calle 3, Ciudad','Regular'),(4,'Luis','Martinez','04141234570','luis.m@example.com','Av. 4, Ciudad','Mayorista'),(5,'Carla','Fernandez','04141234571','carla.f@example.com','Calle 5, Ciudad','Regular'),(6,'Carlos','Sanchez','04161234572','carlos.s@example.com','Calle 6, Ciudad','Premium'),(7,'Laura','Diaz','04161234573','laura.d@example.com','Av. 7, Ciudad','Regular'),(8,'Pedro','Gomez','04161234574','pedro.g@example.com','Calle 8, Ciudad','Regular'),(9,'Sofia','Lopez','04161234575','sofia.l@example.com','Av. 9, Ciudad','Premium'),(10,'Diego','Torres','04161234576','diego.t@example.com','Calle 10, Ciudad','Mayorista'),(11,'Valentina','Ruiz','04161234577','valentina.r@example.com','Av. 11, Ciudad','Regular'),(12,'Andres','Morales','04161234578','andres.m@example.com','Calle 12, Ciudad','Premium'),(13,'Camila','Ortega','04161234579','camila.o@example.com','Av. 13, Ciudad','Regular'),(14,'Javier','Castro','04161234580','javier.c@example.com','Calle 14, Ciudad','Regular'),(15,'Isabella','Mendoza','04161234581','isabella.m@example.com','Av. 15, Ciudad','Premium');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credito`
--

LOCK TABLES `credito` WRITE;
/*!40000 ALTER TABLE `credito` DISABLE KEYS */;
INSERT INTO `credito` VALUES (1,1,30),(2,2,45),(3,3,30),(4,4,60),(5,5,30),(6,6,15),(7,7,30),(8,8,45),(9,9,30),(10,10,60);
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
  `ID_cargo` int DEFAULT NULL,
  `Nombre_em` varchar(40) DEFAULT NULL,
  `Apellido_em` varchar(40) DEFAULT NULL,
  `Celular_em` varchar(15) DEFAULT NULL,
  `Correo_em` varchar(30) DEFAULT NULL,
  `Direccion_em` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ID_em`),
  KEY `fk_empleado_cargo` (`ID_cargo`),
  CONSTRAINT `fk_empleado_cargo` FOREIGN KEY (`ID_cargo`) REFERENCES `cargo` (`ID_cargo`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
INSERT INTO `empleado` VALUES (1001,1,'Roberto','Garcia','04241234567','roberto.g@ituaccesorio.com','Oficina Central'),(1002,2,'Elena','Martin','04241234568','elena.m@ituaccesorio.com','Oficina Central'),(1003,3,'Luisana','Perez','04241234569','luisana.p@ituaccesorio.com','Sucursal Norte'),(1004,3,'Gabriel','Rojas','04241234570','gabriel.r@ituaccesorio.com','Sucursal Norte'),(1005,3,'Daniela','Flores','04241234571','daniela.f@ituaccesorio.com','Sucursal Sur'),(1006,4,'Jorge','Silva','04241234572','jorge.s@ituaccesorio.com','Taller Central'),(1007,4,'Mariana','Rios','04241234573','mariana.r@ituaccesorio.com','Taller Central'),(1008,5,'Ricardo','Nunez','04241234574','ricardo.n@ituaccesorio.com','Taller Central'),(1009,6,'Fernando','Calderon','04241234575','fernando.c@ituaccesorio.com','Almacen'),(1010,7,'Andres','Salazar','04161234582','andres.s@ituaccesorio.com','Delivery'),(1011,7,'Miguel','Hernandez','04161234583','miguel.h@ituaccesorio.com','Delivery'),(1012,8,'Carolina','Mendez','04241234576','carolina.m@ituaccesorio.com','Oficina Central');
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
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
INSERT INTO `entrega` VALUES (1,'FAC-2026-0001',1,'Calle 1, Ciudad','2026-05-02','10:30'),(1,'FAC-2026-0003',1,'Calle 3, Ciudad','2026-05-03','09:45'),(1,'FAC-2026-0007',0,'Calle 7, Ciudad','2026-05-05','00:00'),(2,'FAC-2026-0002',1,'Av. 2, Ciudad','2026-05-02','11:00'),(2,'FAC-2026-0005',0,'Calle 5, Ciudad','2026-05-04','00:00'),(2,'FAC-2026-0011',0,'Av. 11, Ciudad','2026-05-07','00:00'),(3,'FAC-2026-0004',1,'Av. 4, Ciudad','2026-05-03','14:20'),(3,'FAC-2026-0009',1,'Av. 9, Ciudad','2026-05-06','11:45'),(4,'FAC-2026-0006',1,'Calle 6, Ciudad','2026-05-04','10:15'),(4,'FAC-2026-0013',1,'Av. 13, Ciudad','2026-05-08','10:00'),(5,'FAC-2026-0008',1,'Calle 8, Ciudad','2026-05-05','16:30'),(5,'FAC-2026-0015',0,'Av. 15, Ciudad','2026-05-09','00:00'),(6,'FAC-2026-0010',1,'Calle 10, Ciudad','2026-05-06','09:00'),(7,'FAC-2026-0012',1,'Calle 12, Ciudad','2026-05-07','15:20'),(8,'FAC-2026-0014',1,'Calle 14, Ciudad','2026-05-08','12:30');
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
  `Cantidad_e` int DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entrega_p`
--

LOCK TABLES `entrega_p` WRITE;
/*!40000 ALTER TABLE `entrega_p` DISABLE KEYS */;
INSERT INTO `entrega_p` VALUES (1,1010,1,1,5,'2026-04-05','14:00','OC-001'),(2,1010,2,3,10,'2026-04-07','10:30','OC-002'),(3,1011,3,8,10,'2026-04-09','11:45','OC-003'),(4,1010,4,2,10,'2026-04-12','09:15','OC-004'),(5,1011,5,7,10,'2026-04-15','15:00','OC-005'),(7,1011,7,13,10,'2026-04-18','10:00','OC-007'),(8,1010,8,15,40,'2026-04-22','12:00','OC-008'),(9,1011,9,14,30,'2026-04-25','14:45','OC-009'),(10,1010,10,11,10,'2026-04-28','11:30','OC-010');
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
  `des_especialidad` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `especialidad`
--

LOCK TABLES `especialidad` WRITE;
/*!40000 ALTER TABLE `especialidad` DISABLE KEYS */;
INSERT INTO `especialidad` VALUES (1,'Cambio de Pantalla','Reparacion y reemplazo de pantallas rotas'),(2,'Cambio de Bateria','Reemplazo de baterias de dispositivos moviles'),(3,'Reparacion de Carga','Reparacion de puertos y flex de carga'),(4,'Reparacion de Audio','Reparacion de altavoces, microfonos y auriculares'),(5,'Reparacion de Camaras','Cambio de modulos de camara frontal y trasera'),(6,'Reparacion de Botones','Reparacion de botones fisicos y flex'),(7,'Reparacion Placa Madre','Microsoldadura y reparacion de componentes'),(8,'Software y Desbloqueos','Instalacion de software, desbloqueos y flasheo'),(9,'Reparacion de Agua','Limpieza y restauracion por humedad/liquidos'),(10,'Cambio de Conectores','Reemplazo de conectores y flexes internos');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia_e`
--

LOCK TABLES `evidencia_e` WRITE;
/*!40000 ALTER TABLE `evidencia_e` DISABLE KEYS */;
INSERT INTO `evidencia_e` VALUES (1,1,'/fotos/orden1/antes_pantalla.jpg'),(2,1,'/fotos/orden1/despues_pantalla.jpg'),(3,2,'/fotos/orden2/puerto_danado.jpg'),(4,3,'/fotos/orden3/bateria_vieja.jpg'),(5,4,'/fotos/orden4/camara_rota.jpg'),(6,5,'/fotos/orden5/boton_danado.jpg'),(7,6,'/fotos/orden6/placa_madre.jpg'),(8,7,'/fotos/orden7/altavoz.jpg'),(9,8,'/fotos/orden8/mica_rota.jpg'),(10,9,'/fotos/orden9/wifi.jpg');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia_r`
--

LOCK TABLES `evidencia_r` WRITE;
/*!40000 ALTER TABLE `evidencia_r` DISABLE KEYS */;
INSERT INTO `evidencia_r` VALUES (1,1,'/fotos/test1/mica_trasera.jpg'),(2,2,'/fotos/test2/puerto_carga.jpg'),(3,4,'/fotos/test4/boton_power.jpg'),(4,5,'/fotos/test5/altavoz.jpg'),(5,6,'/fotos/test6/lcd_roto.jpg'),(6,7,'/fotos/test7/wifi.jpg'),(7,8,'/fotos/test8/camaras.jpg'),(8,10,'/fotos/test10/boton_volumen.jpg'),(9,3,'/fotos/test3/equipo_ok.jpg'),(10,9,'/fotos/test9/perfecto.jpg');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia_t`
--

LOCK TABLES `evidencia_t` WRITE;
/*!40000 ALTER TABLE `evidencia_t` DISABLE KEYS */;
INSERT INTO `evidencia_t` VALUES (1,1,'/productos/s23_ultra_negro.jpg'),(2,2,'/productos/s23_plus_verde.jpg'),(3,3,'/productos/a54_blanco.jpg'),(4,4,'/productos/iphone15_pro_max_titanio.jpg'),(5,5,'/productos/iphone15_pro_azul.jpg'),(6,6,'/productos/iphone14_morado.jpg'),(7,7,'/productos/xiaomi13pro_negro.jpg'),(8,8,'/productos/xiaomi12lite_rosa.jpg'),(9,9,'/productos/moto_g84_azul.jpg'),(10,10,'/productos/moto_edge40_negro.jpg');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencia_t_tradein`
--

LOCK TABLES `evidencia_t_tradein` WRITE;
/*!40000 ALTER TABLE `evidencia_t_tradein` DISABLE KEYS */;
INSERT INTO `evidencia_t_tradein` VALUES (1,1,'/tradein/trade1_galaxy_s23.jpg'),(2,2,'/tradein/trade2_iphone15pm.jpg'),(3,3,'/tradein/trade3_iphone14.jpg'),(4,4,'/tradein/trade4_xiaomi12lite.jpg'),(5,5,'/tradein/trade5_moto_edge40.jpg'),(6,6,'/tradein/trade6_pixel7a.jpg'),(7,7,'/tradein/trade7_case.jpg'),(8,8,'/tradein/trade8_s23plus.jpg'),(9,9,'/tradein/trade9_iphone15pro.jpg'),(10,10,'/tradein/trade10_ipadpro.jpg');
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
INSERT INTO `interaccion` VALUES (1006,1,'Diagnostico inicial'),(1006,2,'Revision de equipo'),(1006,6,'Reparacion en curso'),(1006,9,'Revision de software'),(1007,3,'Reparacion completada'),(1007,4,'Esperando repuestos'),(1007,7,'Pruebas finales'),(1007,10,'Reparacion de carga'),(1008,5,'Diagnostico avanzado'),(1008,8,'Cambio de pantalla');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lista_carrito`
--

LOCK TABLES `lista_carrito` WRITE;
/*!40000 ALTER TABLE `lista_carrito` DISABLE KEYS */;
INSERT INTO `lista_carrito` VALUES (1,1,1,1,0),(2,5,2,2,0),(3,3,3,1,0),(4,7,4,1,0),(5,10,5,1,0),(6,12,6,1,0),(7,14,7,3,0),(8,2,8,1,0),(9,9,9,1,0),(10,13,10,2,0);
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
INSERT INTO `lista_compra` VALUES (1,'FAC-2026-0001',1),(2,'FAC-2026-0005',1),(3,'FAC-2026-0003',1),(4,'FAC-2026-0004',1),(5,'FAC-2026-0002',1),(6,'FAC-2026-0006',1),(7,'FAC-2026-0011',1),(8,'FAC-2026-0012',1),(9,'FAC-2026-0013',1),(10,'FAC-2026-0008',1),(11,'FAC-2026-0009',1),(12,'FAC-2026-0007',1),(13,'FAC-2026-0014',2),(14,'FAC-2026-0010',1),(15,'FAC-2026-0015',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marca_producto`
--

LOCK TABLES `marca_producto` WRITE;
/*!40000 ALTER TABLE `marca_producto` DISABLE KEYS */;
INSERT INTO `marca_producto` VALUES (1,1,'Samsung'),(2,1,'Apple'),(3,1,'Xiaomi'),(4,1,'Motorola'),(5,1,'Google'),(6,3,'Sony'),(7,3,'JBL'),(8,4,'Anker'),(9,4,'Belkin'),(10,5,'OtterBox');
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
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modelo_producto`
--

LOCK TABLES `modelo_producto` WRITE;
/*!40000 ALTER TABLE `modelo_producto` DISABLE KEYS */;
INSERT INTO `modelo_producto` VALUES (1,1,'Galaxy S23 Ultra'),(2,1,'Galaxy S23 Plus'),(3,1,'Galaxy A54'),(4,2,'iPhone 15 Pro Max'),(5,2,'iPhone 15 Pro'),(6,2,'iPhone 14'),(7,3,'Xiaomi 13 Pro'),(8,3,'Xiaomi 12 Lite'),(9,4,'Moto G84'),(10,4,'Moto Edge 40'),(11,5,'Pixel 8 Pro'),(12,5,'Pixel 7a'),(13,6,'WH-1000XM5'),(14,7,'Charge 5'),(15,8,'PowerCore 10000'),(16,9,'BoostCharge 65W'),(17,10,'Defender Case'),(18,1,'Galaxy Tab S9'),(19,2,'iPad Pro 11'),(20,10,'Smartwatch 5 Pro');
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
  `ID_proveedor` int DEFAULT NULL,
  `Fecha_o` varchar(10) DEFAULT NULL,
  `Costo_venta` int DEFAULT NULL,
  PRIMARY KEY (`ID_orden_c`),
  KEY `ID_em` (`ID_em`),
  KEY `ID_proveedor` (`ID_proveedor`),
  CONSTRAINT `orden_compra_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`),
  CONSTRAINT `orden_compra_ibfk_2` FOREIGN KEY (`ID_proveedor`) REFERENCES `proveedor` (`ID_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orden_compra`
--

LOCK TABLES `orden_compra` WRITE;
/*!40000 ALTER TABLE `orden_compra` DISABLE KEYS */;
INSERT INTO `orden_compra` VALUES (1,1009,1,'2026-04-01',5500000),(2,1009,2,'2026-04-03',2500000),(3,1009,3,'2026-04-05',3800000),(4,1009,4,'2026-04-08',4800000),(5,1009,5,'2026-04-10',7000000),(6,1009,6,'2026-04-12',1250000),(7,1009,7,'2026-04-15',1800000),(8,1009,8,'2026-04-18',2200000),(9,1009,9,'2026-04-20',960000),(10,1009,10,'2026-04-22',9800000),(11,1009,1,'2026-05-02',3300000),(12,1009,2,'2026-05-05',3150000),(13,1009,3,'2026-05-08',1500000),(14,1009,4,'2026-05-10',1900000),(15,1009,5,'2026-05-12',2800000);
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
  `Fecha_e` date DEFAULT NULL,
  `Fecha_s` date DEFAULT NULL,
  `Nota` varchar(300) DEFAULT NULL,
  `Reparacion` varchar(300) DEFAULT NULL,
  `Revision` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID_orden_e`),
  KEY `ID_modelo` (`ID_modelo`),
  KEY `ID_c` (`ID_c`),
  CONSTRAINT `orden_e_ibfk_1` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`),
  CONSTRAINT `orden_e_ibfk_2` FOREIGN KEY (`ID_c`) REFERENCES `cliente` (`ID_c`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orden_e`
--

LOCK TABLES `orden_e` WRITE;
/*!40000 ALTER TABLE `orden_e` DISABLE KEYS */;
INSERT INTO `orden_e` VALUES (1,1,1,'Pendiente','Pantalla rota por caida',1234,'0000',250000,NULL,NULL,NULL,NULL,NULL),(2,4,2,'En Proceso','No carga, puerto danado',5678,'1111',120000,NULL,NULL,NULL,NULL,NULL),(3,3,3,'Completado','Bateria no dura',9012,'2222',80000,NULL,NULL,NULL,NULL,NULL),(4,6,4,'Pendiente','Camara no funciona',3456,'3333',150000,NULL,NULL,NULL,NULL,NULL),(5,7,5,'En Proceso','Boton power atascado',7890,'4444',60000,NULL,NULL,NULL,NULL,NULL),(6,9,6,'Pendiente','No enciende',1122,'5555',180000,NULL,NULL,NULL,NULL,NULL),(7,11,7,'Completado','Altavoz distorsionado',3344,'6666',70000,NULL,NULL,NULL,NULL,NULL),(8,2,8,'En Proceso','Mica trasera rota',5566,'7777',90000,NULL,NULL,NULL,NULL,NULL),(9,5,9,'Pendiente','Problemas de WiFi',7788,'8888',100000,NULL,NULL,NULL,NULL,NULL),(10,8,10,'Completado','Puerto de carga suelto',9900,'9999',80000,NULL,NULL,NULL,NULL,NULL),(11,10,11,'Pendiente','Fallo en lector huella',1212,'1010',95000,NULL,NULL,NULL,NULL,NULL),(12,12,12,'En Proceso','Camara frontal pixeleada',3434,'1212',110000,NULL,NULL,NULL,NULL,NULL);
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
INSERT INTO `pago_carrito` VALUES (1,'FAC-2026-0001'),(2,'FAC-2026-0002'),(3,'FAC-2026-0003'),(4,'FAC-2026-0004'),(5,'FAC-2026-0005'),(6,'FAC-2026-0006'),(7,'FAC-2026-0007'),(8,'FAC-2026-0008'),(9,'FAC-2026-0009'),(10,'FAC-2026-0010');
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
INSERT INTO `pago_orden` VALUES (1,'FAC-2026-0001'),(2,'FAC-2026-0002'),(3,'FAC-2026-0003'),(4,'FAC-2026-0004'),(5,'FAC-2026-0005'),(6,'FAC-2026-0006'),(7,'FAC-2026-0007'),(8,'FAC-2026-0008'),(9,'FAC-2026-0009'),(10,'FAC-2026-0010'),(11,'FAC-2026-0011'),(12,'FAC-2026-0012');
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
INSERT INTO `personal_delivery` VALUES (1,'Andres','Salazar','04161234582'),(2,'Miguel','Hernandez','04161234583'),(3,'Luis','Paredes','04161234584'),(4,'Carlos','Mata','04161234585'),(5,'Jose','Rodriguez','04161234586'),(6,'Ricardo','Gomez','04161234587'),(7,'Pedro','Diaz','04161234588'),(8,'Jesus','Lopez','04161234589'),(9,'Rafael','Torres','04161234590'),(10,'David','Ramos','04161234591');
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
  `Cantidad_p` int DEFAULT NULL,
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
INSERT INTO `productos_orden` VALUES (1,1,5),(1,2,3),(2,3,10),(2,9,5),(3,8,10),(4,2,10),(5,7,10),(6,17,50),(7,13,10),(8,15,40),(9,14,30),(10,11,10),(11,4,2),(11,5,2),(12,6,5),(12,10,2),(13,12,10),(14,8,5),(15,9,10);
/*!40000 ALTER TABLE `productos_orden` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor`
--

DROP TABLE IF EXISTS `proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor` (
  `ID_proveedor` int NOT NULL,
  `N_proveedor` varchar(40) DEFAULT NULL,
  `Tipo_proveedor` varchar(20) DEFAULT NULL,
  `Celular_pr` varchar(15) DEFAULT NULL,
  `Correo_pr` varchar(30) DEFAULT NULL,
  `Direccion_pr` varchar(60) DEFAULT NULL,
  `Limite_credito` int DEFAULT NULL,
  PRIMARY KEY (`ID_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor`
--

LOCK TABLES `proveedor` WRITE;
/*!40000 ALTER TABLE `proveedor` DISABLE KEYS */;
INSERT INTO `proveedor` VALUES (1,'TechImport SRL','Internacional','04121234567','ventas@techimport.com','Zona Franca, Caracas',50000000),(2,'Repuestos Mobile CA','Nacional','04121234568','contacto@repuestosmobile.com','Av. Principal, Maracaibo',20000000),(3,'Accesorios Plus','Nacional','04121234569','info@accesoriosplus.com','Calle Comercio, Valencia',15000000),(4,'Battery World','Internacional','04121234570','sales@batteryworld.com','Miami, USA',100000000),(5,'Screen Pro','Nacional','04121234571','pedidos@screenpro.com','Av. Libertador, Caracas',25000000),(6,'Case Factory','Nacional','04121234572','ventas@casefactory.com','Zona Industrial, Barquisimeto',8000000),(7,'AudioTech','Internacional','04121234573','info@audiotech.com','Shenzhen, China',60000000),(8,'CableMaster','Nacional','04121234574','contacto@cablemaster.com','Calle 5, Maracay',5000000),(9,'ToolFix','Nacional','04121234575','herramientas@toolfix.com','Av. Principal, Puerto La Cruz',3000000),(10,'SmartParts','Internacional','04121234576','parts@smartparts.com','Hong Kong',75000000);
/*!40000 ALTER TABLE `proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores_productos`
--

DROP TABLE IF EXISTS `proveedores_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores_productos` (
  `ID_proveedor` int NOT NULL,
  `ID_modelo` int NOT NULL,
  `Costo` int DEFAULT NULL,
  PRIMARY KEY (`ID_proveedor`,`ID_modelo`),
  KEY `ID_modelo` (`ID_modelo`),
  CONSTRAINT `proveedores_productos_ibfk_1` FOREIGN KEY (`ID_proveedor`) REFERENCES `proveedor` (`ID_proveedor`),
  CONSTRAINT `proveedores_productos_ibfk_2` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores_productos`
--

LOCK TABLES `proveedores_productos` WRITE;
/*!40000 ALTER TABLE `proveedores_productos` DISABLE KEYS */;
INSERT INTO `proveedores_productos` VALUES (1,1,550000),(1,4,950000),(1,9,220000),(2,3,250000),(2,6,600000),(2,10,450000),(3,8,380000),(3,12,150000),(4,2,480000),(5,7,700000),(6,17,25000),(7,13,180000),(8,15,55000),(9,14,32000),(10,11,980000);
/*!40000 ALTER TABLE `proveedores_productos` ENABLE KEYS */;
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
INSERT INTO `repuestos_u` VALUES (1,1,1),(2,4,1),(3,3,1),(6,6,1),(7,5,1),(8,2,1),(10,9,1),(12,7,1),(13,10,1),(14,8,1);
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
INSERT INTO `revision_orden` VALUES (1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(1,11),(2,12);
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
INSERT INTO `revision_test` VALUES (1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10);
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock`
--

LOCK TABLES `stock` WRITE;
/*!40000 ALTER TABLE `stock` DISABLE KEYS */;
INSERT INTO `stock` VALUES (1,1,15,750000),(2,2,10,650000),(3,3,25,350000),(4,4,8,1200000),(5,5,12,1100000),(6,6,20,800000),(7,7,10,950000),(8,8,18,500000),(9,9,30,300000),(10,10,12,600000),(11,11,5,1300000),(12,13,15,250000),(13,15,40,80000),(14,17,50,45000),(15,19,7,1000000);
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
  `Senal` int DEFAULT NULL,
  `Sensor_proximidad` int DEFAULT NULL,
  `Face_id` int DEFAULT NULL,
  `Bluetooth` int DEFAULT NULL,
  `Observaciones` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID_test`),
  KEY `ID_em` (`ID_em`),
  CONSTRAINT `test_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test`
--

LOCK TABLES `test` WRITE;
/*!40000 ALTER TABLE `test` DISABLE KEYS */;
INSERT INTO `test` VALUES (1,1006,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,'Mica trasera danada'),(2,1007,2,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,'Puerto de carga defectuoso'),(3,1008,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,'Todo funciona correctamente'),(4,1006,4,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,'Boton power y mute no funcionan'),(5,1007,5,1,1,0,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,'Altavoz y microfono danados'),(6,1008,6,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0,0,1,'LCD, tactil y sensor rotos'),(7,1006,7,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,0,'WiFi y Bluetooth no funcionan'),(8,1007,8,1,1,1,1,1,1,1,1,0,0,1,0,1,1,1,1,1,1,'Camaras y flash danados'),(9,1008,9,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,'Dispositivo en perfecto estado'),(10,1006,10,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,'Boton volumen no responde');
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tradein`
--

LOCK TABLES `tradein` WRITE;
/*!40000 ALTER TABLE `tradein` DISABLE KEYS */;
INSERT INTO `tradein` VALUES (1,1003,1,1,300000,'2026-05-01','Negro',12,'Liberado'),(2,1004,2,4,500000,'2026-05-02','Titanio',6,'Liberado'),(3,1005,3,6,250000,'2026-05-03','Morado',18,'Con Cuenta'),(4,1003,4,8,180000,'2026-05-04','Azul',24,'Liberado'),(5,1004,5,10,220000,'2026-05-05','Negro',10,'Liberado'),(6,1005,6,12,350000,'2026-05-06','Blanco',8,'Con Cuenta'),(7,1003,7,14,80000,'2026-05-07','Negro',15,'Liberado'),(8,1004,8,2,400000,'2026-05-08','Verde',5,'Liberado'),(9,1005,9,5,480000,'2026-05-09','Azul',7,'Con Cuenta'),(10,1003,10,15,380000,'2026-05-10','Gris Espacial',3,'Liberado');
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
INSERT INTO `venta` VALUES ('FAC-2026-0001',1003,1,750000,'2026-05-01'),('FAC-2026-0002',1004,2,1100000,'2026-05-01'),('FAC-2026-0003',1003,3,350000,'2026-05-02'),('FAC-2026-0004',1005,4,1200000,'2026-05-02'),('FAC-2026-0005',1003,5,650000,'2026-05-03'),('FAC-2026-0006',1004,6,800000,'2026-05-03'),('FAC-2026-0007',1005,7,250000,'2026-05-04'),('FAC-2026-0008',1003,8,600000,'2026-05-04'),('FAC-2026-0009',1004,9,1300000,'2026-05-05'),('FAC-2026-0010',1005,10,45000,'2026-05-05'),('FAC-2026-0011',1003,11,950000,'2026-05-06'),('FAC-2026-0012',1004,12,500000,'2026-05-06'),('FAC-2026-0013',1005,13,300000,'2026-05-07'),('FAC-2026-0014',1003,14,80000,'2026-05-07'),('FAC-2026-0015',1004,15,1000000,'2026-05-08');
/*!40000 ALTER TABLE `venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'ituaccesoriobd'
--

--
-- Dumping routines for database 'ituaccesoriobd'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-13 19:43:02
