"""Pruebas unitarias de la clase CatalogoModel (app.models.catalogo).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from decimal import Decimal

import pytest

from app.models.catalogo import CatalogoModel
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
INVENTARIO_ID = "INV-0001"
PRODUCTO_ID = "PROD-01"
CLASE_ID = "2"
MARCA_ID = "3"

BUSQUEDA_MINIMA = "ab"  # 2 caracteres (mínimo para aplicar el filtro)
BUSQUEDA_MAXIMA = "q" * 100  # 100 caracteres (máximo para aplicar el filtro)


class TestListarProductosCatalogo:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id": INVENTARIO_ID,
                "nombre": "Funda transparente",
                "marca": "Genérica",
                "clase": "Accesorios",
                "precio_usd": 5.5,
                "stock": 10,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = CatalogoModel().listar_productos_catalogo()

        assert resultado == filas
        assert "FROM Existencias_productos" in ultima_sentencia(cursor)
        assert "e.Existencia > 0" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == ()
        db.cursor.assert_called_once_with(dictionary=True)

    def test_convierte_decimal_a_float(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {"id": INVENTARIO_ID, "precio_usd": Decimal("12.50"), "stock": 1}
        ]

        resultado = CatalogoModel().listar_productos_catalogo()

        assert resultado[0]["precio_usd"] == 12.5
        assert isinstance(resultado[0]["precio_usd"], float)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert CatalogoModel().listar_productos_catalogo() == []

    def test_filtros_clase_marca_y_busqueda(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel(
            clase_id=" 2 ", marca_id="3", q="  samsung  "
        ).listar_productos_catalogo()

        sentencia = ultima_sentencia(cursor)
        assert "p.ID_Clase = %s" in sentencia
        assert "p.ID_marca = %s" in sentencia
        assert "p.Nombre_producto LIKE %s" in sentencia
        assert cursor.execute.call_args.args[1] == (
            CLASE_ID,
            MARCA_ID,
            "%samsung%",
            "%samsung%",
        )

    def test_escapa_comodines_de_busqueda(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel(q="100%_x").listar_productos_catalogo()

        assert cursor.execute.call_args.args[1] == (
            "%100\\%\\_x%",
            "%100\\%\\_x%",
        )

    @pytest.mark.parametrize(
        "busqueda",
        [
            pytest.param("a", id="demasiado-corta"),
            pytest.param("q" * 101, id="demasiado-larga"),
            pytest.param("   ", id="solo-espacios"),
            pytest.param("", id="vacia"),
        ],
    )
    def test_busqueda_no_aplicable_se_ignora(self, conexion_falsa, busqueda):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel(q=busqueda).listar_productos_catalogo()

        assert cursor.execute.call_args.args[1] == ()
        assert "LIKE %s" not in ultima_sentencia(cursor)

    def test_filtros_en_blanco_se_ignoran(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel(clase_id="   ", marca_id=" ", q=None).listar_productos_catalogo()

        assert cursor.execute.call_args.args[1] == ()
        sentencia = ultima_sentencia(cursor)
        assert "p.ID_Clase = %s" not in sentencia
        assert "p.ID_marca = %s" not in sentencia

    def test_busqueda_en_el_limite_maximo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel(q=BUSQUEDA_MAXIMA).listar_productos_catalogo()

        assert cursor.execute.call_args.args[1] == (
            f"%{BUSQUEDA_MAXIMA}%",
            f"%{BUSQUEDA_MAXIMA}%",
        )

    def test_conexion_caida(self, conexion_caída):
        assert CatalogoModel().listar_productos_catalogo() == []

    def test_error_de_bd_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert CatalogoModel().listar_productos_catalogo() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().listar_productos_catalogo()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().listar_productos_catalogo()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerProducto:

    def test_producto_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "id": INVENTARIO_ID,
            "nombre": "Funda transparente",
            "marca": "Genérica",
            "precio_usd": 5.5,
            "stock": 10,
        }
        cursor.fetchone.return_value = esperado

        resultado = CatalogoModel(inventario_id=INVENTARIO_ID).obtener_producto()

        assert resultado == esperado
        assert "FROM Existencias_productos" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (INVENTARIO_ID,)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_convierte_decimal_a_float(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "id": INVENTARIO_ID,
            "precio_usd": Decimal("99.99"),
        }

        resultado = CatalogoModel(inventario_id=INVENTARIO_ID).obtener_producto()

        assert resultado["precio_usd"] == 99.99
        assert isinstance(resultado["precio_usd"], float)

    def test_producto_no_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert CatalogoModel(inventario_id=INVENTARIO_ID).obtener_producto() is None

    @pytest.mark.parametrize(
        "inventario_id",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
            pytest.param("   ", id="solo-espacios"),
        ],
    )
    def test_sin_id_valido_no_toca_la_bd(self, conexion_falsa, inventario_id):
        db, cursor = conexion_falsa

        assert (
            CatalogoModel(inventario_id=inventario_id).obtener_producto() is None
        )
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_normaliza_el_id_con_espacios(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        CatalogoModel(inventario_id=f"  {INVENTARIO_ID}  ").obtener_producto()

        assert cursor.execute.call_args.args[1] == (INVENTARIO_ID,)

    def test_conexion_caida(self, conexion_caída):
        assert CatalogoModel(inventario_id=INVENTARIO_ID).obtener_producto() is None

    def test_error_de_bd_se_propaga_y_cierra_recursos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            CatalogoModel(inventario_id=INVENTARIO_ID).obtener_producto()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": INVENTARIO_ID}

        CatalogoModel(inventario_id=INVENTARIO_ID).obtener_producto()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarClases:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {"id": "1", "nombre": "Accesorios"},
            {"id": "2", "nombre": "Repuestos"},
        ]
        cursor.fetchall.return_value = filas

        resultado = CatalogoModel().listar_clases()

        assert resultado == filas
        assert "FROM Clase_producto" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert CatalogoModel().listar_clases() == []

    def test_conexion_caida(self, conexion_caída):
        assert CatalogoModel().listar_clases() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().listar_clases()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().listar_clases()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarMarcas:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": "3", "nombre": "Samsung"}]
        cursor.fetchall.return_value = filas

        resultado = CatalogoModel().listar_marcas()

        assert resultado == filas
        assert "FROM Marca_producto" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert CatalogoModel().listar_marcas() == []

    def test_conexion_caida(self, conexion_caída):
        assert CatalogoModel().listar_marcas() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().listar_marcas()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().listar_marcas()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestProductosMasVendidos:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id": INVENTARIO_ID,
                "nombre": "Funda",
                "marca": "Genérica",
                "precio_usd": 5.5,
                "veces_vendido": 12,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = CatalogoModel().productos_mas_vendidos()

        assert resultado == filas
        assert "LIMIT %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (5,)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_convierte_decimal_a_float(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {"id": INVENTARIO_ID, "precio_usd": Decimal("7.25")}
        ]

        resultado = CatalogoModel().productos_mas_vendidos()

        assert resultado[0]["precio_usd"] == 7.25
        assert isinstance(resultado[0]["precio_usd"], float)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert CatalogoModel().productos_mas_vendidos() == []

    @pytest.mark.parametrize(
        "limite, esperado",
        [
            pytest.param(3, 3, id="entero-valido"),
            pytest.param("7", 7, id="texto-numerico"),
            pytest.param(50, 50, id="maximo-permitido"),
            pytest.param(51, 50, id="supera-el-maximo"),
            pytest.param(0, 5, id="cero-usa-el-valor-por-defecto"),
            pytest.param(-3, 5, id="negativo-usa-el-valor-por-defecto"),
            pytest.param("abc", 5, id="texto-invalido-usa-el-valor-por-defecto"),
            pytest.param(None, 5, id="none-usa-el-valor-por-defecto"),
        ],
    )
    def test_limites_del_limite(self, conexion_falsa, limite, esperado):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().productos_mas_vendidos(limite)

        assert cursor.execute.call_args.args[1] == (esperado,)

    def test_conexion_caida(self, conexion_caída):
        assert CatalogoModel().productos_mas_vendidos() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().productos_mas_vendidos()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        CatalogoModel().productos_mas_vendidos()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()
