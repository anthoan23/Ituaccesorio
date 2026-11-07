"""Pruebas de integración de la clase Cargo contra MySQL real."""
import pytest

from app.models.cargos import Cargo

CARGOS = [
    {
        "id": "CRG0000001",
        "nombre": "Técnico",
        "descripcion": "Encargado de las revisiones y reparaciones",
    },
    {
        "id": "CRG0000002",
        "nombre": "Administrador",
        "descripcion": "Administrador del sistema con acceso total",
    },
]

DESCRIPCION = "Cargo temporal"
ID_VALIDO = "CRG0000001"
CARGO_AGREGAR = "Cargo Temporal Agregar"
CARGO_ACTUALIZAR = "Cargo Temporal Actualizar"
CARGO_MISMO_NOMBRE = "Cargo Temporal Mismo Nombre"
CARGO_DUPLICADO = "Cargo Temporal Duplicado"
CARGO_ELIMINAR = "Cargo Temporal Eliminar"


class TestListarCargos:

    def test_listar_cargos(self):
        assert Cargo().listar_cargos() == CARGOS


class TestVerificarCargo:

    def test_verificar_cargo_existente(self):
        assert Cargo("CRG0000001").verificar_cargo_por_id() is True

    def test_verificar_cargo_inexistente(self):
        assert Cargo("CRG9999999").verificar_cargo_por_id() is False


class TestObtenerIdPorNombre:

    def test_obtener_id_por_nombre(self):
        assert Cargo(nombre_cargo="Administrador").obtener_id_por_nombre() == "CRG0000002"

    def test_obtener_id_por_nombre_inexistente(self):
        assert Cargo(nombre_cargo="Gerente").obtener_id_por_nombre() is None


