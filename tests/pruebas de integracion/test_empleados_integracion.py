"""Pruebas de integración de la clase Empleados contra MySQL real."""
import pytest

from app.models.empleados import Empleados
from app.models.especialidades import Especialidad

CARGOS = [
    {
        "id": "CRG0000002",
        "nombre": "Administrador",
        "descripcion": "Administrador del sistema con acceso total",
    },
    {
        "id": "CRG0000001",
        "nombre": "Técnico",
        "descripcion": "Encargado de las revisiones y reparaciones",
    },
]

EMPLEADO = {
    "cedula": 12345678,
    "nombre": "Super",
    "apellido": "Admin",
    "celular": "04140000000",
    "correo": "admin@ituaccesorio.com",
    "direccion": "Barquisimeto",
    "cargo_id": "CRG0000002",
    "cargo": "Administrador",
}

CELULAR = "0414123456"
ID_CARGO_VALIDO = "CRG0000001"
DESCRIPCION_ESPECIALIDAD = "Especialidad temporal"
CEDULA_INEXISTENTE = "999999999"
CEDULA_AGREGAR = "987654321"
CEDULA_AGREGAR_ESPECIALIDAD = "987654322"
CEDULA_ACTUALIZAR = "987654323"
CEDULA_ACTUALIZAR_ESPECIALIDAD = "987654324"
CEDULA_ELIMINAR = "987654325"
CEDULA_ELIMINAR_CAPACITACION = "987654326"


def datos_empleado(**cambios):
    datos = {
        "id_empleado": CEDULA_INEXISTENTE,
        "id_cargo": ID_CARGO_VALIDO,
        "nombre_empleado": "Empleado",
        "apellido_empleado": "Prueba",
        "celular_empleado": CELULAR,
        "correo_empleado": "prueba@mail.com",
        "direccion_empleado": "Barquisimeto",
    }
    datos.update(cambios)
    return datos


class TestListadosEmpleados:

    def test_listar_empleados(self):
        assert Empleados().listar_empleados() == [
            {
                "cedula": EMPLEADO["cedula"],
                "nombre": EMPLEADO["nombre"],
                "apellido": EMPLEADO["apellido"],
                "cargo": EMPLEADO["cargo"],
            }
        ]

    def test_listar_cargos(self):
        assert Empleados().listar_cargos() == CARGOS

    def test_listar_especialidades(self):
        especialidades = Empleados().listar_especialidades()

        assert len(especialidades) == 5
        assert {especialidad["id"] for especialidad in especialidades} == {
            "ESP0000001",
            "ESP0000002",
            "ESP0000003",
            "ESP0000004",
            "ESP0000005",
        }

    def test_listar_empleados_por_cargo(self):
        assert Empleados().listar_empleados_por_cargo() == [
            {"nombre": "Administrador", "cantidad": 1},
            {"nombre": "Técnico", "cantidad": 0},
        ]

    def test_listar_empleados_por_especialidad(self):
        especialidades = Empleados().listar_empleados_por_especialidad()

        assert len(especialidades) == 5
        assert all(especialidad["cantidad"] == 0 for especialidad in especialidades)

    def test_listar_tecnicos(self):
        assert Empleados().listar_tecnicos() == []


class TestConsultarEmpleado:

    def test_consultar_empleado(self):
        assert Empleados(id_empleado=str(EMPLEADO["cedula"])).consultar_empleado() == EMPLEADO

    def test_consultar_empleado_inexistente(self):
        assert Empleados(id_empleado="87654321").consultar_empleado() is None

    def test_consultar_especialidades_del_empleado(self):
        assert Empleados(id_empleado=str(EMPLEADO["cedula"])).consultar_especialidades_empleado() == []


class TestVerificarEmpleado:

    def test_verificar_empleado_existente(self):
        assert Empleados(id_empleado=str(EMPLEADO["cedula"])).verificar_empleado() is True

    def test_verificar_empleado_inexistente(self):
        assert Empleados(id_empleado="87654321").verificar_empleado() is False


