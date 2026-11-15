"""Pruebas de integración de las clases de Productos contra MySQL real."""
import pytest

from app.models.database import conectar
from app.models.productos import (
    Categoria,
    ClaseProducto,
    MarcaProducto,
    Producto,
    Productos,
)
from seed_helpers import (
    crear_existencia_temporal,
    crear_producto_temporal,
    eliminar_producto_temporal,
)

# El seed trae: clases 1-7 y marcas 1-7 (con 'Iphone' duplicado en 1 y 2,
# por eso se usa Samsung "3" para no depender de un nombre único).
CLASE_TELEFONO = "1"
MARCA_SEED = "3"
ID_CLASE_INEXISTENTE = "999999"
ID_MARCA_INEXISTENTE = "999999"


# ==================== HELPERS LOCALES (solo para este módulo) ====================


def _crear_clase(nombre: str) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT COALESCE(MAX(CAST(ID_Clase AS UNSIGNED)), 0) + 1 FROM Clase_producto"
        )
        id_clase = str(cursor.fetchone()[0])
        cursor.execute(
            "INSERT INTO Clase_producto (ID_Clase, Nombre_Clase) VALUES (%s, %s)",
            (id_clase, nombre),
        )
        db.commit()
        return id_clase
    finally:
        cursor.close()
        db.close()


def _eliminar_clase(id_clase: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Clase_producto WHERE ID_Clase = %s", (id_clase,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _crear_marca(nombre: str) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT COALESCE(MAX(CAST(ID_marca AS UNSIGNED)), 0) + 1 FROM Marca_producto"
        )
        id_marca = str(cursor.fetchone()[0])
        cursor.execute(
            "INSERT INTO Marca_producto (ID_marca, Nombre_marca) VALUES (%s, %s)",
            (id_marca, nombre),
        )
        db.commit()
        return id_marca
    finally:
        cursor.close()
        db.close()


