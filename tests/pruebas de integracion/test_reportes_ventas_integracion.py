"""Pruebas de integración de ReportesVentasModel contra MySQL real."""
import random
import re
from datetime import datetime

import pytest

from app.models.reportes_ventas import ReportesVentasModel
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
    cedula = _cedula_cliente_aleatoria()
    id_producto = None
    crear_cliente_temporal(cedula, nombre="Cliente", apellido="Reportes")
    try:
        id_producto = crear_producto_temporal(
            nombre="iPhone Reportes", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
        )
        id_inventario = crear_existencia_temporal(id_producto, existencia=10, costo=500.0)
        yield {
            "cliente_id": cedula,
            "id_producto": id_producto,
            "id_inventario": id_inventario,
        }
    finally:
        _limpiar_ventas_del_cliente(cedula)
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_cliente_temporal(cedula)


def _limpiar_ventas_del_cliente(cedula: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute("SELECT ID_factura FROM Venta WHERE ID_cliente = %s", (cedula,))
        for (factura,) in cursor.fetchall():
            cursor.execute("DELETE FROM Detalle_venta WHERE ID_factura = %s", (factura,))
            cursor.execute("DELETE FROM Metodo_pago WHERE ID_factura = %s", (factura,))
            cursor.execute("DELETE FROM Venta WHERE ID_factura = %s", (factura,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


# ==================== REPORTES ====================

class TestObtenerReportesVentas:

    def test_filtros_vacios(self):
        resultado = ReportesVentasModel().obtener_reportes_ventas({})

        assert resultado["success"] is True
        assert "ventas" in resultado
        assert "total" in resultado
        assert isinstance(resultado["total"], int)

    def test_incluye_venta_local_creada(self, cliente_producto_stock):
        info = cliente_producto_stock
        try:
            ReportesVentasModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 1}],
                metodo_pago="efectivo_usd",
            ).registrar_venta_local()

            resultado = ReportesVentasModel().obtener_reportes_ventas(
                {"q": info["cliente_id"]}
            )

            assert resultado["success"] is True
            assert resultado["total"] >= 1
            assert resultado["locales"] >= 1
            factura = next(
                v for v in resultado["ventas"]
                if v["cliente_id"] == info["cliente_id"]
            )
            assert factura["tipo_venta"] == "Local"
            assert PATRON_FACTURA.match(factura["factura_id"])
        finally:
            _limpiar_ventas_del_cliente(info["cliente_id"])

    def test_filtro_fecha_desde_invalida(self):
        resultado = ReportesVentasModel().obtener_reportes_ventas(
            {"fecha_desde": "31-12-2025"}
        )
        assert resultado["success"] is False
        assert "Formato de fecha inválido" in resultado["error"]

    def test_filtro_fecha_desde_mayor_hasta(self):
        resultado = ReportesVentasModel().obtener_reportes_ventas(
            {"fecha_desde": "2026-12-31", "fecha_hasta": "2026-01-01"}
        )
        assert resultado["success"] is False
        assert "no puede ser mayor" in resultado["error"]

    def test_filtro_monto_min_mayor_max(self):
        resultado = ReportesVentasModel().obtener_reportes_ventas(
            {"monto_min": "100", "monto_max": "50"}
        )
        assert resultado["success"] is False
        assert "no puede ser mayor" in resultado["error"]


# ==================== DETALLE ====================

class TestObtenerDetalleVentaCompleto:

    def test_venta_existente(self, cliente_producto_stock):
        info = cliente_producto_stock
        factura_id = None
        try:
            factura_id = ReportesVentasModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 2}],
                metodo_pago="efectivo_usd",
            ).registrar_venta_local()

            resultado = ReportesVentasModel(
                factura_id=factura_id
            ).obtener_detalle_venta_completo()

            assert resultado["success"] is True
            assert resultado["venta"]["factura_id"] == factura_id
            assert resultado["venta"]["cliente_id"] == info["cliente_id"]
            assert len(resultado["productos"]) == 1
            assert resultado["productos"][0]["Cantidad_articulo"] == 2
            assert resultado["total_venta"] == 1000.0
        finally:
            if factura_id:
                _limpiar_ventas_del_cliente(info["cliente_id"])

    def test_sin_factura(self):
        resultado = ReportesVentasModel().obtener_detalle_venta_completo()
        assert resultado["success"] is False
        assert "no especificada" in resultado["error"]

    def test_factura_inexistente(self):
        resultado = ReportesVentasModel(
            factura_id="FAC-202601-XXXXXX"
        ).obtener_detalle_venta_completo()
        assert resultado["success"] is False
        assert "no encontrada" in resultado["error"]

    def test_factura_invalida(self):
        resultado = ReportesVentasModel(
            factura_id="con espacios"
        ).obtener_detalle_venta_completo()
        assert resultado["success"] is False


