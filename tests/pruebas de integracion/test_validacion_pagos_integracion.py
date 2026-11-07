"""Pruebas de integración de ValidacionPagosModel contra MySQL real."""
import random

import pytest

from app.models.validacion_pagos import ValidacionPagosModel
from seed_helpers import (
    crear_cliente_temporal,
    crear_existencia_temporal,
    crear_producto_temporal,
    crear_venta_temporal,
    eliminar_cliente_temporal,
    eliminar_producto_temporal,
    eliminar_venta_temporal,
    limpiar_bitacora_por_descripcion,
)


CLASE_TELEFONO = "1"
MARCA_IPHONE = "1"
EMPLEADO_ADMIN = "12345678"
USUARIO_ADMIN = "USR-001"


def _cedula_cliente_aleatoria() -> str:
    return str(random.randint(10**7, 10**8 - 1))


@pytest.fixture
def venta_pendiente():
    """Cliente + producto + venta con Metodo_pago pendiente. Limpia al final."""
    cedula = _cedula_cliente_aleatoria()
    id_producto = None
    factura_id = None
    crear_cliente_temporal(cedula, nombre="Cliente", apellido="Pagos")
    try:
        id_producto = crear_producto_temporal(
            nombre="iPhone Pagos", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
        )
        id_inventario = crear_existencia_temporal(id_producto, existencia=10, costo=500.0)
        factura_id = crear_venta_temporal(
            cedula_cliente=cedula,
            id_inventario=id_inventario,
            empleado_id=EMPLEADO_ADMIN,
            monto=500.0,
            metodo="pago_movil",
            estado_pago="pendiente",
        )
        yield {
            "cliente_id": cedula,
            "id_producto": id_producto,
            "id_inventario": id_inventario,
            "factura_id": factura_id,
        }
    finally:
        if factura_id:
            eliminar_venta_temporal(factura_id)
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_cliente_temporal(cedula)
        limpiar_bitacora_por_descripcion("pago")


# ==================== LISTAR PAGOS ====================

class TestPagosPendientes:

    def test_devuelve_lista(self):
        assert isinstance(ValidacionPagosModel().obtener_pagos_pendientes(), list)

    def test_incluye_pago_pendiente_creado(self, venta_pendiente):
        info = venta_pendiente
        pendientes = ValidacionPagosModel().obtener_pagos_pendientes()

        factura = next(
            (p for p in pendientes if p["factura_id"] == info["factura_id"]), None
        )
        assert factura is not None
        assert factura["estado"] == "pendiente"
        assert factura["metodo_pago"] == "pago_movil"
        assert factura["Monto"] == 500.0
        assert isinstance(factura["Monto"], float)


class TestPagosAprobados:

    def test_devuelve_lista(self):
        assert isinstance(ValidacionPagosModel().obtener_pagos_aprobados(), list)


class TestPagosRechazados:

    def test_devuelve_lista(self):
        assert isinstance(ValidacionPagosModel().obtener_pagos_rechazados(), list)


# ==================== APROBAR ====================

class TestAprobarPago:

    def test_aprueba_pago_pendiente(self, venta_pendiente):
        info = venta_pendiente

        resultado = ValidacionPagosModel(
            usuario_id=USUARIO_ADMIN
        ).aprobar_pago(
            factura_id=info["factura_id"], empleado_id=EMPLEADO_ADMIN
        )

        assert resultado == {"success": True, "message": "Pago aprobado exitosamente."}

        aprobados = ValidacionPagosModel().obtener_pagos_aprobados()
        factura = next(
            (p for p in aprobados if p["factura_id"] == info["factura_id"]), None
        )
        assert factura is not None
        assert factura["estado"] == "aprobado"
        assert factura["Aprobado_por"] == EMPLEADO_ADMIN

    def test_factura_inexistente(self):
        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id="FAC-202601-XXXXXX", empleado_id=EMPLEADO_ADMIN
        )
        assert resultado == {
            "success": False,
            "error": "La factura 'FAC-202601-XXXXXX' no existe.",
        }

    def test_empleado_inexistente(self, venta_pendiente):
        info = venta_pendiente
        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=info["factura_id"], empleado_id="99999999"
        )
        assert resultado == {
            "success": False,
            "error": "El empleado con ID 99999999 no existe.",
        }

    def test_pago_ya_procesado(self, venta_pendiente):
        info = venta_pendiente
        ValidacionPagosModel().aprobar_pago(
            factura_id=info["factura_id"], empleado_id=EMPLEADO_ADMIN
        )

        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=info["factura_id"], empleado_id=EMPLEADO_ADMIN
        )
        assert resultado == {
            "success": False,
            "error": "El pago no está pendiente o ya fue procesado.",
        }

    @pytest.mark.parametrize(
        "factura_id, empleado_id, esperado",
        [
            pytest.param(
                "", EMPLEADO_ADMIN,
                "El ID de la factura no puede estar vacío.",
                id="factura-vacia",
            ),
            pytest.param(
                "con espacios", EMPLEADO_ADMIN,
                "El campo Factura solo puede contener letras, números y guiones.",
                id="factura-invalida",
            ),
            pytest.param(
                "FAC-202601-ABC123", "",
                "El ID del empleado no puede estar vacío.",
                id="empleado-vacio",
            ),
            pytest.param(
                "FAC-202601-ABC123", "12345",
                "El campo Empleado debe tener al menos 6 dígitos.",
                id="empleado-demasiado-corto",
            ),
        ],
    )
    def test_datos_invalidos(self, factura_id, empleado_id, esperado):
        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=factura_id, empleado_id=empleado_id
        )
        assert resultado == {"success": False, "error": esperado}


