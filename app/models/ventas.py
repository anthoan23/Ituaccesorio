from __future__ import annotations
from app.models.database import conectar
from datetime import datetime
import uuid
from decimal import Decimal
import json

class VentasModel(conectar):

    _ESTADO_CARRITO = "carrito"
    
    # ==================== CATÁLOGO ====================
    
    def listar_productos_catalogo(self, clase_id: int = None, marca_id: int = None, q: str = None):
        """Listar productos con precios en USD para el catálogo"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            where = ["i.Existencia > 0"]
            params = []
            
            if clase_id:
                where.append("cl.ID_Clase = %s")
                params.append(clase_id)
            if marca_id:
                where.append("ma.ID_marca = %s")
                params.append(marca_id)
            if q:
                where.append("(p.Nombre_producto LIKE %s OR ma.Nombre_marca LIKE %s)")
                params.append(f"%{q}%")
                params.append(f"%{q}%")
            
            where_sql = " AND ".join(where)
            
            # En el esquema nuevo, el identificador a usar en el catálogo es ID_inventario.
            query = f"""
                SELECT
                    i.ID_inventario AS id,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    COALESCE(cl.Nombre_Clase, '') AS clase,
                    i.Costo_venta AS precio_usd,
                    i.Existencia AS stock,
                    COALESCE((
                        SELECT fi.Foto_inventario
                        FROM Fotos_inventario fi
                        WHERE fi.ID_inventario = i.ID_inventario
                        ORDER BY fi.ID_foto_inventario DESC
                        LIMIT 1
                    ), CONCAT('/static/img/productos/', p.ID_producto, '.jpg')) AS imagen,
                    p.ID_producto AS id_producto,
                    p.ID_marca AS id_marca,
                    p.ID_Clase AS id_clase,
                    COALESCE((
                        SELECT SUM(dv.Cantidad_articulo)
                        FROM Detalle_venta dv
                        WHERE dv.ID_inventario = i.ID_inventario
                    ), 0) AS veces_vendido
                FROM Inventario i
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE {where_sql}
                ORDER BY veces_vendido DESC, cl.Nombre_Clase ASC, ma.Nombre_marca ASC, p.Nombre_producto ASC
            """
            
            cursor.execute(query, tuple(params))
            resultados = cursor.fetchall()

            # Normalizar decimales
            for r in resultados or []:
                val = r.get("precio_usd")
                if isinstance(val, Decimal):
                    r["precio_usd"] = float(val)
            
            return resultados
        finally:
            cursor.close()
            db.close()
    
    def obtener_producto(self, producto_id: int):
        """Obtener un producto por su ID"""
        db = self.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    i.ID_inventario AS id,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    i.Costo_venta AS precio_usd,
                    i.Existencia AS stock
                FROM Inventario i
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                WHERE i.ID_inventario = %s
                """,
                (producto_id,),
            )
            row = cursor.fetchone()
            if row and isinstance(row.get("precio_usd"), Decimal):
                row["precio_usd"] = float(row["precio_usd"])
            return row
        finally:
            cursor.close()
            db.close()
    
    def productos_mas_vendidos(self, limite: int = 5):
        """Obtener productos más vendidos"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    i.ID_inventario AS id,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    i.Costo_venta AS precio_usd,
                    SUM(dv.Cantidad_articulo) AS veces_vendido
                FROM Detalle_venta dv
                JOIN Inventario i ON dv.ID_inventario = i.ID_inventario
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                GROUP BY i.ID_inventario, p.Nombre_producto, ma.Nombre_marca, i.Costo_venta
                ORDER BY veces_vendido DESC
                LIMIT %s
                """,
                (limite,),
            )
            rows = cursor.fetchall()
            for r in rows or []:
                if isinstance(r.get("precio_usd"), Decimal):
                    r["precio_usd"] = float(r["precio_usd"])
            return rows
        finally:
            cursor.close()
            db.close()
    
    # ==================== CARRITO ====================
    
    def obtener_carrito(self, cliente_id: int):
        """Obtener items del carrito de un cliente"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    lc.ID_lista_compra AS id,
                    lc.ID_inventario AS producto_id,
                    lc.Cantidad_producto AS cantidad,
                    i.Costo_venta AS precio_usd,
                    p.Nombre_producto AS nombre,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    i.Existencia AS stock_disponible
                FROM Lista_compra lc
                JOIN Inventario i ON lc.ID_inventario = i.ID_inventario
                JOIN Producto p ON i.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                WHERE lc.ID_cliente = %s
                  AND (lc.Estado_lista_compra IS NULL OR lc.Estado_lista_compra = %s)
                """,
                (cliente_id, self._ESTADO_CARRITO),
            )
            rows = cursor.fetchall()
            for r in rows or []:
                if isinstance(r.get("precio_usd"), Decimal):
                    r["precio_usd"] = float(r["precio_usd"])
            return rows
        finally:
            cursor.close()
            db.close()
    
    def agregar_carrito(self, cliente_id: int, producto_id: int, cantidad: int):
        """Agregar o actualizar item en el carrito"""
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            cant = int(cantidad)
            if cant <= 0:
                raise ValueError("La cantidad debe ser mayor que 0")

            inv_id = int(producto_id)

            # Validar stock disponible
            cursor.execute(
                "SELECT Existencia FROM Inventario WHERE ID_inventario = %s LIMIT 1",
                (inv_id,),
            )
            stock_row = cursor.fetchone()
            if not stock_row:
                raise ValueError("Producto no encontrado en inventario")
            stock = int(stock_row[0] or 0)
            if stock <= 0:
                raise ValueError("Producto sin stock")

            # Verificar si ya existe en el carrito
            cursor.execute(
                """
                SELECT ID_lista_compra, Cantidad_producto
                FROM Lista_compra
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
                LIMIT 1
                """,
                (int(cliente_id), inv_id, self._ESTADO_CARRITO),
            )
            existente = cursor.fetchone()

            if existente:
                nueva_cantidad = int(existente[1] or 0) + cant
                if nueva_cantidad > stock:
                    raise ValueError("La cantidad supera el stock disponible")
                cursor.execute(
                    "UPDATE Lista_compra SET Cantidad_producto = %s WHERE ID_lista_compra = %s",
                    (nueva_cantidad, int(existente[0])),
                )
            else:
                if cant > stock:
                    raise ValueError("La cantidad supera el stock disponible")
                cursor.execute(
                    """
                    INSERT INTO Lista_compra (ID_inventario, ID_cliente, Cantidad_producto, Estado_lista_compra)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (inv_id, int(cliente_id), cant, self._ESTADO_CARRITO),
                )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def eliminar_carrito_item(self, cliente_id: int, producto_id: int):
        """Eliminar item del carrito"""
        db = self.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute(
                """
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
                """,
                (int(cliente_id), int(producto_id), self._ESTADO_CARRITO),
            )
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()
    
    def actualizar_carrito_cantidad(self, cliente_id: int, producto_id: int, cantidad: int):
        """Actualizar cantidad de un item en el carrito"""
        if cantidad <= 0:
            self.eliminar_carrito_item(cliente_id, producto_id)
            return
        
        db = self.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            # Validar stock
            cursor.execute(
                "SELECT Existencia FROM Inventario WHERE ID_inventario = %s LIMIT 1",
                (int(producto_id),),
            )
            row = cursor.fetchone()
            stock = int(row[0] or 0) if row else 0
            if int(cantidad) > stock:
                raise ValueError("La cantidad supera el stock disponible")

            cursor.execute(
                """
                UPDATE Lista_compra
                SET Cantidad_producto = %s, Estado_lista_compra = %s
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
                """,
                (int(cantidad), self._ESTADO_CARRITO, int(cliente_id), int(producto_id), self._ESTADO_CARRITO),
            )
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()
    
    def vaciar_carrito(self, cliente_id: int):
        """Vaciar todo el carrito"""
        db = self.conexion1()
        if not db:
            return
        
        cursor = db.cursor()
        try:
            cursor.execute(
                """
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
                """,
                (int(cliente_id), self._ESTADO_CARRITO),
            )
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()
    
    # ==================== VENTAS ====================
    
    def generar_factura_id(self):
        """Generar ID de factura único"""
        fecha = datetime.now().strftime("%Y-%m")
        random_part = str(uuid.uuid4().hex[:6]).upper()
        return f"FAC-{fecha}-{random_part}"
    
    def crear_venta(self, cliente_id: int, items: list, total_usd: float, total_bs: float, metodo_pago: str, estado_pago: str = "Por Verificar"):
        """Crear una nueva venta desde carrito"""
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        factura_id = self.generar_factura_id()
        fecha_actual = datetime.now()
        
        cursor = db.cursor()
        try:
            moneda = "USD"
            if metodo_pago in ("pago_movil", "efectivo_bs"):
                moneda = "VES"
            elif metodo_pago == "binance":
                moneda = "USDT"

            # Insertar venta (esquema nuevo)
            cursor.execute(
                """
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (factura_id, None, int(cliente_id), moneda, fecha_actual),
            )

            # Insertar detalle + descontar stock (Inventario)
            for item in items or []:
                inv_id = int(item["producto_id"])
                qty = int(item["cantidad"])
                if qty <= 0:
                    continue

                cursor.execute(
                    "SELECT Existencia FROM Inventario WHERE ID_inventario=%s LIMIT 1",
                    (inv_id,),
                )
                row = cursor.fetchone()
                existencia = int(row[0] or 0) if row else 0
                if existencia < qty:
                    raise ValueError("Stock insuficiente para completar la compra")

                cursor.execute(
                    """
                    INSERT INTO Detalle_venta (ID_inventario, ID_factura, Cantidad_articulo)
                    VALUES (%s, %s, %s)
                    """,
                    (inv_id, factura_id, qty),
                )
                cursor.execute(
                    "UPDATE Inventario SET Existencia = Existencia - %s WHERE ID_inventario = %s",
                    (qty, inv_id),
                )

            # Marcar/limpiar carrito del cliente
            cursor.execute(
                """
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
                """,
                (int(cliente_id), self._ESTADO_CARRITO),
            )
            
            db.commit()
            return factura_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def crear_venta_local(self, cliente_id: int, empleado_id: int, items: list, total_usd: float, total_bs: float, metodo_pago: str, total_pagado: float = None):
        """Crear venta desde el local (empleado)"""
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        factura_id = self.generar_factura_id()
        fecha_actual = datetime.now()
        
        cursor = db.cursor()
        try:
            moneda = "USD"
            if metodo_pago in ("pago_movil", "efectivo_bs"):
                moneda = "VES"
            elif metodo_pago == "binance":
                moneda = "USDT"

            cursor.execute(
                """
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (factura_id, int(empleado_id) if empleado_id is not None else None, int(cliente_id), moneda, fecha_actual),
            )

            for item in items or []:
                inv_id = int(item["producto_id"])
                qty = int(item["cantidad"])
                if qty <= 0:
                    continue

                cursor.execute(
                    "SELECT Existencia FROM Inventario WHERE ID_inventario=%s LIMIT 1",
                    (inv_id,),
                )
                row = cursor.fetchone()
                existencia = int(row[0] or 0) if row else 0
                if existencia < qty:
                    raise ValueError("Stock insuficiente")

                cursor.execute(
                    "INSERT INTO Detalle_venta (ID_inventario, ID_factura, Cantidad_articulo) VALUES (%s, %s, %s)",
                    (inv_id, factura_id, qty),
                )
                cursor.execute(
                    "UPDATE Inventario SET Existencia = Existencia - %s WHERE ID_inventario = %s",
                    (qty, inv_id),
                )
            
            db.commit()
            return factura_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def guardar_reporte_pago(self, factura_id: str, metodo_pago: str, datos: dict):
        """Guardar reporte de pago en la tabla reporte_pagos"""
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            fecha_actual = datetime.now()

            moneda = "USD"
            if metodo_pago in ("pago_movil", "efectivo_bs"):
                moneda = "VES"
            elif metodo_pago == "binance":
                moneda = "USDT"

            # En el dump nuevo existe Transferencia (muy básica). Guardamos un resumen en Capture.
            capture = None
            try:
                capture = json.dumps({"metodo": metodo_pago, "datos": datos or {}}, ensure_ascii=False)
            except Exception:
                capture = None

            if capture and len(capture) > 255:
                capture = capture[:255]

            cursor.execute(
                """
                INSERT INTO Transferencia (ID_factura, Moneda, Fecha_pago, Capture)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE Moneda=VALUES(Moneda), Fecha_pago=VALUES(Fecha_pago), Capture=VALUES(Capture)
                """,
                (factura_id, moneda, fecha_actual, capture),
            )
            
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    # ==================== VALIDACIÓN DE PAGOS ====================
    
    def obtener_pagos_pendientes(self):
        """Obtener ventas con estado 'Por Verificar'"""
        # El esquema nuevo (Venta/Detalle_venta/Transferencia) no incluye estado de validación.
        # Para evitar errores SQL en el panel admin, devolvemos una lista vacía por ahora.
        return []
    
    def obtener_pagos_aprobados(self):
        """Obtener ventas aprobadas"""
        return []
    
    def obtener_pagos_rechazados(self):
        """Obtener ventas rechazadas"""
        return []
    
    def aprobar_pago(self, factura_id: str, empleado_id: int):
        """Aprobar un pago"""
        raise RuntimeError("La validación de pagos (aprobar) no está soportada con el esquema de BD actual.")
    
    def rechazar_pago(self, factura_id: str, empleado_id: int, motivo: str):
        """Rechazar un pago con motivo"""
        raise RuntimeError("La validación de pagos (rechazar) no está soportada con el esquema de BD actual.")
    
    # ==================== ENTREGAS ====================
    
    def registrar_entrega(self, factura_id: str, empleado_delivery_id: int, direccion: str):
        """Registrar entrega de un producto"""
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO entrega (ID_factura, ID_p, Direccion_e, Estado, Fecha_e)
                VALUES (%s, %s, %s, 0, %s)
            """, (factura_id, empleado_delivery_id, direccion, datetime.now().strftime("%Y-%m-%d")))
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()