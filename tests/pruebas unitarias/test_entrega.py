"""Pruebas unitarias de la clase EntregaModel (app.models.entrega).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from datetime import datetime
from unittest.mock import patch

import pytest

from app.models.entrega import EntregaModel
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos"

# ==================== Datos de frontera ====================
ENTREGA_ID_MINIMO = "1"  # 1 carácter (mínimo)
ENTREGA_ID_MAXIMO = "ENT1234567"  # 10 caracteres (máximo)

FACTURA_MINIMA = "1"  # 1 carácter (mínimo)
FACTURA_VALIDA = "FAC-202601-000001"
FACTURA_MAXIMA = "F" * 20  # 20 caracteres (máximo)

CEDULA_DELIVERY_MINIMA = "123456"  # 6 dígitos (mínimo)
CEDULA_DELIVERY_MAXIMA = "1" * 15  # 15 dígitos (máximo)

DIRECCION_MINIMA = "A"  # 1 carácter (mínimo)
DIRECCION_MAXIMA = "D" * 60  # 60 caracteres (máximo)

ESTADO_VALIDO = 1  # En camino
USUARIO_ID = "7"
FECHA_ENTREGA = datetime(2026, 1, 2, 10, 30)


@pytest.fixture
def validador_estado_sin_regex():
    """Simula que la validación numérica del estado pasa.

    En la versión actual de `validators.py`, `validar_numero_entero` con
    `max_decimales=0` compila un patrón inválido y lanza un error de `re`.
    Para poder probar el flujo propio del modelo se neutraliza esa llamada.
    """
    with patch("app.models.entrega.validar_numero_entero", return_value=None):
        yield


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


class TestGenerarIdEntrega:

    def test_continua_desde_el_ultimo_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("ENT0000004",)

        resultado = EntregaModel()._generar_id_entrega()

        assert resultado == "ENT0000005"
        assert ultima_sentencia(cursor) == "SELECT MAX(ID_entrega) FROM Entrega"

    def test_empieza_en_uno_si_no_hay_registros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert EntregaModel()._generar_id_entrega() == "ENT0000001"

    def test_ultimo_id_con_prefijo_incorrecto_empieza_en_uno(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("XYZ0000009",)

        assert EntregaModel()._generar_id_entrega() == "ENT0000001"

    def test_ultimo_id_con_numero_invalido_empieza_en_uno(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("ENTabc",)

        assert EntregaModel()._generar_id_entrega() == "ENT0000001"

    def test_conexion_caida_devuelve_id_inicial(self, conexion_caída):
        assert EntregaModel()._generar_id_entrega() == "ENT0000001"

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("ENT0000004",)

        EntregaModel()._generar_id_entrega()

        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestListarEntregas:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id": "ENT0000001",
                "factura_id": FACTURA_VALIDA,
                "estado": 0,
                "direccion": DIRECCION_MINIMA,
            },
        ]
        cursor.fetchall.return_value = filas

        resultado = EntregaModel().listar_entregas()

        assert resultado[0]["id"] == "ENT0000001"
        assert resultado[0]["estado_texto"] == "Pendiente"
        assert resultado[0]["estado_clase"] == "estado-pendiente"
        assert "FROM Entrega" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

    @pytest.mark.parametrize(
        "estado, texto, clase",
        [
            pytest.param(0, "Pendiente", "estado-pendiente", id="pendiente"),
            pytest.param(1, "En camino", "estado-camino", id="en-camino"),
            pytest.param(2, "Entregado", "estado-entregado", id="entregado"),
            pytest.param(3, "Cancelado", "estado-cancelado", id="cancelado"),
            pytest.param(9, "Programado", "estado-programado", id="desconocido"),
        ],
    )
    def test_traduce_el_estado(self, conexion_falsa, estado, texto, clase):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [{"id": "ENT0000001", "estado": estado}]

        resultado = EntregaModel().listar_entregas()

        assert resultado[0]["estado_texto"] == texto
        assert resultado[0]["estado_clase"] == clase

    def test_sin_estado_se_asume_pendiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [{"id": "ENT0000001"}]

        resultado = EntregaModel().listar_entregas()

        assert resultado[0]["estado_texto"] == "Pendiente"

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert EntregaModel().listar_entregas() == []

    def test_conexion_caida(self, conexion_caída):
        assert EntregaModel().listar_entregas() == []

    def test_error_de_bd_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert EntregaModel().listar_entregas() == []
        cierra_recursos(db, cursor)

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        EntregaModel().listar_entregas()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        EntregaModel().listar_entregas()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerEntregaPorId:

    def test_entrega_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "id": ENTREGA_ID_MAXIMO,
            "factura_id": FACTURA_VALIDA,
            "estado": 2,
            "direccion": DIRECCION_MINIMA,
        }
        cursor.fetchone.return_value = esperado

        resultado = EntregaModel().obtener_entrega_por_id(ENTREGA_ID_MAXIMO)

        assert resultado["id"] == ENTREGA_ID_MAXIMO
        assert resultado["estado_texto"] == "Entregado"
        assert resultado["estado_clase"] == "estado-entregado"
        assert "WHERE e.ID_entrega = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ENTREGA_ID_MAXIMO,)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_usa_el_id_de_la_instancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ENTREGA_ID_MAXIMO, "estado": 0}

        EntregaModel(entrega_id=ENTREGA_ID_MAXIMO).obtener_entrega_por_id()

        assert cursor.execute.call_args.args[1] == (ENTREGA_ID_MAXIMO,)

    def test_el_parametro_tiene_prioridad(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ENTREGA_ID_MAXIMO, "estado": 0}

        EntregaModel(entrega_id="OTRO").obtener_entrega_por_id(ENTREGA_ID_MAXIMO)

        assert cursor.execute.call_args.args[1] == (ENTREGA_ID_MAXIMO,)

    @pytest.mark.parametrize(
        "estado, texto, clase",
        [
            pytest.param(0, "Pendiente", "estado-pendiente", id="pendiente"),
            pytest.param(1, "En camino", "estado-camino", id="en-camino"),
            pytest.param(2, "Entregado", "estado-entregado", id="entregado"),
            pytest.param(3, "Cancelado", "estado-cancelado", id="cancelado"),
            pytest.param(8, "Programado", "estado-programado", id="desconocido"),
        ],
    )
    def test_traduce_el_estado(self, conexion_falsa, estado, texto, clase):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ENTREGA_ID_MAXIMO, "estado": estado}

        resultado = EntregaModel().obtener_entrega_por_id(ENTREGA_ID_MAXIMO)

        assert resultado["estado_texto"] == texto
        assert resultado["estado_clase"] == clase

    @pytest.mark.parametrize(
        "entrega_id",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
            pytest.param("   ", id="solo-espacios"),
        ],
    )
    def test_sin_id_no_toca_la_bd(self, conexion_falsa, entrega_id):
        db, cursor = conexion_falsa

        assert EntregaModel().obtener_entrega_por_id(entrega_id) is None

        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "entrega_id",
        [
            pytest.param("ENT#0001", id="caracter-invalido"),
            pytest.param("ENT12345678", id="demasiado-largo"),
        ],
    )
    def test_id_invalido_no_toca_la_bd(self, conexion_falsa, entrega_id):
        db, cursor = conexion_falsa

        assert EntregaModel().obtener_entrega_por_id(entrega_id) is None

        cursor.execute.assert_not_called()

    def test_entrega_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert EntregaModel().obtener_entrega_por_id(ENTREGA_ID_MINIMO) is None

    def test_conexion_caida(self, conexion_caída):
        assert EntregaModel().obtener_entrega_por_id(ENTREGA_ID_MINIMO) is None

    def test_error_de_bd_se_propaga_y_cierra_recursos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            EntregaModel().obtener_entrega_por_id(ENTREGA_ID_MINIMO)

        cierra_recursos(db, cursor)

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        EntregaModel().obtener_entrega_por_id(ENTREGA_ID_MINIMO)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"id": ENTREGA_ID_MINIMO, "estado": 0}

        EntregaModel().obtener_entrega_por_id(ENTREGA_ID_MINIMO)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestRegistrarEntrega:

    def test_datos_validos(self, conexion_falsa, validador_estado_sin_regex):
        db, cursor = conexion_falsa
        # 1ª: MAX(ID_entrega); 2ª: factura; 3ª: delivery
        cursor.fetchone.side_effect = [("ENT0000004",), (1,), (1,)]

        with patch("app.models.entrega.datetime") as fecha_cls:
            fecha_cls.now.return_value = FECHA_ENTREGA
            modelo = EntregaModel(
                factura_id=FACTURA_VALIDA,
                cedula_delivery=CEDULA_DELIVERY_MINIMA,
                direccion=DIRECCION_MINIMA,
                estado=ESTADO_VALIDO,
            )
            resultado = modelo.registrar_entrega()

        assert resultado == "ENT0000005"
        assert modelo.entrega_id == "ENT0000005"
        assert cursor.execute.call_args_list[0].args == (
            "SELECT MAX(ID_entrega) FROM Entrega",
        )
        assert llamada_con(cursor, "FROM Venta").args[1] == (FACTURA_VALIDA,)
        assert llamada_con(cursor, "FROM Personal_delivery").args[1] == (
            CEDULA_DELIVERY_MINIMA,
        )
        assert llamada_con(cursor, "INSERT INTO Entrega").args[1] == (
            "ENT0000005",
            FACTURA_VALIDA,
            CEDULA_DELIVERY_MINIMA,
            ESTADO_VALIDO,
            DIRECCION_MINIMA,
            FECHA_ENTREGA,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_valores_maximos(self, conexion_falsa, validador_estado_sin_regex):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("ENT0000009",), (1,), (1,)]

        with patch("app.models.entrega.datetime") as fecha_cls:
            fecha_cls.now.return_value = FECHA_ENTREGA
            resultado = EntregaModel(
                factura_id=FACTURA_MAXIMA,
                cedula_delivery=CEDULA_DELIVERY_MAXIMA,
                direccion=DIRECCION_MAXIMA,
                estado=3,
            ).registrar_entrega()

        assert resultado == "ENT0000010"
        assert llamada_con(cursor, "INSERT INTO Entrega").args[1][1:] == (
            FACTURA_MAXIMA,
            CEDULA_DELIVERY_MAXIMA,
            3,
            DIRECCION_MAXIMA,
            FECHA_ENTREGA,
        )
        db.commit.assert_called_once()

    def test_factura_minima(self, conexion_falsa, validador_estado_sin_regex):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (1,), (1,)]

        with patch("app.models.entrega.datetime") as fecha_cls:
            fecha_cls.now.return_value = FECHA_ENTREGA
            resultado = EntregaModel(
                factura_id=FACTURA_MINIMA,
                cedula_delivery=CEDULA_DELIVERY_MINIMA,
                direccion=DIRECCION_MINIMA,
                estado="0",
            ).registrar_entrega()

        assert resultado == "ENT0000001"
        assert llamada_con(cursor, "INSERT INTO Entrega").args[1][3] == 0

    @pytest.mark.parametrize(
        "factura_id, cedula_delivery, direccion, estado, esperado",
        [
            pytest.param(
                "",
                CEDULA_DELIVERY_MINIMA,
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "La factura es obligatoria.",
                id="factura-vacia",
            ),
            pytest.param(
                "F" * 21,
                CEDULA_DELIVERY_MINIMA,
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "El campo Factura no puede tener más de 20 caracteres.",
                id="factura-demasiado-larga",
            ),
            pytest.param(
                "FAC 2026",
                CEDULA_DELIVERY_MINIMA,
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "El campo Factura solo puede contener letras, números y guiones.",
                id="factura-caracteres-invalidos",
            ),
            pytest.param(
                FACTURA_VALIDA,
                "",
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "El delivery es obligatorio.",
                id="delivery-vacio",
            ),
            pytest.param(
                FACTURA_VALIDA,
                "12345",
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "El campo Cédula del delivery debe tener al menos 6 dígitos.",
                id="delivery-demasiado-corto",
            ),
            pytest.param(
                FACTURA_VALIDA,
                "1" * 16,
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "El campo Cédula del delivery no puede tener más de 15 dígitos.",
                id="delivery-demasiado-largo",
            ),
            pytest.param(
                FACTURA_VALIDA,
                "12345a",
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "El campo Cédula del delivery solo puede contener números.",
                id="delivery-no-numerico",
            ),
            pytest.param(
                FACTURA_VALIDA,
                CEDULA_DELIVERY_MINIMA,
                "",
                ESTADO_VALIDO,
                "La dirección es obligatoria.",
                id="direccion-vacia",
            ),
            pytest.param(
                FACTURA_VALIDA,
                CEDULA_DELIVERY_MINIMA,
                "D" * 61,
                ESTADO_VALIDO,
                "El campo Dirección no puede tener más de 60 caracteres.",
                id="direccion-demasiado-larga",
            ),
            pytest.param(
                FACTURA_VALIDA,
                CEDULA_DELIVERY_MINIMA,
                "Calle #1",
                ESTADO_VALIDO,
                "El campo Dirección no puede contener caracteres especiales.",
                id="direccion-caracteres-invalidos",
            ),
            pytest.param(
                FACTURA_VALIDA,
                CEDULA_DELIVERY_MINIMA,
                DIRECCION_MINIMA,
                None,
                "El estado es obligatorio.",
                id="estado-none",
            ),
            pytest.param(
                FACTURA_VALIDA,
                CEDULA_DELIVERY_MINIMA,
                DIRECCION_MINIMA,
                0,
                "El campo Estado no puede estar vacío.",
                id="estado-cero-entero",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self,
        conexion_falsa,
        factura_id,
        cedula_delivery,
        direccion,
        estado,
        esperado,
    ):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as error:
            EntregaModel(
                factura_id=factura_id,
                cedula_delivery=cedula_delivery,
                direccion=direccion,
                estado=estado,
            ).registrar_entrega()

        assert str(error.value) == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "estado, esperado",
        [
            pytest.param(
                4,
                "El estado debe ser 0 (Pendiente), 1 (En camino), "
                "2 (Entregado) o 3 (Cancelado).",
                id="fuera-de-rango",
            ),
            pytest.param(
                -1,
                "El estado debe ser 0 (Pendiente), 1 (En camino), "
                "2 (Entregado) o 3 (Cancelado).",
                id="negativo",
            ),
            pytest.param(
                "abc",
                "El estado debe ser un número entero válido.",
                id="no-numerico",
            ),
            pytest.param(
                "2.5",
                "El estado debe ser un número entero válido.",
                id="con-decimales",
            ),
        ],
    )
    def test_estado_invalido_no_toca_la_bd(
        self, conexion_falsa, validador_estado_sin_regex, estado, esperado
    ):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError) as error:
            EntregaModel(
                factura_id=FACTURA_VALIDA,
                cedula_delivery=CEDULA_DELIVERY_MINIMA,
                direccion=DIRECCION_MINIMA,
                estado=estado,
            ).registrar_entrega()

        assert str(error.value) == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_factura_inexistente(
        self, conexion_falsa, validador_estado_sin_regex
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("ENT0000001",), None]

        with pytest.raises(ValueError) as error:
            EntregaModel(
                factura_id=FACTURA_VALIDA,
                cedula_delivery=CEDULA_DELIVERY_MINIMA,
                direccion=DIRECCION_MINIMA,
                estado=ESTADO_VALIDO,
            ).registrar_entrega()

        assert str(error.value) == f"La factura {FACTURA_VALIDA} no existe"
        sin_sentencia(cursor, "INSERT")
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_delivery_inexistente(
        self, conexion_falsa, validador_estado_sin_regex
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("ENT0000001",), (1,), None]

        with pytest.raises(ValueError) as error:
            EntregaModel(
                factura_id=FACTURA_VALIDA,
                cedula_delivery=CEDULA_DELIVERY_MINIMA,
                direccion=DIRECCION_MINIMA,
                estado=ESTADO_VALIDO,
            ).registrar_entrega()

        assert str(error.value) == (
            f"El delivery con cédula {CEDULA_DELIVERY_MINIMA} no existe"
        )
        sin_sentencia(cursor, "INSERT")
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída, validador_estado_sin_regex):
        with pytest.raises(
            RuntimeError, match="No se pudo conectar a la base de datos"
        ):
            EntregaModel(
                factura_id=FACTURA_VALIDA,
                cedula_delivery=CEDULA_DELIVERY_MINIMA,
                direccion=DIRECCION_MINIMA,
                estado=ESTADO_VALIDO,
            ).registrar_entrega()

    def test_error_de_bd_hace_rollback_y_propaga(
        self, conexion_falsa, validador_estado_sin_regex
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("ENT0000001",), (1,), (1,)]
        # 1ª: MAX(ID); 2ª: factura; 3ª: delivery; 4ª: INSERT que falla
        cursor.execute.side_effect = [
            None,
            None,
            None,
            Exception("fallo simulado"),
        ]

        with pytest.raises(Exception, match="fallo simulado"):
            EntregaModel(
                factura_id=FACTURA_VALIDA,
                cedula_delivery=CEDULA_DELIVERY_MINIMA,
                direccion=DIRECCION_MINIMA,
                estado=ESTADO_VALIDO,
            ).registrar_entrega()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_en_bitacora_con_usuario(
        self, conexion_falsa, validador_estado_sin_regex
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("ENT0000004",), (1,), (1,)]

        with patch("app.models.entrega.datetime") as fecha_cls:
            fecha_cls.now.return_value = FECHA_ENTREGA
            with patch("app.models.entrega.Bitacora") as bitacora_cls:
                EntregaModel(
                    factura_id=FACTURA_VALIDA,
                    cedula_delivery=CEDULA_DELIVERY_MINIMA,
                    direccion=DIRECCION_MINIMA,
                    estado=ESTADO_VALIDO,
                    usuario_id=USUARIO_ID,
                ).registrar_entrega()

        bitacora_cls.assert_called_once_with(
            accion="Registrar entrega",
            descripcion=(
                "Se registró la entrega ID: ENT0000005 "
                f"para factura: {FACTURA_VALIDA}"
            ),
            usuario_id=USUARIO_ID,
            modulo_nombre="Entregas",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(
        self, conexion_falsa, validador_estado_sin_regex
    ):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [("ENT0000004",), (1,), (1,)]

        with patch("app.models.entrega.datetime") as fecha_cls:
            fecha_cls.now.return_value = FECHA_ENTREGA
            with patch("app.models.entrega.Bitacora") as bitacora_cls:
                EntregaModel(
                    factura_id=FACTURA_VALIDA,
                    cedula_delivery=CEDULA_DELIVERY_MINIMA,
                    direccion=DIRECCION_MINIMA,
                    estado=ESTADO_VALIDO,
                ).registrar_entrega()

        bitacora_cls.assert_not_called()


class TestActualizarEntrega:

    def test_datos_validos(self, conexion_falsa, validador_estado_sin_regex):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = EntregaModel(
            entrega_id=ENTREGA_ID_MAXIMO,
            direccion=DIRECCION_MINIMA,
            estado=2,
        ).actualizar_entrega()

        assert resultado == "Entrega actualizada exitosamente"
        assert llamada_con(cursor, "UPDATE Entrega").args[1] == (
            DIRECCION_MINIMA,
            2,
            ENTREGA_ID_MAXIMO,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_valores_maximos(self, conexion_falsa, validador_estado_sin_regex):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = EntregaModel(
            entrega_id=ENTREGA_ID_MAXIMO,
            direccion=DIRECCION_MAXIMA,
            estado=3,
        ).actualizar_entrega()

        assert resultado == "Entrega actualizada exitosamente"
        assert llamada_con(cursor, "UPDATE Entrega").args[1] == (
            DIRECCION_MAXIMA,
            3,
            ENTREGA_ID_MAXIMO,
        )

    @pytest.mark.parametrize(
        "entrega_id, direccion, estado, esperado",
        [
            pytest.param(
                "",
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "ID de entrega no especificado.",
                id="id-vacio",
            ),
            pytest.param(
                "   ",
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "ID de entrega no especificado.",
                id="id-solo-espacios",
            ),
            pytest.param(
                "ENT12345678",
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "El campo ID de entrega no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
            pytest.param(
                "ENT#0001",
                DIRECCION_MINIMA,
                ESTADO_VALIDO,
                "El campo ID de entrega solo puede contener letras, números, "
                "acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
            pytest.param(
                ENTREGA_ID_MAXIMO,
                "",
                ESTADO_VALIDO,
                "La dirección es obligatoria.",
                id="direccion-vacia",
            ),
            pytest.param(
                ENTREGA_ID_MAXIMO,
                "D" * 61,
                ESTADO_VALIDO,
                "El campo Dirección no puede tener más de 60 caracteres.",
                id="direccion-demasiado-larga",
            ),
            pytest.param(
                ENTREGA_ID_MAXIMO,
                "Calle #1",
                ESTADO_VALIDO,
                "El campo Dirección no puede contener caracteres especiales.",
                id="direccion-caracteres-invalidos",
            ),
            pytest.param(
                ENTREGA_ID_MAXIMO,
                DIRECCION_MINIMA,
                None,
                "El estado es obligatorio.",
                id="estado-none",
            ),
            pytest.param(
                ENTREGA_ID_MAXIMO,
                DIRECCION_MINIMA,
                0,
                "El campo Estado no puede estar vacío.",
                id="estado-cero-entero",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self,
        conexion_falsa,
        entrega_id,
        direccion,
        estado,
        esperado,
    ):
        db, cursor = conexion_falsa

        resultado = EntregaModel(
            entrega_id=entrega_id,
            direccion=direccion,
            estado=estado,
        ).actualizar_entrega()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "estado, esperado",
        [
            pytest.param(
                4,
                "El estado debe ser 0 (Pendiente), 1 (En camino), "
                "2 (Entregado) o 3 (Cancelado).",
                id="fuera-de-rango",
            ),
            pytest.param(
                -1,
                "El estado debe ser 0 (Pendiente), 1 (En camino), "
                "2 (Entregado) o 3 (Cancelado).",
                id="negativo",
            ),
            pytest.param(
                "abc",
                "El estado debe ser un número entero válido.",
                id="no-numerico",
            ),
        ],
    )
    def test_estado_invalido_no_toca_la_bd(
        self, conexion_falsa, validador_estado_sin_regex, estado, esperado
    ):
        db, cursor = conexion_falsa

        resultado = EntregaModel(
            entrega_id=ENTREGA_ID_MAXIMO,
            direccion=DIRECCION_MINIMA,
            estado=estado,
        ).actualizar_entrega()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_entrega_inexistente(self, conexion_falsa, validador_estado_sin_regex):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        resultado = EntregaModel(
            entrega_id=ENTREGA_ID_MAXIMO,
            direccion=DIRECCION_MINIMA,
            estado=ESTADO_VALIDO,
        ).actualizar_entrega()

        assert resultado == "Entrega no encontrada"
        db.commit.assert_not_called()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_conexion_caida(self, conexion_caída, validador_estado_sin_regex):
        resultado = EntregaModel(
            entrega_id=ENTREGA_ID_MAXIMO,
            direccion=DIRECCION_MINIMA,
            estado=ESTADO_VALIDO,
        ).actualizar_entrega()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(
        self, conexion_falsa, validador_estado_sin_regex
    ):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = EntregaModel(
            entrega_id=ENTREGA_ID_MAXIMO,
            direccion=DIRECCION_MINIMA,
            estado=ESTADO_VALIDO,
        ).actualizar_entrega()

        assert resultado == "Error al actualizar: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_en_bitacora_con_usuario(
        self, conexion_falsa, validador_estado_sin_regex
    ):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        with patch("app.models.entrega.Bitacora") as bitacora_cls:
            EntregaModel(
                entrega_id=ENTREGA_ID_MAXIMO,
                direccion=DIRECCION_MINIMA,
                estado=ESTADO_VALIDO,
                usuario_id=USUARIO_ID,
            ).actualizar_entrega()

        bitacora_cls.assert_called_once_with(
            accion="Actualizar entrega",
            descripcion=f"Se actualizó la entrega ID: {ENTREGA_ID_MAXIMO}",
            usuario_id=USUARIO_ID,
            modulo_nombre="Entregas",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(
        self, conexion_falsa, validador_estado_sin_regex
    ):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        with patch("app.models.entrega.Bitacora") as bitacora_cls:
            EntregaModel(
                entrega_id=ENTREGA_ID_MAXIMO,
                direccion=DIRECCION_MINIMA,
                estado=ESTADO_VALIDO,
            ).actualizar_entrega()

        bitacora_cls.assert_not_called()


class TestEliminarEntrega:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = EntregaModel(entrega_id=ENTREGA_ID_MAXIMO).eliminar_entrega()

        assert resultado == "Entrega eliminada exitosamente"
        assert ultima_sentencia(cursor) == (
            "DELETE FROM Entrega WHERE ID_entrega = %s"
        )
        assert cursor.execute.call_args.args[1] == (ENTREGA_ID_MAXIMO,)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_id_minimo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = EntregaModel(entrega_id=ENTREGA_ID_MINIMO).eliminar_entrega()

        assert resultado == "Entrega eliminada exitosamente"
        assert cursor.execute.call_args.args[1] == (ENTREGA_ID_MINIMO,)

    @pytest.mark.parametrize(
        "entrega_id, esperado",
        [
            pytest.param(
                None,
                "ID de entrega no especificado.",
                id="none",
            ),
            pytest.param(
                "",
                "ID de entrega no especificado.",
                id="vacio",
            ),
            pytest.param(
                "   ",
                "ID de entrega no especificado.",
                id="solo-espacios",
            ),
            pytest.param(
                "ENT12345678",
                "El campo ID de entrega no puede tener más de 10 caracteres.",
                id="demasiado-largo",
            ),
            pytest.param(
                "ENT#0001",
                "El campo ID de entrega solo puede contener letras, números, "
                "acentos y espacios.",
                id="caracteres-invalidos",
            ),
        ],
    )
    def test_id_invalido_no_toca_la_bd(self, conexion_falsa, entrega_id, esperado):
        db, cursor = conexion_falsa

        resultado = EntregaModel(entrega_id=entrega_id).eliminar_entrega()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_entrega_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        resultado = EntregaModel(entrega_id=ENTREGA_ID_MAXIMO).eliminar_entrega()

        assert resultado == "Entrega no encontrada"
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_conexion_caida(self, conexion_caída):
        resultado = EntregaModel(entrega_id=ENTREGA_ID_MAXIMO).eliminar_entrega()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = EntregaModel(entrega_id=ENTREGA_ID_MAXIMO).eliminar_entrega()

        assert resultado == "Error al eliminar: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        with patch("app.models.entrega.Bitacora") as bitacora_cls:
            EntregaModel(
                entrega_id=ENTREGA_ID_MAXIMO,
                usuario_id=USUARIO_ID,
            ).eliminar_entrega()

        bitacora_cls.assert_called_once_with(
            accion="Eliminar entrega",
            descripcion=f"Se eliminó la entrega ID: {ENTREGA_ID_MAXIMO}",
            usuario_id=USUARIO_ID,
            modulo_nombre="Entregas",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        with patch("app.models.entrega.Bitacora") as bitacora_cls:
            EntregaModel(entrega_id=ENTREGA_ID_MAXIMO).eliminar_entrega()

        bitacora_cls.assert_not_called()


class TestObtenerFacturasPendientes:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "factura_id": FACTURA_VALIDA,
                "cliente_id": "1",
                "Fecha_venta": "2026-01-02 10:30",
                "cliente_nombre": "Ana",
                "cliente_apellido": "Paz",
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = EntregaModel().obtener_facturas_pendientes()

        assert resultado == filas
        assert "WHERE e.ID_entrega IS NULL" in ultima_sentencia(cursor)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert EntregaModel().obtener_facturas_pendientes() == []

    def test_conexion_caida(self, conexion_caída):
        assert EntregaModel().obtener_facturas_pendientes() == []

    def test_error_de_bd_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert EntregaModel().obtener_facturas_pendientes() == []
        cierra_recursos(db, cursor)

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        EntregaModel().obtener_facturas_pendientes()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        EntregaModel().obtener_facturas_pendientes()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()
