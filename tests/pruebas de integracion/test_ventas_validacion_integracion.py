"""Pruebas de integración del flujo de ventas y validación de pagos.

El flujo relaciona Clientes, Productos, Inventario, Carrito, Ventas y
Validación de Pagos sobre las BD reales de prueba; no requiere el servidor Flask.
"""
import pytest

from app.models.carrito import CarritoModel
from app.models.clientes import Persona_natural
from app.models.database import conectar
from app.models.productos import Producto
from app.models.validacion_pagos import ValidacionPagosModel
from app.models.venta import VentaModel


CEDULA_CLIENTE = "98765421"
NOMBRE_CLIENTE = "Integracion"
APELLIDO_CLIENTE = "Ventas"
NOMBRE_PRODUCTO = "Producto Temporal Ventas"
ID_INVENTARIO = "INV999998"
ID_EMPLEADO_VALIDACION = "12345678"
STOCK_INICIAL = 5
CANTIDAD_VENDIDA = 2
PRECIO_UNITARIO = 125.50


def _ejecutar_sql(sql, parametros=(), obtener=False):
    """Ejecuta SQL en la BD principal, confirma escrituras y cierra recursos."""
    db = conectar().conexion1()
    if not db:
        raise RuntimeError("No se pudo conectar a la BD principal de pruebas.")
    cursor = db.cursor()
    try:
        cursor.execute(sql, parametros)
        resultado = cursor.fetchall() if obtener else None
        if not obtener:
            db.commit()
        return resultado
    finally:
        cursor.close()
        db.close()


def limpiar_datos_temporales():
    """Elimina los registros del flujo de prueba respetando las claves foráneas."""
    facturas = _ejecutar_sql(
        "SELECT ID_factura FROM Venta WHERE ID_cliente = %s",
        (CEDULA_CLIENTE,),
        obtener=True,
    )
    for (factura_id,) in facturas:
        _ejecutar_sql("DELETE FROM Metodo_pago WHERE ID_factura = %s", (factura_id,))
        _ejecutar_sql("DELETE FROM Detalle_venta WHERE ID_factura = %s", (factura_id,))
        _ejecutar_sql("DELETE FROM Venta WHERE ID_factura = %s", (factura_id,))

    _ejecutar_sql("DELETE FROM Lista_compra WHERE ID_cliente = %s", (CEDULA_CLIENTE,))
    _ejecutar_sql(
        "DELETE FROM Existencias_productos WHERE ID_inventario = %s",
        (ID_INVENTARIO,),
    )
    for producto in Producto().listar_productos(q=NOMBRE_PRODUCTO):
        if producto.get("nombre") == NOMBRE_PRODUCTO:
            Producto(id_producto=producto["id"]).eliminar_producto()
    _ejecutar_sql(
        "DELETE FROM Persona_natural WHERE ID_cliente = %s", (CEDULA_CLIENTE,)
    )
    _ejecutar_sql("DELETE FROM Cliente WHERE ID_cliente = %s", (CEDULA_CLIENTE,))


def _crear_cliente_y_producto():
    mensaje = Persona_natural(
        Cedula_cliente=CEDULA_CLIENTE,
        Nombre_cliente=NOMBRE_CLIENTE,
        Apellido_cliente=APELLIDO_CLIENTE,
        Telefono_cliente="04141234567",
        Correo_cliente="integracion.ventas@gmail.com",
        Direccion_cliente="Barquisimeto",
    ).registrar_persona_natural()
    assert "se registró exitosamente" in mensaje, mensaje

    id_producto = Producto(
        id_clase="1",
        id_marca="1",
        nombre=NOMBRE_PRODUCTO,
        descripcion="Producto para integración de ventas",
    ).registrar_producto()
    assert id_producto

    _ejecutar_sql(
        """
        INSERT INTO Existencias_productos
            (ID_inventario, ID_producto, Existencia, Costo_venta)
        VALUES (%s, %s, %s, %s)
        """,
        (ID_INVENTARIO, id_producto, STOCK_INICIAL, PRECIO_UNITARIO),
    )


