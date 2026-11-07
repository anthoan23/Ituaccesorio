"""Pruebas de integración de CarritoModel contra MySQL real."""
import random

import pytest

from app.models.carrito import CarritoModel
from seed_helpers import (
    crear_cliente_temporal,
    crear_existencia_temporal,
    crear_producto_temporal,
    eliminar_cliente_temporal,
    eliminar_producto_temporal,
)


CLASE_TELEFONO = "1"
MARCA_IPHONE = "1"
ESTADO_CARRITO = "carrito"


def _cedula_cliente_aleatoria() -> str:
    return str(random.randint(10**7, 10**8 - 1))


@pytest.fixture
def cliente_y_producto():
    """Crea un cliente y un producto con stock temporal. Limpia al final."""
    cedula = _cedula_cliente_aleatoria()
    id_producto = None
    crear_cliente_temporal(cedula, nombre="Cliente", apellido="Carrito")
    try:
        id_producto = crear_producto_temporal(
            nombre="iPhone Carrito", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
        )
        id_inventario = crear_existencia_temporal(id_producto, existencia=10, costo=500.0)
        yield {
            "cliente_id": cedula,
            "id_producto": id_producto,
            "id_inventario": id_inventario,
        }
    finally:
        # Limpiar Lista_compra del cliente (por si quedó algo)
        _limpiar_lista_compra(cedula)
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_cliente_temporal(cedula)


def _limpiar_lista_compra(cliente_id: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Lista_compra WHERE ID_cliente = %s", (cliente_id,)
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _obtener_existencia(id_inventario: str) -> int:
    from app.models.database import conectar
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


# ==================== OBTENER CARRITO ====================

class TestObtenerCarrito:

    def test_sin_cliente_devuelve_estructura_vacia(self):
        resultado = CarritoModel().obtener_carrito()
        assert resultado == {
            "items": [],
            "total": 0,
            "tasas": {"oficial": 0, "paralelo": 0},
        }

    def test_carrito_vacio_para_cliente_nuevo(self, cliente_y_producto):
        resultado = CarritoModel(
            cliente_id=cliente_y_producto["cliente_id"]
        ).obtener_carrito()

        assert resultado["items"] == []
        assert resultado["total"] == 0
        assert "oficial" in resultado["tasas"]
        assert "paralelo" in resultado["tasas"]

    def test_carrito_con_item(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=2,
            ).agregar_al_carrito()

            resultado = CarritoModel(cliente_id=info["cliente_id"]).obtener_carrito()

            assert len(resultado["items"]) == 1
            item = resultado["items"][0]
            assert item["ID_inventario"] == info["id_inventario"]
            assert item["Cantidad_producto"] == 2
            assert item["Costo_venta"] == 500.0
            assert item["producto_id"] == info["id_inventario"]
            assert item["cantidad"] == 2
            assert item["precio_usd"] == 500.0
            assert resultado["total"] == 1000.0
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_carrito_con_dos_items(self, cliente_y_producto):
        info = cliente_y_producto
        id_producto_2 = None
        try:
            id_producto_2 = crear_producto_temporal(
                nombre="iPhone Carrito 2", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            id_inventario_2 = crear_existencia_temporal(
                id_producto_2, existencia=5, costo=200.0
            )
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=1,
            ).agregar_al_carrito()
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=id_inventario_2,
                cantidad=2,
            ).agregar_al_carrito()

            resultado = CarritoModel(cliente_id=info["cliente_id"]).obtener_carrito()

            assert len(resultado["items"]) == 2
            assert resultado["total"] == 900.0  # 500 + 200*2
        finally:
            _limpiar_lista_compra(info["cliente_id"])
            if id_producto_2:
                eliminar_producto_temporal(id_producto_2)


# ==================== AGREGAR AL CARRITO ====================

