"""Pruebas de integración del módulo Proveedores contra MySQL real.

Escenario: se registra un proveedor, se verifica su existencia, 
y se elimina; además se verifica que un proveedor con relaciones activas
(órdenes de compra o productos suministrados)
no se pueda eliminar.

"""
from app.models.proveedores import Proveedores

# Datos temporales de la prueba (zona que no interfiere con el seed).
NOMBRE_PROVEEDOR = "Proveedor Temporal Integracion"
RIF_PROVEEDOR = "J-98765432-1"
TIPO_PROVEEDOR = "Mayorista"
CELULAR_PROVEEDOR = "04149876543"
CORREO_PROVEEDOR = "proveedor.integracion@mail.com"
DIRECCION_PROVEEDOR = "Barquisimeto"
LIMITE_CREDITO = 1000

# Datos sembrados directamente en la BD de prueba
# (bd/tests/ituaccesoriobd.sql, sección 2.1 registros CRUD):
#   - proveedor 101: tiene la orden de compra OC0000101 (Pendiente).
#   - proveedor 901: tiene productos en Suministra (producto 903).
ID_PROVEEDOR_CON_OC = 101
ID_PROVEEDOR_CON_PRODUCTOS = 901

# Producto del seed (901/902/903) usado para la relación Suministra temporal.
ID_MODELO_SEED = "903"


def limpiar_proveedor_temporal():
    """Elimina el proveedor temporal (de esta corrida o de una previa abortada)."""
    for proveedor in Proveedores().listar_proveedores(q=NOMBRE_PROVEEDOR):
        if proveedor.get("nombre") != NOMBRE_PROVEEDOR:
            continue
        id_proveedor = proveedor["id"]
        # Primero sus productos suministrados (la FK Suministra_ibfk_1
        # restringiría borrar el proveedor mientras existan).
        for producto in Proveedores(
            id_proveedor=id_proveedor
        ).listar_productos_por_proveedor():
            Proveedores(id_proveedor=id_proveedor).eliminar_producto_proveedor(
                id_modelo=producto["id_modelo"]
            )
        Proveedores(id_proveedor=id_proveedor).eliminar_proveedor()


def test_registrar_y_eliminar_proveedor():
    limpiar_proveedor_temporal()
    try:
        # 1. Registrar el proveedor (el SP sp_registrar_proveedor genera el ID).
        id_proveedor = Proveedores(
            rif=RIF_PROVEEDOR,
            nombre=NOMBRE_PROVEEDOR,
            tipo=TIPO_PROVEEDOR,
            celular=CELULAR_PROVEEDOR,
            correo=CORREO_PROVEEDOR,
            direccion=DIRECCION_PROVEEDOR,
            limite_credito=LIMITE_CREDITO,
        ).crear_proveedor()
        assert id_proveedor

        assert Proveedores(id_proveedor=id_proveedor).verificar_existencia() is True

        consulta = Proveedores(id_proveedor=id_proveedor).obtener_proveedor()
        assert consulta is not None
        assert consulta["nombre"] == NOMBRE_PROVEEDOR
        assert consulta["rif"] == RIF_PROVEEDOR

        assert any(
            proveedor["id"] == id_proveedor
            for proveedor in Proveedores().listar_proveedores(q=NOMBRE_PROVEEDOR)
        )

        # 2. Eliminar el proveedor (sin relaciones, el DELETE directo es válido).
        assert Proveedores(id_proveedor=id_proveedor).eliminar_proveedor() is True
        assert Proveedores(id_proveedor=id_proveedor).verificar_existencia() is False
    finally:
        limpiar_proveedor_temporal()


def test_no_se_puede_eliminar_proveedor_con_relaciones():
    # Proveedor 101: orden de compra Pendiente (bloquea el borrado).
    modelo_oc = Proveedores(id_proveedor=ID_PROVEEDOR_CON_OC)
    assert modelo_oc.verificar_existencia() is True
    tiene_relaciones, mensaje = modelo_oc.tiene_relaciones_activas()
    assert tiene_relaciones is True
    assert "órdenes de compra" in mensaje

    # Proveedor 901: productos suministrados en Suministra (bloquea el borrado).
    modelo_suministro = Proveedores(id_proveedor=ID_PROVEEDOR_CON_PRODUCTOS)
    assert modelo_suministro.verificar_existencia() is True
    tiene_relaciones, mensaje = modelo_suministro.tiene_relaciones_activas()
    assert tiene_relaciones is True
    assert "productos asociados" in mensaje

    # Los registros del seed quedan intactos.
    assert modelo_oc.verificar_existencia() is True
    assert modelo_suministro.verificar_existencia() is True


def test_registrar_proveedor_con_productos_suministrados():
    limpiar_proveedor_temporal()
    try:
        # Registrar el proveedor con un producto suministrado (Suministra).
        id_proveedor = Proveedores(
            rif=RIF_PROVEEDOR,
            nombre=NOMBRE_PROVEEDOR,
            tipo=TIPO_PROVEEDOR,
            celular=CELULAR_PROVEEDOR,
            correo=CORREO_PROVEEDOR,
            direccion=DIRECCION_PROVEEDOR,
            limite_credito=LIMITE_CREDITO,
        ).crear_proveedor_con_productos(
            [{"id_modelo": ID_MODELO_SEED, "costo": 50}]
        )
        assert id_proveedor

        # La relación Suministra se refleja en los productos del proveedor.
        productos = Proveedores(id_proveedor=id_proveedor).listar_productos_por_proveedor()
        assert len(productos) == 1
        assert productos[0]["id_modelo"] == ID_MODELO_SEED
        assert productos[0]["costo"] == 50
    finally:
        limpiar_proveedor_temporal()
