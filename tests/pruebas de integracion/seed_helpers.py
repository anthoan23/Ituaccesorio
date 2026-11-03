"""Helpers para crear/borrar datos base temporales en las BD de test.
"""
from __future__ import annotations

import uuid

from app.models.database import conectar


def _cursor():
    db = conectar().conexion1()
    if not db:
        raise RuntimeError("No se pudo conectar a ituaccesoriobd (¿está levantado el compose de test?)")
    return db, db.cursor()


def crear_producto_temporal(nombre: str = None, clase: str = "1", marca: str = "1") -> str:
    """Crea un Producto con ID único y devuelve su ID. NO crea inventario."""
    nombre = nombre or f"ProductoTest-{uuid.uuid4().hex[:6]}"
    db, cursor = _cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(CAST(ID_producto AS UNSIGNED)), 0) + 1 FROM Producto")
        siguiente = cursor.fetchone()[0]
        id_producto = str(siguiente)
        cursor.execute(
            "INSERT INTO Producto (ID_producto, ID_Clase, ID_marca, Nombre_producto, Descripcion) "
            "VALUES (%s, %s, %s, %s, %s)",
            (id_producto, clase, marca, nombre, "Producto temporal de pruebas"),
        )
        db.commit()
        return id_producto
    finally:
        cursor.close()
        db.close()


def crear_existencia_temporal(
    id_producto: str, existencia: int = 10, costo: float = 100.00
) -> str:
    """Crea una fila en Existencias_productos y devuelve su ID_inventario."""
    db, cursor = _cursor()
    try:
        cursor.execute(
            "SELECT CONCAT('INV', LPAD(COALESCE(MAX(CAST(SUBSTRING(ID_inventario, 4) AS UNSIGNED)), 0) + 1, 6, '0')) FROM Existencias_productos"
        )
        id_inventario = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO Existencias_productos (ID_inventario, ID_producto, Existencia, Costo_venta, ID_categoria) "
            "VALUES (%s, %s, %s, %s, NULL)",
            (id_inventario, id_producto, existencia, costo),
        )
        db.commit()
        return id_inventario
    finally:
        cursor.close()
        db.close()


def eliminar_producto_temporal(id_producto: str) -> None:
    """Borra el producto y, por FK, sus existencias (si no hay otras FKs)."""
    db, cursor = _cursor()
    try:
        cursor.execute("DELETE FROM Existencias_productos WHERE ID_producto = %s", (id_producto,))
        cursor.execute("DELETE FROM Producto WHERE ID_producto = %s", (id_producto,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def eliminar_existencia_temporal(id_inventario: str) -> None:
    db, cursor = _cursor()
    try:
        cursor.execute("DELETE FROM Existencias_productos WHERE ID_inventario = %s", (id_inventario,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def crear_cliente_temporal(cedula: str, nombre: str = "Cliente", apellido: str = "Prueba") -> str:
    """Crea Cliente + Persona_natural con la cédula dada. Devuelve la cédula."""
    db, cursor = _cursor()
    try:
        cursor.execute(
            "INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente) "
            "VALUES (%s, %s, %s, %s)",
            (cedula, "Barquisimeto", "0414123456", f"{cedula}@mail.com"),
        )
        cursor.execute(
            "INSERT INTO Persona_natural (ID_cliente, Nombre_cliente, Apellido_cliente) "
            "VALUES (%s, %s, %s)",
            (cedula, nombre, apellido),
        )
        db.commit()
        return cedula
    finally:
        cursor.close()
        db.close()


def eliminar_cliente_temporal(cedula: str) -> None:
    db, cursor = _cursor()
    try:
        cursor.execute("DELETE FROM Persona_natural WHERE ID_cliente = %s", (cedula,))
        cursor.execute("DELETE FROM Cliente WHERE ID_cliente = %s", (cedula,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def crear_delivery_temporal(cedula: str, nombre: str = "Delivery", apellido: str = "Prueba") -> str:
    db, cursor = _cursor()
    try:
        cursor.execute(
            "INSERT INTO Personal_delivery (Cedula_delivery, Nombre_delivery, Apellido_delivery) "
            "VALUES (%s, %s, %s)",
            (cedula, nombre, apellido),
        )
        db.commit()
        return cedula
    finally:
        cursor.close()
        db.close()


def eliminar_delivery_temporal(cedula: str) -> None:
    db, cursor = _cursor()
    try:
        cursor.execute("DELETE FROM Personal_delivery WHERE Cedula_delivery = %s", (cedula,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def crear_venta_temporal(
    cedula_cliente: str,
    id_inventario: str,
    empleado_id: str = "12345678",
    monto: float = 500.0,
    metodo: str = "pago_movil",
    estado_pago: str = "pendiente",
    moneda: str = "VES",
) -> str:
    """Crea una Venta + Metodo_pago pendiente. Devuelve el ID_factura.

    Requiere que el cliente y el inventario ya existan (usa crear_cliente_temporal
    y crear_existencia_temporal antes).
    """
    import uuid
    from datetime import datetime

    db, cursor = _cursor()
    try:
        factura_id = f"FAC-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        cursor.execute(
            "INSERT INTO Venta (ID_factura, ID_empleado, ID_cliente, Moneda, Fecha_venta) "
            "VALUES (%s, %s, %s, %s, %s)",
            (factura_id, empleado_id, cedula_cliente, moneda, datetime.now()),
        )
        cursor.execute(
            "INSERT INTO Metodo_pago "
            "(ID_factura, Moneda, Fecha_pago, Metodo, Referencia, Monto, Estado_pago) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                factura_id,
                moneda,
                datetime.now(),
                metodo,
                f"REF-{uuid.uuid4().hex[:8]}",
                monto,
                estado_pago,
            ),
        )
        db.commit()
        return factura_id
    finally:
        cursor.close()
        db.close()


def eliminar_venta_temporal(factura_id: str) -> None:
    """Borra la venta y sus FKs (detalle, método de pago, entrega)."""
    db, cursor = _cursor()
    try:
        cursor.execute("DELETE FROM Detalle_venta WHERE ID_factura = %s", (factura_id,))
        cursor.execute("DELETE FROM Entrega WHERE ID_factura = %s", (factura_id,))
        cursor.execute("DELETE FROM Metodo_pago WHERE ID_factura = %s", (factura_id,))
        cursor.execute("DELETE FROM Venta WHERE ID_factura = %s", (factura_id,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def limpiar_bitacora_por_descripcion(fragmento: str) -> None:
    """Borra registros de bitácora cuyo campo descripcion contenga el fragmento."""
    db = conectar().conexion2()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM bitacora WHERE descripcion LIKE %s", (f"%{fragmento}%",)
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()