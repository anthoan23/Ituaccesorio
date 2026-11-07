"""Pruebas unitarias de la clase PersonalDeliveryModel
(app.models.personal_delivery).

Los fixtures `conexion_falsa`, `conexion_caída` y `db_falsa` viven en
tests/pruebas unitarias/conftest.py; los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import patch

import pytest

from app.models.personal_delivery import PersonalDeliveryModel
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
CEDULA_MINIMA = "123456"  # 6 dígitos (mínimo)
CEDULA_MAXIMA = "1" * 15  # 15 dígitos (máximo)

NOMBRE_MINIMO = "A"  # 1 carácter (mínimo)
NOMBRE_MAXIMO = "N" * 40  # 40 caracteres (máximo)

APELLIDO_MINIMO = "P"  # 1 carácter (mínimo)
APELLIDO_MAXIMO = "A" * 40  # 40 caracteres (máximo)

USUARIO_ID = "7"


class TestListarPersonal:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "cedula": CEDULA_MINIMA,
                "nombre": "Ana",
                "apellido": "Paz",
                "nombre_completo": "Ana Paz",
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = PersonalDeliveryModel().listar_personal()

        assert resultado == filas
        assert "FROM Personal_delivery" in ultima_sentencia(cursor)
        db.commit.assert_not_called()

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert PersonalDeliveryModel().listar_personal() == []

    def test_conexion_caida(self, conexion_caída):
        assert PersonalDeliveryModel().listar_personal() == []

    def test_error_general_devuelve_lista_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert PersonalDeliveryModel().listar_personal() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        PersonalDeliveryModel().listar_personal()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        PersonalDeliveryModel().listar_personal()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerPersonalPorCedula:

    def test_delivery_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "cedula": CEDULA_MINIMA,
            "nombre": "Ana",
            "apellido": "Paz",
            "nombre_completo": "Ana Paz",
        }
        cursor.fetchone.return_value = esperado

        resultado = PersonalDeliveryModel(
            cedula=CEDULA_MINIMA
        ).obtener_personal_por_cedula()

        assert resultado == esperado
        assert "WHERE Cedula_delivery = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA,)

    def test_parametro_tiene_prioridad(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"cedula": CEDULA_MAXIMA}

        PersonalDeliveryModel(cedula="999999").obtener_personal_por_cedula(
            cedula=CEDULA_MAXIMA
        )

        assert cursor.execute.call_args.args[1] == (CEDULA_MAXIMA,)

    def test_sin_cedula_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert PersonalDeliveryModel().obtener_personal_por_cedula() is None

        cursor.execute.assert_not_called()

    def test_delivery_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert PersonalDeliveryModel(
            cedula=CEDULA_MINIMA
        ).obtener_personal_por_cedula() is None

    def test_conexion_caida(self, conexion_caída):
        assert PersonalDeliveryModel(
            cedula=CEDULA_MINIMA
        ).obtener_personal_por_cedula() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        PersonalDeliveryModel(cedula=CEDULA_MINIMA).obtener_personal_por_cedula()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"cedula": CEDULA_MINIMA}

        PersonalDeliveryModel(cedula=CEDULA_MINIMA).obtener_personal_por_cedula()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarPersonalExiste:

    def test_delivery_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert PersonalDeliveryModel(
            cedula=CEDULA_MINIMA
        ).verificar_personal_existe() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Personal_delivery WHERE Cedula_delivery = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA,)

    def test_delivery_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert PersonalDeliveryModel(
            cedula=CEDULA_MINIMA
        ).verificar_personal_existe() is False

    def test_sin_cedula_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert PersonalDeliveryModel().verificar_personal_existe() is False

        cursor.execute.assert_not_called()

    def test_parametro_tiene_prioridad(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        PersonalDeliveryModel(cedula="999999").verificar_personal_existe(
            cedula=CEDULA_MAXIMA
        )

        assert cursor.execute.call_args.args[1] == (CEDULA_MAXIMA,)

    def test_conexion_caida(self, conexion_caída):
        assert PersonalDeliveryModel(
            cedula=CEDULA_MINIMA
        ).verificar_personal_existe() is False

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        PersonalDeliveryModel(cedula=CEDULA_MINIMA).verificar_personal_existe()

        cierra_recursos(db, cursor)


class TestAgregarPersonal:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None  # la cédula aún no existe

        personal = PersonalDeliveryModel(
            CEDULA_MINIMA, "Ana", "Paz"
        )
        resultado = personal.agregar_personal()

        assert resultado == "Delivery registrado exitosamente."
        assert "INSERT INTO Personal_delivery" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            CEDULA_MINIMA,
            "Ana",
            "Paz",
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (verificar duplicado + INSERT): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, NOMBRE_MINIMO, APELLIDO_MINIMO
        ).agregar_personal()

        assert resultado == "Delivery registrado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            CEDULA_MINIMA,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
        )

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = PersonalDeliveryModel(
            CEDULA_MAXIMA, NOMBRE_MAXIMO, APELLIDO_MAXIMO
        ).agregar_personal()

        assert resultado == "Delivery registrado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            CEDULA_MAXIMA,
            NOMBRE_MAXIMO,
            APELLIDO_MAXIMO,
        )

    @pytest.mark.parametrize(
        "cedula, nombre, apellido, esperado",
        [
            pytest.param(
                "",
                "Ana",
                "Paz",
                "La cédula es obligatoria.",
                id="cedula-vacia",
            ),
            pytest.param(
                "12345",
                "Ana",
                "Paz",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                "1" * 16,
                "Ana",
                "Paz",
                "El campo Cédula no puede tener más de 15 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                "12345a",
                "Ana",
                "Paz",
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "",
                "Paz",
                "El nombre es obligatorio.",
                id="nombre-vacio",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "N" * 41,
                "Paz",
                "El campo Nombre no puede tener más de 40 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "Ana #1",
                "Paz",
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "Ana",
                "",
                "El apellido es obligatorio.",
                id="apellido-vacio",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "Ana",
                "A" * 41,
                "El campo Apellido no puede tener más de 40 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "Ana",
                "Paz #1",
                "El campo Apellido solo puede contener letras, acentos y espacios.",
                id="apellido-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, cedula, nombre, apellido, esperado
    ):
        db, cursor = conexion_falsa

        resultado = PersonalDeliveryModel(
            cedula, nombre, apellido
        ).agregar_personal()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_delivery_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # ya existe esa cédula

        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, "Ana", "Paz"
        ).agregar_personal()

        assert resultado == (
            f"Ya existe un delivery con cédula {CEDULA_MINIMA}."
        )
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, "Ana", "Paz"
        ).agregar_personal()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª llamada: verificar duplicado; 2ª: el INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, "Ana", "Paz"
        ).agregar_personal()

        assert resultado == "Error al registrar: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.personal_delivery.Bitacora") as bitacora_cls:
            PersonalDeliveryModel(
                CEDULA_MINIMA, "Ana", "Paz", usuario_id=USUARIO_ID
            ).agregar_personal()

        bitacora_cls.assert_called_once_with(
            accion="Registrar delivery",
            descripcion=(
                f"Se registró al delivery: Ana Paz - Cédula: {CEDULA_MINIMA}"
            ),
            usuario_id=USUARIO_ID,
            modulo_nombre="Entregas",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with patch("app.models.personal_delivery.Bitacora") as bitacora_cls:
            PersonalDeliveryModel(CEDULA_MINIMA, "Ana", "Paz").agregar_personal()

        bitacora_cls.assert_not_called()


class TestActualizarPersonal:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # el delivery sí existe

        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, "Ana", "Paz"
        ).actualizar_personal()

        assert resultado == "Delivery actualizado exitosamente."
        assert "UPDATE Personal_delivery" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            "Ana",
            "Paz",
            CEDULA_MINIMA,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (verificar existencia + UPDATE): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, NOMBRE_MINIMO, APELLIDO_MINIMO
        ).actualizar_personal()

        assert resultado == "Delivery actualizado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CEDULA_MINIMA,
        )

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = PersonalDeliveryModel(
            CEDULA_MAXIMA, NOMBRE_MAXIMO, APELLIDO_MAXIMO
        ).actualizar_personal()

        assert resultado == "Delivery actualizado exitosamente."
        assert cursor.execute.call_args.args[1] == (
            NOMBRE_MAXIMO,
            APELLIDO_MAXIMO,
            CEDULA_MAXIMA,
        )

    @pytest.mark.parametrize(
        "cedula, nombre, apellido, esperado",
        [
            pytest.param(
                "",
                "Ana",
                "Paz",
                "La cédula es obligatoria.",
                id="cedula-vacia",
            ),
            pytest.param(
                "12345",
                "Ana",
                "Paz",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                "12345a",
                "Ana",
                "Paz",
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "",
                "Paz",
                "El nombre es obligatorio.",
                id="nombre-vacio",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "N" * 41,
                "Paz",
                "El campo Nombre no puede tener más de 40 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "Ana #1",
                "Paz",
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "Ana",
                "",
                "El apellido es obligatorio.",
                id="apellido-vacio",
            ),
            pytest.param(
                CEDULA_MINIMA,
                "Ana",
                "Paz #1",
                "El campo Apellido solo puede contener letras, acentos y espacios.",
                id="apellido-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos_no_tocan_la_bd(
        self, conexion_falsa, cedula, nombre, apellido, esperado
    ):
        db, cursor = conexion_falsa

        resultado = PersonalDeliveryModel(
            cedula, nombre, apellido
        ).actualizar_personal()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_delivery_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, "Ana", "Paz"
        ).actualizar_personal()

        assert resultado == (
            f"No existe un delivery con cédula {CEDULA_MINIMA}."
        )
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, "Ana", "Paz"
        ).actualizar_personal()

        assert resultado == (
            f"No existe un delivery con cédula {CEDULA_MINIMA}."
        )

    def test_error_de_conexion_al_actualizar(self, db_falsa):
        db, cursor = db_falsa
        cursor.fetchone.return_value = (1,)

        # verificar y luego la conexión para el UPDATE: falla la última
        with patch(
            "app.models.database.conectar.conexion1",
            side_effect=[db, None],
        ):
            resultado = PersonalDeliveryModel(
                CEDULA_MINIMA, "Ana", "Paz"
            ).actualizar_personal()

        assert resultado == MENSAJE_ERROR_CONEXION
        sin_sentencia(cursor, "UPDATE")

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª llamada: verificar existencia; 2ª: el UPDATE que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = PersonalDeliveryModel(
            CEDULA_MINIMA, "Ana", "Paz"
        ).actualizar_personal()

        assert resultado == "Error al actualizar: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with patch("app.models.personal_delivery.Bitacora") as bitacora_cls:
            PersonalDeliveryModel(
                CEDULA_MINIMA, "Ana", "Paz", usuario_id=USUARIO_ID
            ).actualizar_personal()

        bitacora_cls.assert_called_once_with(
            accion="Actualizar delivery",
            descripcion=(
                f"Se actualizó al delivery con cédula: {CEDULA_MINIMA}"
            ),
            usuario_id=USUARIO_ID,
            modulo_nombre="Entregas",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with patch("app.models.personal_delivery.Bitacora") as bitacora_cls:
            PersonalDeliveryModel(CEDULA_MINIMA, "Ana", "Paz").actualizar_personal()

        bitacora_cls.assert_not_called()


class TestEliminarPersonal:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª: verificar; 2ª: datos del delivery; 3ª: entregas asociadas
        cursor.fetchone.side_effect = [
            (1,),
            {"nombre": "Ana", "apellido": "Paz"},
            None,
        ]

        resultado = PersonalDeliveryModel(cedula=CEDULA_MINIMA).eliminar_personal()

        assert resultado == "Delivery eliminado exitosamente."
        assert ultima_sentencia(cursor) == (
            "DELETE FROM Personal_delivery WHERE Cedula_delivery = %s"
        )
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA,)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (verificar, consultar, verificar entregas y DELETE)
        cierra_recursos(db, cursor)

    def test_no_elimina_si_tiene_entregas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            {"nombre": "Ana", "apellido": "Paz"},
            (1,),
        ]

        resultado = PersonalDeliveryModel(cedula=CEDULA_MINIMA).eliminar_personal()

        assert resultado == (
            "No se puede eliminar el delivery porque tiene entregas asociadas."
        )
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_sin_datos_del_delivery_usa_la_cedula(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), None, None]

        resultado = PersonalDeliveryModel(cedula=CEDULA_MINIMA).eliminar_personal()

        assert resultado == "Delivery eliminado exitosamente."
        db.commit.assert_called_once()

    def test_delivery_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = PersonalDeliveryModel(cedula=CEDULA_MINIMA).eliminar_personal()

        assert resultado == (
            f"No existe un delivery con cédula {CEDULA_MINIMA}."
        )
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "cedula, esperado",
        [
            pytest.param(
                "",
                "La cédula es obligatoria.",
                id="cedula-vacia",
            ),
            pytest.param(
                "12345",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                "1" * 16,
                "El campo Cédula no puede tener más de 15 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                "12345a",
                "El campo Cédula solo puede contener números.",
                id="cedula-no-numerica",
            ),
        ],
    )
    def test_cedula_invalida_no_toca_la_bd(self, conexion_falsa, cedula, esperado):
        db, cursor = conexion_falsa

        resultado = PersonalDeliveryModel(cedula=cedula).eliminar_personal()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = PersonalDeliveryModel(cedula=CEDULA_MINIMA).eliminar_personal()

        assert resultado == (
            f"No existe un delivery con cédula {CEDULA_MINIMA}."
        )

    def test_error_de_conexion_al_eliminar(self, db_falsa):
        db, cursor = db_falsa
        cursor.fetchone.side_effect = [(1,), {"nombre": "Ana", "apellido": "Paz"}]

        # verificar, obtener y luego la conexión para el DELETE: falla la última
        with patch(
            "app.models.database.conectar.conexion1",
            side_effect=[db, db, None],
        ):
            resultado = PersonalDeliveryModel(
                cedula=CEDULA_MINIMA
            ).eliminar_personal()

        assert resultado == MENSAJE_ERROR_CONEXION
        sin_sentencia(cursor, "DELETE")

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            {"nombre": "Ana", "apellido": "Paz"},
            None,
        ]
        # 1ª: verificar; 2ª: obtener; 3ª: verificar entregas; 4ª: DELETE
        cursor.execute.side_effect = [
            None,
            None,
            None,
            Exception("fallo simulado"),
        ]

        resultado = PersonalDeliveryModel(cedula=CEDULA_MINIMA).eliminar_personal()

        assert resultado == "Error al eliminar: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_en_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            {"nombre": "Ana", "apellido": "Paz"},
            None,
        ]

        with patch("app.models.personal_delivery.Bitacora") as bitacora_cls:
            PersonalDeliveryModel(
                cedula=CEDULA_MINIMA, usuario_id=USUARIO_ID
            ).eliminar_personal()

        bitacora_cls.assert_called_once_with(
            accion="Eliminar delivery",
            descripcion=(
                f"Se eliminó al delivery con cédula: {CEDULA_MINIMA} "
                "- Nombre: Ana Paz"
            ),
            usuario_id=USUARIO_ID,
            modulo_nombre="Entregas",
        )
        bitacora_cls.return_value.registrar.assert_called_once_with()

    def test_sin_usuario_no_registra_bitacora(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            {"nombre": "Ana", "apellido": "Paz"},
            None,
        ]

        with patch("app.models.personal_delivery.Bitacora") as bitacora_cls:
            PersonalDeliveryModel(cedula=CEDULA_MINIMA).eliminar_personal()

        bitacora_cls.assert_not_called()
