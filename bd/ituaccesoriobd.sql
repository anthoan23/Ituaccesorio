


DROP TABLE IF EXISTS `capacitacion`;
CREATE TABLE `capacitacion` (
  `ID_especialidad` int NOT NULL,
  `ID_em` int NOT NULL,
  PRIMARY KEY (`ID_especialidad`,`ID_em`),
  KEY `ID_em` (`ID_em`),
  CONSTRAINT `capacitacion_ibfk_1` FOREIGN KEY (`ID_especialidad`) REFERENCES `especialidad` (`ID_especialidad`),
  CONSTRAINT `capacitacion_ibfk_2` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `capacitacion` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `caracteristica`;
CREATE TABLE `caracteristica` (
  `ID_producto` int NOT NULL,
  `Capacidad` varchar(10) DEFAULT NULL,
  `Color` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`ID_producto`),
  CONSTRAINT `caracteristica_ibfk_stock` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `caracteristica` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `cargo`;
CREATE TABLE `cargo` (
  `ID_cargo` int NOT NULL AUTO_INCREMENT,
  `N_cargo` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_cargo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `cargo` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `clase_producto`;
CREATE TABLE `clase_producto` (
  `ID_clase` int NOT NULL AUTO_INCREMENT,
  `N_Clase` varchar(30) DEFAULT NULL,
  `Num_i` int DEFAULT NULL,
  PRIMARY KEY (`ID_clase`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `clase_producto` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `cliente`;
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


LOCK TABLES `cliente` WRITE;
INSERT INTO `cliente` (`ID_c`,`Nombre_c`,`Apellido_c`,`Celular_c`,`Correo_c`,`Direccion_c`,`Tipo_c`) VALUES
  (1,'MarÃ­a','GonzÃ¡lez','04141234567','maria.g@example.com','Calle 1, Ciudad','Regular'),
  (2,'Juan','PÃ©rez','04141234568','juan.p@example.com','Av. 2, Ciudad','Premium'),
  (3,'Ana','RodrÃ­guez','04141234569','ana.r@example.com','Calle 3, Ciudad','Regular'),
  (4,'Luis','MartÃ­nez','04141234570','luis.m@example.com','Av. 4, Ciudad','Mayorista'),
  (5,'Carla','FernÃ¡ndez','04141234571','carla.f@example.com','Calle 5, Ciudad','Regular');
UNLOCK TABLES;


DROP TABLE IF EXISTS `credito`;
CREATE TABLE `credito` (
  `ID_credito` int NOT NULL AUTO_INCREMENT,
  `ID_orden` int DEFAULT NULL,
  `Dias_c` int DEFAULT NULL,
  PRIMARY KEY (`ID_credito`),
  KEY `ID_orden` (`ID_orden`),
  CONSTRAINT `credito_ibfk_1` FOREIGN KEY (`ID_orden`) REFERENCES `orden_compra` (`ID_orden_c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `credito` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `empleado`;
CREATE TABLE `empleado` (
  `ID_em` int NOT NULL,
  `Nombre_em` varchar(40) DEFAULT NULL,
  `Apellido_em` varchar(40) DEFAULT NULL,
  `Celular_em` varchar(15) DEFAULT NULL,
  `Correo_em` varchar(30) DEFAULT NULL,
  `Direccion_em` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`ID_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `empleado` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `empleado_cargo`;
CREATE TABLE `empleado_cargo` (
  `ID_cargo` int NOT NULL,
  `ID_em` int NOT NULL,
  `A_cargo` int DEFAULT NULL,
  PRIMARY KEY (`ID_cargo`,`ID_em`),
  KEY `ID_em` (`ID_em`),
  CONSTRAINT `empleado_cargo_ibfk_1` FOREIGN KEY (`ID_cargo`) REFERENCES `cargo` (`ID_cargo`),
  CONSTRAINT `empleado_cargo_ibfk_2` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `empleado_cargo` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `entrega`;
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


LOCK TABLES `entrega` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `entrega_p`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `entrega_p` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `especialidad`;
CREATE TABLE `especialidad` (
  `ID_especialidad` int NOT NULL AUTO_INCREMENT,
  `N_especialidad` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_especialidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `especialidad` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `evidencia_e`;
CREATE TABLE `evidencia_e` (
  `ID_evidencia_e` int NOT NULL AUTO_INCREMENT,
  `ID_orden` int DEFAULT NULL,
  `Foto_e` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_evidencia_e`),
  KEY `ID_orden` (`ID_orden`),
  CONSTRAINT `evidencia_e_ibfk_1` FOREIGN KEY (`ID_orden`) REFERENCES `orden_e` (`ID_orden_e`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `evidencia_e` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `evidencia_r`;
CREATE TABLE `evidencia_r` (
  `ID_evidencia_r` int NOT NULL AUTO_INCREMENT,
  `ID_test` int DEFAULT NULL,
  `Foto_r` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_evidencia_r`),
  KEY `ID_test` (`ID_test`),
  CONSTRAINT `evidencia_r_ibfk_1` FOREIGN KEY (`ID_test`) REFERENCES `test` (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `evidencia_r` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `evidencia_t`;
CREATE TABLE `evidencia_t` (
  `ID_Foto_s` int NOT NULL AUTO_INCREMENT,
  `ID_producto` int DEFAULT NULL,
  `Foto_s` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_Foto_s`),
  KEY `ID_producto` (`ID_producto`),
  CONSTRAINT `evidencia_t_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `evidencia_t` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `evidencia_t_tradein`;
CREATE TABLE `evidencia_t_tradein` (
  `ID_evidencia_t` int NOT NULL AUTO_INCREMENT,
  `ID_Tradein` int DEFAULT NULL,
  `Foto_t` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_evidencia_t`),
  KEY `ID_Tradein` (`ID_Tradein`),
  CONSTRAINT `evidencia_t_tradein_ibfk_1` FOREIGN KEY (`ID_Tradein`) REFERENCES `tradein` (`ID_Tradein`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `evidencia_t_tradein` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `interaccion`;
CREATE TABLE `interaccion` (
  `ID_em` int NOT NULL,
  `ID_orden` int NOT NULL,
  `Accion` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_em`,`ID_orden`),
  KEY `ID_orden` (`ID_orden`),
  CONSTRAINT `interaccion_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`),
  CONSTRAINT `interaccion_ibfk_2` FOREIGN KEY (`ID_orden`) REFERENCES `orden_e` (`ID_orden_e`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `interaccion` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `lista_carrito`;
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


LOCK TABLES `lista_carrito` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `lista_compra`;
CREATE TABLE `lista_compra` (
  `ID_producto` int NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  `Cantidad` int DEFAULT NULL,
  PRIMARY KEY (`ID_producto`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `lista_compra_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`),
  CONSTRAINT `lista_compra_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `lista_compra` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `marca_producto`;
CREATE TABLE `marca_producto` (
  `ID_marca` int NOT NULL AUTO_INCREMENT,
  `ID_clase` int DEFAULT NULL,
  `N_marca` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_marca`),
  KEY `ID_clase` (`ID_clase`),
  CONSTRAINT `marca_producto_ibfk_1` FOREIGN KEY (`ID_clase`) REFERENCES `clase_producto` (`ID_clase`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `marca_producto` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `modelo_producto`;
CREATE TABLE `modelo_producto` (
  `ID_modelo` int NOT NULL AUTO_INCREMENT,
  `ID_marca` int DEFAULT NULL,
  `N_modelo` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ID_modelo`),
  KEY `modelo_producto_fk_marca` (`ID_marca`),
  CONSTRAINT `modelo_producto_fk_marca` FOREIGN KEY (`ID_marca`) REFERENCES `marca_producto` (`ID_marca`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `modelo_producto` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `orden_compra`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `orden_compra` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `orden_e`;
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


LOCK TABLES `orden_e` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `pago_carrito`;
CREATE TABLE `pago_carrito` (
  `ID_carrito` int NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_carrito`,`ID_factura`),
  KEY `pago_carrito_fk_factura` (`ID_factura`),
  CONSTRAINT `pago_carrito_fk_carrito` FOREIGN KEY (`ID_carrito`) REFERENCES `lista_carrito` (`ID_carrito`),
  CONSTRAINT `pago_carrito_fk_factura` FOREIGN KEY (`ID_factura`) REFERENCES `venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `pago_carrito` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `pago_orden`;
CREATE TABLE `pago_orden` (
  `ID_orden_e` int NOT NULL,
  `ID_factura` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_orden_e`,`ID_factura`),
  KEY `ID_factura` (`ID_factura`),
  CONSTRAINT `pago_orden_ibfk_1` FOREIGN KEY (`ID_orden_e`) REFERENCES `orden_e` (`ID_orden_e`),
  CONSTRAINT `pago_orden_ibfk_2` FOREIGN KEY (`ID_factura`) REFERENCES `venta` (`ID_factura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `pago_orden` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `personal_delivery`;
CREATE TABLE `personal_delivery` (
  `ID_p` int NOT NULL,
  `Nombre_p` varchar(40) DEFAULT NULL,
  `Apellido_p` varchar(40) DEFAULT NULL,
  `Celular_p` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`ID_p`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `personal_delivery` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `productos_orden`;
CREATE TABLE `productos_orden` (
  `ID_orden_c` int NOT NULL,
  `ID_modelo` int NOT NULL,
  `Cantidad_p` int DEFAULT NULL,
  PRIMARY KEY (`ID_orden_c`,`ID_modelo`),
  KEY `ID_modelo` (`ID_modelo`),
  CONSTRAINT `productos_orden_ibfk_1` FOREIGN KEY (`ID_orden_c`) REFERENCES `orden_compra` (`ID_orden_c`),
  CONSTRAINT `productos_orden_ibfk_2` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `productos_orden` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `proveedor`;
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


LOCK TABLES `proveedor` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `proveedores_productos`;
CREATE TABLE `proveedores_productos` (
  `ID_proveedor` int NOT NULL,
  `ID_modelo` int NOT NULL,
  `Costo` int DEFAULT NULL,
  PRIMARY KEY (`ID_proveedor`,`ID_modelo`),
  KEY `ID_modelo` (`ID_modelo`),
  CONSTRAINT `proveedores_productos_ibfk_1` FOREIGN KEY (`ID_proveedor`) REFERENCES `proveedor` (`ID_proveedor`),
  CONSTRAINT `proveedores_productos_ibfk_2` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `proveedores_productos` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `repuestos_u`;
CREATE TABLE `repuestos_u` (
  `ID_producto` int NOT NULL,
  `ID_orden` int NOT NULL,
  `Cantidad` int DEFAULT NULL,
  PRIMARY KEY (`ID_producto`,`ID_orden`),
  KEY `ID_orden` (`ID_orden`),
  CONSTRAINT `repuestos_u_ibfk_1` FOREIGN KEY (`ID_producto`) REFERENCES `stock` (`ID_producto`),
  CONSTRAINT `repuestos_u_ibfk_2` FOREIGN KEY (`ID_orden`) REFERENCES `orden_e` (`ID_orden_e`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `repuestos_u` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `revision_orden`;
CREATE TABLE `revision_orden` (
  `ID_test` int NOT NULL,
  `ID_orden` int NOT NULL,
  PRIMARY KEY (`ID_test`,`ID_orden`),
  KEY `revision_orden_fk_orden` (`ID_orden`),
  CONSTRAINT `revision_orden_fk_orden` FOREIGN KEY (`ID_orden`) REFERENCES `orden_e` (`ID_orden_e`),
  CONSTRAINT `revision_orden_fk_test` FOREIGN KEY (`ID_test`) REFERENCES `test` (`ID_test`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `revision_orden` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `revision_test`;
CREATE TABLE `revision_test` (
  `ID_test` int NOT NULL,
  `ID_Tradein` int NOT NULL,
  PRIMARY KEY (`ID_test`,`ID_Tradein`),
  KEY `ID_Tradein` (`ID_Tradein`),
  CONSTRAINT `revision_test_ibfk_1` FOREIGN KEY (`ID_test`) REFERENCES `test` (`ID_test`),
  CONSTRAINT `revision_test_ibfk_2` FOREIGN KEY (`ID_Tradein`) REFERENCES `tradein` (`ID_Tradein`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `revision_test` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `stock`;
CREATE TABLE `stock` (
  `ID_producto` int NOT NULL AUTO_INCREMENT,
  `ID_modelo` int DEFAULT NULL,
  `Existencia` int DEFAULT NULL,
  `Costo_venta` int DEFAULT NULL,
  PRIMARY KEY (`ID_producto`),
  KEY `ID_modelo` (`ID_modelo`),
  CONSTRAINT `stock_ibfk_1` FOREIGN KEY (`ID_modelo`) REFERENCES `modelo_producto` (`ID_modelo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `stock` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `test`;
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
  `SeÃ±al` int DEFAULT NULL,
  `Sensor_proximidad` int DEFAULT NULL,
  `Face_id` int DEFAULT NULL,
  `Bluetooth` int DEFAULT NULL,
  `Observaciones` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID_test`),
  KEY `ID_em` (`ID_em`),
  CONSTRAINT `test_ibfk_1` FOREIGN KEY (`ID_em`) REFERENCES `empleado` (`ID_em`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `test` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `tradein`;
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


LOCK TABLES `tradein` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `venta`;
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


LOCK TABLES `venta` WRITE;
UNLOCK TABLES;


