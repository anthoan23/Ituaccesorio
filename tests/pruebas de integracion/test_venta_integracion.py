"""Pruebas de integración de VentaModel contra MySQL real."""
import random
import re

import pytest

from app.models.venta import VentaModel
from seed_helpers import (
    crear_cliente_temporal,
    crear_existencia_temporal,
    crear_producto_temporal,
    eliminar_cliente_temporal,
    eliminar_producto_temporal,
)


CLASE_TELEFONO = "1"
MARCA_IPHONE = "1"
EMPLEADO_ADMIN = "12345678"
USUARIO_ADMIN = "USR-001"
PATRON_FACTURA = re.compile(r"^FAC-\d{6}-[0-9A-F]{6}$")


def _cedula_cliente_aleatoria() -> str:
    return str(random.randint(10**7, 10**8 - 1))


@pytest.fixture
def cliente_producto_stock():
    """Cliente + producto con stock. Captura stock inicial y lo restaura."""
    cedula = _cedula_cliente_aleatoria()
    id_producto = None
    crear_cliente_temporal(cedula, nombre="Cliente", apellido="Venta")
    try:
        id_producto = crear_producto_temporal(
            nombre="iPhone Venta", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
        )
        id_inventario = crear_existencia_temporal(id_producto, existencia=10, costo=500.0)
        stock_inicial = _stock(id_inventario)
        yield {
            "cliente_id": cedula,
            "id_producto": id_producto,
            "id_inventario": id_inventario,
            "stock_inicial": stock_inicial,
        }
    finally:
        _limpiar_ventas_del_cliente(cedula)
        _restaurar_stock(
            _stock_por_id_producto(id_producto) if id_producto else None
        )
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_cliente_temporal(cedula)


def _stock(id_inventario: str) -> int:
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return 0
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
            (id_inventario,),
        )
        fila = cursor.fetchone()
        return int(fila[0] or 0) if fila else 0
    finally:
        cursor.close()
        db.close()


def _stock_por_id_producto(id_producto: str) -> dict:
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return {}
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT ID_inventario, Existencia FROM Existencias_productos WHERE ID_producto = %s",
            (id_producto,),
        )
        return {fila[0]: int(fila[1] or 0) for fila in cursor.fetchall()}
    finally:
        cursor.close()
        db.close()


def _restaurar_stock(stocks: dict) -> None:
    if not stocks:
        return
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        for id_inv, cant in stocks.items():
            cursor.execute(
                "UPDATE Existencias_productos SET Existencia = %s WHERE ID_inventario = %s",
                (cant, id_inv),
            )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _limpiar_ventas_del_cliente(cedula: str) -> None:
    """Borra ventas (y sus FKs) del cliente."""
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute("SELECT ID_factura FROM Venta WHERE ID_cliente = %s", (cedula,))
        facturas = [f[0] for f in cursor.fetchall()]
        for factura in facturas:
            cursor.execute("DELETE FROM Detalle_venta WHERE ID_factura = %s", (factura,))
            cursor.execute("DELETE FROM Metodo_pago WHERE ID_factura = %s", (factura,))
            cursor.execute("DELETE FROM Venta WHERE ID_factura = %s", (factura,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


# ==================== CREAR VENTA ====================

class TestCrearVentaDesdeCarrito:

    def test_venta_valida(self, cliente_producto_stock):
        info = cliente_producto_stock
        factura_id = None
        try:
            modelo = VentaModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[
                    {
                        "producto_id": info["id_inventario"],
                        "cantidad": 2,
                        "precio_usd": 500.0,
                    }
                ],
                metodo_pago="efectivo_usd",
            )
            factura_id = modelo.crear_venta_desde_carrito()

            assert PATRON_FACTURA.match(factura_id)
            assert modelo.factura_id == factura_id

            # Verificar que la venta existe en BD
            from app.models.database import conectar
            db = conectar().conexion1()
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT ID_factura, ID_cliente, Moneda FROM Venta WHERE ID_factura = %s",
                (factura_id,),
            )
            venta = cursor.fetchone()
            cursor.close()
            db.close()

            assert venta is not None
            assert venta["ID_cliente"] == info["cliente_id"]
            assert venta["Moneda"] == "USD"

            # Verificar que el stock bajó
            assert _stock(info["id_inventario"]) == info["stock_inicial"] - 2
        finally:
            if factura_id:
                _limpiar_ventas_del_cliente(info["cliente_id"])

    def test_cliente_inexistente(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="no existe"):
            VentaModel(
                cliente_id="99999999",
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 1}],
                metodo_pago="efectivo_usd",
            ).crear_venta_desde_carrito()

    def test_carrito_vacio(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="carrito no puede estar vacío"):
            VentaModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[],
                metodo_pago="efectivo_usd",
            ).crear_venta_desde_carrito()

    def test_stock_insuficiente(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="Stock insuficiente"):
            VentaModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[
                    {"producto_id": info["id_inventario"], "cantidad": 999}
                ],
                metodo_pago="efectivo_usd",
            ).crear_venta_desde_carrito()

    def test_metodo_pago_invalido(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="Método de pago inválido"):
            VentaModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 1}],
                metodo_pago="bitcoin",
            ).crear_venta_desde_carrito()

    def test_producto_duplicado_en_carrito(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="aparece múltiples veces"):
            VentaModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[
                    {"producto_id": info["id_inventario"], "cantidad": 1},
                    {"producto_id": info["id_inventario"], "cantidad": 1},
                ],
                metodo_pago="efectivo_usd",
            ).crear_venta_desde_carrito()


