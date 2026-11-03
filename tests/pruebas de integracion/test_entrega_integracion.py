"""Pruebas de integración de EntregaModel contra MySQL real."""
import random

import pytest

from app.models.entrega import EntregaModel
from seed_helpers import (
    crear_cliente_temporal,
    crear_delivery_temporal,
    crear_existencia_temporal,
    crear_producto_temporal,
    crear_venta_temporal,
    eliminar_cliente_temporal,
    eliminar_delivery_temporal,
    eliminar_producto_temporal,
    eliminar_venta_temporal,
    limpiar_bitacora_por_descripcion,
)


CLASE_TELEFONO = "1"
MARCA_IPHONE = "1"
EMPLEADO_ADMIN = "12345678"
USUARIO_ADMIN = "USR-001"


def _cedula_aleatoria() -> str:
    return str(random.randint(10**7, 10**8 - 1))


@pytest.fixture
def venta_y_delivery():
    """Cliente + producto + venta + delivery. Limpia al final."""
    cedula_cliente = _cedula_aleatoria()
    cedula_delivery = _cedula_aleatoria()
    id_producto = None
    factura_id = None
    crear_cliente_temporal(cedula_cliente, nombre="Cliente", apellido="Entrega")
    crear_delivery_temporal(cedula_delivery, nombre="Delivery", apellido="Test")
    try:
        id_producto = crear_producto_temporal(
            nombre="iPhone Entrega", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
        )
        id_inventario = crear_existencia_temporal(id_producto, existencia=5, costo=500.0)
        factura_id = crear_venta_temporal(
            cedula_cliente=cedula_cliente,
            id_inventario=id_inventario,
            empleado_id=EMPLEADO_ADMIN,
            monto=500.0,
            metodo="efectivo_usd",
            estado_pago="aprobado",
        )
        yield {
            "cliente_id": cedula_cliente,
            "delivery_id": cedula_delivery,
            "id_producto": id_producto,
            "factura_id": factura_id,
        }
    finally:
        # Borrar entregas asociadas a la factura (por FK)
        _borrar_entregas_de_factura(factura_id) if factura_id else None
        if factura_id:
            eliminar_venta_temporal(factura_id)
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_delivery_temporal(cedula_delivery)
        eliminar_cliente_temporal(cedula_cliente)
        limpiar_bitacora_por_descripcion("entrega")


