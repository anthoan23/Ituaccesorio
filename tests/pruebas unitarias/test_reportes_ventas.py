"""Pruebas unitarias de la clase ReportesVentasModel
(app.models.reportes_ventas).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models.reportes_ventas import ReportesVentasModel
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
CLIENTE_MINIMO = "123456"  # 6 dígitos (mínimo)
CLIENTE_MAXIMO = "12345678"  # 8 dígitos (máximo)

PRODUCTO_MINIMO = "1"  # 1 carácter (mínimo)
PRODUCTO_MAXIMO = "1234567890"  # 10 caracteres (máximo)

EMPLEADO_VALIDO = "12345678"
FACTURA_VALIDA = "FAC-202611-ABC123"
FACTURA_GENERADA = "FAC-202611-ABCDEF"
FECHA_FIJA = datetime(2026, 11, 2, 10, 30, 0)

ITEM_VALIDO = {
    "producto_id": PRODUCTO_MINIMO,
    "cantidad": 2,
    "precio_usd": "10.50",
}


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


def preparar_factura():
    """Parchea uuid y datetime para generar una factura determinista."""
    uuid_parche = patch("app.models.reportes_ventas.uuid.uuid4")
    datetime_parche = patch("app.models.reportes_ventas.datetime")
    uuid_mock = uuid_parche.start()
    datetime_mock = datetime_parche.start()
    uuid_mock.return_value.hex = "abcdef123456"
    datetime_mock.now.return_value = FECHA_FIJA
    return uuid_parche, datetime_parche


class TestObtenerReportesVentas:

    def test_con_filtros_y_resumen(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "factura_id": FACTURA_VALIDA,
                "monto_pagado": Decimal("10.50"),
                "estado": "pendiente",
                "tipo_venta": "Local",
            },
            {
                "factura_id": "FAC-202611-DEF456",
                "monto_pagado": Decimal("5.25"),
                "estado": "aprobado",
                "tipo_venta": "Online",
            },
            {
                "factura_id": "FAC-202611-GHI789",
                "monto_pagado": Decimal("1.00"),
                "estado": "rechazado",
                "tipo_venta": "Online",
            },
        ]

        resultado = ReportesVentasModel().obtener_reportes_ventas(
            {
                "q": "ana",
                "estado": "pendiente",
                "metodo_pago": "zelle",
                "moneda": "USD",
                "fecha_desde": "2026-01-01",
                "fecha_hasta": "2026-01-31",
                "monto_min": "1",
                "monto_max": "100",
            }
        )

        assert resultado["success"] is True
        assert resultado["total"] == 3
        assert resultado["total_monto"] == pytest.approx(16.75)
        assert resultado["pendientes"] == 1
        assert resultado["aprobados"] == 1
        assert resultado["rechazados"] == 1
        assert resultado["locales"] == 1
        assert resultado["online"] == 2
        assert resultado["ventas"][0]["monto_pagado"] == 10.5
        consulta = llamada_con(cursor, "FROM Venta v")
        assert "v.ID_factura LIKE %s" in consulta.args[0]
        assert consulta.args[1] == (
            "%ana%",
            "%ana%",
            "%ana%",
            "pendiente",
            "zelle",
            "USD",
            "2026-01-01",
            "2026-01-31",
            "1",
            "100",
        )
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_filtros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        resultado = ReportesVentasModel().obtener_reportes_ventas({})

        assert resultado == {
            "success": True,
            "ventas": [],
            "total": 0,
            "total_monto": 0,
            "pendientes": 0,
            "aprobados": 0,
            "rechazados": 0,
            "locales": 0,
            "online": 0,
        }
        consulta = llamada_con(cursor, "FROM Venta v")
        assert consulta.args[1] == ()
        assert "1=1" in consulta.args[0]

    def test_monto_nulo_no_rompe_el_total(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "monto_pagado": None,
                "estado": "pendiente",
                "tipo_venta": "Online",
            },
            {
                "monto_pagado": Decimal("7.50"),
                "estado": "aprobado",
                "tipo_venta": "Local",
            },
        ]

        resultado = ReportesVentasModel().obtener_reportes_ventas({})

        assert resultado["total_monto"] == 7.5
        assert resultado["pendientes"] == 1
        assert resultado["aprobados"] == 1

    @pytest.mark.parametrize(
        "filtros, esperado",
        [
            pytest.param(
                {"q": "Bus#1"},
                "El campo Búsqueda no puede contener caracteres especiales.",
                id="busqueda-caracteres-invalidos",
            ),
            pytest.param(
                {"q": "B" * 101},
                "El campo Búsqueda no puede tener más de 100 caracteres.",
                id="busqueda-demasiado-larga",
            ),
            pytest.param(
                {"fecha_desde": "2026/01/01"},
                "Formato de fecha inválido. Use YYYY-MM-DD.",
                id="fecha-desde-invalida",
            ),
            pytest.param(
                {"fecha_hasta": "01-01-2026"},
                "Formato de fecha inválido. Use YYYY-MM-DD.",
                id="fecha-hasta-invalida",
            ),
            pytest.param(
                {"fecha_desde": "2026-02-01", "fecha_hasta": "2026-01-01"},
                "La fecha 'desde' no puede ser mayor que la fecha 'hasta'.",
                id="rango-de-fechas-invertido",
            ),
            pytest.param(
                {"monto_min": "abc"},
                "El campo Monto mínimo debe ser un número decimal válido con hasta 2 decimales.",
                id="monto-minimo-invalido",
            ),
            pytest.param(
                {"monto_max": "10000000000"},
                "El campo Monto máximo debe ser menor o igual a 9999999999.99.",
                id="monto-maximo-excedido",
            ),
            pytest.param(
                {"monto_min": "100", "monto_max": "50"},
                "El monto mínimo no puede ser mayor que el monto máximo.",
                id="rango-de-montos-invertido",
            ),
        ],
    )
    def test_filtros_invalidos_no_tocan_la_bd(
        self, conexion_falsa, filtros, esperado
    ):
        db, cursor = conexion_falsa

        resultado = ReportesVentasModel().obtener_reportes_ventas(filtros)

        assert resultado == {
            "success": False,
            "error": esperado,
            "ventas": [],
            "total": 0,
        }
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = ReportesVentasModel().obtener_reportes_ventas({})

        assert resultado == {
            "success": False,
            "error": "Error al conectar",
            "ventas": [],
            "total": 0,
        }

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = ReportesVentasModel().obtener_reportes_ventas({})

        assert resultado == {
            "success": False,
            "error": "fallo simulado",
            "ventas": [],
            "total": 0,
        }
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestObtenerDetalleVentaCompleto:

    def test_venta_con_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "factura_id": FACTURA_VALIDA,
            "monto_total": Decimal("12.50"),
        }
        cursor.fetchall.return_value = [
            {
                "ID_inventario": PRODUCTO_MINIMO,
                "Cantidad_articulo": 2,
                "precio_unitario": Decimal("10.00"),
                "Nombre_producto": "Cable USB",
            },
            {
                "ID_inventario": PRODUCTO_MAXIMO,
                "Cantidad_articulo": 1,
                "precio_unitario": 5.0,
                "Nombre_producto": "Cargador",
            },
        ]

        resultado = ReportesVentasModel(
            factura_id=FACTURA_VALIDA
        ).obtener_detalle_venta_completo()

        assert resultado["success"] is True
        assert resultado["venta"]["monto_total"] == 12.5
        assert resultado["productos"][0]["precio_unitario"] == 10.0
        assert resultado["productos"][0]["subtotal"] == 20.0
        assert resultado["productos"][1]["subtotal"] == 5.0
        assert resultado["total_venta"] == 25.0
        assert cursor.execute.call_args_list[-1].args[1] == (FACTURA_VALIDA,)
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_factura(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = ReportesVentasModel().obtener_detalle_venta_completo()

        assert resultado == {
            "success": False,
            "error": "Factura no especificada",
        }
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "factura, esperado",
        [
            pytest.param(
                "   ",
                "El campo Factura no puede estar vacío.",
                id="factura-en-blanco",
            ),
            pytest.param(
                "FAC#1",
                "El campo Factura solo puede contener letras, números y guiones.",
                id="factura-caracteres-invalidos",
            ),
            pytest.param(
                "FAC-202611-ABCDEFGHIJ",
                "El campo Factura no puede tener más de 20 caracteres.",
                id="factura-demasiado-larga",
            ),
        ],
    )
    def test_factura_invalida(self, conexion_falsa, factura, esperado):
        db, cursor = conexion_falsa

        resultado = ReportesVentasModel(
            factura_id=factura
        ).obtener_detalle_venta_completo()

        assert resultado == {"success": False, "error": esperado}
        cursor.execute.assert_not_called()

    def test_venta_no_encontrada(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = ReportesVentasModel(
            factura_id=FACTURA_VALIDA
        ).obtener_detalle_venta_completo()

        assert resultado == {"success": False, "error": "Venta no encontrada"}
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = ReportesVentasModel(
            factura_id=FACTURA_VALIDA
        ).obtener_detalle_venta_completo()

        assert resultado == {"success": False, "error": "Error al conectar"}

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = ReportesVentasModel(
            factura_id=FACTURA_VALIDA
        ).obtener_detalle_venta_completo()

        assert resultado == {"success": False, "error": "fallo simulado"}
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestObtenerVentasLocales:

    def test_con_busqueda_y_fecha(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "factura_id": FACTURA_VALIDA,
                "monto": Decimal("15.75"),
                "tipo_venta": "Local",
            },
            {
                "factura_id": "FAC-202611-DEF456",
                "monto": None,
                "tipo_venta": "Local",
            },
        ]

        resultado = ReportesVentasModel().obtener_ventas_locales(
            busqueda="ana", fecha="2026-01-15"
        )

        assert resultado[0]["monto"] == 15.75
        assert resultado[1]["monto"] is None
        consulta = llamada_con(cursor, "FROM Venta v")
        assert "mp.Referencia LIKE 'LOCAL-%'" in consulta.args[0]
        assert consulta.args[1] == (
            "%ana%",
            "%ana%",
            "%ana%",
            "%ana%",
            "2026-01-15",
        )
        assert "LIMIT 100" in consulta.args[0]
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_filtros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        resultado = ReportesVentasModel().obtener_ventas_locales()

        assert resultado == []
        consulta = llamada_con(cursor, "FROM Venta v")
        assert consulta.args[1] == ()

    @pytest.mark.parametrize(
        "busqueda, fecha",
        [
            pytest.param("Bus#1", None, id="busqueda-invalida"),
            pytest.param("", "2026/01/15", id="fecha-invalida"),
            pytest.param("ana", "15-01-2026", id="fecha-con-formato-invalido"),
        ],
    )
    def test_filtros_invalidos_no_tocan_la_bd(
        self, conexion_falsa, busqueda, fecha
    ):
        db, cursor = conexion_falsa

        resultado = ReportesVentasModel().obtener_ventas_locales(
            busqueda=busqueda, fecha=fecha
        )

        assert resultado == []
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = ReportesVentasModel().obtener_ventas_locales()

        assert resultado == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = ReportesVentasModel().obtener_ventas_locales()

        assert resultado == []
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestRegistrarVentaLocal:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (10,)]
        uuid_parche, datetime_parche = preparar_factura()

        try:
            resultado = ReportesVentasModel(
                cliente_id=CLIENTE_MINIMO,
                empleado_id=EMPLEADO_VALIDO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).registrar_venta_local()
        finally:
            uuid_parche.stop()
            datetime_parche.stop()

        assert resultado == FACTURA_GENERADA
        insert_venta = llamada_con(cursor, "INSERT INTO Venta")
        assert insert_venta.args[1] == (
            FACTURA_GENERADA,
            EMPLEADO_VALIDO,
            CLIENTE_MINIMO,
            "USD",
            FECHA_FIJA,
        )
        insert_detalle = llamada_con(cursor, "INSERT INTO Detalle_venta")
        assert insert_detalle.args[1] == (
            PRODUCTO_MINIMO,
            FACTURA_GENERADA,
            2,
        )
        insert_pago = llamada_con(cursor, "INSERT INTO Metodo_pago")
        assert insert_pago.args[1] == (
            FACTURA_GENERADA,
            "USD",
            FECHA_FIJA,
            "zelle",
            "LOCAL-ABCDEF",
            21.0,
            "aprobado",
            EMPLEADO_VALIDO,
            FECHA_FIJA,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_dos_items_suman_el_total(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (10,), (5,)]
        uuid_parche, datetime_parche = preparar_factura()

        try:
            ReportesVentasModel(
                cliente_id=CLIENTE_MAXIMO,
                empleado_id=EMPLEADO_VALIDO,
                items=[
                    ITEM_VALIDO,
                    {
                        "producto_id": PRODUCTO_MAXIMO,
                        "cantidad": 1,
                        "precio_usd": 5,
                    },
                ],
                metodo_pago="efectivo_usd",
            ).registrar_venta_local()
        finally:
            uuid_parche.stop()
            datetime_parche.stop()

        insert_pago = llamada_con(cursor, "INSERT INTO Metodo_pago")
        assert insert_pago.args[1][5] == pytest.approx(26.0)

    @pytest.mark.parametrize(
        "cliente, esperado",
        [
            pytest.param(
                "",
                "El campo Cliente es obligatorio.",
                id="cliente-vacio",
            ),
            pytest.param(
                "12345",
                "El campo Cliente debe tener al menos 6 dígitos.",
                id="cliente-demasiado-corto",
            ),
            pytest.param(
                "123456789",
                "El campo Cliente no puede tener más de 8 dígitos.",
                id="cliente-demasiado-largo",
            ),
            pytest.param(
                "12345a",
                "El campo Cliente solo puede contener números.",
                id="cliente-no-numerico",
            ),
        ],
    )
    def test_cliente_invalido(self, conexion_falsa, cliente, esperado):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as excinfo:
            ReportesVentasModel(
                cliente_id=cliente,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).registrar_venta_local()

        assert str(excinfo.value) == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "items, esperado",
        [
            pytest.param([], "Agrega al menos un producto.", id="sin-items"),
            pytest.param(
                ["producto"],
                "El producto #1 no tiene formato válido.",
                id="item-no-dict",
            ),
            pytest.param(
                [{"cantidad": 1}],
                "El producto #1 no tiene ID válido.",
                id="sin-id",
            ),
            pytest.param(
                [{"producto_id": "12345678901", "cantidad": 1}],
                "El campo ID del producto #1 no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                [{"producto_id": "INV#1", "cantidad": 1}],
                "El campo ID del producto #1 solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
            pytest.param(
                [{"producto_id": PRODUCTO_MINIMO, "cantidad": ""}],
                "El campo Cantidad del producto #1 no puede estar vacío.",
                id="cantidad-vacia",
            ),
            pytest.param(
                [{"producto_id": PRODUCTO_MINIMO, "cantidad": "abc"}],
                "El campo Cantidad del producto #1 solo puede contener números.",
                id="cantidad-no-numerica",
            ),
        ],
    )
    def test_items_invalidos(self, conexion_falsa, items, esperado):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as excinfo:
            ReportesVentasModel(
                cliente_id=CLIENTE_MINIMO,
                items=items,
                metodo_pago="zelle",
            ).registrar_venta_local()

        assert str(excinfo.value) == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "metodo, esperado",
        [
            pytest.param(
                None,
                "El campo Método de pago es obligatorio.",
                id="metodo-vacio",
            ),
            pytest.param(
                "tarjeta",
                "Método de pago 'tarjeta' no válido.",
                id="metodo-invalido",
            ),
        ],
    )
    def test_metodo_pago_invalido(self, conexion_falsa, metodo, esperado):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as excinfo:
            ReportesVentasModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago=metodo,
            ).registrar_venta_local()

        assert str(excinfo.value) == esperado
        cursor.execute.assert_not_called()

    def test_cliente_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with pytest.raises(ValueError) as excinfo:
            ReportesVentasModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).registrar_venta_local()

        assert str(excinfo.value) == (
            f"El cliente con ID '{CLIENTE_MINIMO}' no existe."
        )
        db.commit.assert_not_called()

    def test_stock_insuficiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,)]

        with pytest.raises(ValueError) as excinfo:
            ReportesVentasModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).registrar_venta_local()

        assert str(excinfo.value) == (
            f"Stock insuficiente para producto {PRODUCTO_MINIMO}. "
            "Disponible: 1"
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_cantidad_cero_detectada_al_registrar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,)]

        with pytest.raises(ValueError) as excinfo:
            ReportesVentasModel(
                cliente_id=CLIENTE_MINIMO,
                items=[{"producto_id": PRODUCTO_MINIMO, "cantidad": 0}],
                metodo_pago="zelle",
            ).registrar_venta_local()

        assert str(excinfo.value) == (
            f"Cantidad inválida para producto {PRODUCTO_MINIMO}"
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_conexion_caida_despues_de_validar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª conexión: verificar cliente; 2ª: la venta (sin conexión)
        with patch(
            "app.models.database.conectar.conexion1",
            side_effect=[db, None],
        ):
            with pytest.raises(RuntimeError) as excinfo:
                ReportesVentasModel(
                    cliente_id=CLIENTE_MINIMO,
                    items=[ITEM_VALIDO],
                    metodo_pago="zelle",
                ).registrar_venta_local()

        assert str(excinfo.value) == MENSAJE_ERROR_CONEXION

    def test_conexion_caida_en_verificacion_de_cliente(self, conexion_caída):
        with pytest.raises(ValueError) as excinfo:
            ReportesVentasModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).registrar_venta_local()

        assert str(excinfo.value) == (
            f"El cliente con ID '{CLIENTE_MINIMO}' no existe."
        )

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª: verificar cliente; 2ª: INSERT de la venta que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        with pytest.raises(Exception, match="fallo simulado"):
            ReportesVentasModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).registrar_venta_local()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cursor.close.assert_called()
        db.close.assert_called()

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (10,)]
        uuid_parche, datetime_parche = preparar_factura()

        try:
            with patch(
                "app.models.reportes_ventas.Bitacora"
            ) as bitacora_clase:
                ReportesVentasModel(
                    cliente_id=CLIENTE_MINIMO,
                    empleado_id=EMPLEADO_VALIDO,
                    items=[ITEM_VALIDO],
                    metodo_pago="zelle",
                    usuario_id="7",
                ).registrar_venta_local()
        finally:
            uuid_parche.stop()
            datetime_parche.stop()

        bitacora_clase.assert_called_once_with(
            accion="Registrar venta local",
            descripcion=(
                f"Venta local registrada: {FACTURA_GENERADA} - "
                f"Cliente: {CLIENTE_MINIMO} - Total: 21.0 USD"
            ),
            usuario_id="7",
            modulo_nombre="Reportes Ventas",
        )
        bitacora_clase.return_value.registrar.assert_called_once()


class TestObtenerMonedaSegunMetodo:

    @pytest.mark.parametrize(
        "metodo, esperado",
        [
            pytest.param("pago_movil", "VES", id="pago-movil"),
            pytest.param("efectivo_bs", "VES", id="efectivo-bs"),
            pytest.param("binance", "USDT", id="binance"),
            pytest.param("zelle", "USD", id="zelle"),
            pytest.param("efectivo_usd", "USD", id="efectivo-usd"),
            pytest.param(None, "USD", id="sin-metodo"),
        ],
    )
    def test_moneda(self, metodo, esperado):
        modelo = ReportesVentasModel(metodo_pago=metodo)

        assert modelo._obtener_moneda_segun_metodo() == esperado


class TestGenerarIdFactura:

    def test_formato_de_factura(self):
        with patch(
            "app.models.reportes_ventas.uuid.uuid4"
        ) as uuid_mock, patch(
            "app.models.reportes_ventas.datetime"
        ) as datetime_mock:
            uuid_mock.return_value.hex = "abcdef123456"
            datetime_mock.now.return_value = FECHA_FIJA

            factura = ReportesVentasModel()._generar_id_factura()

        assert factura == FACTURA_GENERADA


class TestVerificarClienteExiste:

    def test_cliente_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert (
            ReportesVentasModel()._verificar_cliente_existe(CLIENTE_MINIMO)
            is True
        )

    def test_cliente_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert (
            ReportesVentasModel()._verificar_cliente_existe(CLIENTE_MINIMO)
            is False
        )

    def test_conexion_caida(self, conexion_caída):
        assert (
            ReportesVentasModel()._verificar_cliente_existe(CLIENTE_MINIMO)
            is False
        )


class TestVerificarStockDisponible:

    def test_stock_suficiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (5,)

        assert ReportesVentasModel()._verificar_stock_disponible(
            PRODUCTO_MINIMO, 3
        ) == (True, 5)

    def test_stock_insuficiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (2,)

        assert ReportesVentasModel()._verificar_stock_disponible(
            PRODUCTO_MINIMO, 3
        ) == (False, 2)

    def test_producto_sin_registro(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert ReportesVentasModel()._verificar_stock_disponible(
            PRODUCTO_MINIMO, 1
        ) == (False, 0)

    def test_conexion_caida(self, conexion_caída):
        assert ReportesVentasModel()._verificar_stock_disponible(
            PRODUCTO_MINIMO, 1
        ) == (False, 0)
