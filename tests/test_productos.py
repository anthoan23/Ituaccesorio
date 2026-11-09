import time

import pytest

from app.models.productos import ClaseProducto, MarcaProducto, Producto


class TestValidacionEnModelo:
    def test_registrar_clase_valida_nombre_en_modelo(self):
        clase = ClaseProducto(nombre="A")

        with pytest.raises(ValueError, match="al menos 2 caracteres"):
            clase.registrar_clase()

    def test_registrar_marca_valida_nombre_en_modelo(self):
        marca = MarcaProducto(nombre="A")

        with pytest.raises(ValueError, match="al menos 2 caracteres"):
            marca.registrar_marca()

    def test_registrar_producto_valida_datos_en_modelo(self):
        producto = Producto(id_clase="1", id_marca="2", nombre="A")

        with pytest.raises(ValueError, match="al menos 2 caracteres"):
            producto.registrar_producto()

    def test_actualizar_producto_valida_datos_en_modelo(self):
        producto = Producto(id_producto="7", id_clase="1", id_marca="2", nombre="A")

        with pytest.raises(ValueError, match="al menos 2 caracteres"):
            producto.actualizar_producto()

    def test_producto_permite_cincuenta_caracteres_en_nombre(self):
        producto = Producto(id_clase="1", id_marca="2", nombre="A" * 50)

        producto._validar_datos_basicos()

        assert len(producto.nombre) == 50

    def test_registrar_producto_puede_guardarse_con_datos_validos(self):
        nombre = f"Producto valido {int(time.time() * 1000)}"
        producto = Producto(id_clase="1", id_marca="1", nombre=nombre, descripcion="Descripcion valida", usuario_id="1")

        id_producto = producto.registrar_producto()

        assert isinstance(id_producto, str)
        assert id_producto.isdigit()
