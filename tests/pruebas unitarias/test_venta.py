"""Pruebas unitarias de la clase VentaModel (app.models.venta).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from datetime import datetime
from unittest.mock import patch

import pytest

from app.models.venta import VentaModel
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
CLIENTE_MINIMO = "123456"  # 6 dígitos (mínimo)
CLIENTE_MAXIMO = "12345678"  # 8 dígitos (máximo)

PRODUCTO_MINIMO = "1"  # 1 carácter (mínimo)
PRODUCTO_MAXIMO = "1234567890"  # 10 caracteres (máximo)

CANTIDAD_MINIMA = 1
CANTIDAD_MAXIMA = 9999999999  # 10 dígitos (máximo)

EMPLEADO_VALIDO = "12345678"
FACTURA_GENERADA = "FAC-202611-ABCDEF"
FECHA_FIJA = datetime(2026, 11, 2, 10, 30, 0)

ITEM_VALIDO = {"producto_id": PRODUCTO_MINIMO, "cantidad": 2}
DATOS_PAGO_VALIDOS = {"referencia": "123456", "monto": "20.00"}


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


def preparar_factura():
    """Parchea uuid y datetime para generar una factura determinista."""
    uuid_parche = patch("app.models.venta.uuid.uuid4")
    datetime_parche = patch("app.models.venta.datetime")
    uuid_mock = uuid_parche.start()
    datetime_mock = datetime_parche.start()
    uuid_mock.return_value.hex = "abcdef123456"
    datetime_mock.now.return_value = FECHA_FIJA
    return uuid_parche, datetime_parche


class TestCrearVentaDesdeCarrito:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (10,)]
        uuid_parche, datetime_parche = preparar_factura()

        try:
            resultado = VentaModel(
                cliente_id=CLIENTE_MINIMO,
                empleado_id=EMPLEADO_VALIDO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).crear_venta_desde_carrito()
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
        update_stock = llamada_con(cursor, "UPDATE Existencias_productos")
        assert update_stock.args[1] == (2, PRODUCTO_MINIMO)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_item_con_clave_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (5,)]
        uuid_parche, datetime_parche = preparar_factura()

        try:
            resultado = VentaModel(
                cliente_id=CLIENTE_MAXIMO,
                items=[{"id": PRODUCTO_MAXIMO, "cantidad": CANTIDAD_MINIMA}],
                metodo_pago="efectivo_usd",
            ).crear_venta_desde_carrito()
        finally:
            uuid_parche.stop()
            datetime_parche.stop()

        assert resultado == FACTURA_GENERADA
        insert_detalle = llamada_con(cursor, "INSERT INTO Detalle_venta")
        assert insert_detalle.args[1] == (
            PRODUCTO_MAXIMO,
            FACTURA_GENERADA,
            CANTIDAD_MINIMA,
        )

    @pytest.mark.parametrize(
        "metodo, moneda",
        [
            pytest.param("pago_movil", "VES", id="pago-movil"),
            pytest.param("efectivo_bs", "VES", id="efectivo-bs"),
            pytest.param("binance", "USDT", id="binance"),
            pytest.param("zelle", "USD", id="zelle"),
            pytest.param("efectivo_usd", "USD", id="efectivo-usd"),
        ],
    )
    def test_moneda_segun_metodo_de_pago(self, conexion_falsa, metodo, moneda):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (10,)]
        uuid_parche, datetime_parche = preparar_factura()

        try:
            VentaModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago=metodo,
            ).crear_venta_desde_carrito()
        finally:
            uuid_parche.stop()
            datetime_parche.stop()

        insert_venta = llamada_con(cursor, "INSERT INTO Venta")
        assert insert_venta.args[1][3] == moneda

    @pytest.mark.parametrize(
        "cliente, esperado",
        [
            pytest.param(
                "",
                "El ID del cliente no puede estar vacío.",
                id="vacio",
            ),
            pytest.param(
                "12345",
                "El campo Cliente debe tener al menos 6 dígitos.",
                id="demasiado-corto",
            ),
            pytest.param(
                "123456789",
                "El campo Cliente no puede tener más de 8 dígitos.",
                id="demasiado-largo",
            ),
            pytest.param(
                "12345a",
                "El campo Cliente solo puede contener números.",
                id="no-numerico",
            ),
        ],
    )
    def test_cliente_invalido(self, conexion_falsa, cliente, esperado):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                cliente_id=cliente,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).crear_venta_desde_carrito()

        assert str(excinfo.value) == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_cliente_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).crear_venta_desde_carrito()

        assert str(excinfo.value) == (
            f"El cliente con ID '{CLIENTE_MINIMO}' no existe."
        )
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "items, esperado",
        [
            pytest.param([], "El carrito no puede estar vacío.", id="vacio"),
            pytest.param(
                ("1",),
                "Los items deben ser una lista.",
                id="no-es-lista",
            ),
            pytest.param(
                ["producto"],
                "El producto en la posición 1 no tiene formato válido.",
                id="item-no-dict",
            ),
            pytest.param(
                [{"cantidad": 1}],
                "El producto en la posición 1 no tiene ID.",
                id="sin-id",
            ),
            pytest.param(
                [{"producto_id": "   ", "cantidad": 1}],
                "El ID del producto en la posición 1 está vacío.",
                id="id-vacio",
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
            pytest.param(
                [
                    {"producto_id": PRODUCTO_MINIMO, "cantidad": 1},
                    {"producto_id": PRODUCTO_MINIMO, "cantidad": 1},
                ],
                f"El producto '{PRODUCTO_MINIMO}' aparece múltiples veces en el carrito.",
                id="producto-duplicado",
            ),
        ],
    )
    def test_items_invalidos(self, conexion_falsa, items, esperado):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                cliente_id=CLIENTE_MINIMO,
                items=items,
                metodo_pago="zelle",
            ).crear_venta_desde_carrito()

        assert str(excinfo.value) == esperado
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "metodo, esperado",
        [
            pytest.param(
                None,
                "El método de pago no puede estar vacío.",
                id="none",
            ),
            pytest.param(
                "   ",
                "El método de pago no puede estar vacío.",
                id="vacio",
            ),
            pytest.param(
                "tarjeta",
                "Método de pago inválido. Opciones: pago_movil, zelle, binance, efectivo_usd, efectivo_bs.",
                id="invalido",
            ),
        ],
    )
    def test_metodo_pago_invalido(self, conexion_falsa, metodo, esperado):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago=metodo,
            ).crear_venta_desde_carrito()

        assert str(excinfo.value) == esperado
        db.commit.assert_not_called()

    def test_stock_insuficiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,)]

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                cliente_id=CLIENTE_MINIMO,
                items=[{"producto_id": PRODUCTO_MINIMO, "cantidad": 2}],
                metodo_pago="zelle",
            ).crear_venta_desde_carrito()

        assert str(excinfo.value) == (
            f"Stock insuficiente para el producto {PRODUCTO_MINIMO}. "
            "Disponible: 1"
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_producto_sin_registro_de_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), None]

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).crear_venta_desde_carrito()

        assert str(excinfo.value) == (
            f"Stock insuficiente para el producto {PRODUCTO_MINIMO}. "
            "Disponible: 0"
        )
        db.rollback.assert_called_once()

    def test_conexion_caida_despues_de_validar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª conexión: verificar cliente; 2ª: la venta (sin conexión)
        with patch(
            "app.models.database.conectar.conexion1",
            side_effect=[db, None],
        ):
            with pytest.raises(RuntimeError) as excinfo:
                VentaModel(
                    cliente_id=CLIENTE_MINIMO,
                    items=[ITEM_VALIDO],
                    metodo_pago="zelle",
                ).crear_venta_desde_carrito()

        assert str(excinfo.value) == MENSAJE_ERROR_CONEXION

    def test_conexion_caida_en_verificacion_de_cliente(self, conexion_caída):
        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).crear_venta_desde_carrito()

        assert str(excinfo.value) == (
            f"El cliente con ID '{CLIENTE_MINIMO}' no existe."
        )

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª: verificar cliente; 2ª: INSERT de la venta que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        with pytest.raises(Exception, match="fallo simulado"):
            VentaModel(
                cliente_id=CLIENTE_MINIMO,
                items=[ITEM_VALIDO],
                metodo_pago="zelle",
            ).crear_venta_desde_carrito()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cursor.close.assert_called()
        db.close.assert_called()

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (10,)]
        uuid_parche, datetime_parche = preparar_factura()

        try:
            with patch("app.models.venta.Bitacora") as bitacora_clase:
                VentaModel(
                    cliente_id=CLIENTE_MINIMO,
                    items=[ITEM_VALIDO],
                    metodo_pago="zelle",
                    usuario_id="7",
                ).crear_venta_desde_carrito()
        finally:
            uuid_parche.stop()
            datetime_parche.stop()

        bitacora_clase.assert_called_once_with(
            accion="Crear venta",
            descripcion=(
                f"Se creó la venta {FACTURA_GENERADA} para cliente: "
                f"{CLIENTE_MINIMO} - Método: zelle"
            ),
            usuario_id="7",
            modulo_nombre="Ventas",
        )
        bitacora_clase.return_value.registrar.assert_called_once()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (10,)]
        uuid_parche, datetime_parche = preparar_factura()

        try:
            with patch("app.models.venta.Bitacora") as bitacora_clase:
                VentaModel(
                    cliente_id=CLIENTE_MINIMO,
                    items=[ITEM_VALIDO],
                    metodo_pago="zelle",
                ).crear_venta_desde_carrito()
        finally:
            uuid_parche.stop()
            datetime_parche.stop()

        bitacora_clase.assert_not_called()


class TestGuardarRegistroPago:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            ("Metodo",),
            ("Referencia",),
            ("Monto",),
            ("Capture",),
            ("Estado_pago",),
        ]
        fecha_pago = datetime(2026, 10, 15, 9, 0, 0)

        VentaModel(
            factura_id=FACTURA_GENERADA,
            metodo_pago="zelle",
            datos_pago={
                "referencia": "123456",
                "monto": "25.50",
                "capture": "captura.jpg",
                "fecha_pago": fecha_pago,
            },
        ).guardar_registro_pago()

        llamada = llamada_con(cursor, "INSERT INTO Metodo_pago")
        assert llamada.args[1] == [
            FACTURA_GENERADA,
            "USD",
            fecha_pago,
            "zelle",
            "123456",
            "25.50",
            "captura.jpg",
            "pendiente",
        ]
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_columnas_opcionales(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        VentaModel(
            factura_id=FACTURA_GENERADA,
            metodo_pago="efectivo_usd",
        ).guardar_registro_pago()

        llamada = llamada_con(cursor, "INSERT INTO Metodo_pago")
        assert llamada.args[1] == [
            FACTURA_GENERADA,
            "USD",
            llamada.args[1][2],
        ]
        assert isinstance(llamada.args[1][2], datetime)
        # Solo se incluyen los campos base: no hay columnas opcionales
        assert (
            "INSERT INTO Metodo_pago (ID_factura, Moneda, Fecha_pago)"
            in llamada.args[0]
        )
        db.commit.assert_called_once()

    def test_fecha_de_pago_por_defecto_es_ahora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        with patch("app.models.venta.datetime") as datetime_mock:
            datetime_mock.now.return_value = FECHA_FIJA
            VentaModel(
                factura_id=FACTURA_GENERADA,
                metodo_pago="efectivo_usd",
            ).guardar_registro_pago()

        llamada = llamada_con(cursor, "INSERT INTO Metodo_pago")
        assert llamada.args[1][2] == FECHA_FIJA

    def test_factura_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                factura_id="",
                metodo_pago="efectivo_usd",
            ).guardar_registro_pago()

        assert str(excinfo.value) == "El ID de la factura no puede estar vacío."
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "metodo, esperado",
        [
            pytest.param(
                None,
                "El método de pago no puede estar vacío.",
                id="metodo-vacio",
            ),
            pytest.param(
                "tarjeta",
                "Método de pago inválido. Opciones: pago_movil, zelle, binance, efectivo_usd, efectivo_bs.",
                id="metodo-invalido",
            ),
        ],
    )
    def test_metodo_pago_invalido(self, conexion_falsa, metodo, esperado):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                factura_id=FACTURA_GENERADA,
                metodo_pago=metodo,
            ).guardar_registro_pago()

        assert str(excinfo.value) == esperado
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "metodo, datos_pago, esperado",
        [
            pytest.param(
                "zelle",
                {"referencia": "@#$", "monto": "10.00"},
                "El campo Referencia no puede contener caracteres especiales.",
                id="referencia-caracteres-invalidos",
            ),
            pytest.param(
                "zelle",
                {"referencia": "R" * 101, "monto": "10.00"},
                "El campo Referencia no puede tener más de 100 caracteres.",
                id="referencia-demasiado-larga",
            ),
            pytest.param(
                "zelle",
                {"referencia": "123456", "monto": ""},
                "El campo Monto no puede estar vacío.",
                id="monto-vacio",
            ),
            pytest.param(
                "zelle",
                {"referencia": "123456", "monto": "1.234"},
                "El campo Monto debe ser un número decimal válido con hasta 2 decimales.",
                id="monto-formato-invalido",
            ),
            pytest.param(
                "zelle",
                {"referencia": "123456", "monto": "10000000000"},
                "El campo Monto debe ser menor o igual a 9999999999.99.",
                id="monto-demasiado-alto",
            ),
            pytest.param(
                "zelle",
                {"referencia": "123456", "monto": "0"},
                "El monto debe ser mayor a 0.",
                id="monto-cero",
            ),
            pytest.param(
                "pago_movil",
                {"monto": "10.00"},
                "La referencia es obligatoria para el método de pago 'pago_movil'.",
                id="referencia-obligatoria",
            ),
        ],
    )
    def test_datos_pago_invalidos(
        self, conexion_falsa, metodo, datos_pago, esperado
    ):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as excinfo:
            VentaModel(
                factura_id=FACTURA_GENERADA,
                metodo_pago=metodo,
                datos_pago=datos_pago,
            ).guardar_registro_pago()

        assert str(excinfo.value) == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(RuntimeError) as excinfo:
            VentaModel(
                factura_id=FACTURA_GENERADA,
                metodo_pago="efectivo_usd",
            ).guardar_registro_pago()

        assert str(excinfo.value) == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []
        # 1ª: consulta de columnas; 2ª: INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        with pytest.raises(Exception, match="fallo simulado"):
            VentaModel(
                factura_id=FACTURA_GENERADA,
                metodo_pago="efectivo_usd",
            ).guardar_registro_pago()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        with patch("app.models.venta.Bitacora") as bitacora_clase:
            VentaModel(
                factura_id=FACTURA_GENERADA,
                metodo_pago="efectivo_usd",
                usuario_id="7",
            ).guardar_registro_pago()

        bitacora_clase.assert_called_once_with(
            accion="Registrar pago",
            descripcion=(
                f"Se registró pago para factura: {FACTURA_GENERADA} "
                "- Método: efectivo_usd"
            ),
            usuario_id="7",
            modulo_nombre="Ventas",
        )
        bitacora_clase.return_value.registrar.assert_called_once()


class TestObtenerVentasHoy:

    def test_con_ventas_del_dia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "total_ventas": "150.50",
            "cantidad_ventas": 3,
            "Moneda": "USD",
        }

        resultado = VentaModel().obtener_ventas_hoy()

        assert resultado == {
            "total_ventas": 150.5,
            "cantidad_ventas": 3,
            "moneda": "USD",
        }
        assert "FROM Venta v" in ultima_sentencia(cursor)

    def test_sin_ventas_en_venta_usa_metodo_pago(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,
            {
                "total_ventas": "75.25",
                "cantidad_ventas": 2,
                "Moneda": "VES",
            },
        ]

        resultado = VentaModel().obtener_ventas_hoy()

        assert resultado == {
            "total_ventas": 75.25,
            "cantidad_ventas": 2,
            "moneda": "VES",
        }
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert len(sentencias) == 2
        assert "FROM Metodo_pago mp" in sentencias[1]

    def test_sin_datos_devuelve_valores_por_defecto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = VentaModel().obtener_ventas_hoy()

        assert resultado == {
            "total_ventas": 0,
            "cantidad_ventas": 0,
            "moneda": "USD",
        }

    def test_conexion_caida(self, conexion_caída):
        resultado = VentaModel().obtener_ventas_hoy()

        assert resultado == {
            "total_ventas": 0,
            "cantidad_ventas": 0,
            "moneda": "USD",
        }

    def test_error_de_bd_devuelve_valores_por_defecto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = VentaModel().obtener_ventas_hoy()

        assert resultado == {
            "total_ventas": 0,
            "cantidad_ventas": 0,
            "moneda": "USD",
        }
        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        VentaModel().obtener_ventas_hoy()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


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
        assert VentaModel(metodo_pago=metodo)._obtener_moneda_segun_metodo() == (
            esperado
        )


class TestGenerarIdFactura:

    def test_formato_de_factura(self):
        with patch("app.models.venta.uuid.uuid4") as uuid_mock, patch(
            "app.models.venta.datetime"
        ) as datetime_mock:
            uuid_mock.return_value.hex = "abcdef123456"
            datetime_mock.now.return_value = FECHA_FIJA

            factura = VentaModel()._generar_id_factura()

        assert factura == FACTURA_GENERADA


class TestVerificarClienteExiste:

    def test_cliente_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert VentaModel()._verificar_cliente_existe(CLIENTE_MINIMO) is True
        assert cursor.execute.call_args.args[1] == (CLIENTE_MINIMO,)

    def test_cliente_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert VentaModel()._verificar_cliente_existe(CLIENTE_MINIMO) is False

    def test_conexion_caida(self, conexion_caída):
        assert VentaModel()._verificar_cliente_existe(CLIENTE_MINIMO) is False


class TestVerificarStockDisponible:

    def test_stock_suficiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (5,)

        assert VentaModel()._verificar_stock_disponible(PRODUCTO_MINIMO, 3) == (
            True,
            5,
        )

    def test_stock_insuficiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (2,)

        assert VentaModel()._verificar_stock_disponible(PRODUCTO_MINIMO, 3) == (
            False,
            2,
        )

    def test_producto_sin_registro(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert VentaModel()._verificar_stock_disponible(PRODUCTO_MINIMO, 1) == (
            False,
            0,
        )

    def test_conexion_caida(self, conexion_caída):
        assert VentaModel()._verificar_stock_disponible(PRODUCTO_MINIMO, 1) == (
            False,
            0,
        )


class TestVerificarProductoExiste:

    def test_producto_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert VentaModel()._verificar_producto_existe(PRODUCTO_MINIMO) is True

    def test_producto_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert VentaModel()._verificar_producto_existe(PRODUCTO_MINIMO) is False

    def test_conexion_caida(self, conexion_caída):
        assert VentaModel()._verificar_producto_existe(PRODUCTO_MINIMO) is False
