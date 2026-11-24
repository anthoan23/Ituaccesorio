"""Pruebas de integración del flujo Cargo → Empleado contra MySQL real.

Escenario: se registra un cargo y luego se registra un empleado que usa ese
mismo cargo, verificando la relación en la BD (FK `Empleado_ibfk_1`).
"""
from app.models.cargos import Cargo
from app.models.empleados import Empleados

NOMBRE_CARGO = "Cargo Temporal Integracion"
DESCRIPCION_CARGO = "Cargo temporal de integración"
CEDULA = "98765420"
CELULAR = "04141234567"
CORREO = "integracion.pruebas@mail.com"

# Datos sembrados directamente en la BD de prueba
# (bd/tests/ituaccesoriobd.sql, sección 2.1 registros CRUD).
ID_CARGO_EN_USO = "CRG0000106"
CEDULA_EN_USO = "51000007"


def limpiar_datos_temporales():
    """Elimina los registros temporales (de esta corrida o de una previa abortada)."""
    # Primero el empleado (la FK restringiría borrar el cargo).
    Empleados(id_empleado=CEDULA).eliminar_empleado()
    id_cargo = Cargo(nombre_cargo=NOMBRE_CARGO).obtener_id_por_nombre()
    if id_cargo:
        Cargo(id_cargo=id_cargo).eliminar_cargo()


def test_registrar_cargo_y_empleado_con_ese_cargo():
    limpiar_datos_temporales()
    try:
        # 1. Registrar el cargo.
        assert (
            Cargo(
                nombre_cargo=NOMBRE_CARGO,
                descripcion_cargo=DESCRIPCION_CARGO,
            ).agregar_cargo()
            == "Cargo agregado exitosamente."
        )

        # El SP Crear_cargo genera el ID (CRG0000001, CRG0000002, ...).
        id_cargo = Cargo(nombre_cargo=NOMBRE_CARGO).obtener_id_por_nombre()
        assert id_cargo is not None
        assert {
            "id": id_cargo,
            "nombre": NOMBRE_CARGO,
            "descripcion": DESCRIPCION_CARGO,
        } in Cargo().listar_cargos()

        # 2. Registrar un empleado con ese mismo cargo.
        assert (
            Empleados(
                id_empleado=CEDULA,
                id_cargo=id_cargo,
                nombre_empleado="Integracion",
                apellido_empleado="Pruebas",
                celular_empleado=CELULAR,
                correo_empleado=CORREO,
                direccion_empleado="Barquisimeto",
            ).agregar_empleado()
            == "Empleado agregado exitosamente."
        )

        consulta = Empleados(id_empleado=CEDULA).consultar_empleado()
        assert consulta["cedula"] == int(CEDULA)
        assert consulta["cargo_id"] == id_cargo
        assert consulta["cargo"] == NOMBRE_CARGO

        assert {
            "cedula": int(CEDULA),
            "nombre": "Integracion",
            "apellido": "Pruebas",
            "cargo": NOMBRE_CARGO,
        } in Empleados().listar_empleados()
    finally:
        limpiar_datos_temporales()


def test_eliminar_cargo_con_empleado_registrado():
    # Datos sembrados directamente en la BD de prueba:
    # el empleado 51000007 usa el cargo CRG0000106.
    assert Cargo(ID_CARGO_EN_USO).verificar_cargo_por_id() is True
    assert Empleados(id_empleado=CEDULA_EN_USO).verificar_empleado() is True

    # La FK Empleado_ibfk_1 (RESTRICT) debe impedir eliminar el cargo.
    assert (
        Cargo(ID_CARGO_EN_USO).eliminar_cargo()
        == "Error al eliminar cargo. Verifica que no esté en uso por empleados."
    )

    # El rollback mantiene el cargo y el empleado intactos.
    assert Cargo(ID_CARGO_EN_USO).verificar_cargo_por_id() is True
    assert Empleados(id_empleado=CEDULA_EN_USO).verificar_empleado() is True
