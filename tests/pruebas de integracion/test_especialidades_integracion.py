"""Pruebas de integración de la clase Especialidad contra MySQL real."""
import pytest

from app.models.empleados import Empleados
from app.models.especialidades import Especialidad

ESPECIALIDADES = [
    {
        "id": "ESP0000001",
        "nombre": "Reparación iOS",
        "descripcion": "Especialista en reparación de dispositivos Apple",
    },
    {
        "id": "ESP0000002",
        "nombre": "Reparación Android",
        "descripcion": "Especialista en reparación de dispositivos Android",
    },
    {
        "id": "ESP0000003",
        "nombre": "Cambio de Pantalla",
        "descripcion": "Especialista en cambio de pantallas",
    },
    {
        "id": "ESP0000004",
        "nombre": "Reparación Placa",
        "descripcion": "Especialista en reparación de placas madre",
    },
    {
        "id": "ESP0000005",
        "nombre": "Software",
        "descripcion": "Especialista en problemas de software",
    },
]

DESCRIPCION = "Especialidad temporal"
ID_VALIDO = "ESP0000001"
ESPECIALIDAD_AGREGAR = "Esp Temporal Agregar"
ESPECIALIDAD_ACTUALIZAR = "Esp Temporal Actualizar"
ESPECIALIDAD_MISMO_NOMBRE = "Esp Mismo Nombre"
ESPECIALIDAD_DUPLICADA = "Esp Duplicada"
ESPECIALIDAD_ELIMINAR = "Esp Temporal Eliminar"
ESPECIALIDAD_EN_USO = "Esp Temporal En Uso"
CEDULA_EN_USO = "987654327"


class TestListarEspecialidades:

    def test_listar_especialidades(self):
        assert Especialidad().listar_especialidades() == ESPECIALIDADES


class TestVerificarEspecialidad:

    def test_verificar_especialidad_existente(self):
        assert Especialidad("ESP0000003").verificar_especialidad_por_id() is True

    def test_verificar_especialidad_inexistente(self):
        assert Especialidad("ESP9999999").verificar_especialidad_por_id() is False


class TestObtenerEspecialidad:

    def test_obtener_especialidad_por_id(self):
        assert Especialidad("ESP0000003").obtener_especialidad_por_id() == ESPECIALIDADES[2]

    def test_obtener_id_por_nombre(self):
        assert Especialidad(nombre_especialidad="Software").obtener_id_por_nombre() == "ESP0000005"


