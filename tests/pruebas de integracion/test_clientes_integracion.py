"""Pruebas de integración de las clases de Clientes contra MySQL real."""
import pytest

from app.models.clientes import Cliente_juridico, Clientes, Persona_natural
from app.models.database import conectar
from seed_helpers import eliminar_cliente_temporal

# ==================== HELPERS LOCALES (solo para este módulo) ====================


def _crear_cliente_juridico(rif: str, razon_social: str = "Empresa Prueba") -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Cliente (ID_cliente, Direccion_cliente, Celular_cliente, Correo_cliente) "
            "VALUES (%s, %s, %s, %s)",
            (rif, "Barquisimeto", "0414123456", "empresa@mail.com"),
        )
        cursor.execute(
            "INSERT INTO Cliente_juridico (ID_cliente, Razon_social, Rif_cliente) "
            "VALUES (%s, %s, %s)",
            (rif, razon_social, rif),
        )
        db.commit()
        return rif
    finally:
        cursor.close()
        db.close()


def _eliminar_cliente_juridico(rif: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Cliente_juridico WHERE ID_cliente = %s", (rif,))
        cursor.execute("DELETE FROM Cliente WHERE ID_cliente = %s", (rif,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()

# Datos fijos por prueba (rangos reservados para este módulo; no se cruzan
# con el seed 12345678 ni con los rangos de otros módulos).
CEDULA_AGREGAR = "80000001"
CEDULA_DUPLICADO = "80000002"
CEDULA_ACTUALIZAR = "80000003"
CEDULA_ACTUALIZAR_INEXISTENTE = "80000004"
CEDULA_CONSULTAR = "80000005"
CEDULA_DATOS_COMPLETOS = "80000006"
CEDULA_VERIFICAR = "80000007"
CEDULA_DELEGADO = "80000008"
CEDULA_LISTADO = "80000009"
CEDULA_NATURALES = "80000010"
CEDULA_DATOS_BASICOS = "80000011"
CEDULA_DATOS_NOMBRE = "80000012"
CEDULA_ELIMINAR = "80000013"
CEDULA_INEXISTENTE = "80000014"
CEDULA_DUMMY = "80000015"        # para validaciones que nunca insertan
CEDULA_CONSULTA_VACIA = "80000016"

RIF_AGREGAR = "J-80000101-1"
RIF_DUPLICADO = "J-80000102-1"
RIF_ACTUALIZAR = "J-80000103-1"
RIF_CONSULTAR = "J-80000104-1"
RIF_LISTADO = "J-80000105-1"
RIF_NATURALES = "J-80000106-1"
RIF_ELIMINAR = "J-80000107-1"
RIF_INEXISTENTE = "J-80000108-1"
RIF_DUMMY = "J-80000109-1"       # para validaciones que nunca insertan
RIF_CONSULTA_VACIA = "J-80000110-1"


class TestRegistrarPersonaNatural:

    def test_datos_validos(self):
        cedula = CEDULA_AGREGAR
        try:
            resultado = Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Cliente",
                Apellido_cliente="Prueba",
                Telefono_cliente="04141234567",
                Correo_cliente=f"{cedula}@mail.com",
                Direccion_cliente="Barquisimeto",
            ).registrar_persona_natural()

            assert resultado == "El cliente 'Cliente Prueba' se registró exitosamente."
            assert Clientes().verificar_cliente_existe(cedula) is True
        finally:
            eliminar_cliente_temporal(cedula)

    def test_cliente_duplicado(self):
        cedula = CEDULA_DUPLICADO
        try:
            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Cliente",
                Apellido_cliente="Prueba",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()

            resultado = Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Otro",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()

            assert resultado == f"El cliente con cédula '{cedula}' ya existe."
        finally:
            eliminar_cliente_temporal(cedula)

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"Cedula_cliente": ""},
                "La cédula del cliente no puede estar vacía.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"Cedula_cliente": "12345"},
                "La cédula del cliente debe tener 7 u 8 caracteres.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"Cedula_cliente": "123456789"},
                "La cédula del cliente debe tener 7 u 8 caracteres.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                {"Cedula_cliente": "12345a"},
                "La cédula del cliente debe contener solo números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"Nombre_cliente": ""},
                "El nombre del cliente no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"Nombre_cliente": "An"},
                "El nombre del cliente debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                {"Nombre_cliente": "N" * 21},
                "El nombre del cliente no puede exceder los 20 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"Apellido_cliente": ""},
                "El apellido del cliente no puede estar vacío.",
                id="apellido-vacio",
            ),
            pytest.param(
                {"Apellido_cliente": "A" * 21},
                "El apellido del cliente no puede exceder los 20 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                {"Telefono_cliente": ""},
                "El campo Celular no puede estar vacío.",
                id="telefono-vacio",
            ),
            pytest.param(
                {"Telefono_cliente": "0414123456"},
                "El campo Celular debe tener al menos 11 dígitos.",
                id="telefono-demasiado-corto",
            ),
            pytest.param(
                {"Telefono_cliente": "041412345678"},
                "El campo Celular no puede tener más de 11 dígitos.",
                id="telefono-demasiado-largo",
            ),
            pytest.param(
                {"Telefono_cliente": "0412abc1234"},
                "El campo Celular solo puede contener números.",
                id="telefono-no-numerico",
            ),
            pytest.param(
                {"Correo_cliente": "correo-sin-arroba"},
                "El campo correo debe contener el símbolo @.",
                id="correo-invalido",
            ),
            pytest.param(
                {"Direccion_cliente": "D" * 41},
                "El campo Dirección no puede tener más de 40 caracteres.",
                id="direccion-demasiado-larga",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        datos = {
            "Cedula_cliente": CEDULA_DUMMY,
            "Nombre_cliente": "Cliente",
            "Apellido_cliente": "Prueba",
            "Telefono_cliente": "04141234567",
            "Correo_cliente": None,
            "Direccion_cliente": None,
        }
        datos.update(cambios)
        resultado = Persona_natural(**datos).registrar_persona_natural()

        assert resultado == esperado


class TestActualizarPersonaNatural:

    def test_datos_validos(self):
        cedula = CEDULA_ACTUALIZAR
        try:
            resultado = Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Cliente",
                Apellido_cliente="Prueba",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()
            assert "exitosamente" in resultado

            resultado = Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Actualizado",
                Apellido_cliente="Cliente",
                Telefono_cliente="04241234567",
                Correo_cliente="actualizado@mail.com",
                Direccion_cliente="Caracas",
            ).actualizar_persona_natural()

            assert resultado == "El cliente 'Actualizado Cliente' se actualizó exitosamente."
            datos = Clientes().obtener_datos_cliente_completo(cedula)
            assert datos["nombre"] == "Actualizado"
            assert datos["apellido"] == "Cliente"
            assert datos["celular"] == "04241234567"
            assert datos["correo"] == "actualizado@mail.com"
            assert datos["direccion"] == "Caracas"
        finally:
            eliminar_cliente_temporal(cedula)

    def test_cliente_inexistente(self):
        # No valida existencia: ejecuta UPDATE sobre 0 filas y reporta éxito.
        cedula = CEDULA_ACTUALIZAR_INEXISTENTE
        resultado = Persona_natural(
            Cedula_cliente=cedula,
            Nombre_cliente="Fantasma",
            Apellido_cliente="Cliente",
            Telefono_cliente="04141234567",
        ).actualizar_persona_natural()

        assert resultado == "El cliente 'Fantasma Cliente' se actualizó exitosamente."
        assert Clientes().verificar_cliente_existe(cedula) is False

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"Cedula_cliente": ""},
                "La cédula del cliente no puede estar vacía.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"Nombre_cliente": ""},
                "El nombre del cliente no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"Apellido_cliente": ""},
                "El apellido del cliente no puede estar vacío.",
                id="apellido-vacio",
            ),
            pytest.param(
                {"Telefono_cliente": "0414123456"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-invalido",
            ),
            pytest.param(
                {"Correo_cliente": "correo-sin-arroba"},
                "El correo electrónico no es válido.",
                id="correo-invalido",
            ),
            pytest.param(
                {"Direccion_cliente": "D" * 41},
                "La dirección no puede exceder los 40 caracteres.",
                id="direccion-demasiado-larga",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        datos = {
            "Cedula_cliente": CEDULA_DUMMY,
            "Nombre_cliente": "Cliente",
            "Apellido_cliente": "Prueba",
            "Telefono_cliente": "04141234567",
        }
        datos.update(cambios)
        resultado = Persona_natural(**datos).actualizar_persona_natural()

        assert resultado == esperado


class TestRegistrarClienteJuridico:

    def test_datos_validos(self):
        rif = RIF_AGREGAR
        try:
            resultado = Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Empresa Prueba C.A.",
                Telefono_cliente="04141234567",
                Correo_cliente="empresa@mail.com",
                Direccion_cliente="Caracas",
            ).registrar_cliente_juridico()

            assert resultado == "El cliente jurídico 'Empresa Prueba C.A.' se registró exitosamente."
            assert Clientes().verificar_cliente_existe(rif) is True
        finally:
            _eliminar_cliente_juridico(rif)

    def test_cliente_duplicado(self):
        rif = RIF_DUPLICADO
        try:
            Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Empresa Prueba C.A.",
                Telefono_cliente="04141234567",
            ).registrar_cliente_juridico()

            resultado = Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Otra Empresa C.A.",
                Telefono_cliente="04141234567",
            ).registrar_cliente_juridico()

            assert resultado == f"El cliente jurídico con RIF '{rif}' ya existe."
        finally:
            _eliminar_cliente_juridico(rif)

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"Rif_cliente": "12345678"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-sin-formato",
            ),
            pytest.param(
                {"Rif_cliente": "X-12345678-9"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-prefijo-invalido",
            ),
            pytest.param(
                {"Rif_cliente": "J-1234567-9"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-digitos-incompletos",
            ),
            pytest.param(
                {"Razon_social": ""},
                "La razón social del cliente no puede estar vacía.",
                id="razon-social-vacia",
            ),
            pytest.param(
                {"Razon_social": "Empresa @ C.A."},
                "La razón social solo puede contener letras, números, puntos, guiones, espacios y &.",
                id="razon-social-caracteres-invalidos",
            ),
            pytest.param(
                {"Razon_social": "R" * 61},
                "La razón social del cliente no puede exceder los 60 caracteres.",
                id="razon-social-demasiado-larga",
            ),
            pytest.param(
                {"Telefono_cliente": ""},
                "El celular/teléfono es obligatorio.",
                id="telefono-vacio",
            ),
            pytest.param(
                {"Correo_cliente": "correo-sin-arroba"},
                "El correo electrónico no es válido.",
                id="correo-invalido",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        datos = {
            "Rif_cliente": RIF_DUMMY,
            "Razon_social": "Empresa Prueba C.A.",
            "Telefono_cliente": "04141234567",
        }
        datos.update(cambios)
        resultado = Cliente_juridico(**datos).registrar_cliente_juridico()

        assert resultado == esperado


class TestActualizarClienteJuridico:

    def test_datos_validos(self):
        rif = RIF_ACTUALIZAR
        try:
            Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Empresa Prueba C.A.",
                Telefono_cliente="04141234567",
            ).registrar_cliente_juridico()

            resultado = Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Empresa Actualizada C.A.",
                Telefono_cliente="04241234567",
                Correo_cliente="actualizada@mail.com",
                Direccion_cliente="Barquisimeto",
            ).actualizar_cliente_juridico()

            assert resultado == "El cliente jurídico 'Empresa Actualizada C.A.' se actualizó exitosamente."
            datos = Clientes().obtener_datos_cliente_completo(rif)
            assert datos["tipo"] == "juridico"
            assert datos["razon_social"] == "Empresa Actualizada C.A."
            assert datos["celular"] == "04241234567"
        finally:
            _eliminar_cliente_juridico(rif)

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"Rif_cliente": "12345678"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-sin-formato",
            ),
            pytest.param(
                {"Razon_social": ""},
                "La razón social del cliente no puede estar vacía.",
                id="razon-social-vacia",
            ),
            pytest.param(
                {"Telefono_cliente": "0414123456"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-invalido",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        datos = {
            "Rif_cliente": RIF_DUMMY,
            "Razon_social": "Empresa Prueba C.A.",
            "Telefono_cliente": "04141234567",
        }
        datos.update(cambios)
        resultado = Cliente_juridico(**datos).actualizar_cliente_juridico()

        assert resultado == esperado


class TestConsultarClientes:

    def test_obtener_cliente_natural_por_id(self):
        cedula = CEDULA_CONSULTAR
        try:
            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Consultado",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
                Correo_cliente=f"{cedula}@mail.com",
                Direccion_cliente="Barquisimeto",
            ).registrar_persona_natural()

            cliente = Clientes(ID_cliente=cedula).obtener_cliente_por_id()

            assert cliente["id"] == cedula
            assert cliente["nombre"] == "Consultado"
            assert cliente["apellido"] == "Cliente"
            assert cliente["nombre_completo"] == "Consultado Cliente"
            assert cliente["tipo"] == "natural"
        finally:
            eliminar_cliente_temporal(cedula)

    def test_obtener_cliente_natural_inexistente(self):
        assert (
            Clientes(ID_cliente=CEDULA_CONSULTA_VACIA).obtener_cliente_por_id()
            is None
        )
        assert Clientes().obtener_cliente_por_id() is None

    def test_obtener_cliente_juridico_por_rif(self):
        rif = RIF_CONSULTAR
        rif_sin_guiones = rif.replace("-", "")
        try:
            Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Empresa Consultada C.A.",
                Telefono_cliente="04141234567",
            ).registrar_cliente_juridico()

            con_guiones = Clientes(ID_cliente=rif).obtener_cliente_por_id()
            sin_guiones = Clientes(ID_cliente=rif_sin_guiones).obtener_cliente_por_id()

            for cliente in (con_guiones, sin_guiones):
                assert cliente["id"] == rif
                assert cliente["razon_social"] == "Empresa Consultada C.A."
                assert cliente["rif"] == rif
                assert cliente["tipo"] == "juridico"
        finally:
            _eliminar_cliente_juridico(rif)

    def test_obtener_datos_cliente_completo_natural(self):
        cedula = CEDULA_DATOS_COMPLETOS
        try:
            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Completo",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
                Correo_cliente=f"{cedula}@mail.com",
                Direccion_cliente="Barquisimeto",
            ).registrar_persona_natural()

            datos = Clientes().obtener_datos_cliente_completo(cedula)

            assert datos == {
                "id": cedula,
                "direccion": "Barquisimeto",
                "celular": "04141234567",
                "correo": f"{cedula}@mail.com",
                "nombre": "Completo",
                "apellido": "Cliente",
                "razon_social": None,
                "rif": None,
                "tipo": "natural",
            }
        finally:
            eliminar_cliente_temporal(cedula)

    def test_obtener_datos_cliente_completo_inexistente(self):
        assert (
            Clientes().obtener_datos_cliente_completo(CEDULA_CONSULTA_VACIA) is None
        )
        assert Clientes().obtener_datos_cliente_completo(None) is None

    def test_verificar_cliente_existe(self):
        cedula = CEDULA_VERIFICAR
        try:
            assert Clientes().verificar_cliente_existe(cedula) is False

            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Verificado",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()

            assert Clientes().verificar_cliente_existe(cedula) is True
        finally:
            eliminar_cliente_temporal(cedula)

    def test_crear_cliente_delegado(self):
        cedula = CEDULA_DELEGADO
        try:
            resultado = Clientes().crear_cliente(
                cedula, "Delegado", "Cliente", "04141234567"
            )

            assert resultado is True
            assert Clientes().verificar_cliente_existe(cedula) is True
        finally:
            eliminar_cliente_temporal(cedula)