# ==================== REGISTRO DE PAGO ====================

class TestGuardarRegistroPago:

    def test_registra_pago(self, cliente_producto_stock):
        info = cliente_producto_stock
        factura_id = None
        try:
            modelo = VentaModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 1}],
                metodo_pago="pago_movil",
            )
            factura_id = modelo.crear_venta_desde_carrito()

            VentaModel(
                factura_id=factura_id,
                metodo_pago="pago_movil",
                estado_pago="pendiente",
                datos_pago={
                    "referencia": "123456789",
                    "monto": 500.0,
                },
            ).guardar_registro_pago()

            # Verificar
            from app.models.database import conectar
            db = conectar().conexion1()
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT Metodo, Referencia, Monto, Estado_pago, Moneda "
                "FROM Metodo_pago WHERE ID_factura = %s",
                (factura_id,),
            )
            pago = cursor.fetchone()
            cursor.close()
            db.close()

            assert pago is not None
            assert pago["Metodo"] == "pago_movil"
            assert pago["Referencia"] == "123456789"
            assert float(pago["Monto"]) == 500.0
            assert pago["Estado_pago"] == "pendiente"
            assert pago["Moneda"] == "VES"
        finally:
            if factura_id:
                _limpiar_ventas_del_cliente(info["cliente_id"])

    def test_sin_factura_id(self):
        with pytest.raises(ValueError, match="ID de la factura no puede estar vacío"):
            VentaModel(metodo_pago="pago_movil").guardar_registro_pago()

    def test_metodo_pago_vacio(self):
        with pytest.raises(ValueError, match="método de pago no puede estar vacío"):
            VentaModel(factura_id="FAC-202601-ABC123").guardar_registro_pago()

    def test_referencia_obligatoria_para_pago_movil(self):
        with pytest.raises(ValueError, match="referencia es obligatoria"):
            VentaModel(
                factura_id="FAC-202601-ABC123",
                metodo_pago="pago_movil",
                datos_pago={},
            ).guardar_registro_pago()


# ==================== VENTAS DEL DÍA ====================

class TestObtenerVentasHoy:

    def test_devuelve_estructura(self):
        resultado = VentaModel().obtener_ventas_hoy()

        assert "total_ventas" in resultado
        assert "cantidad_ventas" in resultado
        assert "moneda" in resultado
        assert isinstance(resultado["total_ventas"], float)
        assert isinstance(resultado["cantidad_ventas"], int)

    def test_incluye_venta_recien_creada(self, cliente_producto_stock):
        info = cliente_producto_stock
        factura_id = None
        try:
            factura_id = VentaModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 1}],
                metodo_pago="efectivo_usd",
            ).crear_venta_desde_carrito()

            resultado = VentaModel().obtener_ventas_hoy()
            assert resultado["cantidad_ventas"] >= 1
        finally:
            if factura_id:
                _limpiar_ventas_del_cliente(info["cliente_id"])