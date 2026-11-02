"""Pruebas unitarias de los modelos de clientes (app.models.clientes).

Cubre la clase base `Clientes` y sus subclases `Persona_natural` y
`Cliente_juridico`. Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en helpers.py.
"""
from unittest.mock import patch

import pytest

from app.models.clientes import Cliente_juridico, Clientes, Persona_natural
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
CEDULA_MINIMA = "1234567"  # 7 dígitos (mínimo)
CEDULA_MAXIMA = "12345678"  # 8 dígitos (máximo)

NOMBRE_MINIMO = "Ana"  # 3 caracteres (mínimo)
NOMBRE_MAXIMO = "N" * 20  # 20 caracteres (máximo)

APELLIDO_MINIMO = "Paz"  # 3 caracteres (mínimo)
APELLIDO_MAXIMO = "A" * 20  # 20 caracteres (máximo)

TELEFONO_VALIDO = "04121234567"  # 11 dígitos exactos

CORREO_VALIDO = "ana.perez@mail.com"

DIRECCION_VALIDA = "Av. Principal"  # 13 caracteres
DIRECCION_MAXIMA = "D" * 40  # 40 caracteres (máximo)

RIF_VALIDO = "J-12345678-9"
RIF_EMPRESA = "E-12345678-9"

RAZON_SOCIAL_MINIMA = "ABC"  # 3 caracteres
RAZON_SOCIAL_MAXIMA = "E" * 60  # 60 caracteres (máximo)


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


def sentencias(cursor):
    """Devuelve la lista de sentencias SQL ejecutadas."""
    return [llamada.args[0] for llamada in cursor.execute.call_args_list]


def datos_persona(**cambios):
    """Devuelve los datos válidos de una persona natural con cambios."""
    datos = {
        "Cedula_cliente": CEDULA_MINIMA,
        "Nombre_cliente": NOMBRE_MINIMO,
        "Apellido_cliente": APELLIDO_MINIMO,
        "Telefono_cliente": TELEFONO_VALIDO,
        "Correo_cliente": CORREO_VALIDO,
        "Direccion_cliente": DIRECCION_VALIDA,
    }
    datos.update(cambios)
    return datos


def persona(**cambios):
    """Crea una Persona_natural con datos válidos salvo los indicados."""
    return Persona_natural(**datos_persona(**cambios))


def datos_juridico(**cambios):
    """Devuelve los datos válidos de un cliente jurídico con cambios."""
    datos = {
        "Id_cliente": RIF_VALIDO,
        "Razon_social": RAZON_SOCIAL_MINIMA,
        "Rif_cliente": RIF_VALIDO,
        "Telefono_cliente": TELEFONO_VALIDO,
        "Correo_cliente": CORREO_VALIDO,
        "Direccion_cliente": DIRECCION_VALIDA,
    }
    datos.update(cambios)
    return datos


def juridico(**cambios):
    """Crea un Cliente_juridico con datos válidos salvo los indicados."""
    return Cliente_juridico(**datos_juridico(**cambios))


class TestConstructores:

    def test_persona_natural_hereda_y_mapea_campos(self):
        cliente = Persona_natural(
            Cedula_cliente=CEDULA_MINIMA,
            Nombre_cliente=NOMBRE_MINIMO,
            Apellido_cliente=APELLIDO_MINIMO,
            Telefono_cliente=TELEFONO_VALIDO,
            Correo_cliente=CORREO_VALIDO,
            Direccion_cliente=DIRECCION_VALIDA,
        )

        assert isinstance(cliente, Clientes)
        assert cliente.ID_cliente == CEDULA_MINIMA
        assert cliente.Cedula_cliente == CEDULA_MINIMA
        assert cliente.Celular_cliente == TELEFONO_VALIDO
        assert cliente.Correo_cliente == CORREO_VALIDO
        assert cliente.Direccion_cliente == DIRECCION_VALIDA

    def test_cliente_juridico_prioriza_id_cliente(self):
        cliente = Cliente_juridico(
            Id_cliente="J-11111111-1",
            Rif_cliente=RIF_VALIDO,
            Razon_social=RAZON_SOCIAL_MINIMA,
        )

        assert isinstance(cliente, Clientes)
        assert cliente.ID_cliente == "J-11111111-1"
        assert cliente.Rif_cliente == RIF_VALIDO

    def test_cliente_juridico_usa_rif_como_codigo(self):
        cliente = Cliente_juridico(
            Rif_cliente=RIF_EMPRESA,
            Razon_social=RAZON_SOCIAL_MINIMA,
        )

        assert cliente.ID_cliente == RIF_EMPRESA
        assert cliente.Rif_cliente == RIF_EMPRESA

    def test_cliente_juridico_acepta_alias_rif(self):
        cliente = Cliente_juridico(
            RIF=RIF_EMPRESA,
            Razon_social=RAZON_SOCIAL_MINIMA,
        )

        assert cliente.ID_cliente == RIF_EMPRESA
        assert cliente.Rif_cliente == RIF_EMPRESA