class TestListarClientes:

    def test_incluye_cliente_natural_y_juridico(self):
        cedula = CEDULA_LISTADO
        rif = RIF_LISTADO
        try:
            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Listado",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()
            Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Empresa Listada C.A.",
                Telefono_cliente="04141234567",
            ).registrar_cliente_juridico()

            clientes = Clientes().listar_clientes()

            natural = next((c for c in clientes if c["id"] == cedula), None)
            assert natural is not None
            assert natural["tipo"] == "natural"
            assert natural["nombre"] == "Listado"

            juridico = next((c for c in clientes if c["id"] == rif), None)
            assert juridico is not None
            assert juridico["tipo"] == "juridico"
            assert juridico["razon_social"] == "Empresa Listada C.A."
        finally:
            eliminar_cliente_temporal(cedula)
            _eliminar_cliente_juridico(rif)

    def test_listar_clientes_naturales(self):
        cedula = CEDULA_NATURALES
        rif = RIF_NATURALES
        try:
            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Natural Listado",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()
            Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Empresa Fuera C.A.",
                Telefono_cliente="04141234567",
            ).registrar_cliente_juridico()

            naturales = Clientes().listar_clientes_naturales()

            natural = next((c for c in naturales if c["cedula"] == cedula), None)
            assert natural is not None
            assert natural["nombre_completo"] == "Natural Listado Cliente"
            assert all(c["cedula"] != rif for c in naturales)
        finally:
            eliminar_cliente_temporal(cedula)
            _eliminar_cliente_juridico(rif)


