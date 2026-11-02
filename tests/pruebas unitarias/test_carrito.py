"""Pruebas unitarias de la clase CarritoModel (app.models.carrito).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models.carrito import CarritoModel
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "No se pudo conectar a la base de datos."

CARRITO_VACIO = {
    "items": [],
    "total": 0,
    "tasas": {"oficial": 0, "paralelo": 0},
}

# ==================== Datos de frontera ====================
CLIENTE_MINIMO = "123456"  # 6 dígitos (mínimo)
CLIENTE_MAXIMO = "12345678"  # 8 dígitos (máximo)

PRODUCTO_MINIMO = "1"  # 1 carácter (mínimo)
PRODUCTO_MAXIMO = "1234567890"  # 10 caracteres (máximo)

CANTIDAD_MINIMA = 1
CANTIDAD_MAXIMA = 9999999999  # 10 dígitos (máximo)

TASAS_POR_DEFECTO = {"oficial": 520.91, "paralelo": 710.12}


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


class TestObtenerCarrito:

    def test_con_items_calcula_total_y_normaliza(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "id": "LST0000001",
                "ID_inventario": "1",
                "Cantidad_producto": 2,
                "Costo_venta": Decimal("10.50"),
                "Nombre_producto": "Cable USB",
                "Nombre_marca": "Genérica",
                "Existencia": 5,
                "Foto_inventario": "cable.jpg",
            },
            {
                "id": "LST0000002",
                "ID_inventario": "2",
                "Cantidad_producto": "3",
                "Costo_venta": "2.50",
                "Nombre_producto": None,
                "Nombre_marca": None,
                "Existencia": None,
                "Foto_inventario": None,
            },
        ]
        cursor.fetchone.return_value = {
            "Tasa_oficial": 520.91,
            "Tasa_paralelo": 710.12,
        }

        resultado = CarritoModel(cliente_id=CLIENTE_MINIMO).obtener_carrito()

        assert resultado["total"] == pytest.approx(28.5)
        assert len(resultado["items"]) == 2
        primer_item = resultado["items"][0]
        assert primer_item["Costo_venta"] == 10.5
        assert primer_item["precio_usd"] == 10.5
        assert primer_item["Cantidad_producto"] == 2
        assert primer_item["Nombre_producto"] == "Cable USB"
        assert primer_item["Nombre_marca"] == "Genérica"
        assert primer_item["Existencia"] == 5
        assert primer_item["stock_disponible"] == 5
        assert primer_item["Foto_inventario"] == "cable.jpg"
        assert primer_item["imagen"] == "cable.jpg"
        segundo_item = resultado["items"][1]
        # Los valores vacíos se normalizan con texto/cero por defecto
        assert segundo_item["Nombre_producto"] == "Producto"
        assert segundo_item["Nombre_marca"] == ""
        assert segundo_item["Foto_inventario"] == ""
        assert segundo_item["Existencia"] == 0
        assert resultado["tasas"] == {"oficial": 520.91, "paralelo": 710.12}

    def test_sin_items(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = {
            "Tasa_oficial": 600.0,
            "Tasa_paralelo": 800.0,
        }

        resultado = CarritoModel(cliente_id=CLIENTE_MAXIMO).obtener_carrito()

        assert resultado["items"] == []
        assert resultado["total"] == 0
        assert resultado["tasas"] == {"oficial": 600.0, "paralelo": 800.0}
        assert "FROM Lista_compra" in cursor.execute.call_args_list[0].args[0]

    def test_sin_cliente_no_consulta_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = CarritoModel(cliente_id=None).obtener_carrito()

        assert resultado == CARRITO_VACIO
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = CarritoModel(cliente_id=CLIENTE_MINIMO).obtener_carrito()

        assert resultado == CARRITO_VACIO

    def test_error_de_bd_devuelve_carrito_vacio(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = CarritoModel(cliente_id=CLIENTE_MINIMO).obtener_carrito()

        assert resultado == CARRITO_VACIO
        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = None

        CarritoModel(cliente_id=CLIENTE_MINIMO).obtener_carrito()

        # Se abren dos cursores (carrito + tasas) y ambos se cierran
        assert cursor.close.call_count == 2
        assert db.close.call_count == 2

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = None

        CarritoModel(cliente_id=CLIENTE_MINIMO).obtener_carrito()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestAgregarAlCarrito:

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(10,), None, None, None]

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=CANTIDAD_MINIMA,
        ).agregar_al_carrito()

        assert resultado == {
            "success": True,
            "message": "Producto agregado al carrito.",
        }
        insert = llamada_con(cursor, "INSERT INTO Lista_compra")
        assert insert.args[1] == (
            "LST0000001",
            PRODUCTO_MINIMO,
            CLIENTE_MINIMO,
            CANTIDAD_MINIMA,
            "carrito",
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (CANTIDAD_MAXIMA,),
            None,
            ("LST0000009",),
            None,
        ]

        resultado = CarritoModel(
            cliente_id=CLIENTE_MAXIMO,
            inventario_id=PRODUCTO_MAXIMO,
            cantidad=CANTIDAD_MAXIMA,
        ).agregar_al_carrito()

        assert resultado["success"] is True
        insert = llamada_con(cursor, "INSERT INTO Lista_compra")
        assert insert.args[1] == (
            "LST0000010",
            PRODUCTO_MAXIMO,
            CLIENTE_MAXIMO,
            CANTIDAD_MAXIMA,
            "carrito",
        )

    def test_agrega_a_item_existente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(10,), ("LST0000003", 2)]

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=3,
        ).agregar_al_carrito()

        assert resultado["success"] is True
        update = llamada_con(cursor, "UPDATE Lista_compra")
        assert update.args[1] == (5, "LST0000003")
        sin_sentencia(cursor, "INSERT INTO Lista_compra")
        db.commit.assert_called_once()

    def test_item_existente_supera_el_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(10,), ("LST0000003", 8)]

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=3,
        ).agregar_al_carrito()

        assert resultado == {
            "success": False,
            "error": "La cantidad supera el stock disponible.",
        }
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_producto_nuevo_supera_el_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(2,), None]

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=3,
        ).agregar_al_carrito()

        assert resultado == {
            "success": False,
            "error": "La cantidad supera el stock disponible.",
        }
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_producto_no_encontrado_en_inventario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=1,
        ).agregar_al_carrito()

        assert resultado == {
            "success": False,
            "error": "Producto no encontrado en inventario.",
        }
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_producto_sin_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (0,)

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=1,
        ).agregar_al_carrito()

        assert resultado == {"success": False, "error": "Producto sin stock."}
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "cliente, inventario, cantidad, esperado",
        [
            pytest.param(
                "",
                PRODUCTO_MINIMO,
                1,
                "El cliente es obligatorio.",
                id="cliente-vacio",
            ),
            pytest.param(
                "12345",
                PRODUCTO_MINIMO,
                1,
                "El campo Cliente debe tener al menos 6 dígitos.",
                id="cliente-demasiado-corto",
            ),
            pytest.param(
                "123456789",
                PRODUCTO_MINIMO,
                1,
                "El campo Cliente no puede tener más de 8 dígitos.",
                id="cliente-demasiado-largo",
            ),
            pytest.param(
                "12345a",
                PRODUCTO_MINIMO,
                1,
                "El campo Cliente solo puede contener números.",
                id="cliente-no-numerico",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                "",
                1,
                "El producto es obligatorio.",
                id="producto-vacio",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                "12345678901",
                1,
                "El campo Producto no puede tener más de 10 caracteres.",
                id="producto-demasiado-largo",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                "INV#1",
                1,
                "El campo Producto solo puede contener letras, números, acentos y espacios.",
                id="producto-caracteres-invalidos",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                PRODUCTO_MINIMO,
                None,
                "La cantidad es obligatoria.",
                id="cantidad-none",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                PRODUCTO_MINIMO,
                0,
                "La cantidad debe ser mayor que 0.",
                id="cantidad-cero",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                PRODUCTO_MINIMO,
                "12345678901",
                "El campo Cantidad no puede tener más de 10 dígitos.",
                id="cantidad-demasiado-larga",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                PRODUCTO_MINIMO,
                "abc",
                "El campo Cantidad solo puede contener números.",
                id="cantidad-no-numerica",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                PRODUCTO_MINIMO,
                "-1",
                "El campo Cantidad solo puede contener números.",
                id="cantidad-negativa",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, cliente, inventario, cantidad, esperado
    ):
        db, cursor = conexion_falsa

        resultado = CarritoModel(
            cliente_id=cliente,
            inventario_id=inventario,
            cantidad=cantidad,
        ).agregar_al_carrito()

        assert resultado == {"success": False, "error": esperado}
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=1,
        ).agregar_al_carrito()

        assert resultado == {"success": False, "error": MENSAJE_ERROR_CONEXION}

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=1,
        ).agregar_al_carrito()

        assert resultado == {
            "success": False,
            "error": "Error al agregar al carrito.",
        }
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(10,), ("LST0000003", 1)]

        with patch("app.models.carrito.Bitacora") as bitacora_clase:
            resultado = CarritoModel(
                cliente_id=CLIENTE_MINIMO,
                inventario_id=PRODUCTO_MINIMO,
                cantidad=1,
                usuario_id="7",
            ).agregar_al_carrito()

        assert resultado["success"] is True
        bitacora_clase.assert_called_once_with(
            accion="Agregar al carrito",
            descripcion=(
                f"Cliente ID: {CLIENTE_MINIMO} agregó producto ID: "
                f"{PRODUCTO_MINIMO} - Cantidad: 1"
            ),
            usuario_id="7",
            modulo_nombre="Carrito",
        )
        bitacora_clase.return_value.registrar.assert_called_once()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(10,), ("LST0000003", 1)]

        with patch("app.models.carrito.Bitacora") as bitacora_clase:
            CarritoModel(
                cliente_id=CLIENTE_MINIMO,
                inventario_id=PRODUCTO_MINIMO,
                cantidad=1,
            ).agregar_al_carrito()

        bitacora_clase.assert_not_called()


class TestActualizarCantidad:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (10,)

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=3,
        ).actualizar_cantidad()

        assert resultado == {"success": True}
        update = llamada_con(cursor, "UPDATE Lista_compra")
        assert update.args[1] == (
            3,
            CLIENTE_MINIMO,
            PRODUCTO_MINIMO,
            "carrito",
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_cantidad_cero_elimina_el_item(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=0,
        ).actualizar_cantidad()

        assert resultado == {
            "success": True,
            "message": "Producto eliminado del carrito.",
        }
        delete = llamada_con(cursor, "DELETE FROM Lista_compra")
        assert delete.args[1] == (
            CLIENTE_MINIMO,
            PRODUCTO_MINIMO,
            "carrito",
        )
        db.commit.assert_called_once()

    def test_cantidad_negativa_elimina_el_item(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=-2,
        ).actualizar_cantidad()

        assert resultado == {
            "success": True,
            "message": "Producto eliminado del carrito.",
        }
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "cantidad",
        [
            pytest.param(None, id="none"),
            pytest.param("abc", id="texto"),
        ],
    )
    def test_cantidad_no_entera(self, conexion_falsa, cantidad):
        db, cursor = conexion_falsa

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=cantidad,
        ).actualizar_cantidad()

        assert resultado == {
            "success": False,
            "error": "La cantidad debe ser un número entero válido.",
        }
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_stock_suficiente_con_valor_string(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("5",)

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=5,
        ).actualizar_cantidad()

        assert resultado == {"success": True}
        db.commit.assert_called_once()

    def test_stock_insuficiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (2,)

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=3,
        ).actualizar_cantidad()

        assert resultado == {
            "success": False,
            "error": "La cantidad supera el stock disponible.",
        }
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_producto_sin_registro_de_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=1,
        ).actualizar_cantidad()

        assert resultado == {
            "success": False,
            "error": "La cantidad supera el stock disponible.",
        }
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "cliente, inventario, esperado",
        [
            pytest.param(
                "",
                PRODUCTO_MINIMO,
                "El cliente es obligatorio.",
                id="cliente-vacio",
            ),
            pytest.param(
                "12345",
                PRODUCTO_MINIMO,
                "El campo Cliente debe tener al menos 6 dígitos.",
                id="cliente-corto",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                "",
                "El producto es obligatorio.",
                id="producto-vacio",
            ),
            pytest.param(
                CLIENTE_MINIMO,
                "INV#1",
                "El campo Producto solo puede contener letras, números, acentos y espacios.",
                id="producto-invalido",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, cliente, inventario, esperado
    ):
        db, cursor = conexion_falsa

        resultado = CarritoModel(
            cliente_id=cliente,
            inventario_id=inventario,
            cantidad=1,
        ).actualizar_cantidad()

        assert resultado == {"success": False, "error": esperado}
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=1,
        ).actualizar_cantidad()

        assert resultado == {"success": False, "error": MENSAJE_ERROR_CONEXION}

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
            cantidad=1,
        ).actualizar_cantidad()

        assert resultado == {
            "success": False,
            "error": "Error al actualizar cantidad.",
        }
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestEliminarItem:

    def test_elimina_el_item(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
        ).eliminar_item()

        assert resultado is None
        delete = llamada_con(cursor, "DELETE FROM Lista_compra")
        assert delete.args[1] == (
            CLIENTE_MINIMO,
            PRODUCTO_MINIMO,
            "carrito",
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "cliente, inventario",
        [
            pytest.param(None, PRODUCTO_MINIMO, id="sin-cliente"),
            pytest.param("", PRODUCTO_MINIMO, id="cliente-vacio"),
            pytest.param(CLIENTE_MINIMO, None, id="sin-producto"),
            pytest.param(CLIENTE_MINIMO, "", id="producto-vacio"),
        ],
    )
    def test_sin_datos_no_toca_la_bd(self, conexion_falsa, cliente, inventario):
        db, cursor = conexion_falsa

        resultado = CarritoModel(
            cliente_id=cliente,
            inventario_id=inventario,
        ).eliminar_item()

        assert resultado is None
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
        ).eliminar_item()

        assert resultado is None

    def test_error_de_bd_hace_rollback_sin_propagar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = CarritoModel(
            cliente_id=CLIENTE_MINIMO,
            inventario_id=PRODUCTO_MINIMO,
        ).eliminar_item()

        assert resultado is None
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestVaciarCarrito:

    def test_vacia_el_carrito(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = CarritoModel(cliente_id=CLIENTE_MINIMO).vaciar_carrito()

        assert resultado is None
        delete = llamada_con(cursor, "DELETE FROM Lista_compra")
        assert delete.args[1] == (CLIENTE_MINIMO, "carrito")
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "cliente",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_sin_cliente_no_toca_la_bd(self, conexion_falsa, cliente):
        db, cursor = conexion_falsa

        resultado = CarritoModel(cliente_id=cliente).vaciar_carrito()

        assert resultado is None
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = CarritoModel(cliente_id=CLIENTE_MINIMO).vaciar_carrito()

        assert resultado is None

    def test_error_de_bd_hace_rollback_sin_propagar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = CarritoModel(cliente_id=CLIENTE_MINIMO).vaciar_carrito()

        assert resultado is None
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestGenerarIdListaCompra:

    def test_continua_desde_el_ultimo_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("LST0000009",), None]

        resultado = CarritoModel()._generar_id_lista_compra()

        assert resultado == "LST0000010"

    def test_empieza_en_uno_si_no_hay_registros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        assert CarritoModel()._generar_id_lista_compra() == "LST0000001"

    def test_ultimo_id_con_formato_invalido_empieza_en_uno(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("XYZ",), None]

        assert CarritoModel()._generar_id_lista_compra() == "LST0000001"

    def test_conexion_caida(self, conexion_caída):
        assert CarritoModel()._generar_id_lista_compra() == "LST0000001"

    def test_error_devuelve_id_alternativo_y_cierra(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = CarritoModel()._generar_id_lista_compra()

        assert resultado.startswith("LST")
        assert len(resultado) > 3
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestObtenerTasas:

    def test_devuelve_las_tasas_actuales(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "Tasa_oficial": "530.50",
            "Tasa_paralelo": "720.25",
        }

        resultado = CarritoModel()._obtener_tasas()

        assert resultado == {"oficial": 530.50, "paralelo": 720.25}
        assert "FROM Tasas_cambio" in ultima_sentencia(cursor)

    def test_sin_registro_usa_tasas_por_defecto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert CarritoModel()._obtener_tasas() == TASAS_POR_DEFECTO

    def test_conexion_caida(self, conexion_caída):
        assert CarritoModel()._obtener_tasas() == TASAS_POR_DEFECTO

    def test_error_de_bd_usa_tasas_por_defecto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert CarritoModel()._obtener_tasas() == TASAS_POR_DEFECTO

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        CarritoModel()._obtener_tasas()

        cursor.close.assert_called_once()
        db.close.assert_called_once()