class TestListarClientes:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id": CEDULA_MINIMA,
                "nombre": "Ana",
                "apellido": "Paz",
                "tipo": "natural",
            },
            {
                "id": RIF_VALIDO,
                "razon_social": "Empresa C.A.",
                "tipo": "juridico",
            },
        ]
        cursor.fetchall.return_value = filas

        resultado = Clientes().listar_clientes()

        assert resultado == filas
        assert "FROM Cliente c" in ultima_sentencia(cursor)
        assert "LEFT JOIN Persona_natural" in ultima_sentencia(cursor)
        assert "LEFT JOIN Cliente_juridico" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args == (ultima_sentencia(cursor),)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Clientes().listar_clientes() == []

    def test_conexion_caida(self, conexion_caída):
        assert Clientes().listar_clientes() == MENSAJE_ERROR_CONEXION

    def test_error_en_consulta(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Clientes().listar_clientes()

        assert resultado == "Error en consulta: fallo simulado"

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Clientes().listar_clientes()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Clientes().listar_clientes()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestEliminarCliente:

    def test_datos_validos_persona_natural(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("Ana Pérez",)
        cursor.fetchall.return_value = []

        resultado = Clientes(ID_cliente=CEDULA_MINIMA).eliminar_cliente()

        assert resultado == (
            f"El cliente 'Ana Pérez' con ID '{CEDULA_MINIMA}' "
            "ha sido eliminado exitosamente."
        )
        assert ultima_sentencia(cursor) == "DELETE FROM Cliente WHERE ID_cliente = %s"
        assert cursor.execute.call_args_list[-1].args[1] == (CEDULA_MINIMA,)
        db.commit.assert_called()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_nombre_desde_cliente_juridico(self, conexion_falsa):
        db, cursor = conexion_falsa
        # No existe en Persona_natural; sí en Cliente_juridico
        cursor.fetchone.side_effect = [None, ("Empresa C.A.",)]
        cursor.fetchall.return_value = []

        resultado = Clientes(ID_cliente=RIF_VALIDO).eliminar_cliente()

        assert resultado == (
            f"El cliente 'Empresa C.A.' con ID '{RIF_VALIDO}' "
            "ha sido eliminado exitosamente."
        )
        assert "SELECT Razon_social FROM Cliente_juridico" in sentencias(cursor)[1]

    def test_sin_registro_de_nombre_usa_el_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]
        cursor.fetchall.return_value = []

        resultado = Clientes(ID_cliente=CEDULA_MINIMA).eliminar_cliente()

        assert resultado == (
            f"El cliente '{CEDULA_MINIMA}' con ID '{CEDULA_MINIMA}' "
            "ha sido eliminado exitosamente."
        )

    @pytest.mark.parametrize(
        "id_cliente",
        [
            pytest.param(CEDULA_MINIMA, id="cedula-minima"),
            pytest.param(CEDULA_MAXIMA, id="cedula-maxima"),
            pytest.param(RIF_VALIDO, id="rif-juridico"),
            pytest.param(RIF_EMPRESA, id="rif-empresa"),
        ],
    )
    def test_limites_de_id(self, conexion_falsa, id_cliente):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("Cliente",)
        cursor.fetchall.return_value = []

        resultado = Clientes(ID_cliente=id_cliente).eliminar_cliente()

        assert "ha sido eliminado exitosamente" in resultado
        assert cursor.execute.call_args_list[-1].args[1] == (id_cliente,)

    def test_elimina_ventas_relacionadas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("Ana",)
        cursor.fetchall.return_value = [("FAC-001",), ("FAC-002",)]

        resultado = Clientes(ID_cliente=CEDULA_MINIMA).eliminar_cliente()

        assert "ha sido eliminado exitosamente" in resultado
        pagos = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "DELETE FROM Metodo_pago" in llamada.args[0]
        ]
        detalles = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "DELETE FROM Detalle_venta" in llamada.args[0]
        ]
        assert pagos == [("FAC-001",), ("FAC-002",)]
        assert detalles == [("FAC-001",), ("FAC-002",)]

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("Ana Pérez",)
        cursor.fetchall.return_value = []

        with patch("app.models.clientes.Bitacora") as bitacora_clase:
            resultado = Clientes(
                ID_cliente=CEDULA_MINIMA, usuario_id="USR-001"
            ).eliminar_cliente()

        assert "ha sido eliminado exitosamente" in resultado
        bitacora_clase.assert_called_once_with(
            accion="Eliminar cliente",
            descripcion=(
                f"Se eliminó el cliente ID: {CEDULA_MINIMA} - Nombre: Ana Pérez"
            ),
            usuario_id="USR-001",
            modulo_nombre="Clientes",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()

    @pytest.mark.parametrize(
        "id_cliente, esperado",
        [
            pytest.param(
                "",
                "El ID del cliente no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "   ",
                "El ID del cliente no puede estar vacío.",
                id="id-solo-espacios",
            ),
            pytest.param(
                "J-1234567-9",
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-incompleto",
            ),
            pytest.param(
                "V-12345678-9",
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-letra-invalida",
            ),
            pytest.param(
                "J123456789",
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-sin-guiones",
            ),
            pytest.param(
                "j-12345678-9",
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-en-minusculas",
            ),
            pytest.param(
                "12345678#",
                "La cédula del cliente debe contener solo números.",
                id="cedula-caracter-invalido",
            ),
            pytest.param(
                "123456",
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
    def test_id_invalido_no_toca_la_bd(self, conexion_falsa, id_cliente, esperado):
        db, cursor = conexion_falsa

        resultado = Clientes(ID_cliente=id_cliente).eliminar_cliente()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Clientes(ID_cliente=CEDULA_MINIMA).eliminar_cliente()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("Ana",)
        cursor.fetchall.return_value = []
        # 1ª: nombre; 2ª: ventas; 3ª: DELETE que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        resultado = Clientes(ID_cliente=CEDULA_MINIMA).eliminar_cliente()

        assert resultado == "Error al eliminar cliente: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_error_clave_foranea_con_detalle(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("Ana",)
        cursor.fetchall.return_value = []
        cursor.execute.side_effect = [
            None,
            None,
            Exception(
                "Cannot delete or update a parent row: a foreign key constraint "
                "fails (`ituaccesoriobd`.`venta`, CONSTRAINT `venta_ibfk_1` "
                "FOREIGN KEY (`ID_cliente`) REFERENCES `cliente` (`ID_cliente`))"
            ),
        ]

        resultado = Clientes(ID_cliente=CEDULA_MINIMA).eliminar_cliente()

        assert resultado == (
            "No se puede eliminar el cliente porque tiene registros "
            "relacionados en la tabla 'cliente' (columna 'ID_cliente')."
        )
        db.rollback.assert_called_once()

    def test_error_clave_foranea_sin_detalle(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("Ana",)
        cursor.fetchall.return_value = []
        cursor.execute.side_effect = [
            None,
            None,
            Exception("foreign key constraint fails sin detalles"),
        ]

        resultado = Clientes(ID_cliente=CEDULA_MINIMA).eliminar_cliente()

        assert resultado == (
            "No se puede eliminar el cliente porque tiene registros "
            "relacionados en otras tablas."
        )
        db.rollback.assert_called_once()


class TestObtenerClientePorId:

    def test_persona_natural_encontrada(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "id": CEDULA_MINIMA,
            "nombre": "Ana",
            "apellido": "Paz",
            "tipo": "natural",
        }
        cursor.fetchone.return_value = esperado

        resultado = Clientes().obtener_cliente_por_id(CEDULA_MINIMA)

        assert resultado == esperado
        assert "INNER JOIN Persona_natural" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA, CEDULA_MINIMA)

    def test_usa_id_de_la_instancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": CEDULA_MINIMA}

        resultado = Clientes(ID_cliente=CEDULA_MINIMA).obtener_cliente_por_id()

        assert resultado == {"id": CEDULA_MINIMA}
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA, CEDULA_MINIMA)

    def test_argumento_tiene_prioridad_sobre_el_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": CEDULA_MAXIMA}

        Clientes(ID_cliente=CEDULA_MINIMA).obtener_cliente_por_id(CEDULA_MAXIMA)

        assert cursor.execute.call_args.args[1] == (CEDULA_MAXIMA, CEDULA_MAXIMA)

    def test_cliente_juridico_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": RIF_VALIDO, "tipo": "juridico"}
        cursor.fetchone.side_effect = [None, esperado]

        resultado = Clientes().obtener_cliente_por_id(RIF_VALIDO)

        assert resultado == esperado
        assert "INNER JOIN Cliente_juridico" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            "J123456789",
            RIF_VALIDO,
            RIF_VALIDO,
            "J123456789",
        )

    def test_rif_normaliza_guiones_y_mayusculas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, {"id": RIF_VALIDO}]

        Clientes().obtener_cliente_por_id("J-12345678-9")

        primera, segunda = cursor.execute.call_args_list
        assert primera.args[1] == ("J123456789", "J-12345678-9")
        assert segunda.args[1] == (
            "J123456789",
            "J-12345678-9",
            "J-12345678-9",
            "J123456789",
        )

    def test_rif_en_minusculas_se_normaliza(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        Clientes().obtener_cliente_por_id("j-12345678-9")

        primera = cursor.execute.call_args_list[0]
        assert primera.args[1] == ("J123456789", "j-12345678-9")

    def test_sin_id_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Clientes().obtener_cliente_por_id() is None
        cursor.execute.assert_not_called()

    def test_cliente_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        assert Clientes().obtener_cliente_por_id(CEDULA_MINIMA) is None

    def test_conexion_caida(self, conexion_caída):
        assert Clientes().obtener_cliente_por_id(CEDULA_MINIMA) is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Clientes().obtener_cliente_por_id(CEDULA_MINIMA) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": CEDULA_MINIMA}

        Clientes().obtener_cliente_por_id(CEDULA_MINIMA)

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": CEDULA_MINIMA}

        Clientes().obtener_cliente_por_id(CEDULA_MINIMA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerDatosClienteCompleto:

    def test_persona_natural(self, conexion_falsa):
        db, cursor = conexion_falsa
        base = {
            "ID_cliente": CEDULA_MINIMA,
            "Direccion_cliente": DIRECCION_VALIDA,
            "Celular_cliente": TELEFONO_VALIDO,
            "Correo_cliente": CORREO_VALIDO,
        }
        persona = {"Nombre_cliente": "Ana", "Apellido_cliente": "Paz"}
        cursor.fetchone.side_effect = [base, persona]

        resultado = Clientes().obtener_datos_cliente_completo(CEDULA_MINIMA)

        assert resultado == {
            "id": CEDULA_MINIMA,
            "direccion": DIRECCION_VALIDA,
            "celular": TELEFONO_VALIDO,
            "correo": CORREO_VALIDO,
            "nombre": "Ana",
            "apellido": "Paz",
            "razon_social": None,
            "rif": None,
            "tipo": "natural",
        }
        assert "FROM Persona_natural" in sentencias(cursor)[1]

    def test_cliente_juridico(self, conexion_falsa):
        db, cursor = conexion_falsa
        base = {
            "ID_cliente": RIF_VALIDO,
            "Direccion_cliente": DIRECCION_VALIDA,
            "Celular_cliente": TELEFONO_VALIDO,
            "Correo_cliente": CORREO_VALIDO,
        }
        juridico = {"Razon_social": "Empresa C.A.", "Rif_cliente": RIF_VALIDO}
        cursor.fetchone.side_effect = [base, None, juridico]

        resultado = Clientes().obtener_datos_cliente_completo(RIF_VALIDO)

        assert resultado == {
            "id": RIF_VALIDO,
            "direccion": DIRECCION_VALIDA,
            "celular": TELEFONO_VALIDO,
            "correo": CORREO_VALIDO,
            "nombre": None,
            "apellido": None,
            "razon_social": "Empresa C.A.",
            "rif": RIF_VALIDO,
            "tipo": "juridico",
        }

    def test_tipo_desconocido(self, conexion_falsa):
        db, cursor = conexion_falsa
        base = {
            "ID_cliente": CEDULA_MINIMA,
            "Direccion_cliente": None,
            "Celular_cliente": None,
            "Correo_cliente": None,
        }
        cursor.fetchone.side_effect = [base, None, None]

        resultado = Clientes().obtener_datos_cliente_completo(CEDULA_MINIMA)

        assert resultado == {
            "id": CEDULA_MINIMA,
            "direccion": None,
            "celular": None,
            "correo": None,
            "nombre": None,
            "apellido": None,
            "razon_social": None,
            "rif": None,
            "tipo": "desconocido",
        }

    def test_encuentra_en_la_segunda_consulta_sin_guiones(self, conexion_falsa):
        db, cursor = conexion_falsa
        base = {
            "ID_cliente": RIF_VALIDO,
            "Direccion_cliente": None,
            "Celular_cliente": None,
            "Correo_cliente": None,
        }
        persona = {"Nombre_cliente": "Ana", "Apellido_cliente": "Paz"}
        # 1ª: con guiones (no); 2ª: sin guiones (sí); 3ª: persona
        cursor.fetchone.side_effect = [None, base, persona]

        resultado = Clientes().obtener_datos_cliente_completo(RIF_VALIDO)

        assert resultado["tipo"] == "natural"
        selects = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if llamada.args[0] == "SELECT * FROM Cliente WHERE ID_cliente = %s"
        ]
        # La primera consulta usa el ID con guiones y la segunda el normalizado
        assert selects[0] == (RIF_VALIDO,)
        assert selects[1] == ("J123456789",)

    def test_encuentra_por_rif_sin_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        base = {
            "ID_cliente": RIF_VALIDO,
            "Direccion_cliente": None,
            "Celular_cliente": None,
            "Correo_cliente": None,
        }
        persona = {"Nombre_cliente": "Ana", "Apellido_cliente": "Paz"}
        cursor.fetchone.side_effect = [None, None, base, persona]

        resultado = Clientes().obtener_datos_cliente_completo("J-99999999-9")

        assert resultado["tipo"] == "natural"
        llamada_rif = llamada_con(cursor, "j.Rif_cliente = %s")
        assert llamada_rif.args[1] == ("J-99999999-9", "J999999999")

    def test_cliente_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        assert Clientes().obtener_datos_cliente_completo(CEDULA_MINIMA) is None

    def test_sin_id_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Clientes().obtener_datos_cliente_completo() is None
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Clientes().obtener_datos_cliente_completo(CEDULA_MINIMA) is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Clientes().obtener_datos_cliente_completo(CEDULA_MINIMA) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        base = {"ID_cliente": CEDULA_MINIMA}
        cursor.fetchone.side_effect = [base, None, None]

        Clientes().obtener_datos_cliente_completo(CEDULA_MINIMA)

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        base = {"ID_cliente": CEDULA_MINIMA}
        cursor.fetchone.side_effect = [base, None, None]

        Clientes().obtener_datos_cliente_completo(CEDULA_MINIMA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestCrearCliente:

    @pytest.mark.parametrize(
        "campo, valor",
        [
            pytest.param("cliente_id", None, id="id-none"),
            pytest.param("cliente_id", "", id="id-vacio"),
            pytest.param("nombre", None, id="nombre-none"),
            pytest.param("nombre", "", id="nombre-vacio"),
            pytest.param("apellido", "", id="apellido-vacio"),
            pytest.param("celular", None, id="celular-none"),
            pytest.param("celular", "", id="celular-vacio"),
        ],
    )
    def test_datos_incompletos_devuelven_false(
        self, conexion_falsa, campo, valor
    ):
        db, cursor = conexion_falsa
        datos = {
            "cliente_id": CEDULA_MINIMA,
            "nombre": NOMBRE_MINIMO,
            "apellido": APELLIDO_MINIMO,
            "celular": TELEFONO_VALIDO,
        }
        datos[campo] = valor

        resultado = Clientes().crear_cliente(**datos)

        assert resultado is False
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Clientes().crear_cliente(
            CEDULA_MINIMA, NOMBRE_MINIMO, APELLIDO_MINIMO, TELEFONO_VALIDO
        )

        assert resultado is True
        assert llamada_con(cursor, "INSERT INTO Cliente (").args[1] == (
            CEDULA_MINIMA,
            None,
            TELEFONO_VALIDO,
            None,
        )
        assert llamada_con(cursor, "INSERT INTO Persona_natural").args[1] == (
            CEDULA_MINIMA,
            APELLIDO_MINIMO,
            NOMBRE_MINIMO,
        )
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_con_correo_y_direccion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Clientes().crear_cliente(
            CEDULA_MAXIMA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            TELEFONO_VALIDO,
            CORREO_VALIDO,
            DIRECCION_VALIDA,
        )

        assert resultado is True
        assert llamada_con(cursor, "INSERT INTO Cliente (").args[1] == (
            CEDULA_MAXIMA,
            DIRECCION_VALIDA,
            TELEFONO_VALIDO,
            CORREO_VALIDO,
        )

    def test_convierte_el_id_a_texto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Clientes().crear_cliente(
            1234567, NOMBRE_MINIMO, APELLIDO_MINIMO, TELEFONO_VALIDO
        )

        assert resultado is True
        assert llamada_con(cursor, "INSERT INTO Persona_natural").args[1][0] == (
            "1234567"
        )

    def test_cliente_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Clientes().crear_cliente(
            CEDULA_MINIMA, NOMBRE_MINIMO, APELLIDO_MINIMO, TELEFONO_VALIDO
        )

        assert resultado is False
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_datos_invalidos_devuelven_false(self, conexion_falsa):
        db, cursor = conexion_falsa

        # Correo inválido: la validación ocurre antes de tocar la BD
        resultado = Clientes().crear_cliente(
            CEDULA_MINIMA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            TELEFONO_VALIDO,
            correo="ana@mail",
        )

        assert resultado is False
        cursor.execute.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.clientes.Bitacora") as bitacora_clase:
            resultado = Clientes(usuario_id="USR-001").crear_cliente(
                CEDULA_MINIMA, NOMBRE_MINIMO, APELLIDO_MINIMO, TELEFONO_VALIDO
            )

        assert resultado is True
        bitacora_clase.assert_called_once_with(
            accion="Registrar cliente natural",
            descripcion=(
                f"Se registró el cliente natural: {CEDULA_MINIMA} - "
                f"{NOMBRE_MINIMO} {APELLIDO_MINIMO}"
            ),
            usuario_id="USR-001",
            modulo_nombre="Clientes",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()

    def test_conexion_caida(self, conexion_caída):
        resultado = Clientes().crear_cliente(
            CEDULA_MINIMA, NOMBRE_MINIMO, APELLIDO_MINIMO, TELEFONO_VALIDO
        )

        assert resultado is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª: verificar duplicado; 2ª: INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Clientes().crear_cliente(
            CEDULA_MINIMA, NOMBRE_MINIMO, APELLIDO_MINIMO, TELEFONO_VALIDO
        )

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestVerificarClienteExiste:

    def test_cliente_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Clientes().verificar_cliente_existe(CEDULA_MINIMA) is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Cliente WHERE ID_cliente = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA,)

    def test_cliente_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Clientes().verificar_cliente_existe(CEDULA_MINIMA) is False

    def test_convierte_el_id_a_texto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Clientes().verificar_cliente_existe(1234567)

        assert cursor.execute.call_args.args[1] == ("1234567",)

    def test_conexion_caida(self, conexion_caída):
        assert Clientes().verificar_cliente_existe(CEDULA_MINIMA) is False

    def test_error_de_bd_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Clientes().verificar_cliente_existe(CEDULA_MINIMA) is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Clientes().verificar_cliente_existe(CEDULA_MINIMA)

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Clientes().verificar_cliente_existe(CEDULA_MINIMA)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarClientesNaturales:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "cedula": CEDULA_MINIMA,
                "nombre_completo": "Ana Paz",
                "nombre": "Ana",
                "apellido": "Paz",
                "celular": TELEFONO_VALIDO,
                "correo": CORREO_VALIDO,
                "direccion": DIRECCION_VALIDA,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Clientes().listar_clientes_naturales()

        assert resultado == filas
        assert "INNER JOIN Persona_natural" in ultima_sentencia(cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Clientes().listar_clientes_naturales() == []

    def test_conexion_caida(self, conexion_caída):
        assert Clientes().listar_clientes_naturales() is None

    def test_error_de_bd_devuelve_none(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Clientes().listar_clientes_naturales() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Clientes().listar_clientes_naturales()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Clientes().listar_clientes_naturales()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestActualizarDatosCliente:

    def test_datos_validos_completos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Clientes().actualizar_datos_cliente(
            CEDULA_MINIMA,
            nombre=NOMBRE_MINIMO,
            apellido=APELLIDO_MINIMO,
            celular=TELEFONO_VALIDO,
            correo=CORREO_VALIDO,
            direccion=DIRECCION_VALIDA,
        )

        assert resultado == "Cliente actualizado exitosamente."
        assert llamada_con(cursor, "UPDATE Cliente SET").args[1] == [
            TELEFONO_VALIDO,
            CORREO_VALIDO,
            DIRECCION_VALIDA,
            CEDULA_MINIMA,
        ]
        assert llamada_con(cursor, "UPDATE Persona_natural SET").args[1] == [
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CEDULA_MINIMA,
        ]
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_solo_datos_de_contacto(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Clientes().actualizar_datos_cliente(
            CEDULA_MINIMA, celular=TELEFONO_VALIDO
        )

        assert resultado == "Cliente actualizado exitosamente."
        assert llamada_con(cursor, "UPDATE Cliente SET").args[1] == [
            TELEFONO_VALIDO,
            CEDULA_MINIMA,
        ]
        assert not any("Persona_natural" in sql for sql in sentencias(cursor))

    def test_solo_nombre_con_persona_existente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Clientes().actualizar_datos_cliente(
            CEDULA_MINIMA, nombre=NOMBRE_MAXIMO
        )

        assert resultado == "Cliente actualizado exitosamente."
        assert llamada_con(cursor, "UPDATE Persona_natural SET").args[1] == [
            NOMBRE_MAXIMO,
            CEDULA_MINIMA,
        ]
        assert not any("UPDATE Cliente SET" in sql for sql in sentencias(cursor))

    def test_solo_nombre_con_persona_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Clientes().actualizar_datos_cliente(
            CEDULA_MINIMA, nombre=NOMBRE_MINIMO
        )

        assert resultado == "Cliente actualizado exitosamente."
        assert not any("UPDATE Persona_natural SET" in sql for sql in sentencias(cursor))
        db.commit.assert_called_once()

    def test_sin_datos_no_ejecuta_sentencias(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Clientes().actualizar_datos_cliente(CEDULA_MINIMA)

        assert resultado == "Cliente actualizado exitosamente."
        cursor.execute.assert_not_called()
        db.commit.assert_called_once()

    def test_campos_vacios_se_ignoran(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Clientes().actualizar_datos_cliente(
            CEDULA_MINIMA,
            nombre="",
            apellido="",
            celular="",
            correo="",
            direccion="",
        )

        assert resultado == "Cliente actualizado exitosamente."
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "cliente_id",
        [
            pytest.param(None, id="id-none"),
            pytest.param("", id="id-vacio"),
            pytest.param(0, id="id-cero"),
        ],
    )
    def test_sin_id_devuelve_error(self, conexion_falsa, cliente_id):
        db, cursor = conexion_falsa

        resultado = Clientes().actualizar_datos_cliente(cliente_id, nombre="Ana")

        assert resultado == "El ID del cliente es obligatorio."
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Clientes().actualizar_datos_cliente(
            CEDULA_MINIMA, nombre=NOMBRE_MINIMO
        )

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª: UPDATE Cliente; 2ª: UPDATE Persona_natural que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Clientes().actualizar_datos_cliente(
            CEDULA_MINIMA,
            nombre=NOMBRE_MINIMO,
            celular=TELEFONO_VALIDO,
        )

        assert resultado == "Error al actualizar cliente: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.clientes.Bitacora") as bitacora_clase:
            resultado = Clientes(usuario_id="USR-001").actualizar_datos_cliente(
                CEDULA_MINIMA, celular=TELEFONO_VALIDO
            )

        assert resultado == "Cliente actualizado exitosamente."
        bitacora_clase.assert_called_once_with(
            accion="Actualizar cliente",
            descripcion=f"Se actualizó el cliente ID: {CEDULA_MINIMA}",
            usuario_id="USR-001",
            modulo_nombre="Clientes",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()


class TestRegistrarPersonaNatural:

    def test_datos_validos_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = persona(
            Correo_cliente=None, Direccion_cliente=None
        ).registrar_persona_natural()

        assert resultado == "El cliente 'Ana Paz' se registró exitosamente."
        assert llamada_con(cursor, "INSERT INTO Cliente (").args[1] == (
            CEDULA_MINIMA,
            None,
            TELEFONO_VALIDO,
            None,
        )
        assert llamada_con(cursor, "INSERT INTO Persona_natural").args[1] == (
            CEDULA_MINIMA,
            APELLIDO_MINIMO,
            NOMBRE_MINIMO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_datos_validos_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = persona(
            Cedula_cliente=CEDULA_MAXIMA,
            Nombre_cliente=NOMBRE_MAXIMO,
            Apellido_cliente=APELLIDO_MAXIMO,
            Direccion_cliente=DIRECCION_MAXIMA,
        ).registrar_persona_natural()

        assert resultado == (
            f"El cliente '{NOMBRE_MAXIMO} {APELLIDO_MAXIMO}' "
            "se registró exitosamente."
        )
        assert llamada_con(cursor, "INSERT INTO Persona_natural").args[1] == (
            CEDULA_MAXIMA,
            APELLIDO_MAXIMO,
            NOMBRE_MAXIMO,
        )
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"Cedula_cliente": ""},
                "La cédula del cliente no puede estar vacía.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"Cedula_cliente": "   "},
                "La cédula del cliente no puede estar vacía.",
                id="cedula-solo-espacios",
            ),
            pytest.param(
                {"Apellido_cliente": ""},
                "El apellido del cliente no puede estar vacío.",
                id="apellido-vacio",
            ),
            pytest.param(
                {"Apellido_cliente": "   "},
                "El apellido del cliente no puede estar vacío.",
                id="apellido-solo-espacios",
            ),
            pytest.param(
                {"Nombre_cliente": ""},
                "El nombre del cliente no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"Nombre_cliente": "   "},
                "El nombre del cliente no puede estar vacío.",
                id="nombre-solo-espacios",
            ),
            pytest.param(
                {"Cedula_cliente": "123456a"},
                "La cédula del cliente debe contener solo números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"Cedula_cliente": "123456"},
                "La cédula del cliente debe tener 7 u 8 caracteres.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"Cedula_cliente": "123456789"},
                "La cédula del cliente debe tener 7 u 8 caracteres.",
                id="cedula-demasiado-larga",
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
                {"Apellido_cliente": "A" * 21},
                "El apellido del cliente no puede exceder los 20 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                {"Telefono_cliente": ""},
                "El celular/teléfono es obligatorio.",
                id="telefono-vacio",
            ),
            pytest.param(
                {"Telefono_cliente": None},
                "El celular/teléfono es obligatorio.",
                id="telefono-none",
            ),
            pytest.param(
                {"Telefono_cliente": "0412123456"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-demasiado-corto",
            ),
            pytest.param(
                {"Telefono_cliente": "041212345678"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-demasiado-largo",
            ),
            pytest.param(
                {"Telefono_cliente": "0412abc4567"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-no-numerico",
            ),
            pytest.param(
                {"Correo_cliente": "ana@mail"},
                "El correo electrónico no es válido.",
                id="correo-sin-punto",
            ),
            pytest.param(
                {"Correo_cliente": "anamail.com"},
                "El correo electrónico no es válido.",
                id="correo-sin-arroba",
            ),
            pytest.param(
                {"Direccion_cliente": "D" * 41},
                "La dirección no puede exceder los 40 caracteres.",
                id="direccion-demasiado-larga",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(self, conexion_falsa, cambios, esperado):
        db, cursor = conexion_falsa

        resultado = persona(**cambios).registrar_persona_natural()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_cliente_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = persona().registrar_persona_natural()

        assert resultado == (
            f"El cliente con cédula '{CEDULA_MINIMA}' ya existe."
        )
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = persona().registrar_persona_natural()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª: verificar duplicado; 2ª: INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = persona().registrar_persona_natural()

        assert resultado == "Error al registrar cliente: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.clientes.Bitacora") as bitacora_clase:
            resultado = persona(usuario_id="USR-001").registrar_persona_natural()

        assert resultado == "El cliente 'Ana Paz' se registró exitosamente."
        bitacora_clase.assert_called_once_with(
            accion="Registrar cliente natural",
            descripcion=(
                f"Se registró el cliente natural: {CEDULA_MINIMA} - "
                f"{NOMBRE_MINIMO} {APELLIDO_MINIMO}"
            ),
            usuario_id="USR-001",
            modulo_nombre="Clientes",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()


class TestActualizarPersonaNatural:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = persona().actualizar_persona_natural()

        assert resultado == "El cliente 'Ana Paz' se actualizó exitosamente."
        assert llamada_con(cursor, "UPDATE Cliente SET").args[1] == (
            DIRECCION_VALIDA,
            TELEFONO_VALIDO,
            CORREO_VALIDO,
            CEDULA_MINIMA,
        )
        assert llamada_con(cursor, "UPDATE Persona_natural SET").args[1] == (
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CEDULA_MINIMA,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_telefono_opcional_vacio(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = persona(Telefono_cliente="").actualizar_persona_natural()

        assert resultado == "El cliente 'Ana Paz' se actualizó exitosamente."
        assert llamada_con(cursor, "UPDATE Cliente SET").args[1][1] is None
        db.commit.assert_called_once()

    def test_telefono_opcional_none(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = persona(Telefono_cliente=None).actualizar_persona_natural()

        assert resultado == "El cliente 'Ana Paz' se actualizó exitosamente."
        assert llamada_con(cursor, "UPDATE Cliente SET").args[1][1] is None

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = persona(
            Cedula_cliente=CEDULA_MAXIMA,
            Nombre_cliente=NOMBRE_MAXIMO,
            Apellido_cliente=APELLIDO_MAXIMO,
            Direccion_cliente=DIRECCION_MAXIMA,
        ).actualizar_persona_natural()

        assert resultado == (
            f"El cliente '{NOMBRE_MAXIMO} {APELLIDO_MAXIMO}' "
            "se actualizó exitosamente."
        )
        assert llamada_con(cursor, "UPDATE Persona_natural SET").args[1] == (
            NOMBRE_MAXIMO,
            APELLIDO_MAXIMO,
            CEDULA_MAXIMA,
        )

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"Cedula_cliente": ""},
                "La cédula del cliente no puede estar vacía.",
                id="cedula-vacia",
            ),
            pytest.param(
                {"Apellido_cliente": ""},
                "El apellido del cliente no puede estar vacío.",
                id="apellido-vacio",
            ),
            pytest.param(
                {"Nombre_cliente": ""},
                "El nombre del cliente no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"Cedula_cliente": "123456a"},
                "La cédula del cliente debe contener solo números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"Cedula_cliente": "123456"},
                "La cédula del cliente debe tener 7 u 8 caracteres.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"Cedula_cliente": "123456789"},
                "La cédula del cliente debe tener 7 u 8 caracteres.",
                id="cedula-demasiado-larga",
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
                {"Apellido_cliente": "A" * 21},
                "El apellido del cliente no puede exceder los 20 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                {"Telefono_cliente": "0412123456"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-demasiado-corto",
            ),
            pytest.param(
                {"Telefono_cliente": "041212345678"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-demasiado-largo",
            ),
            pytest.param(
                {"Correo_cliente": "ana@mail"},
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
    def test_datos_invalidos_no_tocan_la_bd(self, conexion_falsa, cambios, esperado):
        db, cursor = conexion_falsa

        resultado = persona(**cambios).actualizar_persona_natural()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = persona().actualizar_persona_natural()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª: UPDATE Cliente; 2ª: UPDATE Persona_natural que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = persona().actualizar_persona_natural()

        assert resultado == "Error al actualizar cliente: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.clientes.Bitacora") as bitacora_clase:
            resultado = persona(usuario_id="USR-001").actualizar_persona_natural()

        assert resultado == "El cliente 'Ana Paz' se actualizó exitosamente."
        bitacora_clase.assert_called_once_with(
            accion="Actualizar cliente natural",
            descripcion=(
                f"Se actualizó el cliente natural: {CEDULA_MINIMA} - "
                f"{NOMBRE_MINIMO} {APELLIDO_MINIMO}"
            ),
            usuario_id="USR-001",
            modulo_nombre="Clientes",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()


class TestRegistrarClienteJuridico:

    def test_datos_validos_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = juridico(
            Correo_cliente=None, Direccion_cliente=None
        ).registrar_cliente_juridico()

        assert resultado == (
            f"El cliente jurídico '{RAZON_SOCIAL_MINIMA}' se registró exitosamente."
        )
        assert llamada_con(cursor, "INSERT INTO Cliente (").args[1] == (
            RIF_VALIDO,
            None,
            TELEFONO_VALIDO,
            None,
        )
        assert llamada_con(cursor, "INSERT INTO Cliente_juridico").args[1] == (
            RIF_VALIDO,
            RAZON_SOCIAL_MINIMA,
            RIF_VALIDO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_razon_social_maxima(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = juridico(
            Razon_social=RAZON_SOCIAL_MAXIMA
        ).registrar_cliente_juridico()

        assert resultado == (
            f"El cliente jurídico '{RAZON_SOCIAL_MAXIMA}' se registró exitosamente."
        )
        assert llamada_con(cursor, "INSERT INTO Cliente_juridico").args[1] == (
            RIF_VALIDO,
            RAZON_SOCIAL_MAXIMA,
            RIF_VALIDO,
        )

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"Rif_cliente": ""},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-vacio",
            ),
            pytest.param(
                {"Rif_cliente": None},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-none",
            ),
            pytest.param(
                {"Rif_cliente": "J-1234567-9"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-incompleto",
            ),
            pytest.param(
                {"Rif_cliente": "V-12345678-9"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-letra-invalida",
            ),
            pytest.param(
                {"Rif_cliente": "J123456789"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-sin-guiones",
            ),
            pytest.param(
                {"Rif_cliente": "j-12345678-9"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-en-minusculas",
            ),
            pytest.param(
                {"Razon_social": ""},
                "La razón social del cliente no puede estar vacía.",
                id="razon-social-vacia",
            ),
            pytest.param(
                {"Razon_social": "   "},
                "La razón social del cliente no puede estar vacía.",
                id="razon-social-solo-espacios",
            ),
            pytest.param(
                {"Razon_social": "Empresa @ C.A."},
                "La razón social solo puede contener letras, números, puntos, "
                "guiones, espacios y &.",
                id="razon-social-caracteres-invalidos",
            ),
            pytest.param(
                {"Razon_social": "E" * 61},
                "La razón social del cliente no puede exceder los 60 caracteres.",
                id="razon-social-demasiado-larga",
            ),
            pytest.param(
                {"Telefono_cliente": ""},
                "El celular/teléfono es obligatorio.",
                id="telefono-vacio",
            ),
            pytest.param(
                {"Telefono_cliente": "0412123456"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-demasiado-corto",
            ),
            pytest.param(
                {"Telefono_cliente": "0412abc4567"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-no-numerico",
            ),
            pytest.param(
                {"Correo_cliente": "ana@mail"},
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
    def test_datos_invalidos_no_tocan_la_bd(self, conexion_falsa, cambios, esperado):
        db, cursor = conexion_falsa

        resultado = juridico(**cambios).registrar_cliente_juridico()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_cliente_juridico_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = juridico().registrar_cliente_juridico()

        assert resultado == (
            f"El cliente jurídico con RIF '{RIF_VALIDO}' ya existe."
        )
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = juridico().registrar_cliente_juridico()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª: verificar duplicado; 2ª: INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = juridico().registrar_cliente_juridico()

        assert resultado == "Error al registrar cliente jurídico: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.clientes.Bitacora") as bitacora_clase:
            resultado = juridico(usuario_id="USR-001").registrar_cliente_juridico()

        assert resultado == (
            f"El cliente jurídico '{RAZON_SOCIAL_MINIMA}' se registró exitosamente."
        )
        bitacora_clase.assert_called_once_with(
            accion="Registrar cliente jurídico",
            descripcion=(
                f"Se registró el cliente jurídico: {RIF_VALIDO} - "
                f"{RAZON_SOCIAL_MINIMA}"
            ),
            usuario_id="USR-001",
            modulo_nombre="Clientes",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()


class TestActualizarClienteJuridico:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = juridico().actualizar_cliente_juridico()

        assert resultado == (
            f"El cliente jurídico '{RAZON_SOCIAL_MINIMA}' se actualizó exitosamente."
        )
        assert llamada_con(cursor, "UPDATE Cliente SET").args[1] == (
            DIRECCION_VALIDA,
            TELEFONO_VALIDO,
            CORREO_VALIDO,
            RIF_VALIDO,
        )
        assert llamada_con(cursor, "UPDATE Cliente_juridico SET").args[1] == (
            RAZON_SOCIAL_MINIMA,
            RIF_VALIDO,
            RIF_VALIDO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_telefono_opcional_none(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = juridico(
            Telefono_cliente=None
        ).actualizar_cliente_juridico()

        assert resultado == (
            f"El cliente jurídico '{RAZON_SOCIAL_MINIMA}' se actualizó exitosamente."
        )
        assert llamada_con(cursor, "UPDATE Cliente SET").args[1][1] is None

    def test_razon_social_maxima(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = juridico(
            Razon_social=RAZON_SOCIAL_MAXIMA
        ).actualizar_cliente_juridico()

        assert resultado == (
            f"El cliente jurídico '{RAZON_SOCIAL_MAXIMA}' se actualizó exitosamente."
        )
        assert llamada_con(cursor, "UPDATE Cliente_juridico SET").args[1] == (
            RAZON_SOCIAL_MAXIMA,
            RIF_VALIDO,
            RIF_VALIDO,
        )

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"Rif_cliente": ""},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-vacio",
            ),
            pytest.param(
                {"Rif_cliente": "V-12345678-9"},
                "El RIF debe tener el formato: J-12345678-9 o E-12345678-9",
                id="rif-letra-invalida",
            ),
            pytest.param(
                {"Razon_social": ""},
                "La razón social del cliente no puede estar vacía.",
                id="razon-social-vacia",
            ),
            pytest.param(
                {"Razon_social": "Empresa @ C.A."},
                "La razón social solo puede contener letras, números, puntos, "
                "guiones, espacios y &.",
                id="razon-social-caracteres-invalidos",
            ),
            pytest.param(
                {"Razon_social": "E" * 61},
                "La razón social del cliente no puede exceder los 60 caracteres.",
                id="razon-social-demasiado-larga",
            ),
            pytest.param(
                {"Telefono_cliente": "0412123456"},
                "El teléfono debe tener exactamente 11 dígitos numéricos.",
                id="telefono-demasiado-corto",
            ),
            pytest.param(
                {"Correo_cliente": "ana@mail"},
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
    def test_datos_invalidos_no_tocan_la_bd(self, conexion_falsa, cambios, esperado):
        db, cursor = conexion_falsa

        resultado = juridico(**cambios).actualizar_cliente_juridico()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = juridico().actualizar_cliente_juridico()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª: UPDATE Cliente; 2ª: UPDATE Cliente_juridico que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = juridico().actualizar_cliente_juridico()

        assert resultado == (
            "Error al actualizar cliente jurídico: fallo simulado"
        )
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.clientes.Bitacora") as bitacora_clase:
            resultado = juridico(
                usuario_id="USR-001"
            ).actualizar_cliente_juridico()

        assert resultado == (
            f"El cliente jurídico '{RAZON_SOCIAL_MINIMA}' se actualizó exitosamente."
        )
        bitacora_clase.assert_called_once_with(
            accion="Actualizar cliente jurídico",
            descripcion=(
                f"Se actualizó el cliente jurídico: {RIF_VALIDO} - "
                f"{RAZON_SOCIAL_MINIMA}"
            ),
            usuario_id="USR-001",
            modulo_nombre="Clientes",
        )
        bitacora_clase.return_value.registrar.assert_called_once_with()