class TestAgregarEmpleado:

    def test_datos_validos(self):
        try:
            resultado = Empleados(
                **datos_empleado(id_empleado=CEDULA_AGREGAR)
            ).agregar_empleado()

            assert resultado == "Empleado agregado exitosamente."
            empleado = Empleados(id_empleado=CEDULA_AGREGAR).consultar_empleado()
            assert empleado["cedula"] == int(CEDULA_AGREGAR)
            assert empleado["nombre"] == "Empleado"
            assert empleado["apellido"] == "Prueba"
            assert empleado["cargo_id"] == ID_CARGO_VALIDO
        finally:
            if Empleados(id_empleado=CEDULA_AGREGAR).verificar_empleado():
                Empleados(id_empleado=CEDULA_AGREGAR).eliminar_empleado()

    def test_datos_validos_con_especialidades(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad="Esp Empleado Agregar",
                descripcion_especialidad=DESCRIPCION_ESPECIALIDAD,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad="Esp Empleado Agregar"
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None

            resultado = Empleados(
                **datos_empleado(
                    id_empleado=CEDULA_AGREGAR_ESPECIALIDAD,
                    especialidades=[id_especialidad],
                )
            ).agregar_empleado()

            assert resultado == "Empleado agregado exitosamente."
            especialidades = Empleados(
                id_empleado=CEDULA_AGREGAR_ESPECIALIDAD
            ).consultar_especialidades_empleado()
            assert [especialidad["id"] for especialidad in especialidades] == [
                id_especialidad
            ]
        finally:
            if Empleados(
                id_empleado=CEDULA_AGREGAR_ESPECIALIDAD
            ).verificar_empleado():
                Empleados(
                    id_empleado=CEDULA_AGREGAR_ESPECIALIDAD
                ).eliminar_empleado()
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    def test_empleado_duplicado(self):
        resultado = Empleados(
            **datos_empleado(id_empleado=str(EMPLEADO["cedula"]))
        ).agregar_empleado()

        assert resultado == f"El empleado con cédula {EMPLEADO['cedula']} ya existe."

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"id_empleado": ""},
                "El campo Cédula no puede estar vacío.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"id_empleado": "12345"},
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"id_empleado": "1234567890"},
                "El campo Cédula no puede tener más de 9 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                {"id_empleado": "12345a"},
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"id_cargo": ""},
                "El campo ID del Cargo no puede estar vacío.",
                id="cargo-vacio",
            ),
            pytest.param(
                {"id_cargo": "12345678901"},
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="cargo-demasiado-largo",
            ),
            pytest.param(
                {"id_cargo": "Cargo#1"},
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="cargo-caracteres-invalidos",
            ),
            pytest.param(
                {"nombre_empleado": ""},
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"nombre_empleado": "An"},
                "El campo Nombre debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                {"nombre_empleado": "N" * 31},
                "El campo Nombre no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"nombre_empleado": "Ana #1"},
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                {"apellido_empleado": ""},
                "El campo Apellido no puede estar vacío.",
                id="apellido-vacio",
            ),
            pytest.param(
                {"apellido_empleado": "Pz"},
                "El campo Apellido debe tener al menos 3 caracteres.",
                id="apellido-demasiado-corto",
            ),
            pytest.param(
                {"apellido_empleado": "A" * 31},
                "El campo Apellido no puede tener más de 30 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                {"apellido_empleado": "Paz #1"},
                "El campo Apellido solo puede contener letras, acentos y espacios.",
                id="apellido-caracteres-invalidos",
            ),
            pytest.param(
                {"celular_empleado": ""},
                "El campo Celular no puede estar vacío.",
                id="celular-vacio",
            ),
            pytest.param(
                {"celular_empleado": "12345678"},
                "El campo Celular debe tener al menos 9 dígitos.",
                id="celular-demasiado-corto",
            ),
            pytest.param(
                {"celular_empleado": "1234567890123456"},
                "El campo Celular no puede tener más de 15 dígitos.",
                id="celular-demasiado-largo",
            ),
            pytest.param(
                {"celular_empleado": "0412abc123"},
                "El campo Celular solo puede contener números.",
                id="celular-no-numerico",
            ),
            pytest.param(
                {"correo_empleado": ""},
                "El campo correo no puede estar vacío.",
                id="correo-vacio",
            ),
            pytest.param(
                {"correo_empleado": "correo-sin-arroba"},
                "El campo correo debe contener el símbolo @.",
                id="correo-sin-arroba",
            ),
            pytest.param(
                {"direccion_empleado": ""},
                "El campo Dirección no puede estar vacío.",
                id="direccion-vacia",
            ),
            pytest.param(
                {"direccion_empleado": "A"},
                "El campo Dirección debe tener al menos 2 caracteres.",
                id="direccion-demasiado-corta",
            ),
            pytest.param(
                {"direccion_empleado": "D" * 61},
                "El campo Dirección no puede tener más de 60 caracteres.",
                id="direccion-demasiado-larga",
            ),
            pytest.param(
                {"direccion_empleado": "@#$"},
                "El campo Dirección solo puede contener letras, números, acentos y espacios.",
                id="direccion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        resultado = Empleados(**datos_empleado(**cambios)).agregar_empleado()

        assert resultado == esperado


class TestActualizarEmpleado:

    def test_datos_validos(self):
        try:
            resultado = Empleados(
                **datos_empleado(id_empleado=CEDULA_ACTUALIZAR)
            ).agregar_empleado()
            assert resultado == "Empleado agregado exitosamente."

            resultado = Empleados(
                id_empleado=CEDULA_ACTUALIZAR,
                id_cargo="CRG0000002",
                nombre_empleado="Actualizado",
                apellido_empleado="Empleado",
                celular_empleado=CELULAR,
                correo_empleado="actualizado@mail.com",
                direccion_empleado="Caracas",
            ).actualizar_empleado()

            assert resultado == "Empleado actualizado exitosamente."
            empleado = Empleados(id_empleado=CEDULA_ACTUALIZAR).consultar_empleado()
            assert empleado["nombre"] == "Actualizado"
            assert empleado["apellido"] == "Empleado"
            assert empleado["celular"] == CELULAR
            assert empleado["correo"] == "actualizado@mail.com"
            assert empleado["direccion"] == "Caracas"
            assert empleado["cargo_id"] == "CRG0000002"
        finally:
            if Empleados(id_empleado=CEDULA_ACTUALIZAR).verificar_empleado():
                Empleados(id_empleado=CEDULA_ACTUALIZAR).eliminar_empleado()

    def test_datos_validos_con_especialidades(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad="Esp Empleado Actualizar",
                descripcion_especialidad=DESCRIPCION_ESPECIALIDAD,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad="Esp Empleado Actualizar"
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None

            resultado = Empleados(
                **datos_empleado(id_empleado=CEDULA_ACTUALIZAR_ESPECIALIDAD)
            ).agregar_empleado()
            assert resultado == "Empleado agregado exitosamente."

            resultado = Empleados(
                **datos_empleado(
                    id_empleado=CEDULA_ACTUALIZAR_ESPECIALIDAD,
                    especialidades=[id_especialidad],
                )
            ).actualizar_empleado()

            assert resultado == "Empleado actualizado exitosamente."
            especialidades = Empleados(
                id_empleado=CEDULA_ACTUALIZAR_ESPECIALIDAD
            ).consultar_especialidades_empleado()
            assert [especialidad["id"] for especialidad in especialidades] == [
                id_especialidad
            ]
        finally:
            if Empleados(
                id_empleado=CEDULA_ACTUALIZAR_ESPECIALIDAD
            ).verificar_empleado():
                Empleados(
                    id_empleado=CEDULA_ACTUALIZAR_ESPECIALIDAD
                ).eliminar_empleado()
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    def test_empleado_inexistente(self):
        resultado = Empleados(
            **datos_empleado(id_empleado=CEDULA_INEXISTENTE)
        ).actualizar_empleado()

        assert resultado == (
            f"El empleado con identificador {CEDULA_INEXISTENTE} no existe."
        )

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"id_empleado": ""},
                "El campo Cédula no puede estar vacío.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"id_empleado": "12345"},
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"id_empleado": "1234567890"},
                "El campo Cédula no puede tener más de 9 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                {"id_empleado": "12345a"},
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"id_cargo": ""},
                "El campo ID del Cargo no puede estar vacío.",
                id="cargo-vacio",
            ),
            pytest.param(
                {"id_cargo": "12345678901"},
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="cargo-demasiado-largo",
            ),
            pytest.param(
                {"id_cargo": "Cargo#1"},
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="cargo-caracteres-invalidos",
            ),
            pytest.param(
                {"nombre_empleado": ""},
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"nombre_empleado": "An"},
                "El campo Nombre debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                {"nombre_empleado": "N" * 31},
                "El campo Nombre no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"nombre_empleado": "Ana #1"},
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                {"apellido_empleado": ""},
                "El campo Apellido no puede estar vacío.",
                id="apellido-vacio",
            ),
            pytest.param(
                {"apellido_empleado": "Pz"},
                "El campo Apellido debe tener al menos 3 caracteres.",
                id="apellido-demasiado-corto",
            ),
            pytest.param(
                {"apellido_empleado": "A" * 31},
                "El campo Apellido no puede tener más de 30 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                {"apellido_empleado": "Paz #1"},
                "El campo Apellido solo puede contener letras, acentos y espacios.",
                id="apellido-caracteres-invalidos",
            ),
            pytest.param(
                {"celular_empleado": ""},
                "El campo Celular no puede estar vacío.",
                id="celular-vacio",
            ),
            pytest.param(
                {"celular_empleado": "123456789"},
                "El campo Celular debe tener al menos 10 dígitos.",
                id="celular-demasiado-corto",
            ),
            pytest.param(
                {"celular_empleado": "12345678901"},
                "El campo Celular no puede tener más de 10 dígitos.",
                id="celular-demasiado-largo",
            ),
            pytest.param(
                {"celular_empleado": "0412abc123"},
                "El campo Celular solo puede contener números.",
                id="celular-no-numerico",
            ),
            pytest.param(
                {"correo_empleado": ""},
                "El campo correo no puede estar vacío.",
                id="correo-vacio",
            ),
            pytest.param(
                {"correo_empleado": "correo-sin-arroba"},
                "El campo correo debe contener el símbolo @.",
                id="correo-sin-arroba",
            ),
            pytest.param(
                {"direccion_empleado": ""},
                "El campo Dirección no puede estar vacío.",
                id="direccion-vacia",
            ),
            pytest.param(
                {"direccion_empleado": "A"},
                "El campo Dirección debe tener al menos 2 caracteres.",
                id="direccion-demasiado-corta",
            ),
            pytest.param(
                {"direccion_empleado": "D" * 61},
                "El campo Dirección no puede tener más de 60 caracteres.",
                id="direccion-demasiado-larga",
            ),
            pytest.param(
                {"direccion_empleado": "@#$"},
                "El campo Dirección solo puede contener letras, números, acentos y espacios.",
                id="direccion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        resultado = Empleados(**datos_empleado(**cambios)).actualizar_empleado()

        assert resultado == esperado


class TestEliminarEmpleado:

    def test_datos_validos(self):
        try:
            resultado = Empleados(
                **datos_empleado(id_empleado=CEDULA_ELIMINAR)
            ).agregar_empleado()
            assert resultado == "Empleado agregado exitosamente."

            resultado = Empleados(id_empleado=CEDULA_ELIMINAR).eliminar_empleado()

            assert resultado == "Empleado eliminado exitosamente."
            assert Empleados(
                id_empleado=CEDULA_ELIMINAR
            ).verificar_empleado() is False
        finally:
            if Empleados(id_empleado=CEDULA_ELIMINAR).verificar_empleado():
                Empleados(id_empleado=CEDULA_ELIMINAR).eliminar_empleado()

    def test_elimina_las_capacitaciones(self):
        id_especialidad = None
        try:
            resultado = Especialidad(
                nombre_especialidad="Esp Empleado Eliminar",
                descripcion_especialidad=DESCRIPCION_ESPECIALIDAD,
            ).agregar_especialidad()
            id_especialidad = Especialidad(
                nombre_especialidad="Esp Empleado Eliminar"
            ).obtener_id_por_nombre()
            assert resultado == "Especialidad agregada exitosamente."
            assert id_especialidad is not None

            resultado = Empleados(
                **datos_empleado(
                    id_empleado=CEDULA_ELIMINAR_CAPACITACION,
                    especialidades=[id_especialidad],
                )
            ).agregar_empleado()
            assert resultado == "Empleado agregado exitosamente."

            resultado = Empleados(
                id_empleado=CEDULA_ELIMINAR_CAPACITACION
            ).eliminar_empleado()

            assert resultado == "Empleado eliminado exitosamente."
            assert Empleados(
                id_empleado=CEDULA_ELIMINAR_CAPACITACION
            ).verificar_empleado() is False
            assert Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id() is True
        finally:
            if Empleados(
                id_empleado=CEDULA_ELIMINAR_CAPACITACION
            ).verificar_empleado():
                Empleados(
                    id_empleado=CEDULA_ELIMINAR_CAPACITACION
                ).eliminar_empleado()
            if id_especialidad and Especialidad(
                id_especialidad
            ).verificar_especialidad_por_id():
                Especialidad(id_especialidad).eliminar_especialidad()

    def test_empleado_inexistente(self):
        resultado = Empleados(id_empleado=CEDULA_INEXISTENTE).eliminar_empleado()

        assert resultado == (
            f"El empleado con identificador {CEDULA_INEXISTENTE} no existe."
        )

    @pytest.mark.parametrize(
        "cedula, esperado",
        [
            pytest.param(
                "",
                "El campo ID del Empleado no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "12345",
                "El campo ID del Empleado debe tener al menos 6 dígitos.",
                id="id-demasiado-corto",
            ),
            pytest.param(
                "1234567890",
                "El campo ID del Empleado no puede tener más de 9 dígitos.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                "12345a",
                "El campo ID del Empleado solo puede contener números.",
                id="id-no-numerico",
            ),
        ],
    )
    def test_id_invalido(self, cedula, esperado):
        assert Empleados(id_empleado=cedula).eliminar_empleado() == esperado