class TestActualizarDatosCliente:

    def test_actualiza_datos_basicos(self):
        cedula = CEDULA_DATOS_BASICOS
        try:
            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Original",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()

            resultado = Clientes().actualizar_datos_cliente(
                cedula,
                celular="04241234567",
                correo="nuevo@mail.com",
                direccion="Caracas",
            )

            assert resultado == "Cliente actualizado exitosamente."
            datos = Clientes().obtener_datos_cliente_completo(cedula)
            assert datos["celular"] == "04241234567"
            assert datos["nombre"] == "Original"  # el nombre no cambia aquí
        finally:
            eliminar_cliente_temporal(cedula)

    def test_actualiza_nombre_y_apellido(self):
        cedula = CEDULA_DATOS_NOMBRE
        try:
            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Original",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()

            resultado = Clientes().actualizar_datos_cliente(
                cedula, nombre="Renombrado", apellido="Nuevo"
            )

            assert resultado == "Cliente actualizado exitosamente."
            datos = Clientes().obtener_datos_cliente_completo(cedula)
            assert datos["nombre"] == "Renombrado"
            assert datos["apellido"] == "Nuevo"
        finally:
            eliminar_cliente_temporal(cedula)

    def test_sin_id(self):
        assert (
            Clientes().actualizar_datos_cliente(None, nombre="X")
            == "El ID del cliente es obligatorio."
        )


