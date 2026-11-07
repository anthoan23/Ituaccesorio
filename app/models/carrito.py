from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import validar_numero, validar_texto_numero
from decimal import Decimal
from typing import List, Dict, Any, Optional


class CarritoModel:
    """Modelo para operaciones del carrito de compras"""

    _ESTADO_CARRITO = "carrito"

    def __init__(self, cliente_id: str = None, inventario_id: str = None,
                 cantidad: int = 0, usuario_id: str = None):
        self.cliente_id = cliente_id
        self.inventario_id = inventario_id
        self.cantidad = cantidad
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    # ==================== VALIDACIONES ====================

    def _validar_cliente(self, requerido: bool = True) -> Optional[str]:
        cliente_id = str(self.cliente_id).strip() if self.cliente_id is not None else ""
        if not cliente_id:
            if requerido:
                return "El cliente es obligatorio."
            return None
        # Lista_compra.ID_cliente varchar(12); cédula numérica 6–8
        error = validar_numero(cliente_id, 6, 8, "Cliente")
        if error:
            return error
        return None

    def _validar_inventario(self) -> Optional[str]:
        inventario_id = str(self.inventario_id).strip() if self.inventario_id is not None else ""
        if not inventario_id:
            return "El producto es obligatorio."
        # Lista_compra.ID_inventario varchar(10)
        error = validar_texto_numero(inventario_id, 1, 10, "Producto")
        if error:
            return error
        return None

    def _validar_cantidad(self) -> Optional[str]:
        if self.cantidad is None:
            return "La cantidad es obligatoria."
        error = validar_numero(self.cantidad, 1, 10, "Cantidad")
        if error:
            return error
        try:
            cantidad_int = int(self.cantidad)
        except (ValueError, TypeError):
            return "La cantidad debe ser un número entero válido."
        if cantidad_int <= 0:
            return "La cantidad debe ser mayor que 0."
        self.cantidad = cantidad_int
        return None

    # ==================== GENERADORES / HELPERS ====================

    def _generar_id_lista_compra(self) -> str:
        """Genera un ID único para la lista de compra"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return "LST0000001"

        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT ID_lista_compra FROM Lista_compra
                ORDER BY CAST(SUBSTRING(ID_lista_compra, 4) AS UNSIGNED) DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            if row and row[0] and row[0].startswith('LST'):
                num = int(row[0][3:]) + 1
            else:
                num = 1

            nuevo_id = f"LST{num:07d}"

            cursor.execute("SELECT 1 FROM Lista_compra WHERE ID_lista_compra = %s", (nuevo_id,))
            if cursor.fetchone():
                while True:
                    num += 1
                    nuevo_id = f"LST{num:07d}"
                    cursor.execute("SELECT 1 FROM Lista_compra WHERE ID_lista_compra = %s", (nuevo_id,))
                    if not cursor.fetchone():
                        break

            return nuevo_id
        except Exception as e:
            print(f"Error generando ID: {e}")
            import time
            import random
            return f"LST{int(time.time())}{random.randint(10, 99)}"
        finally:
            cursor.close()
            db.close()

    def _obtener_tasas(self) -> Dict[str, float]:
        """Obtiene las tasas de cambio actuales"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return {"oficial": 520.91, "paralelo": 710.12}

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT Tasa_oficial, Tasa_paralelo
                FROM Tasas_cambio
                ORDER BY ID_tasa DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "oficial": float(row.get("Tasa_oficial", 520.91)),
                    "paralelo": float(row.get("Tasa_paralelo", 710.12))
                }
            return {"oficial": 520.91, "paralelo": 710.12}
        except Exception as e:
            print(f"Error obteniendo tasas: {e}")
            return {"oficial": 520.91, "paralelo": 710.12}
        finally:
            cursor.close()
            db.close()

    # ==================== CONSULTAS ====================

    def obtener_carrito(self) -> Dict[str, Any]:
        """
        Obtiene el carrito del cliente con formato compatible con ventas.js
        Retorna: {
            "items": [...],
            "total": 0,
            "tasas": {"oficial": 0, "paralelo": 0}
        }
        """
        if not self.cliente_id:
            return {"items": [], "total": 0, "tasas": {"oficial": 0, "paralelo": 0}}

        db = self.__conexion_bd.conexion1()
        if not db:
            return {"items": [], "total": 0, "tasas": {"oficial": 0, "paralelo": 0}}

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    lc.ID_lista_compra AS id,
                    lc.ID_inventario AS ID_inventario,
                    lc.Cantidad_producto AS Cantidad_producto,
                    e.Costo_venta AS Costo_venta,
                    p.Nombre_producto AS Nombre_producto,
                    COALESCE(ma.Nombre_marca, '') AS Nombre_marca,
                    e.Existencia AS Existencia,
                    COALESCE((
                        SELECT fi.Foto_inventario
                        FROM Fotos_inventario fi
                        WHERE fi.ID_inventario = e.ID_inventario
                        ORDER BY fi.ID_foto_inventario DESC
                        LIMIT 1
                    ), '') AS Foto_inventario
                FROM Lista_compra lc
                JOIN Existencias_productos e ON lc.ID_inventario = e.ID_inventario
                JOIN Producto p ON e.ID_producto = p.ID_producto
                LEFT JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                WHERE lc.ID_cliente = %s
                  AND (lc.Estado_lista_compra IS NULL OR lc.Estado_lista_compra = %s)
            """, (self.cliente_id, self._ESTADO_CARRITO))

            rows = cursor.fetchall()

            items = []
            total = 0

            for row in rows:
                costo_venta = row.get("Costo_venta", 0)
                if isinstance(costo_venta, Decimal):
                    costo_venta = float(costo_venta)
                else:
                    try:
                        costo_venta = float(costo_venta or 0)
                    except (ValueError, TypeError):
                        costo_venta = 0.0

                cantidad = row.get("Cantidad_producto", 0)
                try:
                    cantidad = int(cantidad or 0)
                except (ValueError, TypeError):
                    cantidad = 0

                subtotal = costo_venta * cantidad
                total += subtotal

                item = {
                    # Claves originales (para compatibilidad)
                    "ID_lista_compra": row.get("id", ""),
                    "ID_inventario": row.get("ID_inventario", ""),
                    "Cantidad_producto": cantidad,
                    "Costo_venta": costo_venta,
                    "Nombre_producto": row.get("Nombre_producto", "Producto") or "Producto",
                    "Nombre_marca": row.get("Nombre_marca", "") or "",
                    "Existencia": int(row.get("Existencia", 0) or 0),
                    "Foto_inventario": row.get("Foto_inventario", "") or "",

                    # Claves para ventas.js (normalizadas)
                    "producto_id": row.get("ID_inventario", ""),
                    "precio_usd": costo_venta,
                    "cantidad": cantidad,
                    "nombre": row.get("Nombre_producto", "Producto") or "Producto",
                    "marca": row.get("Nombre_marca", "") or "",
                    "imagen": row.get("Foto_inventario", "") or "",
                    "stock_disponible": int(row.get("Existencia", 0) or 0),
                    "id": row.get("ID_inventario", ""),
                    "precio": costo_venta
                }
                items.append(item)

            tasas = self._obtener_tasas()

            return {
                "items": items,
                "total": total,
                "tasas": tasas
            }
        except Exception as e:
            print(f"Error en obtener_carrito: {e}")
            import traceback
            traceback.print_exc()
            return {"items": [], "total": 0, "tasas": {"oficial": 0, "paralelo": 0}}
        finally:
            cursor.close()
            db.close()

    # ==================== MUTACIONES ====================

    def agregar_al_carrito(self) -> Dict[str, Any]:
        error = self._validar_cliente(requerido=True)
        if error:
            return {"success": False, "error": error}

        error = self._validar_inventario()
        if error:
            return {"success": False, "error": error}

        error = self._validar_cantidad()
        if error:
            return {"success": False, "error": error}

        db = self.__conexion_bd.conexion1()
        if not db:
            return {"success": False, "error": "No se pudo conectar a la base de datos."}

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
                (self.inventario_id,)
            )
            stock_row = cursor.fetchone()
            if not stock_row:
                return {"success": False, "error": "Producto no encontrado en inventario."}

            stock = int(stock_row[0] or 0)
            if stock <= 0:
                return {"success": False, "error": "Producto sin stock."}

            cursor.execute("""
                SELECT ID_lista_compra, Cantidad_producto
                FROM Lista_compra
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
                LIMIT 1
            """, (self.cliente_id, self.inventario_id, self._ESTADO_CARRITO))

            existente = cursor.fetchone()

            if existente:
                nueva_cantidad = int(existente[1] or 0) + self.cantidad
                if nueva_cantidad > stock:
                    return {"success": False, "error": "La cantidad supera el stock disponible."}
                cursor.execute(
                    "UPDATE Lista_compra SET Cantidad_producto = %s WHERE ID_lista_compra = %s",
                    (nueva_cantidad, existente[0])
                )
            else:
                if self.cantidad > stock:
                    return {"success": False, "error": "La cantidad supera el stock disponible."}

                nuevo_id = self._generar_id_lista_compra()
                cursor.execute("""
                    INSERT INTO Lista_compra (ID_lista_compra, ID_inventario, ID_cliente, Cantidad_producto, Estado_lista_compra)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nuevo_id, self.inventario_id, self.cliente_id, self.cantidad, self._ESTADO_CARRITO))

            db.commit()

            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Agregar al carrito",
                    descripcion=f"Cliente ID: {self.cliente_id} agregó producto ID: {self.inventario_id} - Cantidad: {self.cantidad}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Carrito"
                )
                bitacora.registrar()

            return {"success": True, "message": "Producto agregado al carrito."}

        except Exception as e:
            db.rollback()
            print(f"Error en agregar_al_carrito: {e}")
            return {"success": False, "error": "Error al agregar al carrito."}
        finally:
            cursor.close()
            db.close()

    def actualizar_cantidad(self) -> Dict[str, Any]:
        error = self._validar_cliente(requerido=True)
        if error:
            return {"success": False, "error": error}

        error = self._validar_inventario()
        if error:
            return {"success": False, "error": error}

        # Si la cantidad es 0 o inválida negativa → eliminar
        try:
            cantidad_int = int(self.cantidad)
        except (ValueError, TypeError):
            return {"success": False, "error": "La cantidad debe ser un número entero válido."}

        if cantidad_int <= 0:
            self.eliminar_item()
            return {"success": True, "message": "Producto eliminado del carrito."}

        error = self._validar_cantidad()
        if error:
            return {"success": False, "error": error}

        db = self.__conexion_bd.conexion1()
        if not db:
            return {"success": False, "error": "No se pudo conectar a la base de datos."}

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
                (self.inventario_id,)
            )
            row = cursor.fetchone()
            stock = int(row[0] or 0) if row else 0
            if self.cantidad > stock:
                return {"success": False, "error": "La cantidad supera el stock disponible."}

            cursor.execute("""
                UPDATE Lista_compra
                SET Cantidad_producto = %s
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (self.cantidad, self.cliente_id, self.inventario_id, self._ESTADO_CARRITO))

            db.commit()
            return {"success": True}

        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_cantidad: {e}")
            return {"success": False, "error": "Error al actualizar cantidad."}
        finally:
            cursor.close()
            db.close()

    def eliminar_item(self) -> None:
        if not self.cliente_id or not self.inventario_id:
            return

        db = self.__conexion_bd.conexion1()
        if not db:
            return

        cursor = db.cursor()
        try:
            cursor.execute("""
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s AND ID_inventario = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (self.cliente_id, self.inventario_id, self._ESTADO_CARRITO))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()

    def vaciar_carrito(self) -> None:
        if not self.cliente_id:
            return

        db = self.__conexion_bd.conexion1()
        if not db:
            return

        cursor = db.cursor()
        try:
            cursor.execute("""
                DELETE FROM Lista_compra
                WHERE ID_cliente = %s
                  AND (Estado_lista_compra IS NULL OR Estado_lista_compra = %s)
            """, (self.cliente_id, self._ESTADO_CARRITO))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            cursor.close()
            db.close()