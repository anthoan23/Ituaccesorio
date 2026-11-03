"""Pruebas de integración de CatalogoModel contra MySQL real."""
import pytest

from app.models.catalogo import CatalogoModel
from seed_helpers import (
    crear_existencia_temporal,
    crear_producto_temporal,
    eliminar_producto_temporal,
)

CLASE_TELEFONO = "1"
CLASE_REPUESTO = "7"
MARCA_IPHONE = "1"
MARCA_SAMSUNG = "3"


# ==================== listar_clases / listar_marcas (solo seed) ====================

class TestListarClases:

    def test_devuelve_las_7_clases_del_seed(self):
        clases = CatalogoModel().listar_clases()

        assert len(clases) == 7
        assert {c["id"] for c in clases} == {"1", "2", "3", "4", "5", "6", "7"}

    def test_ordenadas_por_nombre(self):
        clases = CatalogoModel().listar_clases()
        nombres = [c["nombre"] for c in clases]

        assert nombres == sorted(nombres)


class TestListarMarcas:

    def test_devuelve_las_7_marcas_del_seed(self):
        marcas = CatalogoModel().listar_marcas()

        assert len(marcas) == 7
        assert {m["id"] for m in marcas} == {"1", "2", "3", "4", "5", "6", "7"}

    def test_ordenadas_por_nombre(self):
        marcas = CatalogoModel().listar_marcas()
        nombres = [m["nombre"] for m in marcas]

        assert nombres == sorted(nombres)


# ==================== listar_productos_catalogo ====================

class TestListarProductosCatalogo:

    def test_sin_productos_devuelve_lista_vacia(self):
        # El seed deja Producto y Existencias_productos vacías.
        resultado = CatalogoModel().listar_productos_catalogo()
        assert resultado == []

    def test_producto_con_stock_aparece(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="iPhone Integracion", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_producto, existencia=5, costo=499.99)

            resultado = CatalogoModel().listar_productos_catalogo()

            assert len(resultado) == 1
            fila = resultado[0]
            assert fila["nombre"] == "iPhone Integracion"
            assert fila["precio_usd"] == 499.99
            assert isinstance(fila["precio_usd"], float)
            assert fila["stock"] == 5
            assert fila["id_producto"] == id_producto
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_producto_sin_stock_no_aparece(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Sin Stock Integracion", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_producto, existencia=0, costo=100.0)

            assert CatalogoModel().listar_productos_catalogo() == []
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_filtra_por_clase(self):
        id_iphone = None
        id_repuesto = None
        try:
            id_iphone = crear_producto_temporal(
                nombre="iPhone Clase Filtro", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_iphone, existencia=3, costo=600.0)

            id_repuesto = crear_producto_temporal(
                nombre="Repuesto Clase Filtro", clase=CLASE_REPUESTO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_repuesto, existencia=3, costo=10.0)

            resultado = CatalogoModel(clase_id=CLASE_TELEFONO).listar_productos_catalogo()

            assert len(resultado) == 1
            assert resultado[0]["id_producto"] == id_iphone
        finally:
            if id_iphone:
                eliminar_producto_temporal(id_iphone)
            if id_repuesto:
                eliminar_producto_temporal(id_repuesto)

    def test_filtra_por_marca(self):
        id_iphone = None
        id_samsung = None
        try:
            id_iphone = crear_producto_temporal(
                nombre="iPhone Marca Filtro", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_iphone, existencia=2, costo=500.0)

            id_samsung = crear_producto_temporal(
                nombre="Galaxy Marca Filtro", clase=CLASE_TELEFONO, marca=MARCA_SAMSUNG
            )
            crear_existencia_temporal(id_samsung, existencia=2, costo=400.0)

            resultado = CatalogoModel(marca_id=MARCA_IPHONE).listar_productos_catalogo()

            assert len(resultado) == 1
            assert resultado[0]["id_producto"] == id_iphone
        finally:
            if id_iphone:
                eliminar_producto_temporal(id_iphone)
            if id_samsung:
                eliminar_producto_temporal(id_samsung)

    def test_filtra_por_clase_y_marca(self):
        id_iphone = None
        id_samsung = None
        try:
            id_iphone = crear_producto_temporal(
                nombre="iPhone Doble Filtro", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_iphone, existencia=2, costo=500.0)

            id_samsung = crear_producto_temporal(
                nombre="Galaxy Doble Filtro", clase=CLASE_TELEFONO, marca=MARCA_SAMSUNG
            )
            crear_existencia_temporal(id_samsung, existencia=2, costo=400.0)

            resultado = CatalogoModel(
                clase_id=CLASE_TELEFONO, marca_id=MARCA_IPHONE
            ).listar_productos_catalogo()

            assert len(resultado) == 1
            assert resultado[0]["id_producto"] == id_iphone
        finally:
            if id_iphone:
                eliminar_producto_temporal(id_iphone)
            if id_samsung:
                eliminar_producto_temporal(id_samsung)

    def test_busqueda_por_nombre(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="iPhone BusquedaXYZ", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_producto, existencia=2, costo=500.0)

            resultado = CatalogoModel(q="BusquedaXYZ").listar_productos_catalogo()

            assert len(resultado) == 1
            assert "BusquedaXYZ" in resultado[0]["nombre"]
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    @pytest.mark.parametrize(
        "q",
        [
            pytest.param("a", id="q-demasiado-corta-se-ignora"),
            pytest.param("Q" * 101, id="q-demasiado-larga-se-ignora"),
            pytest.param("", id="q-vacia"),
        ],
    )
    def test_busqueda_fuera_de_rango_no_filtra(self, q):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Producto Para Rango", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_producto, existencia=2, costo=100.0)

            # Como el filtro se ignora, debe devolver el producto creado.
            resultado = CatalogoModel(q=q).listar_productos_catalogo()

            assert any(r["id_producto"] == id_producto for r in resultado)
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)


