from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import (
    validar_numero,
    validar_texto_numero,
    validar_decimal,
    validar_sin_caracteres_especiales,
    validar_codigo_factura,
)
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
import uuid


class ReportesVentasModel:
    """Modelo para reportes de ventas y ventas locales"""

    METODOS_PAGO_VALIDOS = ["pago_movil", "zelle", "binance", "efectivo_bs", "efectivo_usd"]

    def __init__(self, factura_id: str = None, cliente_id: str = None,
                 items: List[Dict[str, Any]] = None, metodo_pago: str = None,
                 empleado_id: str = None, usuario_id: str = None):
        self.factura_id = factura_id
        self.cliente_id = cliente_id
        self.items = items or []
        self.metodo_pago = metodo_pago
        self.empleado_id = empleado_id
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def _generar_id_factura(self) -> str:
        fecha = datetime.now().strftime("%Y%m")
        random_part = str(uuid.uuid4().hex[:6]).upper()
        return f"FAC-{fecha}-{random_part}"

    def _obtener_moneda_segun_metodo(self) -> str:
        if self.metodo_pago in ("pago_movil", "efectivo_bs"):
            return "VES"
        elif self.metodo_pago == "binance":
            return "USDT"
        else:
            return "USD"

    def _verificar_cliente_existe(self, cliente_id: str) -> bool:
        db = self._conexion()
        if not db:
            return False
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Cliente WHERE ID_cliente = %s LIMIT 1",
                (str(cliente_id),)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def _verificar_stock_disponible(self, inventario_id: str, cantidad: int) -> tuple[bool, int]:
        db = self._conexion()
        if not db:
            return False, 0
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
                (str(inventario_id),)
            )
            row = cursor.fetchone()
            if not row:
                return False, 0
            stock = int(row[0] or 0)
            return stock >= cantidad, stock
        finally:
            cursor.close()
            db.close()

    # ==================== VALIDACIONES ====================

    def _validar_filtros_reportes(self, filtros: Dict[str, Any]) -> Optional[str]:
        """Valida los filtros de reportes. Devuelve mensaje de error o None."""
        if filtros.get("q"):
            error = validar_sin_caracteres_especiales(filtros["q"], 1, 100, "Búsqueda", permitir_espacios=True)
            if error:
                return error

        fecha_desde = filtros.get("fecha_desde")
        fecha_hasta = filtros.get("fecha_hasta")
        if fecha_desde:
            try:
                datetime.strptime(fecha_desde, "%Y-%m-%d")
            except ValueError:
                return "Formato de fecha inválido. Use YYYY-MM-DD."
        if fecha_hasta:
            try:
                datetime.strptime(fecha_hasta, "%Y-%m-%d")
            except ValueError:
                return "Formato de fecha inválido. Use YYYY-MM-DD."
        if fecha_desde and fecha_hasta:
            desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
            hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            if desde > hasta:
                return "La fecha 'desde' no puede ser mayor que la fecha 'hasta'."

        monto_min = filtros.get("monto_min")
        monto_max = filtros.get("monto_max")
        # Metodo_pago.Monto decimal(12,2)
        if monto_min is not None:
            error = validar_decimal(
                monto_min, "Monto mínimo",
                max_decimales=2, min_valor=0, max_valor=9999999999.99
            )
            if error:
                return error
        if monto_max is not None:
            error = validar_decimal(
                monto_max, "Monto máximo",
                max_decimales=2, min_valor=0, max_valor=9999999999.99
            )
            if error:
                return error
        if monto_min is not None and monto_max is not None:
            try:
                if float(monto_min) > float(monto_max):
                    return "El monto mínimo no puede ser mayor que el monto máximo."
            except ValueError:
                pass

        return None

    def _validar_venta_local(self) -> Optional[str]:
        """Valida los datos de una venta local. Devuelve mensaje de error o None."""
        cliente_id = str(self.cliente_id).strip() if self.cliente_id is not None else ""
        if not cliente_id:
            return "El campo Cliente es obligatorio."
        # Venta.ID_cliente varchar(12); cédula numérica 6–8
        error = validar_numero(cliente_id, 6, 8, "Cliente")
        if error:
            return error

        if not self.items:
            return "Agrega al menos un producto."

        for i, item in enumerate(self.items):
            if not isinstance(item, dict):
                return f"El producto #{i+1} no tiene formato válido."

            producto_id = item.get("producto_id")
            cantidad = item.get("cantidad", 0)

            if not producto_id:
                return f"El producto #{i+1} no tiene ID válido."

            # Detalle_venta.ID_inventario varchar(10)
            error = validar_texto_numero(str(producto_id).strip(), 1, 10, f"ID del producto #{i+1}")
            if error:
                return error

            error = validar_numero(cantidad, 1, 10, f"Cantidad del producto #{i+1}")
            if error:
                return error

        if not self.metodo_pago:
            return "El campo Método de pago es obligatorio."
        metodo = str(self.metodo_pago).strip()
        if metodo not in self.METODOS_PAGO_VALIDOS:
            return f"Método de pago '{metodo}' no válido."
        self.metodo_pago = metodo

        return None

    # ==================== CONSULTAS ====================

    def obtener_reportes_ventas(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene ventas para reportes con filtros avanzados"""
        error = self._validar_filtros_reportes(filtros)
        if error:
            return {"success": False, "error": error, "ventas": [], "total": 0}

        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error al conectar", "ventas": [], "total": 0}

        cursor = db.cursor(dictionary=True)
        try:
            where_conditions = ["1=1"]
            params = []

            if filtros.get("q"):
                search = f"%{filtros['q']}%"
                where_conditions.append("(v.ID_factura LIKE %s OR pn.Nombre_cliente LIKE %s OR pn.Apellido_cliente LIKE %s)")
                params.extend([search, search, search])

            if filtros.get("estado"):
                where_conditions.append("mp.Estado_pago = %s")
                params.append(filtros["estado"])

            if filtros.get("metodo_pago"):
                where_conditions.append("mp.Metodo = %s")
                params.append(filtros["metodo_pago"])

            if filtros.get("moneda"):
                where_conditions.append("v.Moneda = %s")
                params.append(filtros["moneda"])

            if filtros.get("fecha_desde"):
                where_conditions.append("DATE(v.Fecha_venta) >= %s")
                params.append(filtros["fecha_desde"])

            if filtros.get("fecha_hasta"):
                where_conditions.append("DATE(v.Fecha_venta) <= %s")
                params.append(filtros["fecha_hasta"])

            if filtros.get("monto_min") is not None:
                where_conditions.append("mp.Monto >= %s")
                params.append(filtros["monto_min"])

            if filtros.get("monto_max") is not None:
                where_conditions.append("mp.Monto <= %s")
                params.append(filtros["monto_max"])

            where_sql = " AND ".join(where_conditions)

            cursor.execute(f"""
                SELECT
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda AS venta_moneda,
                    v.Fecha_venta AS fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(c.Celular_cliente, '') AS cliente_celular,
                    COALESCE(c.Correo_cliente, '') AS cliente_correo,
                    mp.Fecha_pago,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto AS monto_pagado,
                    mp.Estado_pago AS estado,
                    mp.Aprobado_por,
                    mp.Fecha_aprobacion,
                    mp.Rechazado_por,
                    mp.Fecha_rechazo,
                    mp.Motivo_rechazo,
                    mp.Capture AS capture_image,
                    CASE
                        WHEN mp.Referencia LIKE 'LOCAL-%' THEN 'Local'
                        ELSE 'Online'
                    END AS tipo_venta
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE {where_sql}
                ORDER BY v.Fecha_venta DESC
            """, tuple(params))

            ventas = cursor.fetchall()

            total_monto = 0
            pendientes = 0
            aprobados = 0
            rechazados = 0
            locales = 0
            online = 0

            for venta in ventas:
                if venta.get("monto_pagado") and isinstance(venta["monto_pagado"], Decimal):
                    venta["monto_pagado"] = float(venta["monto_pagado"])
                total_monto += venta.get("monto_pagado", 0) or 0

                estado = venta.get("estado", "")
                if estado == "pendiente":
                    pendientes += 1
                elif estado == "aprobado":
                    aprobados += 1
                elif estado == "rechazado":
                    rechazados += 1

                if venta.get("tipo_venta") == "Local":
                    locales += 1
                else:
                    online += 1

            return {
                "success": True,
                "ventas": ventas,
                "total": len(ventas),
                "total_monto": total_monto,
                "pendientes": pendientes,
                "aprobados": aprobados,
                "rechazados": rechazados,
                "locales": locales,
                "online": online
            }
        except Exception as e:
            print(f"Error en obtener_reportes_ventas: {e}")
            return {"success": False, "error": str(e), "ventas": [], "total": 0}
        finally:
            cursor.close()
            db.close()

    def obtener_detalle_venta_completo(self) -> Dict[str, Any]:
        """Obtiene el detalle completo de una venta incluyendo datos del cliente"""
        if not self.factura_id:
            return {"success": False, "error": "Factura no especificada"}
        error = validar_codigo_factura(str(self.factura_id).strip(), 1, 20, "Factura")
        if error:
            return {"success": False, "error": error}

        db = self._conexion()
        if not db:
            return {"success": False, "error": "Error al conectar"}

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda,
                    v.Fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente,
                    c.Correo_cliente,
                    c.Direccion_cliente,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto AS monto_total,
                    mp.Estado_pago AS estado,
                    mp.Fecha_pago,
                    mp.Capture AS capture_image,
                    mp.Aprobado_por,
                    mp.Fecha_aprobacion,
                    mp.Rechazado_por,
                    mp.Fecha_rechazo,
                    mp.Motivo_rechazo,
                    CASE
                        WHEN mp.Referencia LIKE 'LOCAL-%' THEN 'Local'
                        ELSE 'Online'
                    END AS tipo_venta
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE v.ID_factura = %s
                LIMIT 1
            """, (self.factura_id,))

            venta = cursor.fetchone()
            if not venta:
                return {"success": False, "error": "Venta no encontrada"}

            if venta.get("monto_total") and isinstance(venta["monto_total"], Decimal):
                venta["monto_total"] = float(venta["monto_total"])

            cursor.execute("""
                SELECT
                    dv.ID_inventario,
                    dv.Cantidad_articulo,
                    e.Costo_venta AS precio_unitario,
                    p.Nombre_producto,
                    COALESCE(ma.Nombre_marca, '') AS marca,
                    COALESCE(cl.Nombre_Clase, '') AS clase
                FROM Detalle_venta dv
                JOIN Existencias_productos e ON dv.ID_inventario = e.ID_inventario
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                LEFT JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE dv.ID_factura = %s
            """, (self.factura_id,))

            productos = cursor.fetchall()
            total_venta = 0

            for p in productos:
                if p.get("precio_unitario") and isinstance(p["precio_unitario"], Decimal):
                    p["precio_unitario"] = float(p["precio_unitario"])
                p["subtotal"] = p["precio_unitario"] * p["Cantidad_articulo"]
                total_venta += p["subtotal"]

            return {
                "success": True,
                "venta": venta,
                "productos": productos,
                "total_venta": total_venta
            }
        except Exception as e:
            print(f"Error en obtener_detalle_venta_completo: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()

    def obtener_ventas_locales(self, busqueda: str = "", fecha: str = None) -> List[Dict[str, Any]]:
        """Obtiene el historial de ventas locales"""
        if busqueda:
            error = validar_sin_caracteres_especiales(busqueda, 1, 100, "Búsqueda", permitir_espacios=True)
            if error:
                return []
        if fecha:
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except ValueError:
                return []

        db = self._conexion()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            where_conditions = ["mp.Referencia LIKE 'LOCAL-%'"]
            params = []

            if busqueda:
                search = f"%{busqueda}%"
                where_conditions.append(
                    "(v.ID_factura LIKE %s OR pn.Nombre_cliente LIKE %s OR pn.Apellido_cliente LIKE %s OR mp.Referencia LIKE %s)"
                )
                params.extend([search, search, search, search])

            if fecha:
                where_conditions.append("DATE(v.Fecha_venta) = %s")
                params.append(fecha)

            where_sql = " AND ".join(where_conditions)

            cursor.execute(f"""
                SELECT
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Moneda,
                    v.Fecha_venta AS fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    COALESCE(cj.Razon_social, '') AS razon_social,
                    mp.Metodo AS metodo_pago,
                    mp.Referencia,
                    mp.Monto AS monto,
                    mp.Estado_pago AS estado,
                    mp.Fecha_pago,
                    'Local' AS tipo_venta
                FROM Venta v
                INNER JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente_juridico cj ON v.ID_cliente = cj.ID_cliente
                WHERE {where_sql}
                ORDER BY v.Fecha_venta DESC
                LIMIT 100
            """, tuple(params))

            ventas = cursor.fetchall()
            for v in ventas:
                if v.get("monto") and isinstance(v["monto"], Decimal):
                    v["monto"] = float(v["monto"])

            return ventas
        except Exception as e:
            print(f"Error en obtener_ventas_locales: {e}")
            return []
        finally:
            cursor.close()
            db.close()

    def registrar_venta_local(self) -> str:
        """Registra una venta local (en tienda física)"""
        error = self._validar_venta_local()
        if error:
            raise ValueError(error)

        cliente_id_str = str(self.cliente_id).strip()

        if not self._verificar_cliente_existe(cliente_id_str):
            raise ValueError(f"El cliente con ID '{cliente_id_str}' no existe.")

        db = self._conexion()
        if not db:
            raise RuntimeError("Error al conectar a la base de datos.")

        factura_id = self._generar_id_factura()
        fecha_actual = datetime.now()
        moneda = self._obtener_moneda_segun_metodo()

        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
            """, (factura_id, self.empleado_id, cliente_id_str, moneda, fecha_actual))

            total_monto = 0

            for item in self.items:
                inventario_id = str(item.get("producto_id", ""))
                cantidad = int(item.get("cantidad", 0))
                precio = float(item.get("precio_usd", 0))

                if not inventario_id:
                    raise ValueError("Producto sin ID válido")

                if cantidad <= 0:
                    raise ValueError(f"Cantidad inválida para producto {inventario_id}")

                stock_valido, stock_disponible = self._verificar_stock_disponible(inventario_id, cantidad)
                if not stock_valido:
                    raise ValueError(f"Stock insuficiente para producto {inventario_id}. Disponible: {stock_disponible}")

                cursor.execute("""
                    INSERT INTO Detalle_venta (ID_inventario, ID_factura, Cantidad_articulo)
                    VALUES (%s, %s, %s)
                """, (inventario_id, factura_id, cantidad))

                cursor.execute("""
                    UPDATE Existencias_productos
                    SET Existencia = Existencia - %s
                    WHERE ID_inventario = %s
                """, (cantidad, inventario_id))

                total_monto += precio * cantidad

            cursor.execute("""
                INSERT INTO Metodo_pago (
                    ID_factura, Moneda, Fecha_pago, Metodo, Referencia,
                    Monto, Estado_pago, Aprobado_por, Fecha_aprobacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                factura_id, moneda, fecha_actual, self.metodo_pago,
                f"LOCAL-{factura_id[-6:]}", total_monto, 'aprobado',
                self.empleado_id, fecha_actual
            ))

            db.commit()

            if self.usuario_id:
                Bitacora(
                    accion="Registrar venta local",
                    descripcion=f"Venta local registrada: {factura_id} - Cliente: {cliente_id_str} - Total: {total_monto} {moneda}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Reportes Ventas"
                ).registrar()

            return factura_id

        except Exception as e:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()