def _borrar_entregas_de_factura(factura_id: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Entrega WHERE ID_factura = %s", (factura_id,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


# ==================== LISTAR ====================

class TestListarEntregas:

    def test_devuelve_lista(self):
        assert isinstance(EntregaModel().listar_entregas(), list)

    def test_incluye_entrega_creada(self, venta_y_delivery):
        info = venta_y_delivery
        try:
            entrega_id = EntregaModel(
                factura_id=info["factura_id"],
                cedula_delivery=info["delivery_id"],
                direccion="Av Principal",
                estado=0,
            ).registrar_entrega()

            entregas = EntregaModel().listar_entregas()
            fila = next((e for e in entregas if e["id"] == entrega_id), None)

            assert fila is not None
            assert fila["factura_id"] == info["factura_id"]
            assert fila["cedula_delivery"] == info["delivery_id"]
            assert fila["estado"] == 0
            assert fila["estado_texto"] == "Pendiente"
            assert fila["estado_clase"] == "estado-pendiente"
        finally:
            _borrar_entregas_de_factura(info["factura_id"])


# ==================== OBTENER ====================

class TestObtenerEntregaPorId:

    def test_entrega_existente(self, venta_y_delivery):
        info = venta_y_delivery
        try:
            entrega_id = EntregaModel(
                factura_id=info["factura_id"],
                cedula_delivery=info["delivery_id"],
                direccion="Av Principal",
                estado=1,
            ).registrar_entrega()

            resultado = EntregaModel().obtener_entrega_por_id(entrega_id)

            assert resultado is not None
            assert resultado["id"] == entrega_id
            assert resultado["estado"] == 1
            assert resultado["estado_texto"] == "En camino"
            assert resultado["estado_clase"] == "estado-camino"
        finally:
            _borrar_entregas_de_factura(info["factura_id"])

    def test_entrega_inexistente(self):
        assert EntregaModel().obtener_entrega_por_id("ENT9999999") is None

    def test_sin_id(self):
        assert EntregaModel().obtener_entrega_por_id() is None

    def test_id_invalido(self):
        assert EntregaModel().obtener_entrega_por_id("con espacios") is None


# ==================== REGISTRAR ====================

class TestRegistrarEntrega:

    @pytest.mark.parametrize(
        "estado, texto, clase",
        [
            pytest.param(0, "Pendiente", "estado-pendiente", id="pendiente"),
            pytest.param(1, "En camino", "estado-camino", id="en-camino"),
            pytest.param(2, "Entregado", "estado-entregado", id="entregado"),
            pytest.param(3, "Cancelado", "estado-cancelado", id="cancelado"),
        ],
    )
    def test_estados_validos(self, venta_y_delivery, estado, texto, clase):
        info = venta_y_delivery
        try:
            entrega_id = EntregaModel(
                factura_id=info["factura_id"],
                cedula_delivery=info["delivery_id"],
                direccion="Av Principal",
                estado=estado,
            ).registrar_entrega()

            consultado = EntregaModel().obtener_entrega_por_id(entrega_id)
            assert consultado["estado_texto"] == texto
            assert consultado["estado_clase"] == clase
        finally:
            _borrar_entregas_de_factura(info["factura_id"])

    def test_factura_inexistente(self, venta_y_delivery):
        info = venta_y_delivery
        with pytest.raises(ValueError, match="no existe"):
            EntregaModel(
                factura_id="FAC-202601-XXXXXX",
                cedula_delivery=info["delivery_id"],
                direccion="Av Principal",
                estado=0,
            ).registrar_entrega()

    def test_delivery_inexistente(self, venta_y_delivery):
        info = venta_y_delivery
        with pytest.raises(ValueError, match="no existe"):
            EntregaModel(
                factura_id=info["factura_id"],
                cedula_delivery="99999999",
                direccion="Av Principal",
                estado=0,
            ).registrar_entrega()

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"factura_id": ""},
                "La factura es obligatoria.",
                id="factura-vacia",
            ),
            pytest.param(
                {"factura_id": "con espacios"},
                "El campo Factura solo puede contener letras, números y guiones.",
                id="factura-invalida",
            ),
            pytest.param(
                {"cedula_delivery": ""},
                "El delivery es obligatorio.",
                id="delivery-vacio",
            ),
            pytest.param(
                {"cedula_delivery": "12345"},
                "El campo Cédula del delivery debe tener al menos 6 dígitos.",
                id="delivery-demasiado-corto",
            ),
            pytest.param(
                {"direccion": ""},
                "La dirección es obligatoria.",
                id="direccion-vacia",
            ),
            pytest.param(
                {"direccion": "D" * 61},
                "El campo Dirección no puede tener más de 60 caracteres.",
                id="direccion-demasiado-larga",
            ),
            pytest.param(
                {"estado": None},
                "El estado es obligatorio.",
                id="estado-none",
            ),
            pytest.param(
                {"estado": 5},
                "El campo Estado debe ser menor o igual a 3.",
                id="estado-fuera-de-rango",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        datos = {
            "factura_id": "FAC-202601-ABC123",
            "cedula_delivery": "12345678",
            "direccion": "Av Principal",
            "estado": 0,
        }
        datos.update(cambios)
        with pytest.raises(ValueError) as exc:
            EntregaModel(**datos).registrar_entrega()
        assert str(exc.value) == esperado


# ==================== ACTUALIZAR ====================

class TestActualizarEntrega:

    def test_actualiza_direccion_y_estado(self, venta_y_delivery):
        info = venta_y_delivery
        try:
            entrega_id = EntregaModel(
                factura_id=info["factura_id"],
                cedula_delivery=info["delivery_id"],
                direccion="Av Principal",
                estado=0,
            ).registrar_entrega()

            resultado = EntregaModel(
                entrega_id=entrega_id,
                direccion="Calle Nueva",
                estado=2,
            ).actualizar_entrega()

            assert resultado == "Entrega actualizada exitosamente."

            consultado = EntregaModel().obtener_entrega_por_id(entrega_id)
            assert consultado["direccion"] == "Calle Nueva"
            assert consultado["estado"] == 2
        finally:
            _borrar_entregas_de_factura(info["factura_id"])

    def test_entrega_inexistente(self):
        resultado = EntregaModel(
            entrega_id="ENT9999999",
            direccion="Calle Nueva",
            estado=0,
        ).actualizar_entrega()
        assert resultado == "Entrega no encontrada"

    def test_sin_id(self):
        resultado = EntregaModel(
            direccion="Calle Nueva", estado=0
        ).actualizar_entrega()
        assert resultado == "ID de entrega no especificado."

    def test_direccion_vacia(self):
        resultado = EntregaModel(
            entrega_id="ENT0000001", direccion="", estado=0
        ).actualizar_entrega()
        assert resultado == "La dirección es obligatoria."


# ==================== ELIMINAR ====================

class TestEliminarEntrega:

    def test_elimina_entrega(self, venta_y_delivery):
        info = venta_y_delivery
        entrega_id = EntregaModel(
            factura_id=info["factura_id"],
            cedula_delivery=info["delivery_id"],
            direccion="Av Principal",
            estado=0,
        ).registrar_entrega()

        resultado = EntregaModel(entrega_id=entrega_id).eliminar_entrega()

        assert resultado == "Entrega eliminada exitosamente."
        assert EntregaModel().obtener_entrega_por_id(entrega_id) is None

    def test_entrega_inexistente(self):
        resultado = EntregaModel(entrega_id="ENT9999999").eliminar_entrega()
        assert resultado == "Entrega no encontrada"

    @pytest.mark.parametrize(
        "entrega_id, esperado",
        [
            pytest.param("", "ID de entrega no especificado.", id="vacio"),
            pytest.param(
                "con espacios",
                "El campo ID de entrega solo puede contener letras, números, acentos y espacios.",
                id="invalido",
            ),
        ],
    )
    def test_id_invalido(self, entrega_id, esperado):
        assert EntregaModel(entrega_id=entrega_id).eliminar_entrega() == esperado


# ==================== FACTURAS PENDIENTES ====================

class TestObtenerFacturasPendientes:

    def test_devuelve_lista(self):
        assert isinstance(EntregaModel().obtener_facturas_pendientes(), list)

    def test_incluye_factura_sin_entrega(self, venta_y_delivery):
        info = venta_y_delivery
        pendientes = EntregaModel().obtener_facturas_pendientes()

        factura = next(
            (p for p in pendientes if p["factura_id"] == info["factura_id"]), None
        )
        assert factura is not None
        assert factura["cliente_id"] == info["cliente_id"]

    def test_no_incluye_factura_con_entrega(self, venta_y_delivery):
        info = venta_y_delivery
        try:
            EntregaModel(
                factura_id=info["factura_id"],
                cedula_delivery=info["delivery_id"],
                direccion="Av Principal",
                estado=0,
            ).registrar_entrega()

            pendientes = EntregaModel().obtener_facturas_pendientes()
            assert not any(
                p["factura_id"] == info["factura_id"] for p in pendientes
            )
        finally:
            _borrar_entregas_de_factura(info["factura_id"])