def _eliminar_marca(id_marca: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Marca_producto WHERE ID_marca = %s", (id_marca,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


class TestCategorias:
    """La tabla Categoria está vacía en el seed: solo se valida el contrato."""

    def test_listar_categorias_devuelve_lista(self):
        categorias = Categoria().listar_categorias()

        assert isinstance(categorias, list)
        for categoria in categorias:
            assert set(categoria.keys()) == {"id", "nombre"}

    def test_obtener_categoria_sin_id(self):
        assert Categoria().obtener_categoria() is None

    def test_obtener_categoria_inexistente(self):
        assert Categoria(id_categoria=999999).obtener_categoria() is None


class TestListarClases:

    def test_incluye_las_clases_del_seed(self):
        clases = ClaseProducto().listar_clases()
        nombres = {clase["nombre"] for clase in clases}

        assert {"Telefono", "Pantalla", "Tablet", "Repuesto"} <= nombres

    def test_incluye_clase_temporal(self):
        id_clase = _crear_clase("Clase Integra Listado")
        try:
            clases = ClaseProducto().listar_clases()
            assert any(clase["id"] == id_clase for clase in clases)
        finally:
            _eliminar_clase(id_clase)


class TestVerificarObtenerClase:

    def test_verificar_clase_existente(self):
        assert ClaseProducto(id_clase=CLASE_TELEFONO).verificar_clase() is True

    def test_verificar_clase_inexistente(self):
        assert (
            ClaseProducto(id_clase=ID_CLASE_INEXISTENTE).verificar_clase() is False
        )

    def test_verificar_clase_sin_id(self):
        assert ClaseProducto().verificar_clase() is False

    def test_obtener_clase_existente(self):
        assert ClaseProducto(id_clase=CLASE_TELEFONO).obtener_clase() == {
            "id": CLASE_TELEFONO,
            "nombre": "Telefono",
        }

    def test_obtener_clase_inexistente(self):
        assert ClaseProducto(id_clase=ID_CLASE_INEXISTENTE).obtener_clase() is None

    def test_obtener_clase_sin_id(self):
        assert ClaseProducto().obtener_clase() is None


class TestRegistrarClase:

    def test_datos_validos(self):
        nombre = "Clase Integra Agregar"
        id_clase = None
        try:
            id_clase = ClaseProducto(nombre=nombre).registrar_clase()

            assert id_clase is not None
            assert ClaseProducto(id_clase=id_clase).verificar_clase() is True
            assert ClaseProducto(id_clase=id_clase).obtener_clase() == {
                "id": id_clase,
                "nombre": nombre,
            }
        finally:
            if id_clase:
                _eliminar_clase(id_clase)

    def test_nombre_duplicado(self):
        nombre = "Clase Integra Duplicada"
        id_clase = None
        try:
            id_clase = _crear_clase(nombre)
            with pytest.raises(ValueError) as exc:
                ClaseProducto(nombre=nombre).registrar_clase()

            assert str(exc.value) == f"Ya existe una clase con el nombre '{nombre}'."
        finally:
            _eliminar_clase(id_clase)

    def test_nombre_seed_duplicado(self):
        with pytest.raises(ValueError) as exc:
            ClaseProducto(nombre="Telefono").registrar_clase()

        assert str(exc.value) == "Ya existe una clase con el nombre 'Telefono'."

    @pytest.mark.parametrize(
        "nombre, esperado",
        [
            pytest.param(
                "",
                "El campo Nombre de la clase no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "C",
                "El campo Nombre de la clase debe tener al menos 2 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                "C" * 31,
                "El campo Nombre de la clase no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Clase #1",
                "El campo Nombre de la clase solo puede contener letras, espacios, acentos y ñ.",
                id="nombre-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, nombre, esperado):
        with pytest.raises(ValueError) as exc:
            ClaseProducto(nombre=nombre).registrar_clase()

        assert str(exc.value) == esperado


class TestListarMarcas:

    def test_incluye_las_marcas_del_seed(self):
        marcas = MarcaProducto().listar_marcas()
        nombres = {marca["nombre"] for marca in marcas}

        assert {"Samsung", "Xiaomi", "Motorola"} <= nombres

    def test_incluye_marca_temporal(self):
        id_marca = _crear_marca("Marca Integra Listado")
        try:
            marcas = MarcaProducto().listar_marcas()
            assert any(marca["id"] == id_marca for marca in marcas)
        finally:
            _eliminar_marca(id_marca)

    def test_filtro_por_clase(self):
        # listar_marcas(id_clase) solo devuelve marcas con productos en esa clase.
        id_marca = _crear_marca("Marca Integra Filtro")
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                clase=CLASE_TELEFONO, marca=id_marca
            )
            marcas = MarcaProducto().listar_marcas(id_clase=CLASE_TELEFONO)

            assert any(marca["id"] == id_marca for marca in marcas)
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)
            _eliminar_marca(id_marca)


class TestVerificarObtenerMarca:

    def test_verificar_marca_existente(self):
        assert MarcaProducto(id_marca=MARCA_SEED).verificar_marca() is True

    def test_verificar_marca_inexistente(self):
        assert MarcaProducto(id_marca=ID_MARCA_INEXISTENTE).verificar_marca() is False

    def test_verificar_marca_sin_id(self):
        assert MarcaProducto().verificar_marca() is False

    def test_obtener_marca_existente(self):
        assert MarcaProducto(id_marca=MARCA_SEED).obtener_marca() == {
            "id": MARCA_SEED,
            "nombre": "Samsung",
        }

    def test_obtener_marca_inexistente(self):
        assert MarcaProducto(id_marca=ID_MARCA_INEXISTENTE).obtener_marca() is None


class TestRegistrarMarca:

    def test_datos_validos(self):
        nombre = "Marca Integra Agregar"
        id_marca = None
        try:
            id_marca = MarcaProducto(nombre=nombre).registrar_marca()

            assert id_marca is not None
            assert MarcaProducto(id_marca=id_marca).verificar_marca() is True
            assert MarcaProducto(id_marca=id_marca).obtener_marca() == {
                "id": id_marca,
                "nombre": nombre,
            }
        finally:
            if id_marca:
                _eliminar_marca(id_marca)

    def test_nombre_duplicado(self):
        nombre = "Marca Integra Duplicada"
        id_marca = None
        try:
            id_marca = _crear_marca(nombre)
            with pytest.raises(ValueError) as exc:
                MarcaProducto(nombre=nombre).registrar_marca()

            assert str(exc.value) == f"Ya existe una marca con el nombre '{nombre}'."
        finally:
            _eliminar_marca(id_marca)

    @pytest.mark.parametrize(
        "nombre, esperado",
        [
            pytest.param(
                "",
                "El campo Nombre de la marca no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "M",
                "El campo Nombre de la marca debe tener al menos 2 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                "M" * 31,
                "El campo Nombre de la marca no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Marca #1",
                "El campo Nombre de la marca solo puede contener letras, números y espacios.",
                id="nombre-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, nombre, esperado):
        with pytest.raises(ValueError) as exc:
            MarcaProducto(nombre=nombre).registrar_marca()

        assert str(exc.value) == esperado


class TestRegistrarProducto:

    def test_datos_validos(self):
        nombre = "Producto Integra Agregar"
        id_producto = None
        try:
            id_producto = Producto(
                id_clase=CLASE_TELEFONO,
                id_marca=MARCA_SEED,
                nombre=nombre,
                descripcion="Producto temporal de integración",
            ).registrar_producto()

            assert id_producto is not None
            assert Producto(id_producto=id_producto).verificar_producto() is True
            producto = Producto(id_producto=id_producto).obtener_producto()
            assert producto["nombre"] == nombre
            assert producto["marca_nombre"] == "Samsung"
            assert producto["clase_nombre"] == "Telefono"
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_producto_duplicado(self):
        nombre = "Producto Integra Duplicado"
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre=nombre, clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            with pytest.raises(ValueError) as exc:
                Producto(
                    id_clase=CLASE_TELEFONO,
                    id_marca=MARCA_SEED,
                    nombre=nombre,
                ).registrar_producto()

            assert str(exc.value) == (
                f"Ya existe un producto con el nombre '{nombre}' en esta clase y marca."
            )
        finally:
            eliminar_producto_temporal(id_producto)

    def test_clase_inexistente(self):
        with pytest.raises(ValueError) as exc:
            Producto(
                id_clase=ID_CLASE_INEXISTENTE,
                id_marca=MARCA_SEED,
                nombre="Producto Integra Clase Inexistente",
            ).registrar_producto()

        assert str(exc.value) == (
            f"La clase con ID '{ID_CLASE_INEXISTENTE}' no existe."
        )

    def test_marca_inexistente(self):
        with pytest.raises(ValueError) as exc:
            Producto(
                id_clase=CLASE_TELEFONO,
                id_marca=ID_MARCA_INEXISTENTE,
                nombre="Producto Integra Marca Inexistente",
            ).registrar_producto()

        assert str(exc.value) == (
            f"La marca con ID '{ID_MARCA_INEXISTENTE}' no existe."
        )

    def test_descripcion_demasiado_larga(self):
        with pytest.raises(ValueError) as exc:
            Producto(
                id_clase=CLASE_TELEFONO,
                id_marca=MARCA_SEED,
                nombre="Producto Integra Descripcion Larga",
                descripcion="D" * 301,
            ).registrar_producto()

        assert str(exc.value) == "La descripción no puede exceder 300 caracteres."

    @pytest.mark.parametrize(
        "id_clase, id_marca, nombre, esperado",
        [
            pytest.param(
                CLASE_TELEFONO,
                MARCA_SEED,
                "",
                "El campo Nombre del producto no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                CLASE_TELEFONO,
                MARCA_SEED,
                "P",
                "El campo Nombre del producto debe tener al menos 2 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                CLASE_TELEFONO,
                MARCA_SEED,
                "P" * 51,
                "El campo Nombre del producto no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                CLASE_TELEFONO,
                MARCA_SEED,
                "Producto @",
                "El campo Nombre del producto solo puede contener letras, números, espacios, guiones y paréntesis.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                CLASE_TELEFONO,
                "",
                "Producto Sin Marca",
                "La marca es obligatoria.",
                id="marca-vacia",
            ),
            pytest.param(
                "",
                MARCA_SEED,
                "Producto Sin Clase",
                "La clase es obligatoria.",
                id="clase-vacia",
            ),
            pytest.param(
                "abc",
                "abc",
                "Producto IDs No Numericos",
                "Los identificadores de clase y marca deben ser numéricos.",
                id="ids-no-numericos",
            ),
        ],
    )
    def test_datos_invalidos(self, id_clase, id_marca, nombre, esperado):
        with pytest.raises(ValueError) as exc:
            Producto(id_clase=id_clase, id_marca=id_marca, nombre=nombre).registrar_producto()

        assert str(exc.value) == esperado


class TestListarProductos:

    def test_incluye_producto_temporal(self):
        nombre = "Producto Integra Listado"
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre=nombre, clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            productos = Producto().listar_productos()
            fila = next(
                (p for p in productos if p["id"] == id_producto), None
            )

            assert fila is not None
            assert fila["nombre"] == nombre
            assert fila["marca_nombre"] == "Samsung"
            assert fila["clase_nombre"] == "Telefono"
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_filtro_por_marca_y_clase(self):
        nombre = "Producto Integra Filtro"
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre=nombre, clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            por_marca = Producto().listar_productos(id_marca=MARCA_SEED)
            por_clase = Producto().listar_productos(id_clase=CLASE_TELEFONO)

            assert any(p["id"] == id_producto for p in por_marca)
            assert any(p["id"] == id_producto for p in por_clase)
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_filtro_por_busqueda(self):
        nombre = "Producto Integra Buscar XYZ"
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre=nombre, clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            resultado = Producto().listar_productos(q="Buscar XYZ")

            assert [p["id"] for p in resultado] == [id_producto]
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)


class TestActualizarProducto:

    def test_datos_validos(self):
        nombre = "Producto Integra Original"
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre=nombre, clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            nombre_nuevo = "Producto Integra Actualizado"

            resultado = Producto(
                id_producto=id_producto,
                id_clase=CLASE_TELEFONO,
                id_marca=MARCA_SEED,
                nombre=nombre_nuevo,
                descripcion="Descripción actualizada",
            ).actualizar_producto()

            assert resultado is True
            producto = Producto(id_producto=id_producto).obtener_producto()
            assert producto["nombre"] == nombre_nuevo
            assert producto["descripcion"] == "Descripción actualizada"
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_nombre_duplicado_de_otro_producto(self):
        id_producto_a = None
        id_producto_b = None
        try:
            id_producto_a = crear_producto_temporal(
                nombre="Producto Integra A Dup", clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            nombre_b = "Producto Integra B Dup"
            id_producto_b = crear_producto_temporal(
                nombre=nombre_b, clase=CLASE_TELEFONO, marca=MARCA_SEED
            )

            with pytest.raises(ValueError) as exc:
                Producto(
                    id_producto=id_producto_a,
                    id_clase=CLASE_TELEFONO,
                    id_marca=MARCA_SEED,
                    nombre=nombre_b,
                ).actualizar_producto()

            assert str(exc.value) == (
                f"Ya existe otro producto con el nombre '{nombre_b}' en esta clase y marca."
            )
        finally:
            if id_producto_a:
                eliminar_producto_temporal(id_producto_a)
            if id_producto_b:
                eliminar_producto_temporal(id_producto_b)

    def test_producto_inexistente(self):
        with pytest.raises(ValueError) as exc:
            Producto(
                id_producto="999999",
                id_clase=CLASE_TELEFONO,
                id_marca=MARCA_SEED,
                nombre="Producto Integra Fantasma",
            ).actualizar_producto()

        assert str(exc.value) == "El producto con ID '999999' no existe."

    def test_sin_id(self):
        with pytest.raises(ValueError) as exc:
            Producto(
                id_clase=CLASE_TELEFONO,
                id_marca=MARCA_SEED,
                nombre="Producto Integra Sin ID",
            ).actualizar_producto()

        assert str(exc.value) == "ID del producto es requerido para actualizar."


class TestEliminarProducto:

    def test_datos_validos(self):
        id_producto = crear_producto_temporal(
            nombre="Producto Integra Eliminar",
            clase=CLASE_TELEFONO,
            marca=MARCA_SEED,
        )
        try:
            resultado = Producto(id_producto=id_producto).eliminar_producto()

            assert resultado is True
            assert Producto(id_producto=id_producto).verificar_producto() is False
        finally:
            eliminar_producto_temporal(id_producto)

    def test_producto_inexistente(self):
        with pytest.raises(ValueError) as exc:
            Producto(id_producto="999999").eliminar_producto()

        assert str(exc.value) == "El producto con ID '999999' no existe."

    def test_sin_id(self):
        with pytest.raises(ValueError) as exc:
            Producto().eliminar_producto()

        assert str(exc.value) == "ID del producto es requerido para eliminar."


class TestStockProducto:

    def test_con_existencias(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Producto Integra Stock",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            crear_existencia_temporal(id_producto, existencia=7, costo=500.0)
            crear_existencia_temporal(id_producto, existencia=3, costo=400.0)

            assert Producto(id_producto=id_producto).obtener_stock_producto() == 10
            assert Producto(id_producto=id_producto).verificar_stock_asociado() is True
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_sin_existencias(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Producto Integra Sin Stock",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )

            assert Producto(id_producto=id_producto).obtener_stock_producto() == 0
            assert Producto(id_producto=id_producto).verificar_stock_asociado() is False
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_sin_id(self):
        assert Producto().obtener_stock_producto() == 0
        assert Producto().verificar_stock_asociado() is False


class TestBuscarProducto:

    def test_encuentra_por_nombre_clase_marca(self):
        nombre = "Producto Integra Buscar Nombre"
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre=nombre, clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            resultado = Producto().buscar_por_nombre_clase_marca(
                nombre, CLASE_TELEFONO, MARCA_SEED
            )

            assert resultado == id_producto
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_no_encuentra_con_otro_nombre(self):
        resultado = Producto().buscar_por_nombre_clase_marca(
            "Nombre Inexistente XYZ", CLASE_TELEFONO, MARCA_SEED
        )

        assert resultado is None

    def test_sin_datos_completos(self):
        assert Producto().buscar_por_nombre_clase_marca("", "1", "1") is None
        assert Producto().buscar_por_nombre_clase_marca("X", "", "1") is None
        assert Producto().buscar_por_nombre_clase_marca("X", "1", "") is None


class TestCapaCompatibilidad:
    """La clase Productos es la capa de compatibilidad para controladores."""

    def test_listar_clases(self):
        clases = Productos().listar_clases()

        assert isinstance(clases, list)
        assert any(clase["nombre"] == "Telefono" for clase in clases)

    def test_listar_marcas(self):
        marcas = Productos().listar_marcas()

        assert isinstance(marcas, list)
        assert any(marca["nombre"] == "Samsung" for marca in marcas)

    def test_listar_modelos(self):
        modelos = Productos().listar_modelos()

        assert isinstance(modelos, list)

    def test_listar_categorias(self):
        categorias = Productos().listar_categorias()

        assert isinstance(categorias, list)
