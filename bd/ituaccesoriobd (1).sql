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
-- Table structure for table `Cliente`
--

DROP TABLE IF EXISTS `Cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cliente` (
  `ID_cliente` varchar(12) NOT NULL,
  `Direccion_cliente` varchar(40) DEFAULT NULL,
  `Celular_cliente` varchar(15) DEFAULT NULL,
  `Correo_cliente` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Cliente_juridico`
--

DROP TABLE IF EXISTS `Cliente_juridico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cliente_juridico` (
  `ID_cliente` varchar(12) NOT NULL,
  `Razon_social` varchar(60) NOT NULL,
  `Rif_cliente` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`),
  CONSTRAINT `Cliente_juridico_ibfk_1` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `Lista_compra`
--

DROP TABLE IF EXISTS `Lista_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Lista_compra` (
  `ID_lista_compra` varchar(10) NOT NULL,
  `ID_inventario` varchar(10) DEFAULT NULL,
  `ID_cliente` varchar(12) DEFAULT NULL,
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
-- Table structure for table `Orden_servicio`
--

DROP TABLE IF EXISTS `Orden_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Orden_servicio` (
  `ID_orden_servicio` varchar(10) NOT NULL,
  `ID_equipo` varchar(16) DEFAULT NULL,
  `ID_cliente` varchar(12) DEFAULT NULL,
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
-- Table structure for table `Persona_natural`
--

DROP TABLE IF EXISTS `Persona_natural`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Persona_natural` (
  `ID_cliente` varchar(12) NOT NULL,
  `Apellido_cliente` varchar(40) NOT NULL,
  `Nombre_cliente` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`),
  CONSTRAINT `Persona_natural_ibfk_1` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  PRIMARY KEY (`ID_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
-- Table structure for table `Trade_in`
--

DROP TABLE IF EXISTS `Trade_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Trade_in` (
  `ID_Trade_in` varchar(10) NOT NULL,
  `ID_empleado` int DEFAULT NULL,
  `ID_cliente` varchar(12) DEFAULT NULL,
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
-- Table structure for table `Venta`
--

DROP TABLE IF EXISTS `Venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Venta` (
  `ID_factura` varchar(20) NOT NULL,
  `ID_empleado` int DEFAULT NULL,
  `ID_cliente` varchar(12) DEFAULT NULL,
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
-- Dumping events for database 'ituaccesoriobd'
--

--
-- Dumping routines for database 'ituaccesoriobd'
--
/*!50003 DROP PROCEDURE IF EXISTS `Crear_cargo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`user_flask`@`%` PROCEDURE `Crear_cargo`(
IN p_Nombre_cargo VARCHAR(30),
IN p_Descripcion_cargo VARCHAR(250)

)
BEGIN
DECLARE ultimo_id VARCHAR(10);
DECLARE siguiente_numero INT;
DECLARE nuevo_id VARCHAR(10);

-- 1. Buscamos el ID más alto actual en la tabla Cargo
SELECT MAX(`ID_cargo`) INTO ultimo_id FROM `Cargo`;

-- 2. Si la tabla está vacía, empezamos en 1.
--    Si ya hay datos, extraemos los números (desde la posición 4) y sumamos 1.
IF ultimo_id IS NULL THEN
SET siguiente_numero = 1;
ELSE
SET siguiente_numero = CAST(SUBSTRING(ultimo_id, 4) AS UNSIGNED) + 1;
END IF;

-- 3. Formateamos el nuevo ID (Ej: 'CRG' + '000004')
SET nuevo_id = CONCAT('CRG', LPAD(siguiente_numero, 7, '0'));

-- 4. Insertamos el registro
INSERT INTO `Cargo` (`ID_cargo`, `Nombre_cargo`, `Descripcion_cargo`)
VALUES (nuevo_id, p_Nombre_cargo, p_Descripcion_cargo);

-- (Opcional) Mostramos el resultado
SELECT * FROM `Cargo` WHERE `ID_cargo` = nuevo_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Crear_especialidad` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`user_flask`@`%` PROCEDURE `Crear_especialidad`(
IN p_Nombre_especialidad VARCHAR(30),
IN p_Descripcion_especialidad VARCHAR(250)
)
BEGIN
DECLARE ultimo_id VARCHAR(10);
DECLARE siguiente_numero INT;
DECLARE nuevo_id VARCHAR(10);

-- 1. Buscamos el ID más alto actual en la tabla Especialidad
SELECT MAX(`ID_especialidad`) INTO ultimo_id FROM `Especialidad`;

-- 2. Si la tabla está vacía, empezamos en 1.
--    Si ya hay datos, extraemos los números (desde la posición 4) y sumamos 1.
IF ultimo_id IS NULL THEN
SET siguiente_numero = 1;
ELSE
SET siguiente_numero = CAST(SUBSTRING(ultimo_id, 4) AS UNSIGNED) + 1;
END IF;

-- 3. Formateamos el nuevo ID (Ej: 'ESP' + '0000001' = 'ESP0000001')
SET nuevo_id = CONCAT('ESP', LPAD(siguiente_numero, 7, '0'));

-- 4. Insertamos el registro
INSERT INTO `Especialidad` (`ID_especialidad`, `Nombre_especialidad`, `Descripcion_especialidad`)
VALUES (nuevo_id, p_Nombre_especialidad, p_Descripcion_especialidad);

-- 5. Mostramos el resultado del registro creado
SELECT * FROM `Especialidad` WHERE `ID_especialidad` = nuevo_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Listar_ordenes_servicio_con_equipo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`user_flask`@`%` PROCEDURE `Listar_ordenes_servicio_con_equipo`(
-- Parámetros opcionales para filtrar
IN p_ID_orden_servicio VARCHAR(10),
IN p_Estado_orden_servicio VARCHAR(20),
IN p_ID_cliente VARCHAR(10)
)
BEGIN
-- Consulta principal que une Orden_servicio con Equipo y tablas relacionadas
SELECT
-- Datos de la orden de servicio
os.ID_orden_servicio,
os.Estado_orden_servicio,
os.Descripcion_reparacion,
os.Costo_reparacion,
os.Nota_orden_servicio,
os.Fecha_entrada,
os.Fecha_salida,

-- Datos del cliente (a través de Orden_servicio)
os.ID_cliente,
pn.Nombre_cliente,
pn.Apellido_cliente,
c.Celular_cliente,
c.Correo_cliente,
c.Direccion_cliente,

-- Datos del equipo asociado
e.ID_equipo,
e.IMEI,
e.Color,
e.Capacidad,
e.Clave,
e.Patron,

-- Datos del producto (asociado al equipo)
e.ID_producto,
prod.Nombre_producto,
prod.Descripcion,

-- Datos de la clase del producto
cp.Nombre_Clase AS Clase_producto,

-- Datos de la marca
mp.Nombre_marca AS Marca_producto

FROM Orden_servicio os
INNER JOIN Equipo e ON os.ID_equipo = e.ID_equipo
INNER JOIN Producto prod ON e.ID_producto = prod.ID_producto
INNER JOIN Clase_producto cp ON prod.ID_Clase = cp.ID_Clase
INNER JOIN Marca_producto mp ON prod.ID_marca = mp.ID_marca
INNER JOIN Cliente c ON os.ID_cliente = c.ID_cliente
LEFT JOIN Persona_natural pn ON c.ID_cliente = pn.ID_cliente  -- LEFT JOIN porque puede ser cliente jurídico también

WHERE
(p_ID_orden_servicio IS NULL OR os.ID_orden_servicio = p_ID_orden_servicio)
AND (p_Estado_orden_servicio IS NULL OR os.Estado_orden_servicio = p_Estado_orden_servicio)
AND (p_ID_cliente IS NULL OR os.ID_cliente = p_ID_cliente)

ORDER BY os.Fecha_entrada DESC;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_asignar_orden_servicio` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`user_flask`@`%` PROCEDURE `sp_asignar_orden_servicio`(
IN p_ID_orden_servicio VARCHAR(10),
IN p_ID_empleado INT
)
BEGIN
DECLARE v_estado_actual VARCHAR(20);
DECLARE v_tiene_asignacion INT;
DECLARE v_ultimo_id_int VARCHAR(10);
DECLARE v_siguiente_num_int INT;
DECLARE v_nuevo_id_interaccion VARCHAR(10);

-- Manejo de errores
DECLARE EXIT HANDLER FOR SQLEXCEPTION
BEGIN
ROLLBACK;
RESIGNAL;
END;

-- Iniciar transacción
START TRANSACTION;

-- 1. Verificar el estado actual de la orden de servicio
SELECT Estado_orden_servicio INTO v_estado_actual
FROM Orden_servicio
WHERE ID_orden_servicio = p_ID_orden_servicio;

-- Si no existe la orden, mostrar error
IF v_estado_actual IS NULL THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'La orden de servicio no existe';
END IF;

-- Verificar que no esté asignada
IF v_estado_actual = 'Asignada' THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'La orden de servicio ya está asignada';
END IF;

-- 2. Verificar que no exista una interacción con acción 'Asignada' para esta orden
SELECT COUNT(*) INTO v_tiene_asignacion
FROM Interaccion
WHERE ID_orden_servicio = p_ID_orden_servicio
AND Accion = 'Asignada';

IF v_tiene_asignacion > 0 THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'La orden de servicio ya tiene un registro de asignación previa';
END IF;

-- 3. Cambiar el estado de la orden a 'Asignada'
UPDATE Orden_servicio
SET Estado_orden_servicio = 'Asignada'
WHERE ID_orden_servicio = p_ID_orden_servicio;

-- 4. Generar nuevo ID para la interacción
SELECT MAX(ID_interaccion) INTO v_ultimo_id_int FROM Interaccion;

IF v_ultimo_id_int IS NULL THEN
SET v_siguiente_num_int = 1;
ELSE
SET v_siguiente_num_int = CAST(SUBSTRING(v_ultimo_id_int, 4) AS UNSIGNED) + 1;
END IF;

SET v_nuevo_id_interaccion = CONCAT('INT', LPAD(v_siguiente_num_int, 6, '0'));

-- 5. Insertar registro en Interaccion
INSERT INTO Interaccion (ID_interaccion, ID_orden_servicio, ID_empleado, Accion)
VALUES (v_nuevo_id_interaccion, p_ID_orden_servicio, p_ID_empleado, 'Asignada');

-- Confirmar transacción
COMMIT;

-- 6. Devolver resultado
SELECT
p_ID_orden_servicio AS ID_orden_servicio,
'Asignada' AS Nuevo_estado,
v_nuevo_id_interaccion AS ID_interaccion,
'Orden de servicio asignada correctamente' AS Mensaje;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_liberar_orden_servicio` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`user_flask`@`%` PROCEDURE `sp_liberar_orden_servicio`(
IN p_ID_orden_servicio VARCHAR(10),
IN p_ID_empleado INT
)
BEGIN
DECLARE v_estado_actual VARCHAR(20);
DECLARE v_tiene_asignacion INT;

-- Manejo de errores
DECLARE EXIT HANDLER FOR SQLEXCEPTION
BEGIN
ROLLBACK;
RESIGNAL;
END;

-- Iniciar transacción
START TRANSACTION;

-- 1. Verificar el estado actual de la orden de servicio
SELECT Estado_orden_servicio INTO v_estado_actual
FROM Orden_servicio
WHERE ID_orden_servicio = p_ID_orden_servicio;

-- Si no existe la orden, mostrar error
IF v_estado_actual IS NULL THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'La orden de servicio no existe';
END IF;

-- Verificar que esté asignada (solo se puede liberar una orden asignada)
IF v_estado_actual != 'Asignada' THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'La orden de servicio no está asignada, no se puede liberar';
END IF;

-- 2. Verificar que exista una interacción con acción 'Asignada' para esta orden
SELECT COUNT(*) INTO v_tiene_asignacion
FROM Interaccion
WHERE ID_orden_servicio = p_ID_orden_servicio
AND Accion = 'Asignada';

IF v_tiene_asignacion = 0 THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'La orden de servicio no tiene registro de asignación previa';
END IF;

-- 3. Cambiar el estado de la orden a 'En proceso'
UPDATE Orden_servicio
SET Estado_orden_servicio = 'En proceso'
WHERE ID_orden_servicio = p_ID_orden_servicio;

-- 4. Modificar la interacción existente: cambiar acción de 'Asignada' a 'En proceso'
UPDATE Interaccion
SET Accion = 'En proceso'
WHERE ID_orden_servicio = p_ID_orden_servicio
AND Accion = 'Asignada';

-- Confirmar transacción
COMMIT;

-- 5. Devolver resultado
SELECT
p_ID_orden_servicio AS ID_orden_servicio,
'En proceso' AS Nuevo_estado,
'Interacción actualizada correctamente' AS Mensaje;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_obtener_proveedor_completo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `sp_obtener_proveedor_completo`(
    IN p_id_proveedor INT
)
BEGIN
    -- 1. Datos del proveedor
    SELECT 
        ID_proveedor AS id,
        Rif_proveedor AS rif,
        Nombre_proveedor AS nombre,
        Tipo_proveedor AS tipo,
        Celular_proveedor AS celular,
        Correo_proveedor AS correo,
        Direccion_proveedor AS direccion,
        Limite_credito AS limite_credito
    FROM Proveedor
    WHERE ID_proveedor = p_id_proveedor;
    
    -- 2. Productos que suministra
    SELECT 
        s.ID_producto AS id_modelo,
        p.Nombre_producto AS modelo_nombre,
        ma.Nombre_marca AS marca_nombre,
        cl.Nombre_Clase AS clase_nombre,
        s.Costo_producto AS costo
    FROM Suministra s
    JOIN Producto p ON s.ID_producto = p.ID_producto
    JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
    JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
    WHERE s.ID_proveedor = p_id_proveedor
    ORDER BY ma.Nombre_marca ASC, p.Nombre_producto ASC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_registrar_fotos_orden` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`user_flask`@`%` PROCEDURE `sp_registrar_fotos_orden`(
IN p_ID_orden_servicio VARCHAR(10),
IN p_Json_Fotos JSON
)
BEGIN
DECLARE v_ultimo_id_foto VARCHAR(10);
DECLARE v_siguiente_num_foto INT;
DECLARE v_nuevo_id_foto VARCHAR(10);

DECLARE v_items_count INT DEFAULT 0;
DECLARE i INT DEFAULT 0;
DECLARE v_ruta_foto VARCHAR(255);
DECLARE v_orden_existe INT DEFAULT 0;

-- Manejo de errores
DECLARE EXIT HANDLER FOR SQLEXCEPTION
BEGIN
ROLLBACK;
RESIGNAL;
END;

START TRANSACTION;

-- Verificar que la orden existe
SELECT COUNT(*) INTO v_orden_existe
FROM Orden_servicio
WHERE ID_orden_servicio = p_ID_orden_servicio;

IF v_orden_existe = 0 THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'La orden de servicio no existe';
END IF;

-- Validar que el JSON no esté vacío
IF p_Json_Fotos IS NULL OR JSON_LENGTH(p_Json_Fotos) = 0 THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'No se proporcionaron fotos para registrar';
END IF;

SET v_items_count = JSON_LENGTH(p_Json_Fotos);

WHILE i < v_items_count DO
-- Extraer la ruta de la foto del JSON
SET v_ruta_foto = JSON_UNQUOTE(JSON_EXTRACT(p_Json_Fotos, CONCAT('$[', i, ']')));

-- Validar que la ruta no esté vacía
IF v_ruta_foto IS NOT NULL AND v_ruta_foto != '' THEN
-- Generar nuevo ID para la foto
SELECT MAX(`ID_foto_orden_servicio`) INTO v_ultimo_id_foto FROM `Fotos_orden_servicio`;

IF v_ultimo_id_foto IS NULL THEN
SET v_siguiente_num_foto = 1;
ELSE
SET v_siguiente_num_foto = CAST(SUBSTRING(v_ultimo_id_foto, 4) AS UNSIGNED) + 1;
END IF;

SET v_nuevo_id_foto = CONCAT('FOS', LPAD(v_siguiente_num_foto, 6, '0'));

-- Insertar la foto
INSERT INTO `Fotos_orden_servicio` (`ID_foto_orden_servicio`, `ID_orden_servicio`, `Foto_orden_servicio`)
VALUES (v_nuevo_id_foto, p_ID_orden_servicio, v_ruta_foto);
END IF;

SET i = i + 1;
END WHILE;

COMMIT;

-- Devolver resultado
SELECT
p_ID_orden_servicio AS ID_orden_servicio,
v_items_count AS Total_fotos_registradas,
'Fotos registradas exitosamente' AS Mensaje;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_registrar_reparacion` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`user_flask`@`%` PROCEDURE `sp_registrar_reparacion`(
IN p_ID_orden_servicio VARCHAR(10),
IN p_ID_empleado INT,
IN p_Descripcion_reparacion VARCHAR(300),
IN p_Json_Repuestos JSON
)
BEGIN
DECLARE v_estado_actual VARCHAR(20);
DECLARE v_id_interaccion_asignada VARCHAR(10);

DECLARE v_items_count INT DEFAULT 0;
DECLARE i INT DEFAULT 0;
DECLARE v_id_inventario VARCHAR(10);
DECLARE v_cantidad INT;
DECLARE v_existencia_actual INT;
DECLARE v_error_msg VARCHAR(255);

-- Manejador de excepciones mejorado para capturar errores nativos correctamente
DECLARE EXIT HANDLER FOR SQLEXCEPTION
BEGIN
DECLARE v_mysql_error INT;
ROLLBACK;
GET DIAGNOSTICS CONDITION 1
@err_msg = MESSAGE_TEXT,
v_mysql_error = MYSQL_ERRNO;

IF @err_msg IS NULL THEN
SET @err_msg = 'Error desconocido en la base de datos';
ELSE
SET @err_msg = CONCAT('Error (', v_mysql_error, '): ', @err_msg);
END IF;

RESIGNAL SET MESSAGE_TEXT = @err_msg;
END;

START TRANSACTION;

-- Verificar que la orden exista
SELECT Estado_orden_servicio INTO v_estado_actual
FROM Orden_servicio
WHERE ID_orden_servicio = p_ID_orden_servicio;

IF v_estado_actual IS NULL THEN
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La orden de servicio no existe';
END IF;

-- CORRECCIÓN: Permitir que proceda si está en 'Asignada' o 'En proceso'
IF v_estado_actual != 'Asignada' AND v_estado_actual != 'En proceso' THEN
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La orden debe estar en estado Asignada o En proceso';
END IF;

-- CORRECCIÓN: Buscar interacción en estado 'Asignada' o 'En proceso'
SELECT ID_interaccion INTO v_id_interaccion_asignada
FROM Interaccion
WHERE ID_orden_servicio = p_ID_orden_servicio
AND Accion IN ('Asignada', 'En proceso')
ORDER BY ID_interaccion DESC -- Trae la última interacción generada
LIMIT 1;

IF v_id_interaccion_asignada IS NULL THEN
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se encontro una interaccion valida para procesar';
END IF;

-- Actualizar interaccion
UPDATE Interaccion SET Accion = 'Reparada'
WHERE ID_interaccion = v_id_interaccion_asignada;

-- Actualizar orden
UPDATE Orden_servicio
SET Estado_orden_servicio = 'Reparada',
Descripcion_reparacion = p_Descripcion_reparacion,
Fecha_salida = NOW()
WHERE ID_orden_servicio = p_ID_orden_servicio;

-- Procesar repuestos
IF p_Json_Repuestos IS NOT NULL AND JSON_VALID(p_Json_Repuestos) AND JSON_LENGTH(p_Json_Repuestos) > 0 THEN
SET v_items_count = JSON_LENGTH(p_Json_Repuestos);

WHILE i < v_items_count DO
SET v_id_inventario = JSON_UNQUOTE(JSON_EXTRACT(p_Json_Repuestos, CONCAT('$[', i, '].id_inventario')));
SET v_cantidad = JSON_UNQUOTE(JSON_EXTRACT(p_Json_Repuestos, CONCAT('$[', i, '].cantidad')));

IF v_id_inventario IS NULL OR v_id_inventario = '' THEN
SET v_error_msg = CONCAT('Error: No se pudo extraer id_inventario en indice ', i);
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_msg;
END IF;

IF v_cantidad IS NULL OR v_cantidad <= 0 THEN
SET v_error_msg = CONCAT('Cantidad invalida para el repuesto ', v_id_inventario);
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_msg;
END IF;

-- CORRECCIÓN: Se cambió de 'Inventario' a 'Existencias_productos'
SELECT Existencia INTO v_existencia_actual
FROM Existencias_productos
WHERE ID_inventario = v_id_inventario;

IF v_existencia_actual IS NULL THEN
SET v_error_msg = CONCAT('El repuesto con ID ', v_id_inventario, ' no existe en Existencias_productos');
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_msg;
END IF;

IF v_existencia_actual < v_cantidad THEN
SET v_error_msg = CONCAT('Stock insuficiente para ', v_id_inventario,
': disponible ', v_existencia_actual, ', requerido ', v_cantidad);
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_msg;
END IF;

-- NOTA: Asegúrate de tener creada la tabla Repuestos_usados si vas a usar esta sección
INSERT INTO Repuestos_usados (ID_orden_servicio, ID_inventario, Cantidad_usada)
VALUES (p_ID_orden_servicio, v_id_inventario, v_cantidad)
ON DUPLICATE KEY UPDATE Cantidad_usada = Cantidad_usada + v_cantidad;

-- CORRECCIÓN: Descontar stock de la tabla correcta 'Existencias_productos'
UPDATE Existencias_productos
SET Existencia = Existencia - v_cantidad
WHERE ID_inventario = v_id_inventario;

SET i = i + 1;
END WHILE;
END IF;

COMMIT;

SELECT
p_ID_orden_servicio AS ID_orden_servicio,
'Reparada' AS Nuevo_estado,
v_id_interaccion_asignada AS ID_interaccion_actualizada,
p_Descripcion_reparacion AS Descripcion_reparacion,
IFNULL(v_items_count, 0) AS Total_repuestos_usados,
'Orden reparada exitosamente' AS Mensaje;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_registrar_revision_test` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`user_flask`@`%` PROCEDURE `sp_registrar_revision_test`(
IN p_ID_orden_servicio VARCHAR(10),
IN p_ID_empleado INT,
IN p_Num_test INT,            -- El número identificador del lote de test
IN p_Json_Tests JSON          -- El arreglo: [{"nombre":"Mica", "resultado":"Funciona"}, ...]
)
BEGIN
-- Variables para generar ID_interaccion (Formato 'INT0000001')
DECLARE v_ultimo_id_int VARCHAR(10);
DECLARE v_siguiente_num_int INT;
DECLARE v_nuevo_id_interaccion VARCHAR(10);

-- Variables para generar ID_test dentro del ciclo (Formato 'TST0000001')
DECLARE v_ultimo_id_tes VARCHAR(10);
DECLARE v_siguiente_num_tes INT;
DECLARE v_nuevo_id_test VARCHAR(10);

-- Variables para el control del Ciclo Repetitivo (Bucle WHILE)
DECLARE v_items_count INT DEFAULT 0;
DECLARE i INT DEFAULT 0;
DECLARE v_nombre_comp VARCHAR(50);
DECLARE v_resultado_comp VARCHAR(300);

-- Manejo de errores: Si algo falla, deshace todo (Rollback)
DECLARE EXIT HANDLER FOR SQLEXCEPTION
BEGIN
ROLLBACK;
RESIGNAL;
END;

-- Iniciamos la transacción segura
START TRANSACTION;

-- =========================================================================
-- PASO 1: INSERTAR EN LA TABLA Interaccion CON ID AUTOGENERADO
-- =========================================================================
SELECT MAX(`ID_interaccion`) INTO v_ultimo_id_int FROM `Interaccion`;

IF v_ultimo_id_int IS NULL THEN
SET v_siguiente_num_int = 1;
ELSE
SET v_siguiente_num_int = CAST(SUBSTRING(v_ultimo_id_int, 4) AS UNSIGNED) + 1;
END IF;

SET v_nuevo_id_interaccion = CONCAT('INT', LPAD(v_siguiente_num_int, 6, '0'));

-- Registro inicial requerido
INSERT INTO `Interaccion` (`ID_interaccion`, `ID_orden_servicio`, `ID_empleado`, `Accion`)
VALUES (v_nuevo_id_interaccion, p_ID_orden_servicio, p_ID_empleado, 'Revisión');


-- =========================================================================
-- PASO 2: CICLO REPETITIVO PARA PROCESAR EL ARREGLO E INSERTAR EN Test Y LA INTERMEDIA
-- =========================================================================
SET v_items_count = JSON_LENGTH(p_Json_Tests);

WHILE i < v_items_count DO
-- 2.1 Extraer los datos del componente actual del lote JSON
SET v_nombre_comp = JSON_UNQUOTE(JSON_EXTRACT(p_Json_Tests, CONCAT('$[', i, '].nombre')));
SET v_resultado_comp = JSON_UNQUOTE(JSON_EXTRACT(p_Json_Tests, CONCAT('$[', i, '].resultado')));

-- 2.2 Generar el ID_test dinámico (Formato 'TST0000001') para este componente específico
SELECT MAX(`ID_test`) INTO v_ultimo_id_tes FROM `Test`;

IF v_ultimo_id_tes IS NULL THEN
SET v_siguiente_num_tes = 1;
ELSE
SET v_siguiente_num_tes = CAST(SUBSTRING(v_ultimo_id_tes, 4) AS UNSIGNED) + 1;
END IF;

SET v_nuevo_id_test = CONCAT('TST', LPAD(v_siguiente_num_tes, 6, '0'));

-- 2.3 Insertar el registro en la tabla Test usando los nombres correctos de columnas
-- CORREGIDO: Usar 'Num_test' (parámetro) y 'Resultado_test' (columna correcta)
INSERT INTO `Test` (`ID_test`, `Numero_test`, `Nombre_test`, `Resultado_test`)
VALUES (v_nuevo_id_test, p_Num_test, v_nombre_comp, v_resultado_comp);

-- 2.4 Insertar la relación de los códigos en la tabla Test_realizados_interaccion
INSERT INTO `Test_realizados_interaccion` (`ID_interaccion`, `ID_test`)
VALUES (v_nuevo_id_interaccion, v_nuevo_id_test);

-- Avanzar al siguiente elemento del arreglo
SET i = i + 1;
END WHILE;

-- Guardar de manera permanente todos los cambios
COMMIT;

-- Devolver resumen para tu backend
SELECT v_nuevo_id_interaccion AS `ID_interaccion`, v_items_count AS `Total_tests`;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_registrar_trade_in_con_tests` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_registrar_trade_in_con_tests`(
    IN p_ID_empleado INT,
    IN p_ID_cliente VARCHAR(12),
    IN p_ID_producto VARCHAR(10),
    IN p_ID_equipo VARCHAR(16),
    IN p_Color VARCHAR(20),
    IN p_Capacidad VARCHAR(20),
    IN p_Clave INT,
    IN p_Patron VARCHAR(60),
    IN p_Valor_pagado DECIMAL(10,2),
    IN p_Observaciones VARCHAR(300),
    IN p_Json_Fotos JSON,
    IN p_Json_Tests JSON
)
BEGIN
    DECLARE v_trade_in_id VARCHAR(10);
    DECLARE v_ultimo_id VARCHAR(10);
    DECLARE v_siguiente_num INT;
    DECLARE v_items_count INT DEFAULT 0;
    DECLARE i INT DEFAULT 0;
    DECLARE v_foto_url VARCHAR(255);
    DECLARE v_nombre_test VARCHAR(30);
    DECLARE v_resultado_test VARCHAR(300);
    DECLARE v_ultimo_id_test VARCHAR(10);
    DECLARE v_siguiente_num_test INT;
    DECLARE v_nuevo_id_test VARCHAR(10);
    DECLARE v_foto_id VARCHAR(10);
    DECLARE v_ultimo_id_foto VARCHAR(10);
    DECLARE v_siguiente_num_foto INT;

    -- Manejo de errores
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- 1. Verificar si el equipo ya existe
    IF EXISTS (SELECT 1 FROM Equipo WHERE ID_equipo = p_ID_equipo) THEN
        -- Actualizar equipo existente
        UPDATE Equipo 
        SET ID_producto = p_ID_producto,
            Color = COALESCE(p_Color, Color),
            Capacidad = COALESCE(p_Capacidad, Capacidad),
            Clave = COALESCE(p_Clave, Clave),
            Patron = COALESCE(p_Patron, Patron)
        WHERE ID_equipo = p_ID_equipo;
    ELSE
        -- Crear nuevo equipo
        INSERT INTO Equipo (ID_equipo, ID_producto, Color, Capacidad, Clave, Patron)
        VALUES (p_ID_equipo, p_ID_producto, p_Color, p_Capacidad, p_Clave, p_Patron);
    END IF;

    -- 2. Generar ID para Trade_in
    SELECT MAX(ID_Trade_in) INTO v_ultimo_id FROM Trade_in;
    IF v_ultimo_id IS NULL THEN
        SET v_siguiente_num = 1;
    ELSE
        SET v_siguiente_num = CAST(SUBSTRING(v_ultimo_id, 4) AS UNSIGNED) + 1;
    END IF;
    SET v_trade_in_id = CONCAT('TRD', LPAD(v_siguiente_num, 6, '0'));

    -- 3. Insertar Trade_in
    INSERT INTO Trade_in (ID_Trade_in, ID_empleado, ID_cliente, ID_equipo, Numero_utilizado, Fecha_realizado, cotizacion)
    VALUES (v_trade_in_id, p_ID_empleado, p_ID_cliente, p_ID_equipo, 0, NOW(), p_Valor_pagado);

    -- 4. Guardar fotos
    IF p_Json_Fotos IS NOT NULL AND JSON_LENGTH(p_Json_Fotos) > 0 THEN
        SET v_items_count = JSON_LENGTH(p_Json_Fotos);
        SET i = 0;
        
        WHILE i < v_items_count DO
            SET v_foto_url = JSON_UNQUOTE(JSON_EXTRACT(p_Json_Fotos, CONCAT('$[', i, ']')));
            
            -- Generar ID para foto
            SELECT MAX(ID_foto_trade_in) INTO v_ultimo_id_foto FROM Fotos_trade_in;
            IF v_ultimo_id_foto IS NULL THEN
                SET v_siguiente_num_foto = 1;
            ELSE
                SET v_siguiente_num_foto = CAST(SUBSTRING(v_ultimo_id_foto, 4) AS UNSIGNED) + 1;
            END IF;
            SET v_foto_id = CONCAT('FTI', LPAD(v_siguiente_num_foto, 7, '0'));
            
            INSERT INTO Fotos_trade_in (ID_foto_trade_in, ID_Trade_in, Foto_trade_in)
            VALUES (v_foto_id, v_trade_in_id, v_foto_url);
            
            SET i = i + 1;
        END WHILE;
    END IF;

    -- 5. Guardar tests
    IF p_Json_Tests IS NOT NULL AND JSON_LENGTH(p_Json_Tests) > 0 THEN
        SET v_items_count = JSON_LENGTH(p_Json_Tests);
        SET i = 0;
        
        WHILE i < v_items_count DO
            SET v_nombre_test = JSON_UNQUOTE(JSON_EXTRACT(p_Json_Tests, CONCAT('$[', i, '].nombre')));
            SET v_resultado_test = JSON_UNQUOTE(JSON_EXTRACT(p_Json_Tests, CONCAT('$[', i, '].resultado')));
            
            -- Generar ID para test
            SELECT MAX(ID_test) INTO v_ultimo_id_test FROM Test;
            IF v_ultimo_id_test IS NULL THEN
                SET v_siguiente_num_test = 1;
            ELSE
                SET v_siguiente_num_test = CAST(SUBSTRING(v_ultimo_id_test, 4) AS UNSIGNED) + 1;
            END IF;
            SET v_nuevo_id_test = CONCAT('TST', LPAD(v_siguiente_num_test, 6, '0'));
            
            INSERT INTO Test (ID_test, Numero_test, Nombre_test, Resultado_test)
            VALUES (v_nuevo_id_test, 1, v_nombre_test, v_resultado_test);
            
            INSERT INTO Test_realizados_trade_in (ID_Trade_in, ID_test)
            VALUES (v_trade_in_id, v_nuevo_id_test);
            
            SET i = i + 1;
        END WHILE;
    END IF;

    COMMIT;

    -- Devolver resultado
    SELECT v_trade_in_id AS trade_in_id, 'Trade-in registrado exitosamente' AS mensaje;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_verificar_stock_producto` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `sp_verificar_stock_producto`(
    IN p_id_producto VARCHAR(10),
    OUT p_stock_total INT,
    OUT p_tiene_stock BOOLEAN
)
BEGIN
    SELECT COALESCE(SUM(Existencia), 0) INTO p_stock_total
    FROM Existencias_productos
    WHERE ID_producto = p_id_producto;
    
    SET p_tiene_stock = (p_stock_total > 0);
    
    -- También devolver el detalle
    SELECT 
        ID_inventario,
        Existencia,
        Costo_venta
    FROM Existencias_productos
    WHERE ID_producto = p_id_producto
    AND Existencia > 0;
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

-- Dump completed on 2026-08-17 12:24:31