# ==================== VENTAS LOCALES ====================

class TestObtenerVentasLocales:

    def test_sin_filtros(self):
        resultado = ReportesVentasModel().obtener_ventas_locales()

        assert isinstance(resultado, list)
        assert all(v["tipo_venta"] == "Local" for v in resultado)

    def test_filtra_por_busqueda(self, cliente_producto_stock):
        info = cliente_producto_stock
        try:
            factura_id = ReportesVentasModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 1}],
                metodo_pago="efectivo_usd",
            ).registrar_venta_local()

            resultado = ReportesVentasModel().obtener_ventas_locales(
                busqueda=info["cliente_id"]
            )

            assert any(v["factura_id"] == factura_id for v in resultado)
        finally:
            _limpiar_ventas_del_cliente(info["cliente_id"])

    def test_busqueda_invalida(self):
        assert ReportesVentasModel().obtener_ventas_locales(
            busqueda="@#$"
        ) == []

    def test_fecha_invalida(self):
        assert ReportesVentasModel().obtener_ventas_locales(
            fecha="31-12-2025"
        ) == []


# ==================== REGISTRAR VENTA LOCAL ====================

class TestRegistrarVentaLocal:

    def test_venta_local_valida(self, cliente_producto_stock):
        info = cliente_producto_stock
        factura_id = None
        try:
            factura_id = ReportesVentasModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[
                    {"producto_id": info["id_inventario"], "cantidad": 3, "precio_usd": 500.0}
                ],
                metodo_pago="efectivo_usd",
                usuario_id=USUARIO_ADMIN,
            ).registrar_venta_local()

            assert PATRON_FACTURA.match(factura_id)

            # Verificar venta + pago
            from app.models.database import conectar
            db = conectar().conexion1()
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT v.ID_cliente, mp.Referencia, mp.Estado_pago, mp.Monto "
                "FROM Venta v JOIN Metodo_pago mp ON v.ID_factura = mp.ID_factura "
                "WHERE v.ID_factura = %s",
                (factura_id,),
            )
            fila = cursor.fetchone()
            cursor.close()
            db.close()

            assert fila is not None
            assert fila["ID_cliente"] == info["cliente_id"]
            assert fila["Referencia"].startswith("LOCAL-")
            assert fila["Estado_pago"] == "aprobado"
            assert float(fila["Monto"]) == 1500.0
        finally:
            if factura_id:
                _limpiar_ventas_del_cliente(info["cliente_id"])

    def test_cliente_inexistente(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="no existe"):
            ReportesVentasModel(
                cliente_id="99999999",
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 1}],
                metodo_pago="efectivo_usd",
            ).registrar_venta_local()

    def test_items_vacios(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="Agrega al menos un producto"):
            ReportesVentasModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[],
                metodo_pago="efectivo_usd",
            ).registrar_venta_local()

    def test_metodo_pago_invalido(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="no válido"):
            ReportesVentasModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 1}],
                metodo_pago="bitcoin",
            ).registrar_venta_local()

    def test_stock_insuficiente(self, cliente_producto_stock):
        info = cliente_producto_stock
        with pytest.raises(ValueError, match="Stock insuficiente"):
            ReportesVentasModel(
                cliente_id=info["cliente_id"],
                empleado_id=EMPLEADO_ADMIN,
                items=[{"producto_id": info["id_inventario"], "cantidad": 999}],
                metodo_pago="efectivo_usd",
            ).registrar_venta_local()