class TestAgregarEspecialidad:

    def test_datos_validos(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad=ESPECIALIDAD_AGREGAR,
                descripcion_especialidad=DESCRIPCION,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad=ESPECIALIDAD_AGREGAR
            ).obtener_id_por_nombre()

            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None
            assert {
                "id": id_especialidad,
                "nombre": ESPECIALIDAD_AGREGAR,
                "descripcion": DESCRIPCION,
            } in Especialidad().listar_especialidades()
        finally:
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    def test_especialidad_duplicada(self):
        resultado = Especialidad(
            nombre_especialidad="Software",
            descripcion_especialidad=DESCRIPCION,
        ).agregar_especialidad()

        assert resultado == "La especialidad 'Software' ya existe."

    @pytest.mark.parametrize(
        "nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                DESCRIPCION,
                "El campo Nombre de la especialidad no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "Es",
                DESCRIPCION,
                "El campo Nombre de la especialidad debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                "E" * 31,
                DESCRIPCION,
                "El campo Nombre de la especialidad no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Cel #1",
                DESCRIPCION,
                "El campo Nombre de la especialidad solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                "Especialidad",
                "",
                "El campo Descripción de la especialidad no puede estar vacío.",
                id="descripcion-vacia",
            ),
            pytest.param(
                "Especialidad",
                "Re",
                "El campo Descripción de la especialidad debe tener al menos 3 caracteres.",
                id="descripcion-demasiado-corta",
            ),
            pytest.param(
                "Especialidad",
                "D" * 251,
                "El campo Descripción de la especialidad no puede tener más de 250 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                "Especialidad",
                "@#$%",
                "El campo Descripción de la especialidad solo puede contener letras, números, acentos y espacios.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, nombre, descripcion, esperado):
        resultado = Especialidad(
            nombre_especialidad=nombre,
            descripcion_especialidad=descripcion,
        ).agregar_especialidad()

        assert resultado == esperado


class TestActualizarEspecialidad:

    def test_datos_validos(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad=ESPECIALIDAD_ACTUALIZAR,
                descripcion_especialidad=DESCRIPCION,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad=ESPECIALIDAD_ACTUALIZAR
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None

            resultado = Especialidad(
                id_especialidad,
                "Esp Temporal Actualizada",
                "Descripción actualizada",
            ).actualizar_especialidad()

            assert resultado == "Especialidad actualizada exitosamente."
            assert Especialidad(
                nombre_especialidad="Esp Temporal Actualizada"
            ).obtener_id_por_nombre() == id_especialidad
            assert {
                "id": id_especialidad,
                "nombre": "Esp Temporal Actualizada",
                "descripcion": "Descripción actualizada",
            } in Especialidad().listar_especialidades()
        finally:
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    def test_mismo_nombre_se_permite(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad=ESPECIALIDAD_MISMO_NOMBRE,
                descripcion_especialidad=DESCRIPCION,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad=ESPECIALIDAD_MISMO_NOMBRE
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None

            resultado = Especialidad(
                id_especialidad,
                ESPECIALIDAD_MISMO_NOMBRE,
                "Descripción cambiada",
            ).actualizar_especialidad()

            assert resultado == "Especialidad actualizada exitosamente."
            especialidad = next(
                especialidad
                for especialidad in Especialidad().listar_especialidades()
                if especialidad["id"] == id_especialidad
            )
            assert especialidad["descripcion"] == "Descripción cambiada"
        finally:
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    def test_especialidad_inexistente(self):
        resultado = Especialidad(
            "ESP9999999",
            "Especialidad Nueva",
            "Descripción nueva",
        ).actualizar_especialidad()

        assert resultado == "La especialidad con identificador ESP9999999 no existe."

    def test_nombre_duplicado_de_otra_especialidad(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad=ESPECIALIDAD_DUPLICADA,
                descripcion_especialidad=DESCRIPCION,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad=ESPECIALIDAD_DUPLICADA
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None

            resultado = Especialidad(
                id_especialidad,
                "Software",
                "Descripción nueva",
            ).actualizar_especialidad()

            assert resultado == "La especialidad 'Software' ya existe."
            assert Especialidad(
                nombre_especialidad=ESPECIALIDAD_DUPLICADA
            ).obtener_id_por_nombre() == id_especialidad
        finally:
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    @pytest.mark.parametrize(
        "id_especialidad, nombre, descripcion, esperado",
        [
            pytest.param(
                "",
                "Especialidad Nueva",
                "Descripción nueva",
                "El campo ID de la especialidad no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "1234567",
                "Especialidad Nueva",
                "Descripción nueva",
                "El campo ID de la especialidad debe tener al menos 9 caracteres.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "Especialidad Nueva",
                "Descripción nueva",
                "El campo ID de la especialidad no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                "12345678#",
                "Especialidad Nueva",
                "Descripción nueva",
                "El campo ID de la especialidad solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
            pytest.param(
                ID_VALIDO,
                "",
                "Descripción nueva",
                "El campo Nombre de la especialidad no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                ID_VALIDO,
                "Es",
                "Descripción nueva",
                "El campo Nombre de la especialidad debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                ID_VALIDO,
                "E" * 31,
                "Descripción nueva",
                "El campo Nombre de la especialidad no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                ID_VALIDO,
                "Cel #1",
                "Descripción nueva",
                "El campo Nombre de la especialidad solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                ID_VALIDO,
                "Especialidad Nueva",
                "",
                "El campo Descripción de la especialidad no puede estar vacío.",
                id="descripcion-vacia",
            ),
            pytest.param(
                ID_VALIDO,
                "Especialidad Nueva",
                "De",
                "El campo Descripción de la especialidad debe tener al menos 3 caracteres.",
                id="descripcion-demasiado-corta",
            ),
            pytest.param(
                ID_VALIDO,
                "Especialidad Nueva",
                "D" * 251,
                "El campo Descripción de la especialidad no puede tener más de 250 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                ID_VALIDO,
                "Especialidad Nueva",
                "@#$%",
                "El campo Descripción de la especialidad solo puede contener letras, números, acentos y espacios.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, id_especialidad, nombre, descripcion, esperado):
        resultado = Especialidad(
            id_especialidad,
            nombre,
            descripcion,
        ).actualizar_especialidad()

        assert resultado == esperado


class TestEliminarEspecialidad:

    def test_datos_validos(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad=ESPECIALIDAD_ELIMINAR,
                descripcion_especialidad=DESCRIPCION,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad=ESPECIALIDAD_ELIMINAR
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None

            resultado = Especialidad(id_especialidad).eliminar_especialidad()

            assert resultado == "Especialidad eliminada exitosamente."
            assert Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id() is False
        finally:
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    def test_especialidad_inexistente(self):
        resultado = Especialidad("ESP9999999").eliminar_especialidad()

        assert resultado == "La especialidad con identificador ESP9999999 no existe."

    def test_especialidad_en_uso_por_empleado(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad=ESPECIALIDAD_EN_USO,
                descripcion_especialidad=DESCRIPCION,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad=ESPECIALIDAD_EN_USO
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None

            resultado = Empleados(
                id_empleado=CEDULA_EN_USO,
                id_cargo="CRG0000001",
                nombre_empleado="Empleado",
                apellido_empleado="Prueba",
                celular_empleado="0414123456",
                correo_empleado="prueba@mail.com",
                direccion_empleado="Barquisimeto",
                especialidades=[id_especialidad],
            ).agregar_empleado()
            assert resultado == "Empleado agregado exitosamente."

            resultado = Especialidad(id_especialidad).eliminar_especialidad()

            assert resultado == (
                f"No se puede eliminar la especialidad con ID {id_especialidad} "
                "porque está en uso por empleados."
            )
            assert Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id() is True
        finally:
            if Empleados(id_empleado=CEDULA_EN_USO).verificar_empleado():
                Empleados(id_empleado=CEDULA_EN_USO).eliminar_empleado()
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    @pytest.mark.parametrize(
        "id_especialidad, esperado",
        [
            pytest.param(
                "",
                "El campo ID de la especialidad no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "1234567",
                "El campo ID de la especialidad debe tener al menos 9 caracteres.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "El campo ID de la especialidad no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                "12345678#",
                "El campo ID de la especialidad solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
        ],
    )
    def test_id_invalido(self, id_especialidad, esperado):
        assert Especialidad(id_especialidad).eliminar_especialidad() == esperado
