"""Pruebas unitarias de la clase Inventario (app.models.inventario).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models.inventario import Inventario
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ID_INVENTARIO = "INV-0001"
ID_PRODUCTO = "PROD-01"

STOCK_MINIMO = 0
STOCK_MAXIMO = 9999

LIMITE_POR_DEFECTO = 10


class TestListarInventario:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id_inventario": ID_INVENTARIO,
                "id_producto": ID_PRODUCTO,
                "existencia": 10,
                "costo_venta": 5.5,
                "nombre_producto": "Funda",
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Inventario().listar_inventario()

        assert resultado == filas
        assert "FROM Existencias_productos" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_convierte_decimal_a_float(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {"id_inventario": ID_INVENTARIO, "costo_venta": Decimal("15.75")}
        ]

        resultado = Inventario().listar_inventario()

        assert resultado[0]["costo_venta"] == 15.75
        assert isinstance(resultado[0]["costo_venta"], float)

    @pytest.mark.parametrize(
        "filas",
        [
            pytest.param([], id="lista-vacia"),
            pytest.param(None, id="fetchall-none"),
        ],
    )
    def test_sin_datos(self, conexion_falsa, filas):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = filas

        assert Inventario().listar_inventario() == []

    def test_conexion_caida(self, conexion_caída):
        assert Inventario().listar_inventario() == []

    def test_error_de_bd_se_propaga_y_cierra_recursos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            Inventario().listar_inventario()

        cierra_recursos(db, cursor)

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_inventario()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_inventario()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarInventarioPorModelo:

    @pytest.mark.parametrize(
        "nombre_modelo",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_sin_modelo_delega_en_listar_inventario(
        self, conexion_falsa, nombre_modelo
    ):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        resultado = Inventario().listar_inventario_por_modelo(nombre_modelo)

        assert resultado == []
        assert "LIKE %s" not in ultima_sentencia(cursor)

    def test_con_modelo_filtra_por_nombre(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id_inventario": ID_INVENTARIO, "nombre_producto": "Funda"}]
        cursor.fetchall.return_value = filas

        resultado = Inventario().listar_inventario_por_modelo("Funda")

        assert resultado == filas
        assert "p.Nombre_producto LIKE %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == ("%Funda%",)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_convierte_decimal_a_float(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [{"costo_venta": Decimal("3.10")}]

        resultado = Inventario().listar_inventario_por_modelo("Funda")

        assert resultado[0]["costo_venta"] == 3.1
        assert isinstance(resultado[0]["costo_venta"], float)

    @pytest.mark.parametrize(
        "filas",
        [
            pytest.param([], id="lista-vacia"),
            pytest.param(None, id="fetchall-none"),
        ],
    )
    def test_sin_datos(self, conexion_falsa, filas):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = filas

        assert Inventario().listar_inventario_por_modelo("Funda") == []

    def test_conexion_caida(self, conexion_caída):
        assert Inventario().listar_inventario_por_modelo("Funda") == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_inventario_por_modelo("Funda")

        cierra_recursos(db, cursor)


class TestListarInventarioGeneral:

    def test_delega_en_listar_inventario(self):
        filas = [{"id_inventario": ID_INVENTARIO}]

        with patch.object(
            Inventario, "listar_inventario", return_value=filas
        ) as listar:
            resultado = Inventario().listar_inventario_general()

        assert resultado == filas
        listar.assert_called_once_with()

    def test_devuelve_lista_vacia_si_no_hay_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Inventario().listar_inventario_general() == []


class TestListarProductosBajoStock:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id_inventario": ID_INVENTARIO,
                "existencia": STOCK_MINIMO,
                "costo_venta": 2.5,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Inventario().listar_productos_bajo_stock()

        assert resultado == filas
        sentencia = ultima_sentencia(cursor)
        assert "e.Existencia <= %s" in sentencia
        assert "LIMIT %s" in sentencia
        assert cursor.execute.call_args.args[1] == (LIMITE_POR_DEFECTO,) * 2
        db.cursor.assert_called_once_with(dictionary=True)

    @pytest.mark.parametrize(
        "limite",
        [
            pytest.param(0, id="cero"),
            pytest.param(25, id="valor-personalizado"),
        ],
    )
    def test_limite_se_usa_en_ambos_placeholders(self, conexion_falsa, limite):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_productos_bajo_stock(limite)

        assert cursor.execute.call_args.args[1] == (limite, limite)

    def test_convierte_decimal_a_float(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [{"costo_venta": Decimal("8.20")}]

        resultado = Inventario().listar_productos_bajo_stock()

        assert resultado[0]["costo_venta"] == 8.2
        assert isinstance(resultado[0]["costo_venta"], float)

    @pytest.mark.parametrize(
        "filas",
        [
            pytest.param([], id="lista-vacia"),
            pytest.param(None, id="fetchall-none"),
        ],
    )
    def test_sin_datos(self, conexion_falsa, filas):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = filas

        assert Inventario().listar_productos_bajo_stock() == []

    def test_conexion_caida(self, conexion_caída):
        assert Inventario().listar_productos_bajo_stock() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_productos_bajo_stock()

        cierra_recursos(db, cursor)


class TestListarProductosSinStock:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id_inventario": ID_INVENTARIO,
                "existencia": STOCK_MINIMO,
                "costo_venta": 1.25,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Inventario().listar_productos_sin_stock()

        assert resultado == filas
        assert "e.Existencia = 0" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_convierte_decimal_a_float(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [{"costo_venta": Decimal("4.40")}]

        resultado = Inventario().listar_productos_sin_stock()

        assert resultado[0]["costo_venta"] == 4.4
        assert isinstance(resultado[0]["costo_venta"], float)

    @pytest.mark.parametrize(
        "filas",
        [
            pytest.param([], id="lista-vacia"),
            pytest.param(None, id="fetchall-none"),
        ],
    )
    def test_sin_datos(self, conexion_falsa, filas):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = filas

        assert Inventario().listar_productos_sin_stock() == []

    def test_conexion_caida(self, conexion_caída):
        assert Inventario().listar_productos_sin_stock() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_productos_sin_stock()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_productos_sin_stock()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestAumentarStock:

    def test_aumenta_correctamente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = Inventario(
            id_inventario=ID_INVENTARIO
        ).aumentar_stock(5)

        assert resultado is True
        sentencia = ultima_sentencia(cursor)
        assert "UPDATE Existencias_productos" in sentencia
        assert "Existencia = Existencia + %s" in sentencia
        assert cursor.execute.call_args.args[1] == (5, ID_INVENTARIO)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_filas_afectadas_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        resultado = Inventario(
            id_inventario=ID_INVENTARIO
        ).aumentar_stock(5)

        assert resultado is False
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "id_inventario",
        [
            pytest.param("", id="vacio"),
            pytest.param(None, id="none"),
        ],
    )
    def test_id_requerido(self, conexion_falsa, id_inventario):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError, match="ID del inventario es requerido"):
            Inventario(id_inventario=id_inventario).aumentar_stock(5)

        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "cantidad",
        [
            pytest.param(0, id="cero"),
            pytest.param(-5, id="negativa"),
        ],
    )
    def test_cantidad_debe_ser_positiva(self, conexion_falsa, cantidad):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError, match="La cantidad debe ser mayor a 0"):
            Inventario(id_inventario=ID_INVENTARIO).aumentar_stock(cantidad)

        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(
            RuntimeError, match="No se pudo conectar a la base de datos."
        ):
            Inventario(id_inventario=ID_INVENTARIO).aumentar_stock(5)

    def test_error_de_bd_hace_rollback_y_propaga(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            Inventario(id_inventario=ID_INVENTARIO).aumentar_stock(5)

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)


class TestListarInventarioTaller:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "ID_inventario": ID_INVENTARIO,
                "Nombre_producto": "Pantalla",
                "Existencia": 3,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Inventario().listar_inventario_taller()

        assert resultado == filas
        assert "e.ID_categoria = 2" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Inventario().listar_inventario_taller() == []

    def test_conexion_caida(self, conexion_caída):
        assert Inventario().listar_inventario_taller() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_inventario_taller()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Inventario().listar_inventario_taller()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()
