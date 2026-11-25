from __future__ import annotations
import logging
from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import (
    validar_numero,
    validar_texto_numero,
    validar_decimal,
)
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import uuid


logger = logging.getLogger(__name__)


class VentaModel:
    """Modelo para operaciones de ventas y facturación"""

    METODOS_PAGO_VALIDOS = ["pago_movil", "zelle", "binance", "efectivo_usd", "efectivo_bs"]

    def __init__(self, factura_id: str = None, cliente_id: str = None,
                 empleado_id: str = None, items: List[Dict[str, Any]] = None,
                 metodo_pago: str = None, estado_pago: str = "pendiente",
                 datos_pago: Dict[str, Any] = None, usuario_id: str = None):
        self.factura_id = factura_id
        self.cliente_id = cliente_id
        self.empleado_id = empleado_id
        self.items = items or []
        self.metodo_pago = metodo_pago
        self.estado_pago = estado_pago
        self.datos_pago = datos_pago or {}
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

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
        db = self.__conexion_bd.conexion1()
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
        db = self.__conexion_bd.conexion1()
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

    def _verificar_producto_existe(self, inventario_id: str) -> bool:
        db = self.__conexion_bd.conexion1()
        if not db:
            return False
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM Existencias_productos WHERE ID_inventario = %s LIMIT 1",
                (str(inventario_id),)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    # ==================== VALIDACIONES ====================

    def _validar_cliente(self, cliente_id: Any) -> Optional[str]:
        cliente_id_str = str(cliente_id).strip() if cliente_id is not None else ""
        if not cliente_id_str:
            return "El ID del cliente no puede estar vacío."
        # Cliente.ID_cliente varchar(12); operación usa cédula numérica 6–8
        error = validar_numero(cliente_id_str, 6, 8, "Cliente")
        if error:
            return error
        if not self._verificar_cliente_existe(cliente_id_str):
            return f"El cliente con ID '{cliente_id_str}' no existe."
        return None

    def _validar_items(self) -> Optional[str]:
        if not self.items:
            return "El carrito no puede estar vacío."
        if not isinstance(self.items, list):
            return "Los items deben ser una lista."

        productos_vistos = set()
        for i, item in enumerate(self.items):
            if not isinstance(item, dict):
                return f"El producto en la posición {i+1} no tiene formato válido."

            producto_id = item.get("producto_id") or item.get("id")
            if not producto_id:
                return f"El producto en la posición {i+1} no tiene ID."

            producto_id_str = str(producto_id).strip()
            if not producto_id_str:
                return f"El ID del producto en la posición {i+1} está vacío."

            # Existencias_productos.ID_inventario varchar(10)
            error = validar_texto_numero(producto_id_str, 1, 10, f"ID del producto #{i+1}")
            if error:
                return error

            cantidad = item.get("cantidad", 0)
            error = validar_numero(cantidad, 1, 10, f"Cantidad del producto #{i+1}")
            if error:
                return error

            # '0' tiene 1 dígito y pasa validar_numero; sin este check se
            # insertaba un Detalle_venta con cantidad 0 y Existencia - 0.
            if int(cantidad) <= 0:
                return f"La cantidad del producto #{i+1} debe ser mayor que 0."

            if producto_id_str in productos_vistos:
                return f"El producto '{producto_id_str}' aparece múltiples veces en el carrito."
            productos_vistos.add(producto_id_str)
        return None

    def _validar_metodo_pago(self) -> Optional[str]:
        if not self.metodo_pago or not str(self.metodo_pago).strip():
            return "El método de pago no puede estar vacío."
        metodo = str(self.metodo_pago).strip()
        if metodo not in self.METODOS_PAGO_VALIDOS:
            return f"Método de pago inválido. Opciones: {', '.join(self.METODOS_PAGO_VALIDOS)}."
        self.metodo_pago = metodo
        return None

    # Reglas de pago movidas del controller (ventas.py): fuente única en
    # el modelo para el catálogo de métodos y sus políticas.
    # Catálogo completo (lo consume /api/metodos_pago) y sus políticas
    CATALOGO_METODOS_PAGO = (
        {"id": "pago_movil", "nombre": "Pago Móvil (Bs)", "moneda": "VES"},
        {"id": "zelle", "nombre": "Zelle (USD)", "moneda": "USD"},
        {"id": "binance", "nombre": "Binance (USDT)", "moneda": "USDT"},
        {"id": "efectivo_bs", "nombre": "Efectivo (Bs)", "moneda": "VES"},
        {"id": "efectivo_usd", "nombre": "Efectivo (USD)", "moneda": "USD"},
    )
    METODOS_PAGO = tuple(m["id"] for m in CATALOGO_METODOS_PAGO)
    METODOS_PAGO_SIN_CAPTURE = ("efectivo_bs", "efectivo_usd")

    @classmethod
    def requiere_capture(cls, metodo_pago) -> bool:
        return str(metodo_pago or "") not in cls.METODOS_PAGO_SIN_CAPTURE

    @classmethod
    def estado_inicial_para(cls, metodo_pago) -> str:
        return "aprobado" if str(metodo_pago or "") in cls.METODOS_PAGO_SIN_CAPTURE else "pendiente"

    def _validar_datos_pago(self) -> Optional[str]:
        referencia = self.datos_pago.get("referencia", "")
        monto = self.datos_pago.get("monto", None)

        # Metodo_pago.Referencia varchar(100)
        if referencia:
            error = validar_texto_numero(referencia, 1, 100, "Referencia")
            if error:
                return error

        # Metodo_pago.Monto decimal(12,2)
        if monto is not None:
            error = validar_decimal(
                monto, "Monto",
                max_decimales=2, min_valor=0, max_valor=9999999999.99
            )
            if error:
                return error
            try:
                monto_float = float(monto)
                if monto_float <= 0:
                    return "El monto debe ser mayor a 0."
            except (ValueError, TypeError):
                return "El monto debe ser un valor numérico válido."

        if self.metodo_pago in ["pago_movil", "zelle", "binance"] and not referencia:
            return f"La referencia es obligatoria para el método de pago '{self.metodo_pago}'."

        return None

    # ==================== CREAR VENTA ====================

    def crear_venta_desde_carrito(self) -> str:
        """Crea una venta a partir del carrito de compras"""
        error = self._validar_cliente(self.cliente_id)
        if error:
            raise ValueError(error)

        cliente_id_str = str(self.cliente_id).strip()

        error = self._validar_items()
        if error:
            raise ValueError(error)

        error = self._validar_metodo_pago()
        if error:
            raise ValueError(error)

        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("Error al conectar a la base de datos.")

        factura_id = self._generar_id_factura()
        # -04:00: el contenedor va en UTC y MySQL escribe en -04:00 (mismo
        # desfase corregido en tradein_empleados). Sin esto, las ventas de
        # 00:00-04:00 locales quedaban atribuidas al día anterior.
        fecha_actual = datetime.now(timezone(timedelta(hours=-4)))
        moneda = self._obtener_moneda_segun_metodo()

        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
            """, (factura_id, self.empleado_id, cliente_id_str, moneda, fecha_actual))

            for item in self.items:
                inventario_id = str(item.get("producto_id", item.get("id", "")))
                cantidad = int(item.get("cantidad", 0))

                stock_valido, stock_disponible = self._verificar_stock_disponible(inventario_id, cantidad)
                if not stock_valido:
                    raise ValueError(f"Stock insuficiente para el producto {inventario_id}. Disponible: {stock_disponible}")

                cursor.execute("""
                    INSERT INTO Detalle_venta (ID_inventario, ID_factura, Cantidad_articulo)
                    VALUES (%s, %s, %s)
                """, (inventario_id, factura_id, cantidad))

                # Descuento de stock ATÓMICO: la condición de stock va en el
                # WHERE (y se comprueba rowcount) para que dos ventas
                # simultáneas no puedan dejar la Existencia en negativo.
                cursor.execute("""
                    UPDATE Existencias_productos
                    SET Existencia = Existencia - %s
                    WHERE ID_inventario = %s AND Existencia >= %s
                """, (cantidad, inventario_id, cantidad))
                if cursor.rowcount == 0:
                    raise ValueError(
                        f"Stock insuficiente para el producto {inventario_id}. "
                        f"Disponible: {stock_disponible}"
                    )

            db.commit()

            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear venta",
                    descripcion=f"Se creó la venta {factura_id} para cliente: {cliente_id_str} - Método: {self.metodo_pago}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Ventas"
                )
                bitacora.registrar()

            self.factura_id = factura_id
            return factura_id

        except Exception as e:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()

    # ==================== REGISTRO DE PAGO ====================

    def guardar_registro_pago(self) -> None:
        """Guarda el registro de pago de una venta"""
        if not self.factura_id or not str(self.factura_id).strip():
            raise ValueError("El ID de la factura no puede estar vacío.")

        error = self._validar_metodo_pago()
        if error:
            raise ValueError(error)

        error = self._validar_datos_pago()
        if error:
            raise ValueError(error)

        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("Error al conectar a la base de datos.")

        cursor = db.cursor()
        try:
            # -04:00: el contenedor va en UTC y MySQL escribe en -04:00.
            fecha_actual = datetime.now(timezone(timedelta(hours=-4)))
            moneda = self._obtener_moneda_segun_metodo()

            referencia = self.datos_pago.get("referencia", "")
            monto = self.datos_pago.get("monto", None)
            capture_image = self.datos_pago.get("capture", "")
            fecha_pago_cliente = self.datos_pago.get("fecha_pago", None)

            fecha_pago = fecha_pago_cliente if fecha_pago_cliente else fecha_actual

            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'Metodo_pago' AND TABLE_SCHEMA = DATABASE()
            """)
            columnas = [row[0] for row in cursor.fetchall()]

            campos = ["ID_factura", "Moneda", "Fecha_pago"]
            valores = [self.factura_id, moneda, fecha_pago]

            if "Metodo" in columnas:
                campos.append("Metodo")
                valores.append(self.metodo_pago)

            if "Referencia" in columnas and referencia:
                campos.append("Referencia")
                valores.append(referencia)

            if "Monto" in columnas and monto is not None:
                campos.append("Monto")
                valores.append(monto)

            if "Capture" in columnas and capture_image:
                campos.append("Capture")
                valores.append(capture_image)

            if "Estado_pago" in columnas:
                campos.append("Estado_pago")
                valores.append(self.estado_pago)

            placeholders = ", ".join(["%s"] * len(campos))
            # Columnas fijas del código, valores parametrizados
            query = f"""
                INSERT INTO Metodo_pago ({', '.join(campos)})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE
                    Moneda = VALUES(Moneda),
                    Fecha_pago = VALUES(Fecha_pago),
                    Metodo = VALUES(Metodo),
                    Referencia = VALUES(Referencia),
                    Monto = VALUES(Monto),
                    Capture = VALUES(Capture),
                    Estado_pago = CASE
                        WHEN Estado_pago IS NULL OR LOWER(TRIM(Estado_pago)) = 'pendiente'
                            THEN 'pendiente'
                        -- Reenvío: si el cliente resubió datos de pago, la
                        -- solicitud vuelve a pendiente para ser revalidada
                        -- (antes quedaba congelada en 'rechazado' para siempre).
                        WHEN Referencia <> VALUES(Referencia)
                            OR COALESCE(Capture, '') <> COALESCE(VALUES(Capture), '')
                            OR Monto <> VALUES(Monto)
                            THEN 'pendiente'
                        ELSE Estado_pago
                    END
            """  # nosec B608

            cursor.execute(query, valores)
            db.commit()

            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar pago",
                    descripcion=f"Se registró pago para factura: {self.factura_id} - Método: {self.metodo_pago}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Ventas"
                )
                bitacora.registrar()

        except Exception as e:
            db.rollback()
            logger.error(f"Error en guardar_registro_pago: {e}")
            raise
        finally:
            cursor.close()
            db.close()

    def obtener_ventas_hoy(self) -> dict:
        """Obtiene el resumen de ventas del día.

        Fuente: `Venta` (todas las ventas, con o sin pago registrado), no
        `Metodo_pago` (que solo tiene filas cuando se llama a
        guardar_registro_pago y por tanto deja fuera las ventas en efectivo).

        Contrato de retorno (no cambiar: lo consume el front):
            {"total_ventas": float, "cantidad_ventas": int, "moneda": str}
        """
        db = self.__conexion_bd.conexion1()
        if not db:
            return {"total_ventas": 0.0, "cantidad_ventas": 0, "moneda": "USD"}

        cursor = db.cursor(dictionary=True)
        try:
            # Rango semiabierto sobre Fecha_venta (sargable) en lugar de
            # DATE(Fecha_venta) = CURDATE(). La conexión fija time_zone='-04:00'
            # (ver database.py), así que CURDATE() coincide con la zona con la
            # que se inserta Fecha_venta desde Python.
            cursor.execute("""
                SELECT
                    COUNT(*) AS cantidad_ventas,
                    COALESCE(SUM(
                        (SELECT COALESCE(SUM(dv.Cantidad_articulo * ep.Precio_venta), 0)
                        FROM Detalle_venta dv
                        JOIN Existencias_productos ep
                        ON ep.ID_inventario = dv.ID_inventario
                        WHERE dv.ID_factura = v.ID_factura)
                    ), 0) AS total_ventas,
                    v.Moneda
                FROM Venta v
                WHERE v.Fecha_venta >= CURDATE()
                AND v.Fecha_venta <  CURDATE() + INTERVAL 1 DAY
                GROUP BY v.Moneda
                ORDER BY v.Moneda DESC
                LIMIT 1
            """)
            resultado = cursor.fetchone()

            if resultado and resultado.get("cantidad_ventas"):
                return {
                    "total_ventas": float(resultado.get("total_ventas") or 0.0),
                    "cantidad_ventas": int(resultado.get("cantidad_ventas") or 0),
                    "moneda": resultado.get("Moneda") or "USD",
                }

            return {"total_ventas": 0.0, "cantidad_ventas": 0, "moneda": "USD"}
        except Exception as e:
            logger.error(f"Error en obtener_ventas_hoy: {e}")
            return {"total_ventas": 0.0, "cantidad_ventas": 0, "moneda": "USD"}
        finally:
            cursor.close()
            db.close()