# ==================== RECHAZAR ====================

class TestRechazarPago:

    def test_rechaza_pago_pendiente(self, venta_pendiente):
        info = venta_pendiente

        resultado = ValidacionPagosModel(
            usuario_id=USUARIO_ADMIN
        ).rechazar_pago(
            factura_id=info["factura_id"],
            empleado_id=EMPLEADO_ADMIN,
            motivo="Comprobante ilegible",
        )

        assert resultado == {
            "success": True,
            "message": "Pago rechazado exitosamente.",
        }

        rechazados = ValidacionPagosModel().obtener_pagos_rechazados()
        factura = next(
            (p for p in rechazados if p["factura_id"] == info["factura_id"]), None
        )
        assert factura is not None
        assert factura["estado"] == "rechazado"
        assert factura["Motivo_rechazo"] == "Comprobante ilegible"
        assert factura["Rechazado_por"] == EMPLEADO_ADMIN

    def test_motivo_vacio(self, venta_pendiente):
        info = venta_pendiente
        resultado = ValidacionPagosModel().rechazar_pago(
            factura_id=info["factura_id"],
            empleado_id=EMPLEADO_ADMIN,
            motivo="",
        )
        assert resultado == {
            "success": False,
            "error": "El motivo de rechazo no puede estar vacío.",
        }

    def test_motivo_demasiado_corto(self, venta_pendiente):
        info = venta_pendiente
        resultado = ValidacionPagosModel().rechazar_pago(
            factura_id=info["factura_id"],
            empleado_id=EMPLEADO_ADMIN,
            motivo="abc",
        )
        assert resultado == {
            "success": False,
            "error": "El campo Motivo del rechazo debe tener al menos 5 caracteres.",
        }


# ==================== DETALLE ====================

class TestObtenerDetalleVenta:

    def test_factura_sin_detalle_devuelve_vacio(self, venta_pendiente):
        info = venta_pendiente
        resultado = ValidacionPagosModel(
            factura_id=info["factura_id"]
        ).obtener_detalle_venta()
        assert resultado == []

    def test_sin_factura(self):
        assert ValidacionPagosModel().obtener_detalle_venta() == []

    def test_factura_invalida(self):
        assert ValidacionPagosModel(
            factura_id="con espacios"
        ).obtener_detalle_venta() == []


# ==================== REPORTES ====================

class TestObtenerReportesPagos:

    def test_filtros_vacios(self):
        resultado = ValidacionPagosModel().obtener_reportes_pagos({})

        assert resultado["success"] is True
        assert "pagos" in resultado
        assert isinstance(resultado["total"], int)
        assert isinstance(resultado["total_monto"], float)

    def test_filtra_por_estado_pendiente(self, venta_pendiente):
        info = venta_pendiente
        resultado = ValidacionPagosModel().obtener_reportes_pagos(
            {"estado": "pendiente", "q": info["cliente_id"]}
        )

        assert resultado["success"] is True
        assert resultado["total"] >= 1

    def test_fecha_invalida(self):
        resultado = ValidacionPagosModel().obtener_reportes_pagos(
            {"fecha_desde": "31-12-2025"}
        )
        assert resultado["success"] is False
        assert "Formato de fecha inválido" in resultado["error"]


# ==================== ACTUALIZAR FECHA ====================

class TestActualizarFechaPago:

    def test_actualiza_fecha(self, venta_pendiente):
        info = venta_pendiente
        ValidacionPagosModel(
            factura_id=info["factura_id"]
        ).actualizar_fecha_pago()

        from app.models.database import conectar
        db = conectar().conexion1()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT Fecha_pago FROM Metodo_pago WHERE ID_factura = %s",
            (info["factura_id"],),
        )
        fila = cursor.fetchone()
        cursor.close()
        db.close()

        assert fila is not None
        assert fila["Fecha_pago"] is not None

    def test_sin_factura_no_falla(self):
        ValidacionPagosModel().actualizar_fecha_pago()  # no debe lanzar


# ==================== GETTERS ====================

class TestGetters:

    def test_metodos_pago_disponibles(self):
        metodos = ValidacionPagosModel().obtener_metodos_pago_disponibles()
        assert "pago_movil" in metodos
        assert "zelle" in metodos
        assert "binance" in metodos

    def test_monedas_disponibles(self):
        monedas = ValidacionPagosModel().obtener_monedas_disponibles()
        assert monedas == ["USD", "VES", "USDT"]