# ==================== obtener_producto ====================

class TestObtenerProducto:

    def test_producto_existente(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="iPhone Obtener", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            id_inventario = crear_existencia_temporal(id_producto, existencia=4, costo=550.0)

            resultado = CatalogoModel(inventario_id=id_inventario).obtener_producto()

            assert resultado is not None
            assert resultado["id"] == id_inventario
            assert resultado["nombre"] == "iPhone Obtener"
            assert resultado["precio_usd"] == 550.0
            assert isinstance(resultado["precio_usd"], float)
            assert resultado["stock"] == 4
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_producto_inexistente(self):
        assert CatalogoModel(inventario_id="INV999999").obtener_producto() is None

    def test_sin_inventario_id(self):
        assert CatalogoModel().obtener_producto() is None

    def test_inventario_id_vacio(self):
        assert CatalogoModel(inventario_id="   ").obtener_producto() is None


# ==================== productos_mas_vendidos ====================

class TestProductosMasVendidos:

    def test_sin_ventas_devuelve_todos_con_cero(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="iPhone Top", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            crear_existencia_temporal(id_producto, existencia=5, costo=500.0)

            resultado = CatalogoModel().productos_mas_vendidos()

            assert len(resultado) >= 1
            fila = next(r for r in resultado if r["id_producto"] == id_producto)
            assert fila["veces_vendido"] == 0
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    @pytest.mark.parametrize(
        "limite, esperado_max",
        [
            pytest.param(1, 1, id="limite-1"),
            pytest.param(50, 50, id="limite-50"),
        ],
    )
    def test_respeta_limite(self, limite, esperado_max):
        resultado = CatalogoModel().productos_mas_vendidos(limite=limite)
        assert len(resultado) <= esperado_max

    @pytest.mark.parametrize(
        "limite",
        [
            pytest.param(0, id="limite-cero-cae-a-5"),
            pytest.param(-3, id="limite-negativo-cae-a-5"),
            pytest.param("abc", id="limite-texto-cae-a-5"),
        ],
    )
    def test_limite_invalido_cae_a_5(self, limite):
        resultado = CatalogoModel().productos_mas_vendidos(limite=limite)
        assert len(resultado) <= 5

    def test_limite_mayor_a_50_se_capea(self):
        resultado = CatalogoModel().productos_mas_vendidos(limite=999)
        assert len(resultado) <= 50