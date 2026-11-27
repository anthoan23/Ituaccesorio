"""Pruebas de integración del flujo completo de una Orden de Servicio.

Verifica contra las BD de prueba el flujo real del módulo (API actual):
cliente natural (Persona_natural) → producto/modelo (Producto, el ID lo
genera sp_registrar_producto) → equipo (Equipo) → crear_orden → consulta →
revisión técnica (Tests.registrar_revision_test, sp_registrar_revision_test)
→ limpieza completa respetando las FKs.

REQUISITO: las BD de prueba deben estar levantadas antes de ejecutar:

    docker compose --env-file .env.test -p ituaccesorio_test \
        -f docker-compose.test.yml up -d --wait

(no se usa el servidor Flask: la prueba ejercita los modelos directamente).
"""
from app.models.clientes import Clientes, Persona_natural
from app.models.productos import Producto
from app.models.equipo import Equipo
from app.models.ordenes_servicio import Orden_servicio
from app.models.test import Tests

# --- Datos temporales generados por este test ---
CEDULA_CLIENTE_TEMP = "98765420"          # crear_orden exige cédula de 7-8 dígitos
NOMBRE_CLIENTE = "Integracion"
APELLIDO_CLIENTE = "Pruebas"
NOMBRE_PRODUCTO_TEMP = "Equipo Temporal Integracion"
ID_EQUIPO_TEMP = "123456789123456"        # IMEI: crear_orden exige 15 dígitos

# --- Datos ya sembrados en bd/tests/ituaccesoriobd.sql ---
ID_CLASE_PRODUCTO = "1"       # Clase_producto -> 'Telefono'
ID_MARCA_PRODUCTO = "1"       # Marca_producto -> 'Apple'
ID_EMPLEADO_TECNICO = 12345678  # Empleado -> 'Super Admin'

# --- Datos de negocio del test ---
DESCRIPCION_ORDEN = "Pantalla no enciende"
NOTA_ORDEN = "Equipo recibido en recepción"
ESTADO_INICIAL = "Pendiente"
COLOR_EQUIPO = "Negro"
CAPACIDAD_EQUIPO = "128GB"
CLAVE_EQUIPO = "123456"
PATRON_EQUIPO = "1-8-5-2-9"

TESTS_REVISION = [
    {"nombre": "Botón Power", "resultado": "Funciona"},
    {"nombre": "Mica", "resultado": "No funciona"},
    {"nombre": "LCD", "resultado": "Funciona"},
    {"nombre": "Táctil", "resultado": "Funciona"},
]


def limpiar_datos_temporales(id_orden=None):
    """Deja la BD como estaba. Orden de borrado respetando las FKs:
    orden (en cascada borra interacciones y tests) → equipo → producto → cliente.

    Dos IDs no son predecibles y se localizan antes de borrar:
    - La orden es autogenerada (OS#######): si una corrida abortó se
      lista el listado general y se filtra por el IMEI del equipo.
    - El ID del producto lo genera sp_registrar_producto: se localiza
      por el nombre único de la prueba.
    """
    if id_orden:
        Orden_servicio().eliminar_orden(id_orden)
    for orden in Orden_servicio().listado_ordenes_servicio():
        if orden.get("Equipo") == ID_EQUIPO_TEMP:
            Orden_servicio().eliminar_orden(orden.get("ID_orden"))
    Equipo(ID_equipo=ID_EQUIPO_TEMP).eliminar_equipo()
    for p in Producto(nombre=NOMBRE_PRODUCTO_TEMP).listar_productos(q=NOMBRE_PRODUCTO_TEMP):
        Producto(id_producto=p["id"]).eliminar_producto()
    Clientes(ID_cliente=CEDULA_CLIENTE_TEMP).eliminar_cliente()


