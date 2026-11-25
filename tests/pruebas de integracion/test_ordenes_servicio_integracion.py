"""Pruebas de integración del flujo completo de una Orden de Servicio.


El objetivo es verificar que una orden solo puede registrarse cuando existen
las entidades que la soportan (cliente + equipo) y que la revisión inicial
queda persistida en las 3 tablas del módulo de test.
"""
from app.models.clientes import Cliente
from app.models.productos import Producto
from app.models.equipo import Equipo
from app.models.ordenes_servicio import OrdenServicio

# --- Datos temporales generados por este test ---
CEDULA_CLIENTE_TEMP = "98765420"
ID_PRODUCTO_TEMP = "99001"
ID_EQUIPO_TEMP = "123456789123456"
ID_ORDEN_TEMP = "OSR0000001"

# --- Datos ya sembrados en bd/tests/ituaccesoriobd.sql ---
ID_CLASE_PRODUCTO = "1"       # Clase_producto -> 'Telefono'
ID_MARCA_PRODUCTO = "1"       # Marca_producto -> 'Apple'
ID_EMPLEADO_TECNICO = 12345678  # Empleado -> 'Super Admin'

# --- Datos de negocio del test ---
DESCRIPCION_ORDEN = "Pantalla no enciende"
NOTA_ORDEN = "Equipo recibido en recepción"
FECHA_ENTRADA = "2026-11-24 10:00:00"
ESTADO_INICIAL = "Pendiente"

TESTS_REVISION = [
    {"nombre": "Botón Power", "resultado": "Funciona"},
    {"nombre": "Mica", "resultado": "No funciona"},
    {"nombre": "LCD", "resultado": "Funciona"},
    {"nombre": "Táctil", "resultado": "Funciona"},
]


def limpiar_datos_temporales():
    """Elimina los registros temporales de esta corrida (o de una abortada)."""
    OrdenServicio(id_orden_servicio=ID_ORDEN_TEMP).eliminar_revision_y_tests()

    OrdenServicio(id_orden_servicio=ID_ORDEN_TEMP).eliminar_orden()

    Equipo(id_equipo=ID_EQUIPO_TEMP).eliminar_equipo()

    Producto(id_producto=ID_PRODUCTO_TEMP).eliminar_producto()

    Cliente(cedula=CEDULA_CLIENTE_TEMP).eliminar_cliente()



def test_registrar_orden_servicio_con_cliente_equipo_y_revision():
    limpiar_datos_temporales()
    try:
        
        # 1. Módulo de clientes
        
        assert (
            Cliente(
                cedula=CEDULA_CLIENTE_TEMP,
                tipo="natural",
                nombre="Integracion",
                apellido="Pruebas",
                celular="04141234567",
                correo="integracion.orden@gmail.com",
                direccion="Barquisimeto",
            ).agregar_cliente()
            == "Cliente agregado exitosamente."
        )
        assert Cliente(cedula=CEDULA_CLIENTE_TEMP).verificar_cliente() is True


        # 2. Catálogo: Producto + Equipo 
     
        assert (
            Producto(
                id_producto=ID_PRODUCTO_TEMP,
                id_clase=ID_CLASE_PRODUCTO,
                id_marca=ID_MARCA_PRODUCTO,
                nombre_producto="Equipo Temporal Integracion",
                descripcion="Producto temporal de integración",
            ).agregar_producto()
            == "Producto agregado exitosamente."
        )
        assert Producto(id_producto=ID_PRODUCTO_TEMP).verificar_producto() is True

        assert (
            Equipo(
                id_equipo=ID_EQUIPO_TEMP,
                id_producto=ID_PRODUCTO_TEMP,
                color="Negro",
                capacidad="128GB",
                clave=123456,
                patron="1-8-5-2-9",
            ).agregar_equipo()
            == "Equipo agregado exitosamente."
        )
        assert Equipo(id_equipo=ID_EQUIPO_TEMP).verificar_equipo() is True

        
        # 3. Orden de servicio (relaciona Cliente + Equipo)
        
        assert (
            OrdenServicio(
                id_orden_servicio=ID_ORDEN_TEMP,
                id_equipo=ID_EQUIPO_TEMP,
                id_cliente=CEDULA_CLIENTE_TEMP,
                estado=ESTADO_INICIAL,
                descripcion_reparacion=DESCRIPCION_ORDEN,
                costo_reparacion=0.00,
                nota=NOTA_ORDEN,
                fecha_entrada=FECHA_ENTRADA,
            ).agregar_orden()
            == "Orden de servicio agregada exitosamente."
        )

        consulta_orden = OrdenServicio(
            id_orden_servicio=ID_ORDEN_TEMP
        ).consultar_orden()
        assert consulta_orden["id_orden_servicio"] == ID_ORDEN_TEMP
        assert consulta_orden["id_equipo"] == ID_EQUIPO_TEMP
        assert consulta_orden["id_cliente"] == CEDULA_CLIENTE_TEMP
        assert consulta_orden["estado"] == ESTADO_INICIAL
        assert consulta_orden["descripcion_reparacion"] == DESCRIPCION_ORDEN

        assert {
            "id_orden_servicio": ID_ORDEN_TEMP,
            "id_cliente": CEDULA_CLIENTE_TEMP,
            "id_equipo": ID_EQUIPO_TEMP,
            "estado": ESTADO_INICIAL,
        } in OrdenServicio().listar_ordenes()

        
        # 4. Revisión inicial (módulo test): Interaccion + Test + intermedia
        
        resultado = OrdenServicio(
            id_orden_servicio=ID_ORDEN_TEMP
        ).registrar_revision_test(
            id_empleado=ID_EMPLEADO_TECNICO,
            numero_test=1,
            tests=TESTS_REVISION,
        )
        assert resultado["ID_orden_servicio"] == ID_ORDEN_TEMP
        assert resultado["Total_tests"] == len(TESTS_REVISION)
        id_interaccion = resultado["ID_interaccion"]
        assert id_interaccion is not None

        # 4.a Interaccion creada con la acción correcta.
        interaccion = OrdenServicio(
            id_orden_servicio=ID_ORDEN_TEMP
        ).consultar_ultima_interaccion()
        assert interaccion["id_interaccion"] == id_interaccion
        assert interaccion["accion"] == "Revisión"
        assert interaccion["id_empleado"] == ID_EMPLEADO_TECNICO

        # 4.b Tests guardados y enlazados a la interacción.
        tests_guardados = OrdenServicio(
            id_orden_servicio=ID_ORDEN_TEMP
        ).listar_tests_de_orden()
        assert len(tests_guardados) == len(TESTS_REVISION)
        assert {t["nombre_test"] for t in tests_guardados} == {
            t["nombre"] for t in TESTS_REVISION
        }
        # Cada test debe estar enlazado a la interacción recién creada.
        assert all(
            t["id_interaccion"] == id_interaccion for t in tests_guardados
        )

        # 4.c La orden sigue existiendo después de la revisión.
        assert OrdenServicio(
            id_orden_servicio=ID_ORDEN_TEMP
        ).verificar_orden() is True
    finally:
        limpiar_datos_temporales()