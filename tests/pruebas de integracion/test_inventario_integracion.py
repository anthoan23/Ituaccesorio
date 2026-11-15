"""Pruebas de integración de la clase Inventario contra MySQL real."""
import pytest

from app.models.database import conectar
from app.models.inventario import Inventario
from seed_helpers import (
    crear_producto_temporal,
    eliminar_producto_temporal,
)

CLASE_TELEFONO = "1"
MARCA_SEED = "3"


# ==================== HELPERS LOCALES (solo para este módulo) ====================


def _crear_existencia(
    id_producto: str, existencia: int = 10, costo: float = 100.0, id_categoria=None
) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT CONCAT('INV', LPAD(COALESCE(MAX(CAST(SUBSTRING(ID_inventario, 4) AS UNSIGNED)), 0) + 1, 6, '0')) "
            "FROM Existencias_productos"
        )
        id_inventario = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO Existencias_productos (ID_inventario, ID_producto, Existencia, Costo_venta, ID_categoria) "
            "VALUES (%s, %s, %s, %s, %s)",
            (id_inventario, id_producto, existencia, costo, id_categoria),
        )
        db.commit()
        return id_inventario
    finally:
        cursor.close()
        db.close()


def _stock(id_inventario: str) -> int:
    db = conectar().conexion1()
    if not db:
        return 0
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
            (id_inventario,),
        )
        fila = cursor.fetchone()
        return int(fila[0] or 0) if fila else 0
    finally:
        cursor.close()
        db.close()


def _stock_por_id_producto(id_producto: str) -> dict:
    db = conectar().conexion1()
    if not db:
        return {}
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT ID_inventario, Existencia FROM Existencias_productos "
            "WHERE ID_producto = %s",
            (id_producto,),
        )
        return {fila[0]: int(fila[1] or 0) for fila in cursor.fetchall()}
    finally:
        cursor.close()
        db.close()


def _restaurar_stock(stocks: dict) -> None:
    if not stocks:
        return
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        for id_inv, cantidad in stocks.items():
            cursor.execute(
                "UPDATE Existencias_productos SET Existencia = %s WHERE ID_inventario = %s",
                (cantidad, id_inv),
            )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


class TestListarInventario:

    def test_incluye_producto_con_existencias(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Inventario", clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            id_inventario = _crear_existencia(
                id_producto, existencia=10, costo=500.0
            )

            filas = Inventario().listar_inventario()
            fila = next(
                (i for i in filas if i["id_inventario"] == id_inventario), None
            )

            assert fila is not None
            assert fila["id_producto"] == id_producto
            assert fila["nombre_producto"] == "Prod Integra Inventario"
            assert fila["existencia"] == 10
            assert fila["costo_venta"] == 500.0
            assert fila["nombre_marca"] == "Samsung"
            assert fila["nombre_clase"] == "Telefono"
            assert fila["foto_inventario"] is None
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_sin_producto_no_aparece(self):
        # Producto temporal sin existencias: no debe aparecer en el listado.
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Inventario Vacio",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            filas = Inventario().listar_inventario()

            assert all(fila["id_producto"] != id_producto for fila in filas)
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)


class TestListarInventarioPorModelo:

    def test_filtro_por_nombre(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Modelo Especial",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _crear_existencia(id_producto, existencia=5, costo=100.0)

            resultado = Inventario().listar_inventario_por_modelo(
                "Integra Modelo Especial"
            )

            assert [fila["id_producto"] for fila in resultado] == [id_producto]
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_sin_filtro_devuelve_todo(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Sin Filtro", clase=CLASE_TELEFONO, marca=MARCA_SEED
            )
            id_inventario = _crear_existencia(id_producto, existencia=5)

            con_filtro = Inventario().listar_inventario_por_modelo(None)
            assert any(
                fila["id_inventario"] == id_inventario for fila in con_filtro
            )
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_listar_inventario_general_igual_a_listar(self):
        assert (
            Inventario().listar_inventario_general()
            == Inventario().listar_inventario()
        )


class TestListarBajoStock:

    def test_incluye_producto_bajo_el_limite(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Bajo Stock",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _crear_existencia(id_producto, existencia=3, costo=100.0)

            resultado = Inventario().listar_productos_bajo_stock(limite=5)
            fila = next(
                (i for i in resultado if i["id_producto"] == id_producto), None
            )

            assert fila is not None
            assert fila["existencia"] == 3
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_excluye_producto_sobre_el_limite(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Stock Sano",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _crear_existencia(id_producto, existencia=50, costo=100.0)

            resultado = Inventario().listar_productos_bajo_stock(limite=5)
            assert all(fila["id_producto"] != id_producto for fila in resultado)
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)


class TestListarSinStock:

    def test_incluye_producto_con_existencia_cero(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Sin Stock Cero",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _crear_existencia(id_producto, existencia=0, costo=100.0)

            resultado = Inventario().listar_productos_sin_stock()
            assert any(fila["id_producto"] == id_producto for fila in resultado)
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_excluye_producto_con_stock(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Con Stock",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _crear_existencia(id_producto, existencia=8, costo=100.0)

            resultado = Inventario().listar_productos_sin_stock()
            assert all(fila["id_producto"] != id_producto for fila in resultado)
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)


class TestListarInventarioTaller:

    def test_solo_incluye_categoria_taller(self):
        id_producto_taller = None
        id_producto_normal = None
        try:
            id_producto_taller = crear_producto_temporal(
                nombre="Prod Integra Taller Inv",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _crear_existencia(
                id_producto_taller, existencia=4, costo=50.0, id_categoria=2
            )

            id_producto_normal = crear_producto_temporal(
                nombre="Prod Integra Venta Inv",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _crear_existencia(id_producto_normal, existencia=9, costo=50.0)

            resultado = Inventario().listar_inventario_taller()

            assert any(
                fila["ID_inventario"]
                and fila["Nombre_producto"] == "Prod Integra Taller Inv"
                for fila in resultado
            )
            assert all(
                fila["Nombre_producto"] != "Prod Integra Venta Inv"
                for fila in resultado
            )
        finally:
            if id_producto_taller:
                eliminar_producto_temporal(id_producto_taller)
            if id_producto_normal:
                eliminar_producto_temporal(id_producto_normal)


class TestAumentarStock:

    def test_datos_validos(self):
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Aumentar",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            id_inventario = _crear_existencia(id_producto, existencia=10)
            stocks_originales = _stock_por_id_producto(id_producto)

            resultado = Inventario(id_inventario=id_inventario).aumentar_stock(5)

            assert resultado is True
            assert _stock(id_inventario) == 15
            _restaurar_stock(stocks_originales)
            assert _stock(id_inventario) == 10
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_sin_id_inventario(self):
        with pytest.raises(ValueError) as exc:
            Inventario(id_inventario="").aumentar_stock(5)

        assert str(exc.value) == "ID del inventario es requerido"

    def test_cantidad_no_positiva(self):
        id_inventario = None
        id_producto = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Cantidad Cero",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            id_inventario = _crear_existencia(id_producto, existencia=10)

            with pytest.raises(ValueError) as exc:
                Inventario(id_inventario=id_inventario).aumentar_stock(0)

            assert str(exc.value) == "La cantidad debe ser mayor a 0"
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)

    def test_id_inexistente(self):
        # El UPDATE no afecta filas: devuelve False sin fallar.
        assert Inventario(id_inventario="INV999999").aumentar_stock(5) is False