@pytest.mark.parametrize(
    ("decision", "estado_esperado"),
    [("aprobar", "aprobado"), ("rechazar", "rechazado")],
)
def test_flujo_carrito_venta_y_validacion_de_pago(
    decision, estado_esperado, monkeypatch
):
    limpiar_datos_temporales()
    monkeypatch.setattr(
        CarritoModel,
        "_obtener_tasas",
        lambda self: {"oficial": 1.0, "paralelo": 1.0},
    )

    try:
        # Clientes y Productos registran los datos que alimentan Inventario.
        _crear_cliente_y_producto()
        assert (
            CarritoModel(
                cliente_id=CEDULA_CLIENTE,
                inventario_id=ID_INVENTARIO,
                cantidad=CANTIDAD_VENDIDA,
            ).agregar_al_carrito()["success"]
            is True
        )

        carrito = CarritoModel(cliente_id=CEDULA_CLIENTE).obtener_carrito()
        assert carrito["total"] == PRECIO_UNITARIO * CANTIDAD_VENDIDA
        assert carrito["items"][0]["producto_id"] == ID_INVENTARIO

        # Ventas consume los artículos del carrito y descuenta existencias.
        metodo_pago = "zelle"
        estado_pago = VentaModel.estado_inicial_para(metodo_pago)
        factura_id = VentaModel(
            cliente_id=CEDULA_CLIENTE,
            items=carrito["items"],
            metodo_pago=metodo_pago,
            estado_pago=estado_pago,
        ).crear_venta_desde_carrito()
        VentaModel(
            factura_id=factura_id,
            metodo_pago=metodo_pago,
            estado_pago=estado_pago,
            datos_pago={
                "referencia": "REF INTEGRACION VENTAS",
                "monto": str(PRECIO_UNITARIO * CANTIDAD_VENDIDA),
            },
        ).guardar_registro_pago()
        CarritoModel(cliente_id=CEDULA_CLIENTE).vaciar_carrito()

        assert not CarritoModel(cliente_id=CEDULA_CLIENTE).obtener_carrito()["items"]
        stock = _ejecutar_sql(
            "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
            (ID_INVENTARIO,),
            obtener=True,
        )
        assert stock[0][0] == STOCK_INICIAL - CANTIDAD_VENDIDA

        validacion = ValidacionPagosModel(
            factura_id=factura_id,
            empleado_id=ID_EMPLEADO_VALIDACION,
        )
        pago_pendiente = next(
            (
                pago
                for pago in validacion.obtener_pagos_pendientes()
                if pago["factura_id"] == factura_id
            ),
            None,
        )
        assert pago_pendiente is not None
        assert pago_pendiente["cliente_id"] == CEDULA_CLIENTE
        assert pago_pendiente["estado"] == "pendiente"

        detalle = validacion.obtener_detalle_venta()
        assert len(detalle) == 1
        assert detalle[0]["ID_inventario"] == ID_INVENTARIO
        assert detalle[0]["Cantidad_articulo"] == CANTIDAD_VENDIDA
        assert detalle[0]["Nombre_producto"] == NOMBRE_PRODUCTO

        if decision == "aprobar":
            resultado = validacion.aprobar_pago()
            pagos_finales = validacion.obtener_pagos_aprobados()
        else:
            resultado = validacion.rechazar_pago(
                motivo="Comprobante de prueba no válido"
            )
            pagos_finales = validacion.obtener_pagos_rechazados()

        assert resultado["success"] is True, resultado
        pago_final = next(
            pago for pago in pagos_finales if pago["factura_id"] == factura_id
        )
        assert pago_final["estado"] == estado_esperado
        assert not any(
            pago["factura_id"] == factura_id
            for pago in validacion.obtener_pagos_pendientes()
        )
    finally:
        limpiar_datos_temporales()
