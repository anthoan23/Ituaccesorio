-- ============================================================
-- ESQUEMA + DATOS DE PRUEBA: ituaccesoriobd (BD principal)
-- ============================================================
-- BD principal de PRUEBAS ya llena con los datos de prueba.
-- docker-compose.test.yml monta este archivo como 01-init.sql en
-- docker-entrypoint-initdb.d: se aplica al crear el volumen.
--
-- Estructura del archivo:
--   1. TABLAS (DDL sin filas)
--   2. VISTAS
--   3. PROCEDIMIENTOS ALMACENADOS
--   4. DATOS DE PRUEBA (al final: limpieza + catálogos base)
--
-- Generado a partir de bd/ituaccesoriobd.sql (backup de la app).
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT=0;
SET SQL_QUOTE_SHOW_CREATE=1;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT=0;
SET SQL_QUOTE_SHOW_CREATE=1;

-- ============================================
-- TABLAS
-- ============================================

-- ----------------------------------------------------
-- Table structure for `Abastece`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Abastece`;
CREATE TABLE `Abastece` (
  `ID_entrega_inventario` varchar(10) NOT NULL,
  `ID_inventario` varchar(10) NOT NULL,
  `Cantidad_entregada` int NOT NULL,
  PRIMARY KEY (`ID_entrega_inventario`,`ID_inventario`),
  KEY `ID_existencia` (`ID_inventario`),
  CONSTRAINT `Abastece_ibfk_1` FOREIGN KEY (`ID_entrega_inventario`) REFERENCES `Entrega_inventario` (`ID_entrega_inventario`) ON DELETE CASCADE,
  CONSTRAINT `Abastece_ibfk_2` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Capacitacion`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Capacitacion`;
CREATE TABLE `Capacitacion` (
  `ID_empleado` int NOT NULL,
  `ID_especialidad` varchar(10) NOT NULL,
  `Nivel_Capacitacion` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID_empleado`,`ID_especialidad`),
  KEY `ID_especialidad` (`ID_especialidad`),
  CONSTRAINT `Capacitacion_ibfk_1` FOREIGN KEY (`ID_empleado`) REFERENCES `Empleado` (`ID_empleado`),
  CONSTRAINT `Capacitacion_ibfk_2` FOREIGN KEY (`ID_especialidad`) REFERENCES `Especialidad` (`ID_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Cargo`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Cargo`;
CREATE TABLE `Cargo` (
  `ID_cargo` varchar(10) NOT NULL,
  `Nombre_cargo` varchar(30) NOT NULL,
  `Descripcion_cargo` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`ID_cargo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Categoria`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Categoria`;
CREATE TABLE `Categoria` (
  `ID_categoria` int NOT NULL AUTO_INCREMENT,
  `Nombre_categoria` varchar(30) NOT NULL,
  PRIMARY KEY (`ID_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Clase_producto`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Clase_producto`;
CREATE TABLE `Clase_producto` (
  `ID_Clase` varchar(10) NOT NULL,
  `Nombre_Clase` varchar(30) NOT NULL,
  PRIMARY KEY (`ID_Clase`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Cliente`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Cliente`;
CREATE TABLE `Cliente` (
  `ID_cliente` varchar(12) NOT NULL,
  `Direccion_cliente` varchar(40) DEFAULT NULL,
  `Celular_cliente` varchar(15) DEFAULT NULL,
  `Correo_cliente` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Cliente_juridico`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Cliente_juridico`;
CREATE TABLE `Cliente_juridico` (
  `ID_cliente` varchar(12) NOT NULL,
  `Razon_social` varchar(60) NOT NULL,
  `Rif_cliente` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`),
  CONSTRAINT `Cliente_juridico_ibfk_1` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Credito`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Credito`;
CREATE TABLE `Credito` (
  `ID_credito` varchar(10) NOT NULL,
  `ID_orden_compra` varchar(10) DEFAULT NULL,
  `Dias_credito` int DEFAULT NULL,
  `Monto_credito` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_credito`),
  KEY `ID_orden_compra` (`ID_orden_compra`),
  CONSTRAINT `Credito_ibfk_1` FOREIGN KEY (`ID_orden_compra`) REFERENCES `Orden_compra` (`ID_orden_compra`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Detalle_orden`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Detalle_orden`;
CREATE TABLE `Detalle_orden` (
  `ID_orden_compra` varchar(10) NOT NULL,
  `ID_producto` varchar(10) NOT NULL,
  `Cantidad_producto` int DEFAULT NULL,
  PRIMARY KEY (`ID_orden_compra`,`ID_producto`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `Detalle_orden_ibfk_1` FOREIGN KEY (`ID_orden_compra`) REFERENCES `Orden_compra` (`ID_orden_compra`),
  CONSTRAINT `Detalle_orden_ibfk_2` FOREIGN KEY (`ID_producto`) REFERENCES `Producto` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Detalle_venta`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Detalle_venta`;
CREATE TABLE `Detalle_venta` (
  `ID_inventario` varchar(10) NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  `Cantidad_articulo` int DEFAULT NULL,
  PRIMARY KEY (`ID_inventario`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `Detalle_venta_ibfk_1` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`),
  CONSTRAINT `Detalle_venta_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `Venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Empleado`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Empleado`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Entrega`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Entrega`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Entrega_inventario`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Entrega_inventario`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Equipo`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Equipo`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Especialidad`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Especialidad`;
CREATE TABLE `Especialidad` (
  `ID_especialidad` varchar(10) NOT NULL,
  `Nombre_especialidad` varchar(30) NOT NULL,
  `Descripcion_especialidad` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`ID_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Existencias_productos`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Existencias_productos`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Fotos_inventario`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Fotos_inventario`;
CREATE TABLE `Fotos_inventario` (
  `ID_foto_inventario` varchar(10) NOT NULL,
  `ID_inventario` varchar(10) DEFAULT NULL,
  `Foto_inventario` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_foto_inventario`),
  KEY `ID_inventario` (`ID_inventario`),
  CONSTRAINT `Fotos_inventario_ibfk_1` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Fotos_orden_servicio`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Fotos_orden_servicio`;
CREATE TABLE `Fotos_orden_servicio` (
  `ID_foto_orden_servicio` varchar(10) NOT NULL,
  `ID_orden_servicio` varchar(10) DEFAULT NULL,
  `Foto_orden_servicio` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_foto_orden_servicio`),
  KEY `ID_orden_servicio` (`ID_orden_servicio`),
  CONSTRAINT `Fotos_orden_servicio_ibfk_1` FOREIGN KEY (`ID_orden_servicio`) REFERENCES `Orden_servicio` (`ID_orden_servicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Fotos_trade_in`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Fotos_trade_in`;
CREATE TABLE `Fotos_trade_in` (
  `ID_foto_trade_in` varchar(10) NOT NULL,
  `ID_Trade_in` varchar(10) DEFAULT NULL,
  `Foto_trade_in` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_foto_trade_in`),
  KEY `ID_Trade_in` (`ID_Trade_in`),
  CONSTRAINT `Fotos_trade_in_ibfk_1` FOREIGN KEY (`ID_Trade_in`) REFERENCES `Trade_in` (`ID_Trade_in`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Interaccion`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Interaccion`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Lista_compra`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Lista_compra`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Marca_producto`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Marca_producto`;
CREATE TABLE `Marca_producto` (
  `ID_marca` varchar(10) NOT NULL,
  `Nombre_marca` varchar(30) NOT NULL,
  PRIMARY KEY (`ID_marca`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Metodo_pago`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Metodo_pago`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Orden_compra`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Orden_compra`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Orden_servicio`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Orden_servicio`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Pago_servicio`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Pago_servicio`;
CREATE TABLE `Pago_servicio` (
  `ID_orden_servicio` varchar(10) NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_orden_servicio`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `Pago_servicio_ibfk_1` FOREIGN KEY (`ID_orden_servicio`) REFERENCES `Orden_servicio` (`ID_orden_servicio`),
  CONSTRAINT `Pago_servicio_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `Venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Persona_natural`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Persona_natural`;
CREATE TABLE `Persona_natural` (
  `ID_cliente` varchar(12) NOT NULL,
  `Apellido_cliente` varchar(40) NOT NULL,
  `Nombre_cliente` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID_cliente`),
  CONSTRAINT `Persona_natural_ibfk_1` FOREIGN KEY (`ID_cliente`) REFERENCES `Cliente` (`ID_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Personal_delivery`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Personal_delivery`;
CREATE TABLE `Personal_delivery` (
  `Cedula_delivery` varchar(15) NOT NULL,
  `Nombre_delivery` varchar(40) NOT NULL,
  `Apellido_delivery` varchar(40) NOT NULL,
  PRIMARY KEY (`Cedula_delivery`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Producto`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Producto`;
CREATE TABLE `Producto` (
  `ID_producto` varchar(10) NOT NULL,
  `ID_Clase` varchar(10) DEFAULT NULL,
  `ID_marca` varchar(10) DEFAULT NULL,
  `Nombre_producto` varchar(50) NOT NULL,
  `Descripcion` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID_producto`),
  KEY `ID_Clase` (`ID_Clase`),
  KEY `ID_marca` (`ID_marca`),
  CONSTRAINT `Producto_ibfk_1` FOREIGN KEY (`ID_Clase`) REFERENCES `Clase_producto` (`ID_Clase`),
  CONSTRAINT `Producto_ibfk_2` FOREIGN KEY (`ID_marca`) REFERENCES `Marca_producto` (`ID_marca`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Proveedor`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Proveedor`;
CREATE TABLE `Proveedor` (
  `ID_proveedor` int NOT NULL,
  `RIF_proveedor` varchar(15) DEFAULT NULL,
  `Nombre_proveedor` varchar(40) NOT NULL,
  `Tipo_proveedor` varchar(20) DEFAULT NULL,
  `Celular_proveedor` varchar(15) DEFAULT NULL,
  `Correo_proveedor` varchar(120) DEFAULT NULL,
  `Direccion_proveedor` varchar(60) DEFAULT NULL,
  `Limite_credito` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Repuestos_usados`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Repuestos_usados`;
CREATE TABLE `Repuestos_usados` (
  `ID_orden_servicio` varchar(10) NOT NULL,
  `ID_inventario` varchar(10) NOT NULL,
  `Cantidad_usada` int NOT NULL,
  PRIMARY KEY (`ID_orden_servicio`,`ID_inventario`),
  KEY `ID_inventario` (`ID_inventario`),
  CONSTRAINT `Repuestos_usados_ibfk_1` FOREIGN KEY (`ID_orden_servicio`) REFERENCES `Orden_servicio` (`ID_orden_servicio`),
  CONSTRAINT `Repuestos_usados_ibfk_2` FOREIGN KEY (`ID_inventario`) REFERENCES `Existencias_productos` (`ID_inventario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Suministra`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Suministra`;
CREATE TABLE `Suministra` (
  `ID_proveedor` int NOT NULL,
  `ID_producto` varchar(10) NOT NULL,
  `Costo_producto` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_proveedor`,`ID_producto`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `Suministra_ibfk_1` FOREIGN KEY (`ID_proveedor`) REFERENCES `Proveedor` (`ID_proveedor`),
  CONSTRAINT `Suministra_ibfk_2` FOREIGN KEY (`ID_producto`) REFERENCES `Producto` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Test`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Test`;
CREATE TABLE `Test` (
  `ID_test` varchar(10) NOT NULL,
  `Numero_test` int DEFAULT NULL,
  `Nombre_test` varchar(30) NOT NULL,
  `Resultado_test` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------


-- ----------------------------------------------------
-- Table structure for `Test_realizados_interaccion`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Test_realizados_interaccion`;
CREATE TABLE `Test_realizados_interaccion` (
  `ID_interaccion` varchar(10) NOT NULL,
  `ID_test` varchar(10) NOT NULL,
  PRIMARY KEY (`ID_interaccion`,`ID_test`),
  KEY `ID_test` (`ID_test`),
  CONSTRAINT `Test_realizados_interaccion_ibfk_1` FOREIGN KEY (`ID_interaccion`) REFERENCES `Interaccion` (`ID_interaccion`),
  CONSTRAINT `Test_realizados_interaccion_ibfk_2` FOREIGN KEY (`ID_test`) REFERENCES `Test` (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------


-- ----------------------------------------------------
-- Table structure for `Test_realizados_trade_in`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Test_realizados_trade_in`;
CREATE TABLE `Test_realizados_trade_in` (
  `ID_Trade_in` varchar(10) NOT NULL,
  `ID_test` varchar(10) NOT NULL,
  PRIMARY KEY (`ID_Trade_in`,`ID_test`),
  KEY `ID_test` (`ID_test`),
  CONSTRAINT `Test_realizados_trade_in_ibfk_1` FOREIGN KEY (`ID_Trade_in`) REFERENCES `Trade_in` (`ID_Trade_in`),
  CONSTRAINT `Test_realizados_trade_in_ibfk_2` FOREIGN KEY (`ID_test`) REFERENCES `Test` (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Trade_in`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Trade_in`;
CREATE TABLE `Trade_in` (
  `ID_Trade_in` varchar(10) NOT NULL,
  `ID_empleado` int DEFAULT NULL,
  `ID_cliente` varchar(12) DEFAULT NULL,
  `ID_inventario` varchar(10) DEFAULT NULL,
  `ID_equipo` varchar(16) DEFAULT NULL,
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

-- ----------------------------------------------------
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `Venta`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `Venta`;
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

-- ----------------------------------------------------
-- ----------------------------------------------------


-- ============================================
-- VISTAS
-- ============================================


-- ============================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================

-- ----------------------------------------------------
-- Procedure structure for `Crear_cargo`
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `Crear_cargo`;
DELIMITER ;;
CREATE PROCEDURE `Crear_cargo`(
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

-- ----------------------------------------------------
-- Procedure structure for `Crear_especialidad`
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `Crear_especialidad`;
DELIMITER ;;
CREATE PROCEDURE `Crear_especialidad`(
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

-- ----------------------------------------------------
-- Procedure structure for `sp_asignar_orden_servicio`
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_asignar_orden_servicio`;
DELIMITER ;;
CREATE PROCEDURE `sp_asignar_orden_servicio`(
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

-- ----------------------------------------------------
-- Procedure structure for `sp_liberar_orden_servicio`
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_liberar_orden_servicio`;
DELIMITER ;;
CREATE PROCEDURE `sp_liberar_orden_servicio`(
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

-- ----------------------------------------------------
-- Procedure structure for `sp_registrar_fotos_orden`
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_registrar_fotos_orden`;
DELIMITER ;;
CREATE PROCEDURE `sp_registrar_fotos_orden`(
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

-- ----------------------------------------------------
-- Procedure structure for `sp_registrar_reparacion`
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_registrar_reparacion`;
DELIMITER ;;
CREATE PROCEDURE `sp_registrar_reparacion`(
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

-- ----------------------------------------------------
-- Procedure structure for `sp_registrar_revision_test`
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_registrar_revision_test`;
DELIMITER ;;
CREATE PROCEDURE `sp_registrar_revision_test`(
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


-- ----------------------------------------------------
-- Procedure: sp_registrar_producto
-- Registra un producto con validaciones y genera su ID
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_registrar_producto`;
DELIMITER ;;
CREATE PROCEDURE `sp_registrar_producto`(
    IN p_id_clase VARCHAR(10),
    IN p_id_marca VARCHAR(10),
    IN p_nombre_producto VARCHAR(50),
    IN p_descripcion VARCHAR(300),
    OUT p_id_producto VARCHAR(10),
    OUT p_estado VARCHAR(20),
    OUT p_mensaje VARCHAR(255)
)
BEGIN
    DECLARE v_existe_clase INT DEFAULT 0;
    DECLARE v_existe_marca INT DEFAULT 0;
    DECLARE v_existe_producto INT DEFAULT 0;
    DECLARE v_siguiente_num INT DEFAULT 0;
    DECLARE v_nuevo_id VARCHAR(10);
    DECLARE v_sqlstate CHAR(5) DEFAULT '';
    DECLARE v_sqlmsg TEXT DEFAULT '';

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_sqlstate = RETURNED_SQLSTATE,
            v_sqlmsg = MESSAGE_TEXT;
        ROLLBACK;
        SET p_id_producto = NULL;
        SET p_estado = 'ERROR';
        SET p_mensaje = COALESCE(NULLIF(TRIM(v_sqlmsg), ''), 'No se pudo registrar el producto');
    END;

    SET p_id_producto = NULL;
    SET p_estado = 'ERROR';
    SET p_mensaje = '';

    -- Validaciones básicas
    IF p_id_clase IS NULL OR TRIM(p_id_clase) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La clase del producto es obligatoria';
    END IF;

    IF p_id_marca IS NULL OR TRIM(p_id_marca) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La marca del producto es obligatoria';
    END IF;

    IF p_nombre_producto IS NULL OR TRIM(p_nombre_producto) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El nombre del producto es obligatorio';
    END IF;

    -- Validar que existan clase y marca
    SELECT COUNT(*) INTO v_existe_clase
    FROM Clase_producto
    WHERE ID_Clase = p_id_clase;

    IF v_existe_clase = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La clase indicada no existe';
    END IF;

    SELECT COUNT(*) INTO v_existe_marca
    FROM Marca_producto
    WHERE ID_marca = p_id_marca;

    IF v_existe_marca = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La marca indicada no existe';
    END IF;

    -- Validar producto duplicado
    SELECT COUNT(*) INTO v_existe_producto
    FROM Producto
    WHERE LOWER(TRIM(Nombre_producto)) = LOWER(TRIM(p_nombre_producto))
      AND ID_Clase = p_id_clase
      AND ID_marca = p_id_marca;

    IF v_existe_producto > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ya existe un producto con ese nombre, clase y marca';
    END IF;

    START TRANSACTION;

    -- Generar ID secuencial compatible con el modelo actual
    SELECT COALESCE(MAX(CAST(ID_producto AS UNSIGNED)), 0) + 1
    INTO v_siguiente_num
    FROM Producto;

    SET v_nuevo_id = CAST(v_siguiente_num AS CHAR);

    INSERT INTO Producto (
        ID_producto,
        ID_Clase,
        ID_marca,
        Nombre_producto,
        Descripcion
    ) VALUES (
        v_nuevo_id,
        p_id_clase,
        p_id_marca,
        TRIM(p_nombre_producto),
        NULLIF(TRIM(p_descripcion), '')
    );

    SET p_id_producto = v_nuevo_id;
    SET p_estado = 'OK';
    SET p_mensaje = 'Producto registrado correctamente';

    COMMIT;

    SELECT
        p_id_producto AS id_producto,
        p_estado AS estado,
        p_mensaje AS mensaje;
END ;;
DELIMITER ;

-- ----------------------------------------------------
-- Procedure: sp_registrar_proveedor
-- Registra un proveedor con validaciones y genera su ID
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_registrar_proveedor`;
DELIMITER ;;
CREATE PROCEDURE `sp_registrar_proveedor`(
    IN p_rif VARCHAR(50),
    IN p_nombre VARCHAR(255),
    IN p_tipo VARCHAR(50),
    IN p_celular VARCHAR(50),
    IN p_correo VARCHAR(200),
    IN p_direccion TEXT,
    IN p_limite_credito DECIMAL(12,2),
    OUT p_id_proveedor INT,
    OUT p_estado VARCHAR(20),
    OUT p_mensaje VARCHAR(255)
)
BEGIN
    DECLARE v_existe_nombre INT DEFAULT 0;
    DECLARE v_existe_rif INT DEFAULT 0;
    DECLARE v_siguiente_id INT DEFAULT 0;
    DECLARE v_nombre_limpio VARCHAR(255);
    DECLARE v_rif_limpio VARCHAR(50);

    SET p_id_proveedor = 0;
    SET p_estado = 'ERROR';
    SET p_mensaje = '';

    SET v_nombre_limpio = TRIM(COALESCE(p_nombre, ''));
    SET v_rif_limpio = TRIM(COALESCE(p_rif, ''));

    IF v_nombre_limpio = '' THEN
        SET p_mensaje = 'El nombre del proveedor es obligatorio.';
    ELSEIF p_limite_credito IS NOT NULL AND p_limite_credito < 0 THEN
        SET p_mensaje = 'El límite de crédito no puede ser negativo.';
    END IF;

    IF p_mensaje = '' THEN
        SELECT COUNT(*)
        INTO v_existe_nombre
        FROM Proveedor
        WHERE LOWER(TRIM(Nombre_proveedor)) = LOWER(v_nombre_limpio);

        IF v_existe_nombre > 0 THEN
            SET p_mensaje = CONCAT('Ya existe un proveedor con el nombre ''', v_nombre_limpio, '''.');
        END IF;
    END IF;

    IF p_mensaje = '' AND v_rif_limpio != '' THEN
        SELECT COUNT(*)
        INTO v_existe_rif
        FROM Proveedor
        WHERE LOWER(TRIM(RIF_proveedor)) = LOWER(v_rif_limpio);

        IF v_existe_rif > 0 THEN
            SET p_mensaje = CONCAT('Ya existe un proveedor con el RIF ''', v_rif_limpio, '''.');
        END IF;
    END IF;

    IF p_mensaje = '' THEN
        SELECT COALESCE(MAX(CAST(ID_proveedor AS UNSIGNED)), 0) + 1
        INTO v_siguiente_id
        FROM Proveedor;

        INSERT INTO Proveedor (
            ID_proveedor,
            RIF_proveedor,
            Nombre_proveedor,
            Tipo_proveedor,
            Celular_proveedor,
            Correo_proveedor,
            Direccion_proveedor,
            Limite_credito
        ) VALUES (
            v_siguiente_id,
            CASE WHEN v_rif_limpio = '' THEN NULL ELSE v_rif_limpio END,
            v_nombre_limpio,
            CASE WHEN TRIM(COALESCE(p_tipo, '')) = '' THEN NULL ELSE TRIM(p_tipo) END,
            CASE WHEN TRIM(COALESCE(p_celular, '')) = '' THEN NULL ELSE TRIM(p_celular) END,
            CASE WHEN TRIM(COALESCE(p_correo, '')) = '' THEN NULL ELSE TRIM(p_correo) END,
            CASE WHEN TRIM(COALESCE(p_direccion, '')) = '' THEN NULL ELSE p_direccion END,
            CASE WHEN p_limite_credito IS NULL THEN 0 ELSE p_limite_credito END
        );

        SET p_id_proveedor = v_siguiente_id;
        SET p_estado = 'OK';
        SET p_mensaje = 'Proveedor registrado correctamente.';
    END IF;
END ;;
DELIMITER ;


-- ============================================
-- FUNCIONES
-- ============================================


-- ============================================
-- TRIGGERS
-- ============================================

-- ----------------------------------------------------
-- Trigger: after_trade_in_insert
-- Al registrar un trade-in, suma el equipo al inventario
-- (o crea su registro de inventario si no existe)
-- ----------------------------------------------------
DROP TRIGGER IF EXISTS `after_trade_in_insert`;
DELIMITER ;;
CREATE TRIGGER `after_trade_in_insert`
AFTER INSERT ON `Trade_in`
FOR EACH ROW
BEGIN
    DECLARE v_id_producto VARCHAR(10);
    DECLARE v_existencia_actual INT;
    DECLARE v_nuevo_id_inv VARCHAR(10);

    -- 1. Obtener el ID del producto
    SELECT ID_producto INTO v_id_producto
    FROM Equipo
    WHERE ID_equipo = NEW.ID_equipo;

    IF v_id_producto IS NOT NULL AND NEW.Numero_utilizado > 0 THEN

        -- Verificar si ya existe en el inventario
        SELECT Existencia INTO v_existencia_actual
        FROM Existencias_productos
        WHERE ID_producto = v_id_producto 
        LIMIT 1;

        IF v_existencia_actual IS NOT NULL THEN
            UPDATE Existencias_productos
            SET Existencia = Existencia + NEW.Numero_utilizado
            WHERE ID_producto = v_id_producto;
        ELSE
            -- Generar el ID_inventario secuencial
            SELECT CONCAT('INV', LPAD(
                COALESCE(
                    MAX(CAST(SUBSTRING(ID_inventario, 4) AS UNSIGNED)), 0
                ) + 1, 6, '0'
            )) INTO v_nuevo_id_inv
            FROM Existencias_productos;

            -- Insertar el equipo recibido como inventario
            -- (ID_categoria queda NULL, igual que el resto de la app)
            INSERT INTO Existencias_productos (
                ID_inventario,
                ID_producto,
                Existencia,
                Costo_venta,
                ID_categoria
            ) VALUES (
                v_nuevo_id_inv,
                v_id_producto,
                NEW.Numero_utilizado,
                COALESCE(NEW.cotizacion, 0),
                NULL
            );
        END IF;
    END IF;
END ;;
DELIMITER ;


-- ============================================
-- EVENTOS
-- ============================================


-- ============================================
-- FIN DEL BACKUP
-- ============================================
SET FOREIGN_KEY_CHECKS=1;
COMMIT;
-- ============================================
-- PROCEDIMIENTO PARA REGISTRAR TRADE-IN CON TESTS
-- ============================================

-- ----------------------------------------------------
-- Procedure: sp_registrar_trade_in_con_tests
-- Registra un trade-in completo con equipo, fotos y tests
-- ----------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_registrar_trade_in_con_tests`;
DELIMITER ;;
CREATE PROCEDURE `sp_registrar_trade_in_con_tests`(
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


-- ============================================================
-- DATOS DE PRUEBA: ituaccesoriobd (BD principal)
-- ============================================================
-- Se cargan automáticamente al crear el volumen del contenedor
-- (docker-compose.test.yml lo monta como docker-entrypoint-initdb.d),
-- de modo que la BD queda LLENA y en un estado conocido.
--
-- Reglas de aislamiento que este seed garantiza:
--   - Las filas de aquí abajo son de SOLO LECTURA para las pruebas:
--     ninguna prueba debe insertar, actualizar ni borrarlas.
--   - Todo dato que una prueba escriba debe ser temporal (IDs únicos)
--     y eliminarse en un bloque finally.
--   - Los IDs con terminación "9999999" se omiten a propósito: varias
--     pruebas los usan como registros INEXISTENTES.
--
-- Formato: sentencias simples terminadas en ';', sin DELIMITER ni
-- procedimientos (el fixture de reset lo ejecuta sentencia por
-- sentencia desde Python).
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. LIMPIEZA GENERAL
--    Se vacían TODAS las tablas (el orden no importa con las FK
--    desactivadas) y más abajo se recarga el escenario completo.
-- ------------------------------------------------------------
DELETE FROM `Abastece`;
DELETE FROM `Capacitacion`;
DELETE FROM `Cargo`;
DELETE FROM `Categoria`;
DELETE FROM `Clase_producto`;
DELETE FROM `Cliente`;
DELETE FROM `Cliente_juridico`;
DELETE FROM `Credito`;
DELETE FROM `Detalle_orden`;
DELETE FROM `Detalle_venta`;
DELETE FROM `Empleado`;
DELETE FROM `Entrega`;
DELETE FROM `Entrega_inventario`;
DELETE FROM `Equipo`;
DELETE FROM `Especialidad`;
DELETE FROM `Existencias_productos`;
DELETE FROM `Fotos_inventario`;
DELETE FROM `Fotos_orden_servicio`;
DELETE FROM `Fotos_trade_in`;
DELETE FROM `Interaccion`;
DELETE FROM `Lista_compra`;
DELETE FROM `Marca_producto`;
DELETE FROM `Metodo_pago`;
DELETE FROM `Orden_compra`;
DELETE FROM `Orden_servicio`;
DELETE FROM `Pago_servicio`;
DELETE FROM `Persona_natural`;
DELETE FROM `Personal_delivery`;
DELETE FROM `Producto`;
DELETE FROM `Proveedor`;
DELETE FROM `Repuestos_usados`;
DELETE FROM `Suministra`;
DELETE FROM `Test`;
DELETE FROM `Test_realizados_interaccion`;
DELETE FROM `Test_realizados_trade_in`;
DELETE FROM `Trade_in`;
DELETE FROM `Venta`;

-- ------------------------------------------------------------
-- 2. CATÁLOGOS BASE (solo lectura para las pruebas)
-- ------------------------------------------------------------

-- Cargo: CRG0000001 y CRG0000002.
-- Usados por test_cargos_integracion (listado, verificación, duplicados,
-- cargo en uso por empleado) y test_empleados_integracion.
INSERT INTO `Cargo` (`ID_cargo`, `Nombre_cargo`, `Descripcion_cargo`) VALUES
('CRG0000001', 'Técnico', 'Encargado de las revisiones y reparaciones'),
('CRG0000002', 'Administrador', 'Administrador del sistema con acceso total');

-- Clase_producto: EXACTAMENTE 7 clases
-- (test_catalogo_integracion::TestListarCatalogo asserts len == 7).
INSERT INTO `Clase_producto` (`ID_Clase`, `Nombre_Clase`) VALUES
('1', 'Telefono'),
('2', 'Pantalla'),
('3', 'Tablet'),
('4', 'Cargador'),
('5', 'Funda'),
('6', 'Audífonos'),
('7', 'Repuesto');

-- Marca_producto: EXACTAMENTE 7 marcas
-- (test_catalogo_integracion::TestListarCatalogo asserts len == 7).
INSERT INTO `Marca_producto` (`ID_marca`, `Nombre_marca`) VALUES
('1', 'Iphone'),
('2', 'Iphone'),
('3', 'Samsung'),
('4', 'Xiaomi'),
('5', 'Motorola'),
('6', 'Huawei'),
('7', 'LG');

-- Especialidad: ESP0000001..ESP0000005
-- (test_especialidades_integracion y test_empleados_integracion).
INSERT INTO `Especialidad` (`ID_especialidad`, `Nombre_especialidad`, `Descripcion_especialidad`) VALUES
('ESP0000001', 'Reparación iOS', 'Especialista en reparación de dispositivos Apple'),
('ESP0000002', 'Reparación Android', 'Especialista en reparación de dispositivos Android'),
('ESP0000003', 'Cambio de Pantalla', 'Especialista en cambio de pantallas'),
('ESP0000004', 'Reparación Placa', 'Especialista en reparación de placas madre'),
('ESP0000005', 'Software', 'Especialista en problemas de software');

-- Empleado administrador del seed. Referenciado como FK por las ventas
-- temporales (seed_helpers.crear_venta_temporal, test_venta_integracion
-- con EMPLEADO_ADMIN = '12345678') y validado por test_empleados.
INSERT INTO `Empleado` (`ID_empleado`, `ID_cargo`, `Nombre_empleado`, `Apellido_empleado`, `Celular_empleado`, `Correo_empleado`, `Direccion_empleado`) VALUES
(12345678, 'CRG0000002', 'Super', 'Admin', '04140000000', 'admin@ituaccesorio.com', 'Barquisimeto');

-- ------------------------------------------------------------
-- 2.1. REGISTROS DEDICADOS PARA LAS PRUEBAS CRUD
--      Cada operación de prueba usa SU PROPIO registro, todos
--      distintos entre sí, para que las pruebas queden aisladas:
--
--      Cargos (test_cargos_integracion):
--        CRG0000101  Cargo de Consulta       → verificar/consultar
--        CRG0000102  Cargo a Modificar       → actualizar_cargo
--        CRG0000103  Cargo a Eliminar        → eliminar_cargo (se consume)
--        CRG0000104  Cargo con Mismo Nombre  → actualizar manteniendo nombre
--        CRG0000105  Cargo a Renombrar       → renombre a nombre existente
--        CRG0000106  Cargo con Empleado      → eliminar con empleado registrado
--                    (la FK Empleado_ibfk_1 lo impide; NO se consume)
--
--      Especialidades (test_especialidades_integracion):
--        ESP0000101  Especialidad de Consulta       → consultar
--        ESP0000102  Especialidad a Modificar       → actualizar
--        ESP0000103  Especialidad a Eliminar        → eliminar (se consume)
--        ESP0000104  Especialidad con Mismo Nombre  → actualizar mismo nombre
--        ESP0000105  Especialidad a Renombrar       → renombre duplicado
--        ESP0000106  Especialidad con Empleado      → eliminar con empleado
--                    registrado (la FK Capacitacion_ibfk_2 lo impide; NO se consume)
--
--      Empleados (test_empleados_integracion):
--        51000001  Empleado De Consulta            → consultar/verificar/listar
--        51000002  Empleado A Modificar            → actualizar_empleado
--        51000003  Empleado A Eliminar             → eliminar_empleado (se consume)
--        51000004  Empleado Con Capacitacion       → especialidades del empleado
--        51000005  Empleado A Eliminar Capacitacion→ eliminar con capacitación
--        51000006  Empleado A Modificar Especialidades → actualizar con especialidades
--        51000007  Empleado De Cargo En Uso  → empleado que usa CRG0000106
--        51000008  Empleado De Especialidad En Uso → empleado con ESP0000106
--
--      Los registros "se consumen" (CRG0000103, ESP0000103, 51000003,
--      51000005) desaparecen al correr las pruebas; para restaurarlos,
--      reinicia el entorno de pruebas (tmpfs recarga este SQL en cada up):
--        docker compose --env-file .env.test -p ituaccesorio_test \
--            -f docker-compose.test.yml down -v
--        docker compose --env-file .env.test -p ituaccesorio_test \
--            -f docker-compose.test.yml up --build
-- ------------------------------------------------------------
INSERT INTO `Cargo` (`ID_cargo`, `Nombre_cargo`, `Descripcion_cargo`) VALUES
('CRG0000101', 'Cargo de Consulta', 'Cargo del seed para pruebas de consulta'),
('CRG0000102', 'Cargo a Modificar', 'Cargo del seed para pruebas de modificación'),
('CRG0000103', 'Cargo a Eliminar', 'Cargo del seed para pruebas de eliminación'),
('CRG0000104', 'Cargo con Mismo Nombre', 'Cargo del seed para actualizar manteniendo el nombre'),
('CRG0000105', 'Cargo a Renombrar', 'Cargo del seed para probar renombre con nombre existente'),
('CRG0000106', 'Cargo con Empleado', 'Cargo del seed para probar eliminación con empleado registrado');

INSERT INTO `Especialidad` (`ID_especialidad`, `Nombre_especialidad`, `Descripcion_especialidad`) VALUES
('ESP0000101', 'Especialidad de Consulta', 'Especialidad del seed para pruebas de consulta'),
('ESP0000102', 'Especialidad a Modificar', 'Especialidad del seed para pruebas de modificación'),
('ESP0000103', 'Especialidad a Eliminar', 'Especialidad del seed para pruebas de eliminación'),
('ESP0000104', 'Especialidad con Mismo Nombre', 'Especialidad del seed para actualizar manteniendo el nombre'),
('ESP0000105', 'Especialidad a Renombrar', 'Especialidad del seed para probar renombre con nombre existente'),
('ESP0000106', 'Especialidad con Empleado', 'Especialidad del seed para probar eliminación con empleado registrado');

INSERT INTO `Empleado` (`ID_empleado`, `ID_cargo`, `Nombre_empleado`, `Apellido_empleado`, `Celular_empleado`, `Correo_empleado`, `Direccion_empleado`) VALUES
(51000001, 'CRG0000001', 'Empleado', 'De Consulta', '04140000011', 'empleado.consulta@ituaccesorio.com', 'Barquisimeto'),
(51000002, 'CRG0000001', 'Empleado', 'A Modificar', '04140000012', 'empleado.modificar@ituaccesorio.com', 'Barquisimeto'),
(51000003, 'CRG0000001', 'Empleado', 'A Eliminar', '04140000013', 'empleado.eliminar@ituaccesorio.com', 'Barquisimeto'),
(51000004, 'CRG0000001', 'Empleado', 'Con Capacitacion', '04140000014', 'empleado.capacitacion@ituaccesorio.com', 'Barquisimeto'),
(51000005, 'CRG0000001', 'Empleado', 'A Eliminar Capacitacion', '04140000015', 'empleado.eliminar.capacitacion@ituaccesorio.com', 'Barquisimeto'),
(51000006, 'CRG0000001', 'Empleado', 'A Modificar Especialidades', '04140000016', 'empleado.modificar.especialidades@ituaccesorio.com', 'Barquisimeto'),
(51000007, 'CRG0000106', 'Empleado', 'De Cargo En Uso', '04140000017', 'empleado.cargo.en.uso@ituaccesorio.com', 'Barquisimeto'),
(51000008, 'CRG0000001', 'Empleado', 'De Especialidad En Uso', '04140000018', 'empleado.especialidad.en.uso@ituaccesorio.com', 'Barquisimeto');

INSERT INTO `Capacitacion` (`ID_empleado`, `ID_especialidad`, `Nivel_Capacitacion`) VALUES
(51000004, 'ESP0000002', 'Avanzado'),
(51000005, 'ESP0000003', 'Basico'),
(51000008, 'ESP0000106', 'Basico');

-- ------------------------------------------------------------
-- 3. DATOS OPERATIVOS (escenario "Seed")
--    Escenario completo y coherente: cliente natural + jurídico,
--    productos con stock y foto, venta aprobada con detalle y
--    entrega, proveedor con orden de compra, abastecimiento,
--    crédito, equipo con orden de taller (asignada, con test y
--    foto), trade-in con foto y pago de servicio.
--
--    Convención de IDs: zona "901" (y cédulas 4xxxxxxx/5xxxxxxx),
--    que no interfiere con los IDs temporales de las pruebas
--    (ellas usan la zona 0000001-0000xxx y "…9999999" para
--    registros inexistentes). Los registros del seed son de
--    SOLO LECTURA para las pruebas.
-- ------------------------------------------------------------

-- Categorías de inventario
INSERT INTO `Categoria` (`ID_categoria`, `Nombre_categoria`) VALUES
(1, 'Equipos'),
(2, 'Repuestos');

-- Productos del seed (con su existencia y foto)
INSERT INTO `Producto` (`ID_producto`, `ID_Clase`, `ID_marca`, `Nombre_producto`, `Descripcion`) VALUES
('901', '1', '1', 'Seed iPhone 13', 'Equipo del seed de pruebas'),
('902', '1', '3', 'Seed Galaxy S22', 'Equipo del seed de pruebas'),
('903', '2', '1', 'Seed Pantalla iPhone 12', 'Repuesto del seed de pruebas');

INSERT INTO `Existencias_productos` (`ID_inventario`, `ID_producto`, `Existencia`, `Costo_venta`, `ID_categoria`) VALUES
('INV000901', '901', 10, 350.00, 1),
('INV000902', '902', 5, 300.00, 1),
('INV000903', '903', 20, 80.00, 2);

INSERT INTO `Fotos_inventario` (`ID_foto_inventario`, `ID_inventario`, `Foto_inventario`) VALUES
('FIN000901', 'INV000901', '/static/img/inventario/seed_inv000901.jpg');

-- Clientes: natural y jurídico
INSERT INTO `Cliente` (`ID_cliente`, `Direccion_cliente`, `Celular_cliente`, `Correo_cliente`) VALUES
('V40000001', 'Barquisimeto', '04140000001', 'seed.cliente@mail.com'),
('J40000002', 'Barquisimeto', '02510000001', 'seed.empresa@mail.com');

INSERT INTO `Persona_natural` (`ID_cliente`, `Apellido_cliente`, `Nombre_cliente`) VALUES
('V40000001', 'Seed', 'Cliente');

INSERT INTO `Cliente_juridico` (`ID_cliente`, `Razon_social`, `Rif_cliente`) VALUES
('J40000002', 'Seed Distribuidora C.A.', 'J-40000002-0');

-- Empleado técnico del seed (además del administrador 12345678)
INSERT INTO `Empleado` (`ID_empleado`, `ID_cargo`, `Nombre_empleado`, `Apellido_empleado`, `Celular_empleado`, `Correo_empleado`, `Direccion_empleado`) VALUES
(40000001, 'CRG0000001', 'Empleado', 'Seed', '04140000002', 'tecnico.seed@ituaccesorio.com', 'Barquisimeto');

INSERT INTO `Capacitacion` (`ID_empleado`, `ID_especialidad`, `Nivel_Capacitacion`) VALUES
(40000001, 'ESP0000001', 'Avanzado');

-- Personal de entrega
INSERT INTO `Personal_delivery` (`Cedula_delivery`, `Nombre_delivery`, `Apellido_delivery`) VALUES
('V50000001', 'Delivery', 'Seed');

-- Venta aprobada del seed, con detalle, pago y entrega
INSERT INTO `Venta` (`ID_factura`, `ID_empleado`, `ID_cliente`, `Moneda`, `Fecha_venta`) VALUES
('FAC-SEED-000001', 12345678, 'V40000001', 'VES', '2026-01-15 10:00:00');

INSERT INTO `Metodo_pago` (`ID_factura`, `Moneda`, `Fecha_pago`, `Capture`, `Estado_pago`, `Metodo`, `Referencia`, `Monto`, `Aprobado_por`, `Fecha_aprobacion`, `Motivo_rechazo`, `Fecha_rechazo`, `Rechazado_por`) VALUES
('FAC-SEED-000001', 'VES', '2026-01-15 10:05:00', NULL, 'aprobado', 'pago_movil', 'REF-SEED-0001', 350.00, 'super_admin', '2026-01-15 11:00:00', NULL, NULL, NULL);

INSERT INTO `Detalle_venta` (`ID_inventario`, `ID_factura`, `Cantidad_articulo`) VALUES
('INV000901', 'FAC-SEED-000001', 1);

INSERT INTO `Entrega` (`ID_entrega`, `ID_factura`, `Cedula_delivery`, `Estado_entrega`, `Direccion_entrega`, `Fecha_entrega`) VALUES
('ENT000901', 'FAC-SEED-000001', 'V50000001', 2, 'Seed: Av. Libertador, Barquisimeto', '2026-01-16 14:00:00');

-- Proveedor con orden de compra recibida, abastecimiento y crédito
INSERT INTO `Proveedor` (`ID_proveedor`, `RIF_proveedor`, `Nombre_proveedor`, `Tipo_proveedor`, `Celular_proveedor`, `Correo_proveedor`, `Direccion_proveedor`, `Limite_credito`) VALUES
(901, 'J-40123456-7', 'Seed Tecnología C.A.', 'Distribuidor', '02510000002', 'seed.proveedor@mail.com', 'Barquisimeto', 5000.00);

INSERT INTO `Suministra` (`ID_proveedor`, `ID_producto`, `Costo_producto`) VALUES
(901, '903', 60.00);

INSERT INTO `Orden_compra` (`ID_orden_compra`, `ID_empleado`, `ID_proveedor`, `Estado_orden_compra`, `Fecha_orden_compra`, `Factura_compra`) VALUES
('OC000901', 40000001, 901, 'Recibida', '2026-01-10 09:00:00', 'FAC-COMPRA-0001');

INSERT INTO `Detalle_orden` (`ID_orden_compra`, `ID_producto`, `Cantidad_producto`) VALUES
('OC000901', '903', 10);

INSERT INTO `Entrega_inventario` (`ID_entrega_inventario`, `ID_empleado`, `ID_orden_compra`, `Fecha_entrega_inventario`) VALUES
('EI000901', 40000001, 'OC000901', '2026-01-11 08:30:00');

INSERT INTO `Abastece` (`ID_entrega_inventario`, `ID_inventario`, `Cantidad_entregada`) VALUES
('EI000901', 'INV000903', 10);

INSERT INTO `Credito` (`ID_credito`, `ID_orden_compra`, `Dias_credito`, `Monto_credito`) VALUES
('CR000901', 'OC000901', 15, 1200.00);

-- ============================================================
-- TALLER: flujo completo con los 3 estados, más órdenes nuevas
--   OS0000901 Pendiente → vista "Órdenes" del taller (se puede tomar)
--   OS0000902 Asignada  → vista "Reparaciones asignadas" del usuario
--                         admin (empleado 12345678 = USR-001)
--   OS0000903 Reparada  → historia completa en el módulo Órdenes de
--                         servicio (reparada con el repuesto INV000903)
--   OS0000904..OS0000908 → 5 órdenes nuevas registradas por el sistema
--                         (mismo formato que genera el registro de
--                         órdenes: ID 'OS'+7 dígitos, estado 'Pendiente'
--                         e interacción inicial 'Pendiente')
-- ============================================================
INSERT INTO `Equipo` (`ID_equipo`, `ID_producto`, `Color`, `Capacidad`, `Clave`, `Patron`) VALUES
('EQ000000901', '901', 'Negro', '128GB', 1234, '1234'),
('EQ000000902', '902', 'Blanco', '256GB', NULL, NULL),
('EQ000000903', '901', 'Azul', '128GB', NULL, NULL),
('EQ000000904', '901', 'Negro', '256GB', 2580, NULL),
('EQ000000905', '902', 'Gris', '128GB', NULL, '1472583690'),
('EQ000000906', '901', 'Rojo', '128GB', NULL, NULL),
('EQ000000907', '902', 'Azul', '512GB', 9021, NULL),
('EQ000000908', '901', 'Blanco', '256GB', NULL, NULL);

INSERT INTO `Orden_servicio` (`ID_orden_servicio`, `ID_equipo`, `ID_cliente`, `Estado_orden_servicio`, `Descripcion_reparacion`, `Costo_reparacion`, `Nota_orden_servicio`, `Fecha_entrada`, `Fecha_salida`) VALUES
('OS0000901', 'EQ000000903', 'V40000001', 'Pendiente', 'Seed: cambio de batería', 30.00, 'Seed: equipo del seed de pruebas', '2026-01-16 09:00:00', NULL),
('OS0000902', 'EQ000000902', 'V40000001', 'Asignada', 'Seed: el equipo no enciende', 40.00, NULL, '2026-01-17 08:00:00', NULL),
('OS0000903', 'EQ000000901', 'V40000001', 'Reparada', 'Seed: cambio de pantalla', 50.00, NULL, '2026-01-05 09:00:00', '2026-01-07 17:00:00'),
('OS0000904', 'EQ000000904', 'V40000001', 'Pendiente', 'Seed: pantalla trizada', 45.00, NULL, '2026-01-18 09:30:00', NULL),
('OS0000905', 'EQ000000905', 'J40000002', 'Pendiente', 'Seed: no carga la batería', 35.00, 'Seed: revisar puerto de carga', '2026-01-18 11:00:00', NULL),
('OS0000906', 'EQ000000906', 'V40000001', 'Pendiente', 'Seed: no enciende', 60.00, NULL, '2026-01-19 10:15:00', NULL),
('OS0000907', 'EQ000000907', 'J40000002', 'Pendiente', 'Seed: audio intermitente', 20.00, NULL, '2026-01-19 15:40:00', NULL),
('OS0000908', 'EQ000000908', 'V40000001', 'Pendiente', 'Seed: cámara no enfoca', 55.00, 'Seed: cliente pide presupuesto antes', '2026-01-20 08:50:00', NULL);

-- Interacciones del flujo. Las órdenes nuevas replican el registro del
-- sistema: una interacción 'Pendiente' con el empleado que la registró
-- (12345678), igual que hace el registro de órdenes.
INSERT INTO `Interaccion` (`ID_interaccion`, `ID_orden_servicio`, `ID_empleado`, `Accion`) VALUES
('INT000901', 'OS0000902', 12345678, 'Asignada'),
('INT000902', 'OS0000902', 12345678, 'Revisión'),
('INT000903', 'OS0000903', 12345678, 'Asignada'),
('INT000904', 'OS0000903', 12345678, 'Reparada'),
('INT000905', 'OS0000904', 12345678, 'Pendiente'),
('INT000906', 'OS0000905', 12345678, 'Pendiente'),
('INT000907', 'OS0000906', 12345678, 'Pendiente'),
('INT000908', 'OS0000907', 12345678, 'Pendiente'),
('INT000909', 'OS0000908', 12345678, 'Pendiente');

INSERT INTO `Test` (`ID_test`, `Numero_test`, `Nombre_test`, `Resultado_test`) VALUES
('TST000901', 1, 'Seed Pantalla', 'Funciona');

INSERT INTO `Test_realizados_interaccion` (`ID_interaccion`, `ID_test`) VALUES
('INT000902', 'TST000901');

INSERT INTO `Fotos_orden_servicio` (`ID_foto_orden_servicio`, `ID_orden_servicio`, `Foto_orden_servicio`) VALUES
('FOS000901', 'OS0000901', '/static/img/evidencias/seed_os000901.jpg'),
('FOS000902', 'OS0000902', '/static/img/evidencias/seed_os000902.jpg'),
('FOS000903', 'OS0000903', '/static/img/evidencias/seed_os000903.jpg'),
('FOS000904', 'OS0000904', '/static/img/evidencias/seed_os000904.jpg'),
('FOS000905', 'OS0000905', '/static/img/evidencias/seed_os000905.jpg'),
('FOS000906', 'OS0000906', '/static/img/evidencias/seed_os000906.jpg'),
('FOS000907', 'OS0000907', '/static/img/evidencias/seed_os000907.jpg'),
('FOS000908', 'OS0000908', '/static/img/evidencias/seed_os000908.jpg');

INSERT INTO `Pago_servicio` (`ID_orden_servicio`, `ID_factura`) VALUES
('OS0000903', 'FAC-SEED-000001');

INSERT INTO `Repuestos_usados` (`ID_orden_servicio`, `ID_inventario`, `Cantidad_usada`) VALUES
('OS0000903', 'INV000903', 1);

-- Trade-in con foto (equipo del seed a cambio de un repuesto)
INSERT INTO `Trade_in` (`ID_Trade_in`, `ID_empleado`, `ID_cliente`, `ID_inventario`, `ID_equipo`, `Numero_utilizado`, `Fecha_realizado`, `cotizacion`) VALUES
('TR000901', 40000001, 'V40000001', 'INV000903', 'EQ000000901', 1, '2026-01-12 11:00:00', 200.00);

INSERT INTO `Fotos_trade_in` (`ID_foto_trade_in`, `ID_Trade_in`, `Foto_trade_in`) VALUES
('FTR000901', 'TR000901', '/static/img/tradein/seed_tr000901.jpg');

-- Test de diagnóstico asociado al trade-in del seed
INSERT INTO `Test` (`ID_test`, `Numero_test`, `Nombre_test`, `Resultado_test`) VALUES
('TST000902', 2, 'Seed Batería', 'Funciona');

INSERT INTO `Test_realizados_trade_in` (`ID_Trade_in`, `ID_test`) VALUES
('TR000901', 'TST000902');

-- Carrito activo del cliente del seed
INSERT INTO `Lista_compra` (`ID_lista_compra`, `ID_inventario`, `ID_cliente`, `Cantidad_producto`, `Estado_lista_compra`) VALUES
('LC000901', 'INV000902', 'V40000001', 2, 'activo');

-- ------------------------------------------------------------
-- 4. DETERMINISMO DE IDs AUTO-INCREMENTALES
--    Única tabla con AUTO_INCREMENT en esta BD. Queda en 3 para que
--    las próximas filas continúen después de las 2 del seed.
-- ------------------------------------------------------------
ALTER TABLE `Categoria` AUTO_INCREMENT = 3;

SET FOREIGN_KEY_CHECKS = 1;
