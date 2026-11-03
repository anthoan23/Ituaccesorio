"""Pruebas de integración de PersonalDeliveryModel contra MySQL real."""
import random

import pytest

from app.models.personal_delivery import PersonalDeliveryModel


def _cedula_aleatoria() -> str:
    """Genera una cédula numérica de 8 dígitos única para cada test."""
    return str(random.randint(10**7, 10**8 - 1))


def datos_delivery(**cambios):
    datos = {
        "cedula": _cedula_aleatoria(),
        "nombre": "Delivery",
        "apellido": "Prueba",
    }
    datos.update(cambios)
    return datos


# ==================== LISTAR ====================

class TestListarPersonal:

    def test_devuelve_lista(self):
        # El seed deja Personal_delivery vacía; puede que otros tests dejen
        # basura si fallan, por eso solo verifico el tipo.
        resultado = PersonalDeliveryModel().listar_personal()
        assert isinstance(resultado, list)

    def test_incluye_delivery_creado(self):
        datos = datos_delivery()
        try:
            resultado = PersonalDeliveryModel(**datos).agregar_personal()
            assert resultado == "Delivery registrado exitosamente."

            listado = PersonalDeliveryModel().listar_personal()

            fila = next(d for d in listado if d["cedula"] == datos["cedula"])
            assert fila["nombre"] == datos["nombre"]
            assert fila["apellido"] == datos["apellido"]
            assert fila["nombre_completo"] == f"{datos['nombre']} {datos['apellido']}"
        finally:
            if PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe():
                PersonalDeliveryModel(cedula=datos["cedula"]).eliminar_personal()


# ==================== CONSULTAR ====================

class TestObtenerPersonalPorCedula:

    def test_delivery_existente(self):
        datos = datos_delivery()
        try:
            PersonalDeliveryModel(**datos).agregar_personal()

            resultado = PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).obtener_personal_por_cedula()

            assert resultado is not None
            assert resultado["cedula"] == datos["cedula"]
            assert resultado["nombre"] == datos["nombre"]
            assert resultado["apellido"] == datos["apellido"]
        finally:
            if PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe():
                PersonalDeliveryModel(cedula=datos["cedula"]).eliminar_personal()

    def test_delivery_inexistente(self):
        assert PersonalDeliveryModel(
            cedula="99999999"
        ).obtener_personal_por_cedula() is None

    def test_sin_cedula(self):
        assert PersonalDeliveryModel().obtener_personal_por_cedula() is None


# ==================== VERIFICAR ====================

class TestVerificarPersonalExiste:

    def test_delivery_existente(self):
        datos = datos_delivery()
        try:
            PersonalDeliveryModel(**datos).agregar_personal()

            assert PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe() is True
        finally:
            if PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe():
                PersonalDeliveryModel(cedula=datos["cedula"]).eliminar_personal()

    def test_delivery_inexistente(self):
        assert PersonalDeliveryModel(
            cedula="99999999"
        ).verificar_personal_existe() is False

    def test_sin_cedula(self):
        assert PersonalDeliveryModel().verificar_personal_existe() is False


# ==================== AGREGAR ====================

class TestAgregarPersonal:

    def test_datos_validos(self):
        datos = datos_delivery()
        try:
            resultado = PersonalDeliveryModel(**datos).agregar_personal()
            assert resultado == "Delivery registrado exitosamente."

            consultado = PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).obtener_personal_por_cedula()
            assert consultado["nombre"] == datos["nombre"]
            assert consultado["apellido"] == datos["apellido"]
        finally:
            if PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe():
                PersonalDeliveryModel(cedula=datos["cedula"]).eliminar_personal()

    def test_delivery_duplicado(self):
        datos = datos_delivery()
        try:
            PersonalDeliveryModel(**datos).agregar_personal()

            resultado = PersonalDeliveryModel(**datos).agregar_personal()
            assert resultado == f"Ya existe un delivery con cédula {datos['cedula']}."
        finally:
            if PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe():
                PersonalDeliveryModel(cedula=datos["cedula"]).eliminar_personal()

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"cedula": ""},
                "La cédula es obligatoria.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"cedula": "12345"},
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"cedula": "1" * 16},
                "El campo Cédula no puede tener más de 15 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                {"cedula": "12345a"},
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"nombre": ""},
                "El nombre es obligatorio.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"nombre": "N" * 41},
                "El campo Nombre no puede tener más de 40 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"nombre": "Ana #1"},
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                {"apellido": ""},
                "El apellido es obligatorio.",
                id="apellido-vacio",
            ),
            pytest.param(
                {"apellido": "A" * 41},
                "El campo Apellido no puede tener más de 40 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                {"apellido": "Paz #1"},
                "El campo Apellido solo puede contener letras, acentos y espacios.",
                id="apellido-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        resultado = PersonalDeliveryModel(**datos_delivery(**cambios)).agregar_personal()
        assert resultado == esperado


# ==================== ACTUALIZAR ====================

class TestActualizarPersonal:

    def test_datos_validos(self):
        datos = datos_delivery()
        try:
            PersonalDeliveryModel(**datos).agregar_personal()

            resultado = PersonalDeliveryModel(
                cedula=datos["cedula"],
                nombre="Actualizado",
                apellido="Delivery",
            ).actualizar_personal()

            assert resultado == "Delivery actualizado exitosamente."

            consultado = PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).obtener_personal_por_cedula()
            assert consultado["nombre"] == "Actualizado"
            assert consultado["apellido"] == "Delivery"
        finally:
            if PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe():
                PersonalDeliveryModel(cedula=datos["cedula"]).eliminar_personal()

    def test_delivery_inexistente(self):
        resultado = PersonalDeliveryModel(
            cedula="99999999",
            nombre="Nuevo",
            apellido="Delivery",
        ).actualizar_personal()

        assert resultado == "No existe un delivery con cédula 99999999."

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"cedula": ""},
                "La cédula es obligatoria.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"cedula": "12345"},
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"nombre": "N" * 41},
                "El campo Nombre no puede tener más de 40 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"apellido": ""},
                "El apellido es obligatorio.",
                id="apellido-vacio",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        resultado = PersonalDeliveryModel(
            **datos_delivery(**cambios)
        ).actualizar_personal()
        assert resultado == esperado


# ==================== ELIMINAR ====================

class TestEliminarPersonal:

    def test_elimina_sin_entregas(self):
        datos = datos_delivery()
        try:
            PersonalDeliveryModel(**datos).agregar_personal()

            resultado = PersonalDeliveryModel(cedula=datos["cedula"]).eliminar_personal()

            assert resultado == "Delivery eliminado exitosamente."
            assert PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe() is False
        finally:
            if PersonalDeliveryModel(
                cedula=datos["cedula"]
            ).verificar_personal_existe():
                PersonalDeliveryModel(cedula=datos["cedula"]).eliminar_personal()

    def test_delivery_inexistente(self):
        resultado = PersonalDeliveryModel(cedula="99999999").eliminar_personal()
        assert resultado == "No existe un delivery con cédula 99999999."

    @pytest.mark.parametrize(
        "cedula, esperado",
        [
            pytest.param("", "La cédula es obligatoria.", id="cedula-vacia"),
            pytest.param(
                "12345",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                "12345a",
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
        ],
    )
    def test_cedula_invalida(self, cedula, esperado):
        assert PersonalDeliveryModel(cedula=cedula).eliminar_personal() == esperado