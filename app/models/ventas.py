# app/models/ventas.py
from __future__ import annotations
from app.models.database import conectar
from datetime import datetime
import uuid

class VentasModel(conectar):
    
    # ==================== CATÁLOGO ====================
    
    def listar_productos_catalogo(self, clase_id: int = None, marca_id: int = None, q: str = None):
        """Listar productos con precios en USD para el catálogo"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            where = ["s.Existencia > 0"]
            params = []
            
            if clase_id:
                where.append("cl.ID_clase = %s")
                params.append(clase_id)
            if marca_id:
                where.append("ma.ID_marca = %s")
                params.append(marca_id)
            if q:
                where.append("(mo.N_modelo LIKE %s OR ma.N_marca LIKE %s)")
                params.append(f"%{q}%")
                params.append(f"%{q}%")
            
            where_sql = " AND ".join(where)
            
            # Subconsulta para obtener cantidad de ventas
            query = f"""
                SELECT 
                    s.ID_producto AS id,
                    mo.N_modelo AS nombre,
                    ma.N_marca AS marca,
                    cl.N_Clase AS clase,
                    s.Costo_venta AS precio_usd,
                    s.Existencia AS stock,
                    mo.ID_modelo AS id_modelo,
                    ma.ID_marca AS id_marca,
                    cl.ID_clase AS id_clase,
                    COALESCE((
                        SELECT SUM(lc.Cantidad) 
                        FROM lista_compra lc 
                        WHERE lc.ID_producto = s.ID_producto
                    ), 0) AS veces_vendido
                FROM stock s
                JOIN modelo_producto mo ON s.ID_modelo = mo.ID_modelo
                JOIN marca_producto ma ON mo.ID_marca = ma.ID_marca
                JOIN clase_producto cl ON ma.ID_clase = cl.ID_clase
                WHERE {where_sql}
                ORDER BY veces_vendido DESC, cl.N_Clase ASC, ma.N_marca ASC, mo.N_modelo ASC
            """
            
            cursor.execute(query, tuple(params))
            resultados = cursor.fetchall()
            
            # Agregar URL de imagen
            for r in resultados:
                r["imagen"] = f"/static/img/productos/{r['id']}.jpg" if r['id'] else None
            
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
            cursor.execute("""
                SELECT 
                    s.ID_producto AS id,
                    mo.N_modelo AS nombre,
                    ma.N_marca AS marca,
                    s.Costo_venta AS precio_usd,
                    s.Existencia AS stock
                FROM stock s
                JOIN modelo_producto mo ON s.ID_modelo = mo.ID_modelo
                JOIN marca_producto ma ON mo.ID_marca = ma.ID_marca
                WHERE s.ID_producto = %s
            """, (producto_id,))
            return cursor.fetchone()
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
            cursor.execute("""
                SELECT 
                    s.ID_producto AS id,
                    mo.N_modelo AS nombre,
                    ma.N_marca AS marca,
                    s.Costo_venta AS precio_usd,
                    SUM(lc.Cantidad) AS veces_vendido
                FROM lista_compra lc
                JOIN stock s ON lc.ID_producto = s.ID_producto
                JOIN modelo_producto mo ON s.ID_modelo = mo.ID_modelo
                JOIN marca_producto ma ON mo.ID_marca = ma.ID_marca
                GROUP BY s.ID_producto
                ORDER BY veces_vendido DESC
                LIMIT %s
            """, (limite,))
            return cursor.fetchall()
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
            cursor.execute("""
                SELECT 
                    lc.ID_carrito AS id,
                    lc.ID_producto AS producto_id,
                    lc.Cantidad AS cantidad,
                    s.Costo_venta AS precio_usd,
                    mo.N_modelo AS nombre,
                    ma.N_marca AS marca,
                    s.Existencia AS stock_disponible
                FROM lista_carrito lc
                JOIN stock s ON lc.ID_producto = s.ID_producto
                JOIN modelo_producto mo ON s.ID_modelo = mo.ID_modelo
                JOIN marca_producto ma ON mo.ID_marca = ma.ID_marca
                WHERE lc.ID_c = %s AND lc.Estado_c = 0
            """, (cliente_id,))
            return cursor.fetchall()
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
            # Verificar si ya existe
            cursor.execute(
                "SELECT ID_carrito, Cantidad FROM lista_carrito WHERE ID_c = %s AND ID_producto = %s AND Estado_c = 0",
                (cliente_id, producto_id)
            )
            existente = cursor.fetchone()
            
            if existente:
                nueva_cantidad = existente[1] + cantidad
                cursor.execute(
                    "UPDATE lista_carrito SET Cantidad = %s WHERE ID_carrito = %s",
                    (nueva_cantidad, existente[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO lista_carrito (ID_producto, ID_c, Cantidad, Estado_c) VALUES (%s, %s, %s, 0)",
                    (producto_id, cliente_id, cantidad)
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
                "DELETE FROM lista_carrito WHERE ID_c = %s AND ID_producto = %s AND Estado_c = 0",
                (cliente_id, producto_id)
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
            cursor.execute(
                "UPDATE lista_carrito SET Cantidad = %s WHERE ID_c = %s AND ID_producto = %s AND Estado_c = 0",
                (cantidad, cliente_id, producto_id)
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
                "DELETE FROM lista_carrito WHERE ID_c = %s AND Estado_c = 0",
                (cliente_id,)
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
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        cursor = db.cursor()
        try:
            # Insertar venta
            cursor.execute("""
                INSERT INTO venta (ID_factura, ID_c, Costo_total, Fecha_v, Estado_pago, Metodo_pago)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (factura_id, cliente_id, total_bs, fecha_actual, estado_pago, metodo_pago))
            
            # Insertar items de la compra
            for item in items:
                cursor.execute("""
                    INSERT INTO lista_compra (ID_producto, ID_factura, Cantidad)
                    VALUES (%s, %s, %s)
                """, (item["producto_id"], factura_id, item["cantidad"]))
                
                # Actualizar stock
                cursor.execute("""
                    UPDATE stock SET Existencia = Existencia - %s
                    WHERE ID_producto = %s AND Existencia >= %s
                """, (item["cantidad"], item["producto_id"], item["cantidad"]))
            
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
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        cursor = db.cursor()
        try:
            # Insertar venta
            cursor.execute("""
                INSERT INTO venta (ID_factura, ID_em, ID_c, Costo_total, Fecha_v, Estado_pago, Metodo_pago)
                VALUES (%s, %s, %s, %s, %s, 'Aprobado', %s)
            """, (factura_id, empleado_id, cliente_id, total_bs, fecha_actual, metodo_pago))
            
            # Insertar items
            for item in items:
                cursor.execute("""
                    INSERT INTO lista_compra (ID_producto, ID_factura, Cantidad)
                    VALUES (%s, %s, %s)
                """, (item["producto_id"], factura_id, item["cantidad"]))
                
                cursor.execute("""
                    UPDATE stock SET Existencia = Existencia - %s
                    WHERE ID_producto = %s AND Existencia >= %s
                """, (item["cantidad"], item["producto_id"], item["cantidad"]))
            
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
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            
            if metodo_pago == "pago_movil":
                cursor.execute("""
                    INSERT INTO reporte_pagos 
                    (ID_factura, Metodo_Pago, Banco_Origen, Celular_O_Correo, Referencia_O_Comprobante, Fecha_Pago, Monto_Pagado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    factura_id, "Pago Movil", datos.get("banco"), datos.get("telefono"),
                    datos.get("referencia"), fecha_actual, datos.get("monto", 0)
                ))
            
            elif metodo_pago == "zelle":
                cursor.execute("""
                    INSERT INTO reporte_pagos 
                    (ID_factura, Metodo_Pago, Titular_Cuenta, Celular_O_Correo, Referencia_O_Comprobante, Fecha_Pago, Monto_Pagado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    factura_id, "Zelle", datos.get("titular"), datos.get("correo"),
                    datos.get("referencia"), fecha_actual, datos.get("monto", 0)
                ))
            
            elif metodo_pago == "binance":
                cursor.execute("""
                    INSERT INTO reporte_pagos 
                    (ID_factura, Metodo_Pago, Celular_O_Correo, Referencia_O_Comprobante, Fecha_Pago, Monto_Pagado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    factura_id, "Binance", datos.get("uid"), datos.get("pay_id"),
                    fecha_actual, datos.get("monto", 0)
                ))
            
            elif metodo_pago in ["efectivo_bs", "efectivo_usd"]:
                cursor.execute("""
                    INSERT INTO reporte_pagos 
                    (ID_factura, Metodo_Pago, Billete_Entregado, Fecha_Pago, Monto_Pagado)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    factura_id, "Efectivo " + ("Bolivares" if metodo_pago == "efectivo_bs" else "Dolares"),
                    datos.get("billete"), fecha_actual, datos.get("monto", 0)
                ))
            
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
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.Fecha_v AS fecha,
                    v.Costo_total AS total_bs,
                    v.Metodo_pago AS metodo_pago,
                    c.Nombre_c AS cliente_nombre,
                    c.Apellido_c AS cliente_apellido,
                    c.Celular_c AS cliente_celular,
                    c.Correo_c AS cliente_correo,
                    COALESCE(rp.Referencia_O_Comprobante, 'N/A') AS referencia,
                    COALESCE(rp.Titular_Cuenta, 'N/A') AS titular,
                    COALESCE(rp.Banco_Origen, 'N/A') AS banco,
                    COALESCE(rp.Celular_O_Correo, 'N/A') AS contacto,
                    COALESCE(rp.Billete_Entregado, 'N/A') AS billete
                FROM venta v
                JOIN cliente c ON v.ID_c = c.ID_c
                LEFT JOIN reporte_pagos rp ON v.ID_factura = rp.ID_factura
                WHERE v.Estado_pago = 'Por Verificar'
                ORDER BY v.Fecha_v DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def obtener_pagos_aprobados(self):
        """Obtener ventas aprobadas"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.Fecha_v AS fecha,
                    v.Costo_total AS total_bs,
                    v.Metodo_pago AS metodo_pago,
                    c.Nombre_c AS cliente_nombre,
                    c.Apellido_c AS cliente_apellido
                FROM venta v
                JOIN cliente c ON v.ID_c = c.ID_c
                WHERE v.Estado_pago = 'Aprobado'
                ORDER BY v.Fecha_v DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def obtener_pagos_rechazados(self):
        """Obtener ventas rechazadas"""
        db = self.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.Fecha_v AS fecha,
                    v.Costo_total AS total_bs,
                    v.Metodo_pago AS metodo_pago,
                    c.Nombre_c AS cliente_nombre,
                    c.Apellido_c AS cliente_apellido
                FROM venta v
                JOIN cliente c ON v.ID_c = c.ID_c
                WHERE v.Estado_pago = 'Rechazado'
                ORDER BY v.Fecha_v DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
    
    def aprobar_pago(self, factura_id: str, empleado_id: int):
        """Aprobar un pago"""
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE venta SET Estado_pago = 'Aprobado', ID_em = %s WHERE ID_factura = %s",
                (empleado_id, factura_id)
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def rechazar_pago(self, factura_id: str, empleado_id: int, motivo: str):
        """Rechazar un pago con motivo"""
        db = self.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE venta SET Estado_pago = 'Rechazado', ID_em = %s, Motivo_rechazo = %s WHERE ID_factura = %s",
                (empleado_id, motivo, factura_id)
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
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