class TestAgregarAlCarrito:

    def test_agrega_item_nuevo(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            resultado = CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=1,
            ).agregar_al_carrito()

            assert resultado == {"success": True, "message": "Producto agregado al carrito."}
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_acumula_cantidad_si_ya_existe(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=1,
            ).agregar_al_carrito()
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=2,
            ).agregar_al_carrito()

            carrito = CarritoModel(cliente_id=info["cliente_id"]).obtener_carrito()
            assert carrito["items"][0]["Cantidad_producto"] == 3
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_cantidad_supera_stock(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            resultado = CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=999,
            ).agregar_al_carrito()

            assert resultado == {
                "success": False,
                "error": "La cantidad supera el stock disponible.",
            }
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_acumulado_supera_stock(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=8,
            ).agregar_al_carrito()

            resultado = CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=5,
            ).agregar_al_carrito()

            assert resultado == {
                "success": False,
                "error": "La cantidad supera el stock disponible.",
            }
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_producto_inexistente(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            resultado = CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id="INV999999",
                cantidad=1,
            ).agregar_al_carrito()

            assert resultado == {
                "success": False,
                "error": "Producto no encontrado en inventario.",
            }
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_producto_sin_stock(self, cliente_y_producto):
        info = cliente_y_producto
        id_producto_sin_stock = None
        try:
            id_producto_sin_stock = crear_producto_temporal(
                nombre="Sin Stock Carrito", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
            )
            id_inv = crear_existencia_temporal(id_producto_sin_stock, existencia=0, costo=100.0)

            resultado = CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=id_inv,
                cantidad=1,
            ).agregar_al_carrito()

            assert resultado == {"success": False, "error": "Producto sin stock."}
        finally:
            _limpiar_lista_compra(info["cliente_id"])
            if id_producto_sin_stock:
                eliminar_producto_temporal(id_producto_sin_stock)

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"cliente_id": ""},
                "El cliente es obligatorio.",
                id="cliente-vacio",
            ),
            pytest.param(
                {"cliente_id": "12345"},
                "El campo Cliente debe tener al menos 6 dígitos.",
                id="cliente-demasiado-corto",
            ),
            pytest.param(
                {"cliente_id": "12345a"},
                "El campo Cliente solo puede contener números.",
                id="cliente-no-numerico",
            ),
            pytest.param(
                {"inventario_id": ""},
                "El producto es obligatorio.",
                id="inventario-vacio",
            ),
            pytest.param(
                {"inventario_id": "I" * 11},
                "El campo Producto no puede tener más de 10 caracteres.",
                id="inventario-demasiado-largo",
            ),
            pytest.param(
                {"cantidad": 0},
                "La cantidad debe ser mayor que 0.",
                id="cantidad-cero",
            ),
            pytest.param(
                {"cantidad": -1},
                "El campo Cantidad solo puede contener números.",
                id="cantidad-negativa",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        datos = {
            "cliente_id": "12345678",
            "inventario_id": "INV0000001",
            "cantidad": 1,
        }
        datos.update(cambios)
        resultado = CarritoModel(**datos).agregar_al_carrito()
        assert resultado == {"success": False, "error": esperado}


# ==================== ACTUALIZAR CANTIDAD ====================

class TestActualizarCantidad:

    def test_actualiza_cantidad_existente(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=1,
            ).agregar_al_carrito()

            resultado = CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=3,
            ).actualizar_cantidad()

            assert resultado == {"success": True}
            carrito = CarritoModel(cliente_id=info["cliente_id"]).obtener_carrito()
            assert carrito["items"][0]["Cantidad_producto"] == 3
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_cantidad_cero_elimina_item(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=1,
            ).agregar_al_carrito()

            resultado = CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=0,
            ).actualizar_cantidad()

            assert resultado == {"success": True, "message": "Producto eliminado del carrito."}
            carrito = CarritoModel(cliente_id=info["cliente_id"]).obtener_carrito()
            assert carrito["items"] == []
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_cantidad_supera_stock(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=1,
            ).agregar_al_carrito()

            resultado = CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=999,
            ).actualizar_cantidad()

            assert resultado == {
                "success": False,
                "error": "La cantidad supera el stock disponible.",
            }
        finally:
            _limpiar_lista_compra(info["cliente_id"])


# ==================== VACIAR CARRITO ====================

class TestVaciarCarrito:

    def test_vacia_todos_los_items(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=2,
            ).agregar_al_carrito()

            CarritoModel(cliente_id=info["cliente_id"]).vaciar_carrito()

            carrito = CarritoModel(cliente_id=info["cliente_id"]).obtener_carrito()
            assert carrito["items"] == []
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_vaciar_sin_cliente_no_falla(self):
        CarritoModel().vaciar_carrito()  # no debe lanzar


# ==================== ELIMINAR ITEM ====================

class TestEliminarItem:

    def test_elimina_item_especifico(self, cliente_y_producto):
        info = cliente_y_producto
        try:
            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
                cantidad=1,
            ).agregar_al_carrito()

            CarritoModel(
                cliente_id=info["cliente_id"],
                inventario_id=info["id_inventario"],
            ).eliminar_item()

            carrito = CarritoModel(cliente_id=info["cliente_id"]).obtener_carrito()
            assert carrito["items"] == []
        finally:
            _limpiar_lista_compra(info["cliente_id"])

    def test_eliminar_sin_ids_no_falla(self):
        CarritoModel().eliminar_item()  # no debe lanzar