class TestAgregarCargo:

    def test_datos_validos(self):
        id_cargo = None
        try:
            resultado = Cargo(
                nombre_cargo=CARGO_AGREGAR,
                descripcion_cargo=DESCRIPCION,
            ).agregar_cargo()
            id_cargo = Cargo(nombre_cargo=CARGO_AGREGAR).obtener_id_por_nombre()

            assert resultado == "Cargo agregado exitosamente."
            assert id_cargo is not None
            assert {
                "id": id_cargo,
                "nombre": CARGO_AGREGAR,
                "descripcion": DESCRIPCION,
            } in Cargo().listar_cargos()
        finally:
            if id_cargo and Cargo(id_cargo).verificar_cargo_por_id():
                Cargo(id_cargo).eliminar_cargo()

    def test_cargo_duplicado(self):
        resultado = Cargo(
            nombre_cargo="Técnico",
            descripcion_cargo=DESCRIPCION,
        ).agregar_cargo()

        assert resultado == "El cargo 'Técnico' ya existe."

    @pytest.mark.parametrize(
        "nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                DESCRIPCION,
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "Ca",
                DESCRIPCION,
                "El campo Nombre debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                "C" * 31,
                DESCRIPCION,
                "El campo Nombre no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Caja #1",
                DESCRIPCION,
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                "Cargo",
                "",
                "El campo Descripción no puede estar vacío.",
                id="descripcion-vacia",
            ),
            pytest.param(
                "Cargo",
                "At",
                "El campo Descripción debe tener al menos 3 caracteres.",
                id="descripcion-demasiado-corta",
            ),
            pytest.param(
                "Cargo",
                "D" * 251,
                "El campo Descripción no puede tener más de 250 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                "Cargo",
                "@#$%",
                "El campo Descripción solo puede contener letras, números, acentos y espacios.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, nombre, descripcion, esperado):
        resultado = Cargo(
            nombre_cargo=nombre,
            descripcion_cargo=descripcion,
        ).agregar_cargo()

        assert resultado == esperado


class TestActualizarCargo:

    def test_datos_validos(self):
        id_cargo = None
        try:
            resultado = Cargo(
                nombre_cargo=CARGO_ACTUALIZAR,
                descripcion_cargo=DESCRIPCION,
            ).agregar_cargo()
            id_cargo = Cargo(nombre_cargo=CARGO_ACTUALIZAR).obtener_id_por_nombre()
            assert resultado == "Cargo agregado exitosamente."
            assert id_cargo is not None

            resultado = Cargo(
                id_cargo,
                "Cargo Temporal Actualizado",
                "Descripción actualizada",
            ).actualizar_cargo()

            assert resultado == "Cargo actualizado exitosamente."
            assert Cargo(
                nombre_cargo="Cargo Temporal Actualizado"
            ).obtener_id_por_nombre() == id_cargo
            assert {
                "id": id_cargo,
                "nombre": "Cargo Temporal Actualizado",
                "descripcion": "Descripción actualizada",
            } in Cargo().listar_cargos()
        finally:
            if id_cargo and Cargo(id_cargo).verificar_cargo_por_id():
                Cargo(id_cargo).eliminar_cargo()

    def test_mismo_nombre_se_permite(self):
        id_cargo = None
        try:
            resultado = Cargo(
                nombre_cargo=CARGO_MISMO_NOMBRE,
                descripcion_cargo=DESCRIPCION,
            ).agregar_cargo()
            id_cargo = Cargo(nombre_cargo=CARGO_MISMO_NOMBRE).obtener_id_por_nombre()
            assert resultado == "Cargo agregado exitosamente."
            assert id_cargo is not None

            resultado = Cargo(
                id_cargo,
                CARGO_MISMO_NOMBRE,
                "Descripción cambiada",
            ).actualizar_cargo()

            assert resultado == "Cargo actualizado exitosamente."
            cargo = next(
                cargo for cargo in Cargo().listar_cargos() if cargo["id"] == id_cargo
            )
            assert cargo["descripcion"] == "Descripción cambiada"
        finally:
            if id_cargo and Cargo(id_cargo).verificar_cargo_por_id():
                Cargo(id_cargo).eliminar_cargo()

    def test_cargo_inexistente(self):
        resultado = Cargo(
            "CRG9999999",
            "Cargo Nuevo",
            "Descripción nueva",
        ).actualizar_cargo()

        assert resultado == "El cargo con identificador CRG9999999 no existe."

    def test_nombre_duplicado_de_otro_cargo(self):
        id_cargo = None
        try:
            resultado = Cargo(
                nombre_cargo=CARGO_DUPLICADO,
                descripcion_cargo=DESCRIPCION,
            ).agregar_cargo()
            id_cargo = Cargo(nombre_cargo=CARGO_DUPLICADO).obtener_id_por_nombre()
            assert resultado == "Cargo agregado exitosamente."
            assert id_cargo is not None

            resultado = Cargo(
                id_cargo,
                "Técnico",
                "Descripción nueva",
            ).actualizar_cargo()

            assert resultado == "El cargo 'Técnico' ya existe."
            assert Cargo(nombre_cargo=CARGO_DUPLICADO).obtener_id_por_nombre() == id_cargo
        finally:
            if id_cargo and Cargo(id_cargo).verificar_cargo_por_id():
                Cargo(id_cargo).eliminar_cargo()

    @pytest.mark.parametrize(
        "id_cargo, nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                "Cargo Nuevo",
                "Descripción nueva",
                "El campo ID del Cargo no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "1234567",
                "Cargo Nuevo",
                "Descripción nueva",
                "El campo ID del Cargo debe tener al menos 9 caracteres.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "Cargo Nuevo",
                "Descripción nueva",
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                "12345678#",
                "Cargo Nuevo",
                "Descripción nueva",
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
            pytest.param(
                ID_VALIDO,
                "",
                "Descripción nueva",
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                ID_VALIDO,
                "Ge",
                "Descripción nueva",
                "El campo Nombre debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                ID_VALIDO,
                "G" * 31,
                "Descripción nueva",
                "El campo Nombre no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                ID_VALIDO,
                "Gerente #1",
                "Descripción nueva",
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                ID_VALIDO,
                "Cargo Nuevo",
                "",
                "El campo Descripción no puede estar vacío.",
                id="descripcion-vacia",
            ),
            pytest.param(
                ID_VALIDO,
                "Cargo Nuevo",
                "De",
                "El campo Descripción debe tener al menos 3 caracteres.",
                id="descripcion-demasiado-corta",
            ),
            pytest.param(
                ID_VALIDO,
                "Cargo Nuevo",
                "D" * 251,
                "El campo Descripción no puede tener más de 250 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                ID_VALIDO,
                "Cargo Nuevo",
                "@#$%",
                "El campo Descripción solo puede contener letras, números, acentos y espacios.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, id_cargo, nombre, descripcion, esperado):
        resultado = Cargo(id_cargo, nombre, descripcion).actualizar_cargo()

        assert resultado == esperado


class TestEliminarCargo:

    def test_datos_validos(self):
        id_cargo = None
        try:
            resultado = Cargo(
                nombre_cargo=CARGO_ELIMINAR,
                descripcion_cargo=DESCRIPCION,
            ).agregar_cargo()
            id_cargo = Cargo(nombre_cargo=CARGO_ELIMINAR).obtener_id_por_nombre()
            assert resultado == "Cargo agregado exitosamente."
            assert id_cargo is not None

            resultado = Cargo(id_cargo).eliminar_cargo()

            assert resultado == "Cargo eliminado exitosamente."
            assert Cargo(id_cargo).verificar_cargo_por_id() is False
        finally:
            if id_cargo and Cargo(id_cargo).verificar_cargo_por_id():
                Cargo(id_cargo).eliminar_cargo()

    def test_cargo_inexistente(self):
        resultado = Cargo("CRG9999999").eliminar_cargo()

        assert resultado == "El cargo con identificador CRG9999999 no existe."

    def test_cargo_en_uso_por_empleado(self):
        resultado = Cargo("CRG0000002").eliminar_cargo()

        assert resultado == (
            "Error al eliminar cargo. Verifica que no esté en uso por empleados."
        )
        assert Cargo("CRG0000002").verificar_cargo_por_id() is True

    @pytest.mark.parametrize(
        "id_cargo, esperado",
        [
            pytest.param(
                "",
                "El campo ID del Cargo no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "1234567",
                "El campo ID del Cargo debe tener al menos 9 caracteres.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                "12345678#",
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
        ],
    )
    def test_id_invalido(self, id_cargo, esperado):
        assert Cargo(id_cargo).eliminar_cargo() == esperado
