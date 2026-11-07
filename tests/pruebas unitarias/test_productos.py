"""Pruebas unitarias de los modelos de productos (app.models.productos).

Cubre las clases Categoria, ClaseProducto, MarcaProducto, Producto y la capa
de compatibilidad Productos. Los fixtures `conexion_falsa` y `conexion_caída`
viven en tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import MagicMock, patch

import mysql.connector
import pytest

from app.models.productos import (
    Categoria,
    ClaseProducto,
    MarcaProducto,
    Producto,
    Productos,
)
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ID_CATEGORIA = 1
NOMBRE_CATEGORIA = "Accesorios"

ID_CLASE = "1"
ID_MARCA = "2"
ID_PRODUCTO = "3"

NOMBRE_CLASE = "Celulares"
NOMBRE_MARCA = "Samsung"

NOMBRE_PRODUCTO_MINIMO = "TV"  # 2 caracteres (mínimo)
NOMBRE_PRODUCTO_MAXIMO = "P" * 50  # 50 caracteres (máximo)
DESCRIPCION_MAXIMA = "D" * 300  # 300 caracteres (máximo)

USUARIO_ID = "7"


class TestListarCategorias:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {"id": "1", "nombre": "Accesorios"},
            {"id": "2", "nombre": "Repuestos"},
        ]
        cursor.fetchall.return_value = filas

        resultado = Categoria().listar_categorias()

        assert resultado == filas
        assert "FROM Categoria" in ultima_sentencia(cursor)
        assert "ORDER BY Nombre_categoria ASC" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

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

        assert Categoria().listar_categorias() == []

    def test_conexion_caida(self, conexion_caída):
        assert Categoria().listar_categorias() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Categoria().listar_categorias()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Categoria().listar_categorias()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerCategoria:

    def test_categoria_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": "1", "nombre": "Accesorios"}
        cursor.fetchone.return_value = esperado

        resultado = Categoria(id_categoria=ID_CATEGORIA).obtener_categoria()

        assert resultado == esperado
        assert "WHERE ID_categoria = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_CATEGORIA,)

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Categoria().obtener_categoria() is None

        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_categoria_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Categoria(id_categoria=ID_CATEGORIA).obtener_categoria() is None

    def test_conexion_caida(self, conexion_caída):
        assert Categoria(id_categoria=ID_CATEGORIA).obtener_categoria() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1"}

        Categoria(id_categoria=ID_CATEGORIA).obtener_categoria()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1"}

        Categoria(id_categoria=ID_CATEGORIA).obtener_categoria()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarClases:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": "1", "nombre": "Celulares"}]
        cursor.fetchall.return_value = filas

        resultado = ClaseProducto().listar_clases()

        assert resultado == filas
        assert "FROM Clase_producto" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

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

        assert ClaseProducto().listar_clases() == []

    def test_conexion_caida(self, conexion_caída):
        assert ClaseProducto().listar_clases() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        ClaseProducto().listar_clases()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        ClaseProducto().listar_clases()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarClase:

    def test_clase_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert ClaseProducto(id_clase=ID_CLASE).verificar_clase() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Clase_producto WHERE ID_Clase = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_CLASE,)

    def test_clase_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert ClaseProducto(id_clase=ID_CLASE).verificar_clase() is False

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert ClaseProducto().verificar_clase() is False
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert ClaseProducto(id_clase=ID_CLASE).verificar_clase() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        ClaseProducto(id_clase=ID_CLASE).verificar_clase()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        ClaseProducto(id_clase=ID_CLASE).verificar_clase()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerClase:

    def test_clase_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": "1", "nombre": "Celulares"}
        cursor.fetchone.return_value = esperado

        resultado = ClaseProducto(id_clase=ID_CLASE).obtener_clase()

        assert resultado == esperado
        assert "WHERE ID_Clase = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_CLASE,)

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert ClaseProducto().obtener_clase() is None
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_clase_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert ClaseProducto(id_clase=ID_CLASE).obtener_clase() is None

    def test_conexion_caida(self, conexion_caída):
        assert ClaseProducto(id_clase=ID_CLASE).obtener_clase() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1"}

        ClaseProducto(id_clase=ID_CLASE).obtener_clase()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "1"}

        ClaseProducto(id_clase=ID_CLASE).obtener_clase()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestRegistrarClase:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (duplicado): None; 2ª (MAX): siguiente id = 8
        cursor.fetchone.side_effect = [None, (8,)]

        clase = ClaseProducto(nombre=NOMBRE_CLASE)
        resultado = clase.registrar_clase()

        assert resultado == "8"
        assert clase.id_clase == "8"
        assert cursor.execute.call_args_list[-1].args == (
            "INSERT INTO Clase_producto (ID_Clase, Nombre_Clase) VALUES (%s, %s)",
            ("8", NOMBRE_CLASE),
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (duplicado + INSERT) + _siguiente_id consultan y cierran
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "nombre",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_sin_nombre_no_toca_la_bd(self, conexion_falsa, nombre):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError, match="El nombre de la clase es obligatorio."):
            ClaseProducto(nombre=nombre).registrar_clase()

        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(
            RuntimeError, match="No se pudo conectar a la base de datos."
        ):
            ClaseProducto(nombre=NOMBRE_CLASE).registrar_clase()

    def test_nombre_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with pytest.raises(
            ValueError, match=f"Ya existe una clase con el nombre '{NOMBRE_CLASE}'."
        ):
            ClaseProducto(nombre=NOMBRE_CLASE).registrar_clase()

        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()
        db.rollback.assert_called_once()
        cierra_recursos(db, cursor)

    def test_id_siguiente_con_maximo_nulo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (None,)]

        resultado = ClaseProducto(nombre=NOMBRE_CLASE).registrar_clase()

        assert resultado == "0"
        assert cursor.execute.call_args_list[-1].args[1] == ("0", NOMBRE_CLASE)

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (8,)]
        # 1ª: duplicado; 2ª: MAX; 3ª: el INSERT que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        with pytest.raises(Exception, match="fallo simulado"):
            ClaseProducto(nombre=NOMBRE_CLASE).registrar_clase()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (8,)]

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            ClaseProducto(
                nombre=NOMBRE_CLASE, usuario_id=USUARIO_ID
            ).registrar_clase()

        bitacora_cls.assert_called_once_with(
            accion="Crear clase",
            descripcion=f"Clase creada: {NOMBRE_CLASE} (ID: 8)",
            usuario_id=USUARIO_ID,
            modulo_nombre="Productos",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (8,)]

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            ClaseProducto(nombre=NOMBRE_CLASE).registrar_clase()

        bitacora_cls.assert_not_called()


class TestListarMarcas:

    def test_sin_filtro(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": "2", "nombre": "Samsung"}]
        cursor.fetchall.return_value = filas

        resultado = MarcaProducto().listar_marcas()

        assert resultado == filas
        assert "FROM Marca_producto" in ultima_sentencia(cursor)
        assert "JOIN Producto" not in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args == (ultima_sentencia(cursor),)

    def test_filtro_por_argumento(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        MarcaProducto().listar_marcas(id_clase=ID_CLASE)

        assert "JOIN Producto p ON p.ID_marca = ma.ID_marca" in ultima_sentencia(
            cursor
        )
        assert "WHERE p.ID_Clase = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_CLASE,)

    def test_filtro_por_atributo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        MarcaProducto(id_clase=ID_CLASE).listar_marcas()

        assert cursor.execute.call_args.args[1] == (ID_CLASE,)

    def test_el_argumento_tiene_prioridad_sobre_el_atributo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        MarcaProducto(id_clase="2").listar_marcas(id_clase=ID_CLASE)

        assert cursor.execute.call_args.args[1] == (ID_CLASE,)

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

        assert MarcaProducto().listar_marcas() == []

    def test_conexion_caida(self, conexion_caída):
        assert MarcaProducto().listar_marcas() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        MarcaProducto().listar_marcas()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        MarcaProducto().listar_marcas()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarMarca:

    def test_marca_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert MarcaProducto(id_marca=ID_MARCA).verificar_marca() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Marca_producto WHERE ID_marca = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_MARCA,)

    def test_marca_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert MarcaProducto(id_marca=ID_MARCA).verificar_marca() is False

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert MarcaProducto().verificar_marca() is False
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert MarcaProducto(id_marca=ID_MARCA).verificar_marca() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        MarcaProducto(id_marca=ID_MARCA).verificar_marca()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        MarcaProducto(id_marca=ID_MARCA).verificar_marca()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerMarca:

    def test_marca_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": "2", "nombre": "Samsung"}
        cursor.fetchone.return_value = esperado

        resultado = MarcaProducto(id_marca=ID_MARCA).obtener_marca()

        assert resultado == esperado
        assert "WHERE ID_marca = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_MARCA,)

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert MarcaProducto().obtener_marca() is None
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_marca_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert MarcaProducto(id_marca=ID_MARCA).obtener_marca() is None

    def test_conexion_caida(self, conexion_caída):
        assert MarcaProducto(id_marca=ID_MARCA).obtener_marca() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "2"}

        MarcaProducto(id_marca=ID_MARCA).obtener_marca()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": "2"}

        MarcaProducto(id_marca=ID_MARCA).obtener_marca()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestRegistrarMarca:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (9,)]

        marca = MarcaProducto(nombre=NOMBRE_MARCA)
        resultado = marca.registrar_marca()

        assert resultado == "9"
        assert marca.id_marca == "9"
        assert cursor.execute.call_args_list[-1].args == (
            "INSERT INTO Marca_producto (ID_marca, Nombre_marca) VALUES (%s, %s)",
            ("9", NOMBRE_MARCA),
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "nombre",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_sin_nombre_no_toca_la_bd(self, conexion_falsa, nombre):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError, match="El nombre de la marca es obligatorio."):
            MarcaProducto(nombre=nombre).registrar_marca()

        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(
            RuntimeError, match="No se pudo conectar a la base de datos."
        ):
            MarcaProducto(nombre=NOMBRE_MARCA).registrar_marca()

    def test_nombre_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with pytest.raises(
            ValueError, match=f"Ya existe una marca con el nombre '{NOMBRE_MARCA}'."
        ):
            MarcaProducto(nombre=NOMBRE_MARCA).registrar_marca()

        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()
        db.rollback.assert_called_once()
        cierra_recursos(db, cursor)

    def test_id_siguiente_con_maximo_nulo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (None,)]

        resultado = MarcaProducto(nombre=NOMBRE_MARCA).registrar_marca()

        assert resultado == "0"
        assert cursor.execute.call_args_list[-1].args[1] == ("0", NOMBRE_MARCA)

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (9,)]
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        with pytest.raises(Exception, match="fallo simulado"):
            MarcaProducto(nombre=NOMBRE_MARCA).registrar_marca()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (9,)]

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            MarcaProducto(
                nombre=NOMBRE_MARCA, usuario_id=USUARIO_ID
            ).registrar_marca()

        bitacora_cls.assert_called_once_with(
            accion="Crear marca",
            descripcion=f"Marca creada: {NOMBRE_MARCA} (ID: 9)",
            usuario_id=USUARIO_ID,
            modulo_nombre="Productos",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (9,)]

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            MarcaProducto(nombre=NOMBRE_MARCA).registrar_marca()

        bitacora_cls.assert_not_called()


class TestListarProductos:

    def test_sin_filtros(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": "3", "nombre": "Funda"}]
        cursor.fetchall.return_value = filas

        resultado = Producto().listar_productos()

        assert resultado == filas
        assert "FROM Producto p" in ultima_sentencia(cursor)
        assert "WHERE" not in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == ()

    def test_filtro_por_marca(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Producto().listar_productos(id_marca=ID_MARCA)

        assert "p.ID_marca = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_MARCA,)

    def test_filtro_por_clase(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Producto().listar_productos(id_clase=ID_CLASE)

        assert "p.ID_Clase = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_CLASE,)

    def test_filtros_por_atributos_de_la_instancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Producto(id_clase=ID_CLASE, id_marca=ID_MARCA).listar_productos()

        assert "p.ID_marca = %s" in ultima_sentencia(cursor)
        assert "p.ID_Clase = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_MARCA, ID_CLASE)

    def test_busqueda_por_nombre(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Producto().listar_productos(q="funda")

        assert "p.Nombre_producto LIKE %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == ("%funda%",)

    def test_todos_los_filtros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Producto().listar_productos(id_marca=ID_MARCA, id_clase=ID_CLASE, q="TV")

        assert cursor.execute.call_args.args[1] == (ID_MARCA, ID_CLASE, "%TV%")

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

        assert Producto().listar_productos() == []

    def test_conexion_caida(self, conexion_caída):
        assert Producto().listar_productos() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Producto().listar_productos()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Producto().listar_productos()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarProducto:

    def test_producto_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Producto(id_producto=ID_PRODUCTO).verificar_producto() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Producto WHERE ID_producto = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (ID_PRODUCTO,)

    def test_producto_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Producto(id_producto=ID_PRODUCTO).verificar_producto() is False

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Producto().verificar_producto() is False
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Producto(id_producto=ID_PRODUCTO).verificar_producto() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Producto(id_producto=ID_PRODUCTO).verificar_producto()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Producto(id_producto=ID_PRODUCTO).verificar_producto()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerProducto:

    def test_producto_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "id": ID_PRODUCTO,
            "id_marca": ID_MARCA,
            "id_clase": ID_CLASE,
            "nombre": "Funda",
            "descripcion": "Funda de silicona",
            "marca_nombre": "Samsung",
            "clase_nombre": "Celulares",
        }
        cursor.fetchone.return_value = esperado

        resultado = Producto(id_producto=ID_PRODUCTO).obtener_producto()

        assert resultado == esperado
        assert "LEFT JOIN Marca_producto" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_PRODUCTO,)

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Producto().obtener_producto() is None
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_producto_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Producto(id_producto=ID_PRODUCTO).obtener_producto() is None

    def test_conexion_caida(self, conexion_caída):
        assert Producto(id_producto=ID_PRODUCTO).obtener_producto() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ID_PRODUCTO}

        Producto(id_producto=ID_PRODUCTO).obtener_producto()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ID_PRODUCTO}

        Producto(id_producto=ID_PRODUCTO).obtener_producto()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarStockProcedure:

    def test_sin_id_devuelve_error(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Producto().verificar_stock_procedure()

        assert resultado == {
            "stock_total": 0,
            "tiene_stock": False,
            "detalle": [],
            "success": False,
            "error": "ID de producto no especificado",
        }
        db.cursor.assert_not_called()

    def test_conexion_caida_devuelve_error(self, conexion_caída):
        resultado = Producto(id_producto=ID_PRODUCTO).verificar_stock_procedure()

        assert resultado == {
            "stock_total": 0,
            "tiene_stock": False,
            "detalle": [],
            "success": False,
            "error": "No se pudo conectar a la BD",
        }

    def test_sin_detalle(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"stock_total": 12, "tiene_stock": 1}

        resultado = Producto(id_producto=ID_PRODUCTO).verificar_stock_procedure()

        assert resultado == {
            "stock_total": 12,
            "tiene_stock": True,
            "detalle": [],
            "success": True,
        }
        cursor.callproc.assert_called_once_with(
            "sp_verificar_stock_producto", (ID_PRODUCTO, 0, False)
        )
        assert "SELECT @_sp_verificar_stock_producto_1" in ultima_sentencia(cursor)

    def test_parametros_de_salida_nulos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Producto(id_producto=ID_PRODUCTO).verificar_stock_procedure()

        assert resultado == {
            "stock_total": 0,
            "tiene_stock": False,
            "detalle": [],
            "success": True,
        }

    def test_con_detalle(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"stock_total": 5, "tiene_stock": 1}
        filas = [{"ID_inventario": "INV-1", "Existencia": 5}]
        resultado_mock = MagicMock()
        resultado_mock.fetchall.return_value = filas
        cursor.stored_results.return_value = [resultado_mock]

        resultado = Producto(id_producto=ID_PRODUCTO).verificar_stock_procedure()

        assert resultado["detalle"] == filas
        assert resultado["success"] is True

    def test_el_ultimo_resultado_con_filas_es_el_detalle(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"stock_total": 5, "tiene_stock": 1}
        primero = MagicMock()
        primero.fetchall.return_value = [{"fila": 1}]
        vacio = MagicMock()
        vacio.fetchall.return_value = []
        ultimo = MagicMock()
        ultimo.fetchall.return_value = [{"fila": 2}]
        cursor.stored_results.return_value = [primero, vacio, ultimo]

        resultado = Producto(id_producto=ID_PRODUCTO).verificar_stock_procedure()

        assert resultado["detalle"] == [{"fila": 2}]

    def test_error_de_mysql_devuelve_error(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.callproc.side_effect = mysql.connector.Error("fallo simulado")

        resultado = Producto(id_producto=ID_PRODUCTO).verificar_stock_procedure()

        assert resultado == {
            "stock_total": 0,
            "tiene_stock": False,
            "detalle": [],
            "error": "fallo simulado",
            "success": False,
        }
        cierra_recursos(db, cursor)

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"stock_total": 1, "tiene_stock": 1}

        Producto(id_producto=ID_PRODUCTO).verificar_stock_procedure()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"stock_total": 1, "tiene_stock": 1}

        Producto(id_producto=ID_PRODUCTO).verificar_stock_procedure()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestBuscarPorNombreClaseMarca:

    @pytest.mark.parametrize(
        "nombre, id_clase, id_marca",
        [
            pytest.param("", ID_CLASE, ID_MARCA, id="sin-nombre"),
            pytest.param("Funda", "", ID_MARCA, id="sin-clase"),
            pytest.param("Funda", ID_CLASE, "", id="sin-marca"),
        ],
    )
    def test_parametros_incompletos_no_tocan_la_bd(
        self, conexion_falsa, nombre, id_clase, id_marca
    ):
        db, cursor = conexion_falsa

        resultado = Producto().buscar_por_nombre_clase_marca(
            nombre, id_clase, id_marca
        )

        assert resultado is None
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_producto_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"ID_producto": ID_PRODUCTO}

        resultado = Producto().buscar_por_nombre_clase_marca(
            "Funda", ID_CLASE, ID_MARCA
        )

        assert resultado == ID_PRODUCTO
        assert "LOWER(TRIM(Nombre_producto))" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == ("Funda", ID_CLASE, ID_MARCA)

    def test_producto_no_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert (
            Producto().buscar_por_nombre_clase_marca("Funda", ID_CLASE, ID_MARCA)
            is None
        )

    def test_conexion_caida(self, conexion_caída):
        assert (
            Producto().buscar_por_nombre_clase_marca("Funda", ID_CLASE, ID_MARCA)
            is None
        )

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert (
            Producto().buscar_por_nombre_clase_marca("Funda", ID_CLASE, ID_MARCA)
            is None
        )
        cierra_recursos(db, cursor)

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Producto().buscar_por_nombre_clase_marca("Funda", ID_CLASE, ID_MARCA)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        Producto().buscar_por_nombre_clase_marca("Funda", ID_CLASE, ID_MARCA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestRegistrarProducto:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # clase existe, marca existe, no duplicado, siguiente id
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": 9}]

        producto = Producto(
            id_clase=ID_CLASE,
            id_marca=ID_MARCA,
            nombre="  Funda  ",
            descripcion="  Protector  ",
        )
        resultado = producto.registrar_producto()

        assert resultado == "9"
        assert producto.id_producto == "9"
        assert "INSERT INTO Producto" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            "9",
            ID_CLASE,
            ID_MARCA,
            "Funda",
            "Protector",
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_descripcion_inserta_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": 9}]

        Producto(
            id_clase=ID_CLASE, id_marca=ID_MARCA, nombre="Funda"
        ).registrar_producto()

        assert cursor.execute.call_args_list[-1].args[1][4] is None

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": 9}]

        resultado = Producto(
            id_clase=ID_CLASE,
            id_marca=ID_MARCA,
            nombre=NOMBRE_PRODUCTO_MINIMO,
            descripcion=DESCRIPCION_MAXIMA,
        ).registrar_producto()

        assert resultado == "9"
        db.commit.assert_called_once()

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": 9}]

        resultado = Producto(
            id_clase=ID_CLASE,
            id_marca=ID_MARCA,
            nombre=NOMBRE_PRODUCTO_MAXIMO,
            descripcion=DESCRIPCION_MAXIMA,
        ).registrar_producto()

        assert resultado == "9"
        assert cursor.execute.call_args_list[-1].args[1][3] == NOMBRE_PRODUCTO_MAXIMO
        assert cursor.execute.call_args_list[-1].args[1][4] == DESCRIPCION_MAXIMA

    @pytest.mark.parametrize(
        "id_clase, id_marca, nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                ID_MARCA,
                "Funda",
                None,
                "Clase, marca y nombre son obligatorios.",
                id="clase-vacia",
            ),
            pytest.param(
                ID_CLASE,
                "",
                "Funda",
                None,
                "Clase, marca y nombre son obligatorios.",
                id="marca-vacia",
            ),
            pytest.param(
                ID_CLASE,
                ID_MARCA,
                "",
                None,
                "Clase, marca y nombre son obligatorios.",
                id="nombre-vacio",
            ),
            pytest.param(
                ID_CLASE,
                ID_MARCA,
                "P" * 51,
                None,
                "El nombre no puede exceder 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                ID_CLASE,
                ID_MARCA,
                "Funda",
                "D" * 301,
                "La descripción no puede exceder 300 caracteres.",
                id="descripcion-demasiado-larga",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, id_clase, id_marca, nombre, descripcion, esperado
    ):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as error:
            Producto(
                id_clase=id_clase,
                id_marca=id_marca,
                nombre=nombre,
                descripcion=descripcion,
            ).registrar_producto()

        assert str(error.value) == esperado
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(
            RuntimeError, match="No se pudo conectar a la base de datos."
        ):
            Producto(
                id_clase=ID_CLASE, id_marca=ID_MARCA, nombre="Funda"
            ).registrar_producto()

    def test_clase_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with pytest.raises(
            ValueError, match=f"La clase con ID '{ID_CLASE}' no existe."
        ):
            Producto(
                id_clase=ID_CLASE, id_marca=ID_MARCA, nombre="Funda"
            ).registrar_producto()

        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_marca_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), None]

        with pytest.raises(
            ValueError, match=f"La marca con ID '{ID_MARCA}' no existe."
        ):
            Producto(
                id_clase=ID_CLASE, id_marca=ID_MARCA, nombre="Funda"
            ).registrar_producto()

        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_producto_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), (1,)]

        with pytest.raises(
            ValueError,
            match=(
                f"Ya existe un producto con el nombre 'Funda' "
                "en esta clase y marca."
            ),
        ):
            Producto(
                id_clase=ID_CLASE, id_marca=ID_MARCA, nombre="Funda"
            ).registrar_producto()

        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_siguiente_id_nulo_usa_uno(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": None}]

        resultado = Producto(
            id_clase=ID_CLASE, id_marca=ID_MARCA, nombre="Funda"
        ).registrar_producto()

        assert resultado == "1"

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": 9}]
        # 1ª: clase; 2ª: marca; 3ª: duplicado; 4ª: MAX; 5ª: INSERT que falla
        cursor.execute.side_effect = [
            None,
            None,
            None,
            None,
            Exception("fallo simulado"),
        ]

        with pytest.raises(Exception, match="fallo simulado"):
            Producto(
                id_clase=ID_CLASE, id_marca=ID_MARCA, nombre="Funda"
            ).registrar_producto()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": 9}]

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            Producto(
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
                usuario_id=USUARIO_ID,
            ).registrar_producto()

        bitacora_cls.assert_called_once_with(
            accion="Crear producto",
            descripcion="Producto creado: Funda (ID: 9)",
            usuario_id=USUARIO_ID,
            modulo_nombre="Productos",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": 9}]

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            Producto(
                id_clase=ID_CLASE, id_marca=ID_MARCA, nombre="Funda"
            ).registrar_producto()

        bitacora_cls.assert_not_called()

    def test_error_de_bitacora_no_impide_el_registro(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None, {"next_id": 9}]

        with patch(
            "app.models.productos.Bitacora", side_effect=Exception("bitácora caída")
        ):
            resultado = Producto(
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
                usuario_id=USUARIO_ID,
            ).registrar_producto()

        assert resultado == "9"
        db.commit.assert_called_once()
        db.rollback.assert_not_called()


class TestActualizarProducto:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # producto, clase y marca existen; no hay duplicado
        cursor.fetchone.side_effect = [(1,), (1,), (1,), None]
        cursor.rowcount = 1

        producto = Producto(
            id_producto=ID_PRODUCTO,
            id_clase=ID_CLASE,
            id_marca=ID_MARCA,
            nombre="Funda",
            descripcion="Protector",
        )
        resultado = producto.actualizar_producto()

        assert resultado is True
        assert "UPDATE Producto" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            ID_CLASE,
            ID_MARCA,
            "Funda",
            "Protector",
            ID_PRODUCTO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_descripcion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), (1,), None]
        cursor.rowcount = 1

        resultado = Producto(
            id_producto=ID_PRODUCTO,
            id_clase=ID_CLASE,
            id_marca=ID_MARCA,
            nombre="Funda",
        ).actualizar_producto()

        assert resultado is True
        assert cursor.execute.call_args.args[1][3] is None

    @pytest.mark.parametrize(
        "id_producto, id_clase, id_marca, nombre, esperado",
        [
            pytest.param(
                "",
                ID_CLASE,
                ID_MARCA,
                "Funda",
                "ID del producto es requerido para actualizar.",
                id="id-vacio",
            ),
            pytest.param(
                ID_PRODUCTO,
                "",
                ID_MARCA,
                "Funda",
                "Clase, marca y nombre son obligatorios.",
                id="clase-vacia",
            ),
            pytest.param(
                ID_PRODUCTO,
                ID_CLASE,
                "",
                "Funda",
                "Clase, marca y nombre son obligatorios.",
                id="marca-vacia",
            ),
            pytest.param(
                ID_PRODUCTO,
                ID_CLASE,
                ID_MARCA,
                "",
                "Clase, marca y nombre son obligatorios.",
                id="nombre-vacio",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, id_producto, id_clase, id_marca, nombre, esperado
    ):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as error:
            Producto(
                id_producto=id_producto,
                id_clase=id_clase,
                id_marca=id_marca,
                nombre=nombre,
            ).actualizar_producto()

        assert str(error.value) == esperado
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(
            RuntimeError, match="No se pudo conectar a la base de datos."
        ):
            Producto(
                id_producto=ID_PRODUCTO,
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
            ).actualizar_producto()

    def test_producto_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with pytest.raises(
            ValueError, match=f"El producto con ID '{ID_PRODUCTO}' no existe."
        ):
            Producto(
                id_producto=ID_PRODUCTO,
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
            ).actualizar_producto()

        sin_sentencia(cursor, "UPDATE")
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_clase_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), None]

        with pytest.raises(
            ValueError, match=f"La clase con ID '{ID_CLASE}' no existe."
        ):
            Producto(
                id_producto=ID_PRODUCTO,
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
            ).actualizar_producto()

        sin_sentencia(cursor, "UPDATE")

    def test_marca_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None]

        with pytest.raises(
            ValueError, match=f"La marca con ID '{ID_MARCA}' no existe."
        ):
            Producto(
                id_producto=ID_PRODUCTO,
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
            ).actualizar_producto()

        sin_sentencia(cursor, "UPDATE")

    def test_nombre_duplicado_de_otro_producto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), (1,), (1,)]

        with pytest.raises(
            ValueError,
            match=(
                "Ya existe otro producto con el nombre 'Funda' "
                "en esta clase y marca."
            ),
        ):
            Producto(
                id_producto=ID_PRODUCTO,
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
            ).actualizar_producto()

        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_sin_filas_afectadas_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), (1,), None]
        cursor.rowcount = 0

        resultado = Producto(
            id_producto=ID_PRODUCTO,
            id_clase=ID_CLASE,
            id_marca=ID_MARCA,
            nombre="Funda",
        ).actualizar_producto()

        assert resultado is False
        db.commit.assert_called_once()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), (1,), None]
        # 1ª: producto; 2ª: clase; 3ª: marca; 4ª: duplicado; 5ª: UPDATE falla
        cursor.execute.side_effect = [
            None,
            None,
            None,
            None,
            Exception("fallo simulado"),
        ]

        with pytest.raises(Exception, match="fallo simulado"):
            Producto(
                id_producto=ID_PRODUCTO,
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
            ).actualizar_producto()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), (1,), None]
        cursor.rowcount = 1

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            Producto(
                id_producto=ID_PRODUCTO,
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
                usuario_id=USUARIO_ID,
            ).actualizar_producto()

        bitacora_cls.assert_called_once_with(
            accion="Actualizar producto",
            descripcion=f"Producto actualizado: Funda (ID: {ID_PRODUCTO})",
            usuario_id=USUARIO_ID,
            modulo_nombre="Productos",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_filas_afectadas_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), (1,), None]
        cursor.rowcount = 0

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            Producto(
                id_producto=ID_PRODUCTO,
                id_clase=ID_CLASE,
                id_marca=ID_MARCA,
                nombre="Funda",
                usuario_id=USUARIO_ID,
            ).actualizar_producto()

        bitacora_cls.assert_not_called()


class TestEliminarProducto:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        cursor.rowcount = 1

        resultado = Producto(id_producto=ID_PRODUCTO).eliminar_producto()

        assert resultado is True
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any("DELETE fi FROM Fotos_inventario" in sql for sql in sentencias)
        assert any("DELETE FROM Existencias_productos" in sql for sql in sentencias)
        assert any("DELETE FROM Suministra" in sql for sql in sentencias)
        assert any("DELETE FROM Producto" in sql for sql in sentencias)
        assert cursor.execute.call_args.args[1] == (ID_PRODUCTO,)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_borra_las_dependencias_antes_del_producto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        cursor.rowcount = 1

        Producto(id_producto=ID_PRODUCTO).eliminar_producto()

        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        pos_fotos = next(
            i for i, sql in enumerate(sentencias) if "DELETE fi FROM Fotos_inventario" in sql
        )
        pos_existencias = next(
            i for i, sql in enumerate(sentencias) if "DELETE FROM Existencias_productos" in sql
        )
        pos_suministra = next(
            i for i, sql in enumerate(sentencias) if "DELETE FROM Suministra" in sql
        )
        pos_producto = next(
            i for i, sql in enumerate(sentencias) if "DELETE FROM Producto" in sql
        )
        assert pos_fotos < pos_existencias < pos_suministra < pos_producto

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        with pytest.raises(
            ValueError, match="ID del producto es requerido para eliminar."
        ):
            Producto().eliminar_producto()

        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(
            RuntimeError, match="No se pudo conectar a la base de datos."
        ):
            Producto(id_producto=ID_PRODUCTO).eliminar_producto()

    def test_producto_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with pytest.raises(
            ValueError, match=f"El producto con ID '{ID_PRODUCTO}' no existe."
        ):
            Producto(id_producto=ID_PRODUCTO).eliminar_producto()

        sin_sentencia(cursor, "DELETE")
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_sin_filas_afectadas_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        cursor.rowcount = 0

        resultado = Producto(id_producto=ID_PRODUCTO).eliminar_producto()

        assert resultado is False
        db.commit.assert_called_once()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        with pytest.raises(Exception, match="fallo simulado"):
            Producto(id_producto=ID_PRODUCTO).eliminar_producto()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        cursor.rowcount = 1

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            Producto(
                id_producto=ID_PRODUCTO, usuario_id=USUARIO_ID
            ).eliminar_producto()

        bitacora_cls.assert_called_once_with(
            accion="Eliminar producto",
            descripcion=f"Producto eliminado (ID: {ID_PRODUCTO})",
            usuario_id=USUARIO_ID,
            modulo_nombre="Productos",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_filas_afectadas_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        cursor.rowcount = 0

        with patch("app.models.productos.Bitacora") as bitacora_cls:
            Producto(
                id_producto=ID_PRODUCTO, usuario_id=USUARIO_ID
            ).eliminar_producto()

        bitacora_cls.assert_not_called()


class TestVerificarStockAsociado:

    def test_con_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (2,)

        assert Producto(id_producto=ID_PRODUCTO).verificar_stock_asociado() is True

        assert "FROM Existencias_productos" in ultima_sentencia(cursor)
        assert "Existencia > 0" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_PRODUCTO,)

    @pytest.mark.parametrize(
        "fila, esperado",
        [
            pytest.param((0,), False, id="sin-existencias"),
            pytest.param(None, False, id="fetchone-none"),
        ],
    )
    def test_sin_stock(self, conexion_falsa, fila, esperado):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = fila

        assert (
            Producto(id_producto=ID_PRODUCTO).verificar_stock_asociado()
            is esperado
        )

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Producto().verificar_stock_asociado() is False
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Producto(id_producto=ID_PRODUCTO).verificar_stock_asociado() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Producto(id_producto=ID_PRODUCTO).verificar_stock_asociado()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Producto(id_producto=ID_PRODUCTO).verificar_stock_asociado()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerStockProducto:

    def test_con_stock(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (15,)

        assert Producto(id_producto=ID_PRODUCTO).obtener_stock_producto() == 15

        assert "COALESCE(SUM(Existencia), 0)" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_PRODUCTO,)

    @pytest.mark.parametrize(
        "fila, esperado",
        [
            pytest.param((0,), 0, id="stock-cero"),
            pytest.param(None, 0, id="fetchone-none"),
        ],
    )
    def test_sin_stock(self, conexion_falsa, fila, esperado):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = fila

        assert (
            Producto(id_producto=ID_PRODUCTO).obtener_stock_producto()
            == esperado
        )

    def test_sin_id_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Producto().obtener_stock_producto() == 0
        db.cursor.assert_not_called()
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Producto(id_producto=ID_PRODUCTO).obtener_stock_producto() == 0

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Producto(id_producto=ID_PRODUCTO).obtener_stock_producto()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Producto(id_producto=ID_PRODUCTO).obtener_stock_producto()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestProductosCompatibilidad:

    def test_listar_clases_delega_en_clase_producto(self):
        with patch("app.models.productos.ClaseProducto") as clase_cls:
            clase_cls.return_value.listar_clases.return_value = [{"id": "1"}]

            resultado = Productos().listar_clases()

        assert resultado == [{"id": "1"}]
        clase_cls.assert_called_once_with()
        clase_cls.return_value.listar_clases.assert_called_once_with()

    def test_listar_marcas_delega_con_el_filtro(self):
        with patch("app.models.productos.MarcaProducto") as marca_cls:
            marca_cls.return_value.listar_marcas.return_value = [{"id": "2"}]

            resultado = Productos().listar_marcas(id_clase=ID_CLASE)

        assert resultado == [{"id": "2"}]
        marca_cls.return_value.listar_marcas.assert_called_once_with(
            id_clase=ID_CLASE
        )

    def test_listar_modelos_delega_con_los_filtros(self):
        with patch("app.models.productos.Producto") as producto_cls:
            producto_cls.return_value.listar_productos.return_value = [
                {"id": ID_PRODUCTO}
            ]

            resultado = Productos().listar_modelos(
                id_marca=ID_MARCA, id_clase=ID_CLASE, q="Funda"
            )

        assert resultado == [{"id": ID_PRODUCTO}]
        producto_cls.return_value.listar_productos.assert_called_once_with(
            id_marca=ID_MARCA, id_clase=ID_CLASE, q="Funda"
        )

    def test_listar_categorias_delega_en_categoria(self):
        with patch("app.models.productos.Categoria") as categoria_cls:
            categoria_cls.return_value.listar_categorias.return_value = [
                {"id": "1", "nombre": "Accesorios"}
            ]

            resultado = Productos().listar_categorias()

        assert resultado == [{"id": "1", "nombre": "Accesorios"}]
        categoria_cls.return_value.listar_categorias.assert_called_once_with()