class TestEliminarCliente:

    def test_datos_validos(self):
        cedula = CEDULA_ELIMINAR
        try:
            Persona_natural(
                Cedula_cliente=cedula,
                Nombre_cliente="Eliminable",
                Apellido_cliente="Cliente",
                Telefono_cliente="04141234567",
            ).registrar_persona_natural()

            resultado = Clientes(ID_cliente=cedula).eliminar_cliente()

            assert resultado == (
                f"El cliente 'Eliminable Cliente' con ID '{cedula}' "
                "ha sido eliminado exitosamente."
            )
            assert Clientes().verificar_cliente_existe(cedula) is False
        finally:
            eliminar_cliente_temporal(cedula)

    def test_cliente_juridico(self):
        rif = RIF_ELIMINAR
        try:
            Cliente_juridico(
                Rif_cliente=rif,
                Razon_social="Empresa Eliminable C.A.",
                Telefono_cliente="04141234567",
            ).registrar_cliente_juridico()

            resultado = Clientes(ID_cliente=rif).eliminar_cliente()

            assert resultado == (
                f"El cliente 'Empresa Eliminable C.A.' con ID '{rif}' "
                "ha sido eliminado exitosamente."
            )
            assert Clientes().verificar_cliente_existe(rif) is False
        finally:
            _eliminar_cliente_juridico(rif)

    @pytest.mark.parametrize(
        "id_cliente, esperado",
        [
            pytest.param(
                "",
                "El ID del cliente no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "X-12345678-9",
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-sin-formato",
            ),
            pytest.param(
                "12345abc",
                "La cédula del cliente debe contener solo números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                "12345",
                "La cédula del cliente debe tener 7 u 8 caracteres.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                "123456789",
                "La cédula del cliente debe tener 7 u 8 caracteres.",
                id="cedula-demasiado-larga",
            ),
        ],
    )
    def test_id_invalido(self, id_cliente, esperado):
        assert Clientes(ID_cliente=id_cliente).eliminar_cliente() == esperado
