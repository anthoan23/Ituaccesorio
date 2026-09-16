-- ============================================
-- Backup de: seguridad
-- Fecha: 2026-06-30 20:08:38
-- Tipo: seguridad
-- ============================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT=0;
SET SQL_QUOTE_SHOW_CREATE=1;

-- ============================================
-- TABLAS
-- ============================================

-- ----------------------------------------------------
-- Table structure for `backup`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `backup`;
CREATE TABLE `backup` (
  `id_backup` int NOT NULL AUTO_INCREMENT,
  `id_usuario` varchar(10) NOT NULL,
  `estado` varchar(50) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `direccion_bd` varchar(255) NOT NULL,
  `nombre` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_backup`),
  KEY `fk_usuario_backup` (`id_usuario`),
  CONSTRAINT `fk_usuario_backup` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- Dumping data for `backup`
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `bitacora`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `bitacora`;
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
) ENGINE=InnoDB AUTO_INCREMENT=654 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- Dumping data for `bitacora`
-- ----------------------------------------------------

-- ----------------------------------------------------
-- Table structure for `modulo`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `modulo`;
CREATE TABLE `modulo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- Dumping data for `modulo`
-- ----------------------------------------------------
INSERT INTO `modulo` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Empleados', 'Gestión de empleados del sistema'),
(2, 'Especialidades', 'Gestión de especialidades técnicas'),
(3, 'Cargos', 'Gestión de cargos y posiciones'),
(4, 'Catálogo', 'Catálogo de productos para ventas'),
(5, 'Ventas', 'Gestión de ventas y facturación'),
(6, 'Productos', 'Gestión de productos del inventario'),
(7, 'Inventario', 'Control de stock y existencias'),
(8, 'Proveedores', 'Gestión de proveedores'),
(9, 'Trade-in', 'Módulo de intercambio de equipos'),
(10, 'Taller', 'Gestión de reparaciones y servicio técnico'),
(11, 'Órdenes de servicio', 'Seguimiento de órdenes de servicio'),
(12, 'Órdenes de compra', 'Gestión de compras a proveedores'),
(13, 'Clientes', 'Gestión de clientes del sistema'),
(14, 'Usuarios', 'Administración de usuarios y roles'),
(15, 'Bitácora', 'Registro de actividades del sistema'),
(16, 'Personal', 'Agrupación de módulos de personal');

-- ----------------------------------------------------
-- Table structure for `permiso`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `permiso`;
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

-- ----------------------------------------------------
-- Dumping data for `permiso`
-- ----------------------------------------------------
INSERT INTO `permiso` (`rol_id`, `modulo_id`, `consultar`, `registrar`, `modificar`, `eliminar`) VALUES
(1, 1, 1, 1, 1, 1),
(1, 2, 1, 1, 1, 1),
(1, 3, 1, 1, 1, 1),
(1, 4, 1, 1, 1, 1),
(1, 5, 1, 1, 1, 1),
(1, 6, 1, 1, 1, 1),
(1, 7, 1, 1, 1, 1),
(1, 8, 1, 1, 1, 1),
(1, 9, 1, 1, 1, 1),
(1, 10, 1, 1, 1, 1),
(1, 11, 1, 1, 1, 1),
(1, 12, 1, 1, 1, 1),
(1, 13, 1, 1, 1, 1),
(1, 14, 1, 1, 1, 1),
(1, 15, 1, 1, 1, 1),
(1, 16, 1, 1, 1, 1);

-- ----------------------------------------------------
-- Table structure for `rol`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `rol`;
CREATE TABLE `rol` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------
-- Dumping data for `rol`
-- ----------------------------------------------------
INSERT INTO `rol` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Admin', 'Super administrador con todos los permisos');

-- ----------------------------------------------------
-- Table structure for `usuario`
-- ----------------------------------------------------
DROP TABLE IF EXISTS `usuario`;
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

-- ----------------------------------------------------
-- Dumping data for `usuario`
-- ----------------------------------------------------
INSERT INTO `usuario` (`id`, `nombre`, `cedula`, `password`, `rol_id`, `activo`, `fecha_creacion`, `foto_perfil`, `ultima_actualizacion`) VALUES
('USR-001', 'super_admin', 12345678, 'scrypt:32768:8:1$c74OQEYV9C7Ya99Q$e4c48aac034fc8ae73fb61c4a800c2a4fd707e7e898dd3d264999e8250a5f22e3346fb428a78ba51bbcbb9180ac4c1e655211a02b5a034c67cf902e125590279', 1, 1, '2026-05-09 18:51:02', NULL, '2026-05-09 18:51:02');


-- ============================================
-- VISTAS
-- ============================================


-- ============================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================


-- ============================================
-- FUNCIONES
-- ============================================


-- ============================================
-- TRIGGERS
-- ============================================


-- ============================================
-- EVENTOS
-- ============================================


-- ============================================
-- FIN DEL BACKUP
-- ============================================
SET FOREIGN_KEY_CHECKS=1;
COMMIT;
