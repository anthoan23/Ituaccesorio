-- ============================================
-- Backup de: seguridad
-- Fecha: 2026-06-30 20:08:38
-- Tipo: seguridad
-- ============================================

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
INSERT INTO `backup` (`id_backup`, `id_usuario`, `estado`, `fecha`, `direccion_bd`, `nombre`) VALUES
(7, 'USR-001', 'completado', '2026-06-30 16:08:35', '/app/app/bd/ituaccesorio_backup_20260630_200835.sql', 'ituaccesorio_backup_20260630_200835.sql');

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
INSERT INTO `bitacora` (`id`, `usuario_id`, `modulo_id`, `accion`, `descripcion`, `fecha_hora`) VALUES
(595, 'USR-001', 14, 'Actualizar usuario', 'Se actualizÃ³ el usuario ID: USR-001 - Nuevo nombre: Eduin - Rol ID: 1', '2026-06-06 12:19:35'),
(596, 'USR-001', 14, 'Actualizar usuario', 'Se actualizÃ³ el usuario ID: USR-001 - Nuevo nombre: Eduin - Rol ID: 1', '2026-06-06 12:29:27'),
(597, 'USR-001', 14, 'Actualizar usuario', 'Se actualizÃ³ el usuario ID: USR-002 - Nuevo nombre: Anthoan - Rol ID: 6', '2026-06-06 12:40:49'),
(598, 'USR-001', 14, 'Actualizar usuario', 'Se actualizÃ³ el usuario ID: USR-003 - Nuevo nombre: Elena - Rol ID: 5', '2026-06-06 12:41:02'),
(599, 'USR-001', 14, 'Actualizar usuario', 'Se actualizÃ³ el usuario ID: USR-004 - Nuevo nombre: ClienteTest - Rol ID: 7', '2026-06-06 12:41:14'),
(600, 'USR-001', 14, 'Actualizar usuario', 'Se actualizÃ³ el usuario ID: USR-005 - Nuevo nombre: Prueba - Rol ID: 7', '2026-06-06 12:41:24'),
(601, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Cargador 20W | Base: 25.0 | DeducciÃ³n: 0.0 | Estimado: 25.0', '2026-06-17 13:07:45'),
(602, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 47.5 | Estimado: 902.5 | Fallas: BotÃ³n de power', '2026-06-17 13:13:15'),
(603, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:47'),
(604, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:48'),
(605, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:48'),
(606, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:48'),
(607, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:49'),
(608, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:49'),
(609, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:49'),
(610, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:50'),
(611, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:50'),
(612, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:50'),
(613, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:51'),
(614, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:51'),
(615, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:52'),
(616, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:52'),
(617, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:35:53'),
(618, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:39'),
(619, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:40'),
(620, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:40'),
(621, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:40'),
(622, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:41'),
(623, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:41'),
(624, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:41'),
(625, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:42'),
(626, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:42'),
(627, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:40:43'),
(628, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:18'),
(629, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:19'),
(630, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:19'),
(631, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:20'),
(632, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:20'),
(633, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:20'),
(634, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:21'),
(635, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:21'),
(636, 'None', 9, 'CotizaciÃ³n Trade-in', 'CotizaciÃ³n Trade-in | Modelo: Samsung S24 | Base: 950.0 | DeducciÃ³n: 0.0 | Estimado: 950.0', '2026-06-17 13:44:22'),
(637, 'USR-001', 1, 'Crear backup', 'Se creÃ³ backup: seguridad_backup_20260623_002937.sql en /app/app/bd/seguridad_backup_20260623_002937.sql', '2026-06-22 16:29:37'),
(638, 'USR-001', 1, 'Eliminar backup', 'Se eliminÃ³ el backup ID: 1', '2026-06-22 16:30:52'),
(639, 'USR-001', 1, 'Crear backup', 'Se creÃ³ backup: seguridad_backup_20260623_003335.sql en /app/app/bd/seguridad_backup_20260623_003335.sql', '2026-06-22 16:33:36'),
(640, 'USR-001', 1, 'Crear backup', 'Se creÃ³ backup: ituaccesorio_backup_20260623_003339.sql en /app/app/bd/ituaccesorio_backup_20260623_003339.sql', '2026-06-22 16:33:43'),
(641, 'USR-001', 1, 'Crear backup', 'Se creÃ³ backup: ituaccesorio_backup_20260623_003341.sql en /app/app/bd/ituaccesorio_backup_20260623_003341.sql', '2026-06-22 16:33:44'),
(642, 'USR-001', 1, 'Eliminar backup', 'Se eliminÃ³ el backup ID: 2', '2026-06-22 16:33:58'),
(643, 'USR-001', 1, 'Eliminar backup', 'Se eliminÃ³ el backup ID: 3', '2026-06-22 16:40:27'),
(644, 'USR-001', 1, 'Eliminar backup', 'Se eliminÃ³ el backup ID: 4', '2026-06-22 16:40:31'),
(645, 'USR-001', 1, 'Crear backup', 'Se creó backup: ituaccesorio_backup_20260624_153806.sql en /app/app/bd/ituaccesorio_backup_20260624_153806.sql', '2026-06-24 11:38:07'),
(646, 'USR-001', 1, 'Eliminar backup', 'Se eliminó el backup ID: 5', '2026-06-24 12:24:23'),
(647, 'USR-001', 1, 'Crear backup', 'Se creó backup: ituaccesorio_backup_20260624_162428.sql en /app/app/bd/ituaccesorio_backup_20260624_162428.sql', '2026-06-24 12:24:29'),
(648, 'USR-001', 1, 'Restaurar backup', 'Se restauró el backup ID: 6 - Archivo: ituaccesorio_backup_20260624_162428.sql', '2026-06-24 12:27:41'),
(649, 'USR-001', 10, 'Registrar revisión técnica', 'Se registró revisión técnica para orden: OS0000025 - Test #1', '2026-06-24 17:30:06'),
(650, 'USR-001', 2, 'Crear especialidad', 'Se creó la especialidad: Prueba Uno', '2026-06-28 17:14:29'),
(651, 'USR-001', 2, 'Crear especialidad', 'Se creó la especialidad: Rdfdf', '2026-06-28 17:27:59'),
(652, 'USR-001', 1, 'Eliminar backup', 'Se eliminó el backup ID: 6', '2026-06-30 16:08:31'),
(653, 'USR-001', 1, 'Crear backup', 'Se creó backup: ituaccesorio_backup_20260630_200835.sql en /app/app/bd/ituaccesorio_backup_20260630_200835.sql', '2026-06-30 16:08:35');

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
(1, 'Empleados', 'GestiÃ³n de empleados del sistema'),
(2, 'Especialidades', 'GestiÃ³n de especialidades tÃ©cnicas'),
(3, 'Cargos', 'GestiÃ³n de cargos y posiciones'),
(4, 'CatÃ¡logo', 'CatÃ¡logo de productos para ventas'),
(5, 'Ventas', 'GestiÃ³n de ventas y facturaciÃ³n'),
(6, 'Productos', 'GestiÃ³n de productos del inventario'),
(7, 'Inventario', 'Control de stock y existencias'),
(8, 'Proveedores', 'GestiÃ³n de proveedores'),
(9, 'Trade-in', 'MÃ³dulo de intercambio de equipos'),
(10, 'Taller', 'GestiÃ³n de reparaciones y servicio tÃ©cnico'),
(11, 'Ã“rdenes de servicio', 'Seguimiento de Ã³rdenes de servicio'),
(12, 'Ã“rdenes de compra', 'GestiÃ³n de compras a proveedores'),
(13, 'Clientes', 'GestiÃ³n de clientes del sistema'),
(14, 'Usuarios', 'AdministraciÃ³n de usuarios y roles'),
(15, 'BitÃ¡cora', 'Registro de actividades del sistema'),
(16, 'Personal', 'AgrupaciÃ³n de mÃ³dulos de personal');

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
(5, 1, 0, 0, 0, 0),
(5, 2, 0, 0, 0, 0),
(5, 3, 1, 1, 0, 0),
(5, 4, 1, 1, 1, 1),
(5, 5, 0, 0, 0, 0),
(5, 6, 0, 0, 0, 0),
(5, 7, 0, 0, 0, 0),
(5, 8, 0, 0, 0, 0),
(5, 9, 1, 1, 1, 1),
(5, 10, 0, 0, 0, 0),
(5, 11, 0, 0, 0, 0),
(5, 12, 0, 0, 0, 0),
(5, 13, 0, 0, 0, 0),
(5, 14, 0, 0, 0, 0),
(5, 15, 1, 1, 0, 1),
(5, 16, 0, 0, 0, 0),
(7, 1, 0, 0, 0, 0),
(7, 2, 0, 0, 0, 0),
(7, 3, 1, 1, 0, 0),
(7, 4, 1, 1, 1, 1),
(7, 5, 0, 0, 0, 0),
(7, 6, 0, 0, 0, 0),
(7, 7, 0, 0, 0, 0),
(7, 8, 0, 0, 0, 0),
(7, 9, 1, 1, 1, 1),
(7, 10, 0, 0, 0, 0),
(7, 11, 0, 0, 0, 0),
(7, 12, 0, 0, 0, 0),
(7, 13, 0, 0, 0, 0),
(7, 14, 0, 0, 0, 0),
(7, 15, 1, 0, 1, 1),
(7, 16, 0, 0, 0, 0);

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
(1, 'Admin', 'Administrador del sistema'),
(5, 'Tecnico', 'Rol diseÃ±ado para los tÃ©cnicos del negocio'),
(6, 'Ventas', 'Rol para los empleados de ventas'),
(7, 'Cliente', 'Rol diseÃ±ado para los clientes');

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
('USR-001', 'Eduin', 32014004, 'scrypt:32768:8:1$mxwPiweA9tJ7B6Lo$729382722a55df092f3adef1a1c4517c4451d26aaf40c6d0b8357bc9b5de02de5356fdee34aa5d8cc60889a0fcf891bb36e210f673a7ca8131fadcc9fb291cc4', 1, 1, '2026-05-09 18:51:02', '/static/img/perfil/725ff8bd356d449a8bc7e9cd9e54f579.jpg', '2026-06-06 12:29:27'),
('USR-002', 'Anthoan', 12345543, 'scrypt:32768:8:1$EY3xLxxGteKZdpu8$283663cbdf1749a8cfc820f7bc1355833d83ec376e186559779404adbe072a8cc4f36383549fbe6926338986adb0b6257f7a6472b6fadcdac5da52424c95c9a9', 6, 1, '2026-05-16 18:04:00', NULL, '2026-06-06 12:40:49'),
('USR-003', 'Elena', 30124556, 'scrypt:32768:8:1$9m0ICCxI0bwFmxmk$e8a71fc275c67c8dda2704f227838c02426c980d8f0f7c9de95be5872b7a62edf7e69281b604ae361cb0f07e6078150510ba3e792e0b97f82215e5bfa1e94c53', 5, 1, '2026-05-16 18:04:49', NULL, '2026-06-06 12:41:02'),
('USR-004', 'ClienteTest', 30548845, 'scrypt:32768:8:1$1KR2WxQrRgAhljzc$dc6695d2bf3169711ea51793e015a47738f33cf90114ab562a24409eca2b3107866c3301414a3e9d93e12c252c40faa59dd72d73abbaf94c7f3e7b19d2591c4f', 7, 1, '2026-05-20 19:24:14', NULL, '2026-06-06 12:41:14'),
('USR-005', 'Prueba', 31111555, 'scrypt:32768:8:1$tVHhdy5aM0GpG4Ih$eea5255b05e729be54f83953b0851833a64d51f28ce5e75e55c07f8c247c50c3331dd72a97b9c40f122e5ccfc6c2073b439060771fb67f429324013016c0c475', 7, 1, '2026-06-03 17:09:43', '/static/img/perfil/4bf079567cf44a8086d4cce7a324573a.png', '2026-06-06 12:41:24');


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