def test_registrar_orden_servicio_con_cliente_equipo_y_revision():
    limpiar_datos_temporales()  # limpia restos de una corrida abortada
    id_orden = None
    try:
        # 1. Módulo de clientes: cliente natural
        mensaje = Persona_natural(
            Cedula_cliente=CEDULA_CLIENTE_TEMP,
            Nombre_cliente=NOMBRE_CLIENTE,
            Apellido_cliente=APELLIDO_CLIENTE,
            Telefono_cliente="04141234567",
            Correo_cliente="integracion.orden@gmail.com",
            Direccion_cliente="Barquisimeto",
        ).registrar_persona_natural()
        assert "se registró exitosamente" in mensaje, mensaje
        assert Clientes().verificar_cliente_existe(CEDULA_CLIENTE_TEMP) is True

        # 2. Catálogo: Producto (el "modelo" de la orden). El ID lo genera
        #    sp_registrar_producto, se captura del retorno.
        id_producto = Producto(
            id_clase=ID_CLASE_PRODUCTO,
            id_marca=ID_MARCA_PRODUCTO,
            nombre=NOMBRE_PRODUCTO_TEMP,
            descripcion="Producto temporal de integración",
        ).registrar_producto()
        assert id_producto, "El producto debió registrarse con ID autogenerado"
        assert Producto(id_producto=id_producto).verificar_producto() is True

        # 3. Equipo (IMEI) ligado al producto
        assert Equipo(
            ID_equipo=ID_EQUIPO_TEMP,
            ID_producto=id_producto,
            Color=COLOR_EQUIPO,
            Capacidad=CAPACIDAD_EQUIPO,
            Clave=CLAVE_EQUIPO,
            Patron=PATRON_EQUIPO,
        ).registrar_equipo() == f"Equipo {ID_EQUIPO_TEMP} registrado exitosamente."

        # 4. Orden de servicio (relaciona Cliente + Equipo + modelo)
        id_orden = Orden_servicio(ID_empleado=ID_EMPLEADO_TECNICO).crear_orden(
            id_cliente=CEDULA_CLIENTE_TEMP,
            id_equipo=ID_EQUIPO_TEMP,
            id_modelo=id_producto,
            descripcion=DESCRIPCION_ORDEN,
            nota=NOTA_ORDEN,
            color=COLOR_EQUIPO,
            capacidad=CAPACIDAD_EQUIPO,
        )
        assert id_orden and id_orden.startswith("OS"), id_orden

        # 4.a Consulta directa: columnas crudas y enriquecidas
        consulta = Orden_servicio(ID_orden_servicio=id_orden).consultar_orden()
        assert consulta["ID_orden_servicio"] == id_orden
        assert consulta["ID_equipo"] == ID_EQUIPO_TEMP
        assert consulta["ID_cliente"] == CEDULA_CLIENTE_TEMP
        assert consulta["Estado_orden_servicio"] == ESTADO_INICIAL
        assert consulta["Descripcion_reparacion"] == DESCRIPCION_ORDEN
        assert consulta["Nota_orden_servicio"] == NOTA_ORDEN
        assert consulta["Estado"] == ESTADO_INICIAL
        assert consulta["nombre_cliente"] == f"{NOMBRE_CLIENTE} {APELLIDO_CLIENTE}"

        # 4.b El listado general incluye la orden recién creada
        listado = Orden_servicio().listado_ordenes_servicio()
        assert any(
            o["ID_orden"] == id_orden and o["Equipo"] == ID_EQUIPO_TEMP
            for o in listado
        )

        # 5. Revisión inicial (Interaccion con Accion='Revisión' + Test +
        #    enlaces), vía sp_registrar_revision_test
        resultado = Tests(
            ID_orden=id_orden,
            ID_empleado=ID_EMPLEADO_TECNICO,
            Numero_test=1,
            lista_tests=TESTS_REVISION,
        ).registrar_revision_test()
        assert resultado == "Revisión técnica y pruebas registradas exitosamente.", resultado

        # 5.a Tests guardados y enlazados a la orden
        tests_guardados = Tests().buscar_test_por_orden(id_orden)
        assert len(tests_guardados) == len(TESTS_REVISION)
        assert {t["Nombre_test"] for t in tests_guardados} == {
            t["nombre"] for t in TESTS_REVISION
        }
        assert {t["Observaciones"] for t in tests_guardados} == {
            t["resultado"] for t in TESTS_REVISION
        }
        assert {t["Num_test"] for t in tests_guardados} == {1}

        # 5.b La orden sigue existiendo después de la revisión
        assert (
            Orden_servicio(ID_orden_servicio=id_orden).consultar_orden() is not None
        )
    finally:
        limpiar_datos_temporales(id_orden=id_orden)
