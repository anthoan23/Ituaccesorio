
import pytest

from app.models.empleados import Empleados
from tests.helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = (
    "No se pudo conectar con la base de datos. "
    "Inténtalo de nuevo más tarde o comunícate con los técnicos."
)

# ==================== Datos de frontera ====================
CEDULA_MINIMA = "123456"  # 6 dígitos (mínimo)
CEDULA_MAXIMA = "123456789"  # 9 dígitos (máximo)

CARGO_MINIMO = "1"  # 1 carácter (mínimo)
CARGO_MAXIMO = "1234567890"  # 10 caracteres (máximo)

NOMBRE_MINIMO = "Ana"  # 3 caracteres (mínimo)
NOMBRE_MAXIMO = "N" * 30  # 30 caracteres (máximo)

APELLIDO_MINIMO = "Paz"  # 3 caracteres (mínimo)
APELLIDO_MAXIMO = "A" * 30  # 30 caracteres (máximo)

CELULAR_MINIMO_AGREGAR = "123456789"  # 9 dígitos (mínimo al agregar)
CELULAR_MAXIMO_AGREGAR = "1" * 15  # 15 dígitos (máximo al agregar)
CELULAR_ACTUALIZAR = "1234567890"  # 10 dígitos (exactos al actualizar)

CORREO_VALIDO = "ana.perez@mail.com"
CORREO_MAXIMO = "u" * 41 + "@mail.com"  # 50 caracteres (máximo)

DIRECCION_MINIMA = "Av"  # 2 caracteres (mínimo)
DIRECCION_MAXIMA = "D" * 60  # 60 caracteres (máximo)

DATOS_VALIDOS = {
    "id_empleado": CEDULA_MINIMA,
    "id_cargo": CARGO_MINIMO,
    "nombre_empleado": NOMBRE_MINIMO,
    "apellido_empleado": APELLIDO_MINIMO,
    "celular_empleado": CELULAR_ACTUALIZAR,
    "correo_empleado": CORREO_VALIDO,
    "direccion_empleado": DIRECCION_MINIMA,
}


def datos(**cambios):
    """Devuelve una copia de DATOS_VALIDOS con los campos cambiados."""
    return {**DATOS_VALIDOS, **cambios}


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


class TestListadosEmpleados:

    def test_listar_empleados(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"cedula": CEDULA_MINIMA, "nombre": "Ana", "cargo": "Cajero"}]
        cursor.fetchall.return_value = filas

        resultado = Empleados().listar_empleados()

        assert resultado == filas
        assert "FROM Empleado" in ultima_sentencia(cursor)
        cursor.close.assert_called_once()
        db.close.assert_called_once()
        db.commit.assert_not_called()

    def test_listar_cargos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": "1", "nombre": "Cajero", "descripcion": "Atiende la caja"}]
        cursor.fetchall.return_value = filas

        resultado = Empleados().listar_cargos()

        assert resultado == filas
        assert "FROM Cargo" in ultima_sentencia(cursor)
        cursor.close.assert_called_once()
        db.close.assert_called_once()
        db.commit.assert_not_called()

    def test_listar_especialidades(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": "1", "nombre": "Celulares", "descripcion": "Reparación"}]
        cursor.fetchall.return_value = filas

        resultado = Empleados().listar_especialidades()

        assert resultado == filas
        assert "FROM Especialidad" in ultima_sentencia(cursor)
        cursor.close.assert_called_once()
        db.close.assert_called_once()
        db.commit.assert_not_called()

    def test_listar_empleados_por_cargo(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"nombre": "Cajero", "cantidad": 3}]
        cursor.fetchall.return_value = filas

        resultado = Empleados().listar_empleados_por_cargo()

        assert resultado == filas
        assert "LEFT JOIN Empleado" in ultima_sentencia(cursor)
        cursor.close.assert_called_once()
        db.close.assert_called_once()
        db.commit.assert_not_called()

    def test_listar_empleados_por_especialidad(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"nombre": "Celulares", "cantidad": 2}]
        cursor.fetchall.return_value = filas

        resultado = Empleados().listar_empleados_por_especialidad()

        assert resultado == filas
        assert "LEFT JOIN Capacitacion" in ultima_sentencia(cursor)
        cursor.close.assert_called_once()
        db.close.assert_called_once()
        db.commit.assert_not_called()

    def test_listar_tecnicos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": CEDULA_MINIMA, "nombre": "Ana", "apellido": "Pérez"}]
        cursor.fetchall.return_value = filas

        resultado = Empleados().listar_tecnicos()

        assert resultado == filas
        assert "LOWER(c.Nombre_cargo) = 'técnico'" in ultima_sentencia(cursor)
        cursor.close.assert_called_once()
        db.close.assert_called_once()
        db.commit.assert_not_called()

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []
        empleados = Empleados()

        assert empleados.listar_empleados() == []
        assert empleados.listar_cargos() == []
        assert empleados.listar_especialidades() == []
        assert empleados.listar_empleados_por_cargo() == []
        assert empleados.listar_empleados_por_especialidad() == []
        assert empleados.listar_tecnicos() == []

    def test_conexion_caida(self, conexion_caída):
        empleados = Empleados()

        for metodo in (
            empleados.listar_empleados,
            empleados.listar_cargos,
            empleados.listar_especialidades,
            empleados.listar_empleados_por_cargo,
            empleados.listar_empleados_por_especialidad,
            empleados.listar_tecnicos,
        ):
            assert metodo() == MENSAJE_ERROR_CONEXION

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []
        empleados = Empleados()

        empleados.listar_empleados()
        empleados.listar_cargos()
        empleados.listar_especialidades()
        empleados.listar_empleados_por_cargo()
        empleados.listar_empleados_por_especialidad()
        empleados.listar_tecnicos()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestConsultarEmpleado:

    def test_empleado_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {
            "cedula": CEDULA_MINIMA,
            "nombre": "Ana",
            "apellido": "Pérez",
            "celular": CELULAR_ACTUALIZAR,
            "correo": CORREO_VALIDO,
            "direccion": DIRECCION_MINIMA,
            "cargo_id": "1",
            "cargo": "Cajero",
        }
        cursor.fetchone.return_value = esperado

        resultado = Empleados(id_empleado=CEDULA_MINIMA).consultar_empleado()

        assert resultado == esperado
        assert "JOIN Cargo" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA,)

    def test_empleado_no_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Empleados(id_empleado=CEDULA_MINIMA).consultar_empleado()

        assert resultado is None

    @pytest.mark.parametrize(
        "cedula, esperado",
        [
            pytest.param(
                "",
                "El campo Cédula no puede estar vacío.",
                id="vacia",
            ),
            pytest.param(
                "12345",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="demasiado-corta",
            ),
            pytest.param(
                "1234567890",
                "El campo Cédula no puede tener más de 9 dígitos.",
                id="demasiado-larga",
            ),
            pytest.param(
                "12345a",
                "El campo Cédula solo puede contener números.",
                id="no-numerica",
            ),
        ],
    )
    def test_cedula_invalida_no_toca_la_bd(self, conexion_falsa, cedula, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(id_empleado=cedula).consultar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Empleados(id_empleado=CEDULA_MINIMA).consultar_empleado()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"cedula": CEDULA_MINIMA}

        Empleados(id_empleado=CEDULA_MINIMA).consultar_empleado()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestConsultarEspecialidadesEmpleado:

    def test_con_especialidades(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {"id": "1", "nombre": "Celulares", "descripcion": "Reparación"},
            {"id": "2", "nombre": "Computación", "descripcion": "Laptops"},
        ]
        cursor.fetchall.return_value = filas

        resultado = Empleados(
            id_empleado=CEDULA_MINIMA
        ).consultar_especialidades_empleado()

        assert resultado == filas
        assert "FROM Capacitacion" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA,)

    def test_sin_especialidades(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        resultado = Empleados(
            id_empleado=CEDULA_MINIMA
        ).consultar_especialidades_empleado()

        assert resultado == []

    def test_conexion_caida(self, conexion_caída):
        resultado = Empleados(
            id_empleado=CEDULA_MINIMA
        ).consultar_especialidades_empleado()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Empleados(id_empleado=CEDULA_MINIMA).consultar_especialidades_empleado()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestVerificarEmpleado:

    def test_empleado_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Empleados(id_empleado=CEDULA_MINIMA).verificar_empleado() is True

        assert ultima_sentencia(cursor) == (
            "SELECT 1 FROM Empleado WHERE ID_empleado = %s LIMIT 1"
        )
        assert cursor.execute.call_args.args[1] == (CEDULA_MINIMA,)

    def test_empleado_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Empleados(id_empleado=CEDULA_MINIMA).verificar_empleado() is False

    def test_conexion_caida(self, conexion_caída):
        assert Empleados(id_empleado=CEDULA_MINIMA).verificar_empleado() is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Empleados(id_empleado=CEDULA_MINIMA).verificar_empleado()

        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Empleados(id_empleado=CEDULA_MINIMA).verificar_empleado()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestAgregarEmpleado:

    def test_datos_validos_sin_especialidades(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None  # la cédula aún no existe

        resultado = Empleados(**DATOS_VALIDOS).agregar_empleado()

        assert resultado == "Empleado agregado exitosamente."
        assert llamada_con(cursor, "INSERT INTO Empleado").args[1] == (
            CEDULA_MINIMA,
            CARGO_MINIMO,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_ACTUALIZAR,
            CORREO_VALIDO,
            DIRECCION_MINIMA,
        )
        sin_sentencia(cursor, "Capacitacion")
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (verificar duplicado + INSERT): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_datos_validos_con_especialidades(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Empleados(
            **DATOS_VALIDOS, especialidades=["1", "2"]
        ).agregar_empleado()

        assert resultado == "Empleado agregado exitosamente."
        assert llamada_con(cursor, "INSERT INTO Capacitacion").args[1] == (
            "1",
            CEDULA_MINIMA,
        )
        inserts = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Capacitacion" in llamada.args[0]
        ]
        assert inserts == [("1", CEDULA_MINIMA), ("2", CEDULA_MINIMA)]
        db.commit.assert_called_once()
        db.rollback.assert_not_called()

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Empleados(
            **datos(celular_empleado=CELULAR_MINIMO_AGREGAR)
        ).agregar_empleado()

        assert resultado == "Empleado agregado exitosamente."
        assert llamada_con(cursor, "INSERT INTO Empleado").args[1] == (
            CEDULA_MINIMA,
            CARGO_MINIMO,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_MINIMO_AGREGAR,
            CORREO_VALIDO,
            DIRECCION_MINIMA,
        )
        db.commit.assert_called_once()

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Empleados(
            **datos(
                id_empleado=CEDULA_MAXIMA,
                id_cargo=CARGO_MAXIMO,
                nombre_empleado=NOMBRE_MAXIMO,
                apellido_empleado=APELLIDO_MAXIMO,
                celular_empleado=CELULAR_MAXIMO_AGREGAR,
                correo_empleado=CORREO_MAXIMO,
                direccion_empleado=DIRECCION_MAXIMA,
            )
        ).agregar_empleado()

        assert resultado == "Empleado agregado exitosamente."
        assert llamada_con(cursor, "INSERT INTO Empleado").args[1] == (
            CEDULA_MAXIMA,
            CARGO_MAXIMO,
            NOMBRE_MAXIMO,
            APELLIDO_MAXIMO,
            CELULAR_MAXIMO_AGREGAR,
            CORREO_MAXIMO,
            DIRECCION_MAXIMA,
        )
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "cedula, esperado",
        [
            pytest.param(
                "",
                "El campo Cédula no puede estar vacío.",
                id="vacia",
            ),
            pytest.param(
                "12345",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="demasiado-corta",
            ),
            pytest.param(
                "1234567890",
                "El campo Cédula no puede tener más de 9 dígitos.",
                id="demasiado-larga",
            ),
            pytest.param(
                "12345a",
                "El campo Cédula solo puede contener números.",
                id="no-numerica",
            ),
        ],
    )
    def test_cedula_invalida_no_toca_la_bd(self, conexion_falsa, cedula, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(id_empleado=cedula)
        ).agregar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "cargo, esperado",
        [
            pytest.param(
                "",
                "El campo ID del Cargo no puede estar vacío.",
                id="cargo-vacio",
            ),
            pytest.param(
                "12345678901",
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="cargo-demasiado-largo",
            ),
            pytest.param(
                "Cargo#1",
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="cargo-caracteres-invalidos",
            ),
        ],
    )
    def test_cargo_invalido_no_toca_la_bd(self, conexion_falsa, cargo, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(**datos(id_cargo=cargo)).agregar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "campo, esperado",
        [
            pytest.param(
                "",
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "An",
                "El campo Nombre debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                "N" * 31,
                "El campo Nombre no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Ana #1",
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
        ],
    )
    def test_nombre_invalido_no_toca_la_bd(self, conexion_falsa, campo, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(nombre_empleado=campo)
        ).agregar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "campo, esperado",
        [
            pytest.param(
                "",
                "El campo Apellido no puede estar vacío.",
                id="apellido-vacio",
            ),
            pytest.param(
                "Pz",
                "El campo Apellido debe tener al menos 3 caracteres.",
                id="apellido-demasiado-corto",
            ),
            pytest.param(
                "A" * 31,
                "El campo Apellido no puede tener más de 30 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                "Paz #1",
                "El campo Apellido solo puede contener letras, acentos y espacios.",
                id="apellido-caracteres-invalidos",
            ),
        ],
    )
    def test_apellido_invalido_no_toca_la_bd(self, conexion_falsa, campo, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(apellido_empleado=campo)
        ).agregar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "celular, esperado",
        [
            pytest.param(
                "",
                "El campo Celular no puede estar vacío.",
                id="vacio",
            ),
            pytest.param(
                "12345678",
                "El campo Celular debe tener al menos 9 dígitos.",
                id="demasiado-corto",
            ),
            pytest.param(
                "1234567890123456",
                "El campo Celular no puede tener más de 15 dígitos.",
                id="demasiado-largo",
            ),
            pytest.param(
                "0412abc123",
                "El campo Celular solo puede contener números.",
                id="no-numerico",
            ),
        ],
    )
    def test_celular_invalido_no_toca_la_bd(self, conexion_falsa, celular, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(celular_empleado=celular)
        ).agregar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "correo, esperado",
        [
            pytest.param(
                "",
                "El campo correo no puede estar vacío.",
                id="vacio",
            ),
            pytest.param(
                "anaperez.com",
                "El campo correo debe contener el símbolo @.",
                id="sin-arroba",
            ),
            pytest.param(
                "ana@@mail.com",
                "El campo correo debe contener exactamente un símbolo @.",
                id="dos-arrobas",
            ),
            pytest.param(
                "ana@mail",
                "El campo correo debe tener un punto en el dominio (después del @).",
                id="sin-punto-en-dominio",
            ),
        ],
    )
    def test_correo_invalido_no_toca_la_bd(self, conexion_falsa, correo, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(correo_empleado=correo)
        ).agregar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "direccion, esperado",
        [
            pytest.param(
                "",
                "El campo Dirección no puede estar vacío.",
                id="vacia",
            ),
            pytest.param(
                "A",
                "El campo Dirección debe tener al menos 2 caracteres.",
                id="demasiado-corta",
            ),
            pytest.param(
                "D" * 61,
                "El campo Dirección no puede tener más de 60 caracteres.",
                id="demasiado-larga",
            ),
            pytest.param(
                "Calle #1",
                "El campo Dirección solo puede contener letras, números, acentos y espacios.",
                id="caracteres-invalidos",
            ),
        ],
    )
    def test_direccion_invalida_no_toca_la_bd(
        self, conexion_falsa, direccion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(direccion_empleado=direccion)
        ).agregar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_empleado_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # ya existe esa cédula

        resultado = Empleados(**DATOS_VALIDOS).agregar_empleado()

        assert resultado == f"El empleado con cédula {CEDULA_MINIMA} ya existe."
        sin_sentencia(cursor, "INSERT")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Empleados(**DATOS_VALIDOS).agregar_empleado()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        # 1ª llamada: verificar duplicado; 2ª: el INSERT que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Empleados(**DATOS_VALIDOS).agregar_empleado()

        assert resultado == "Error al agregar empleado."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestActualizarEmpleado:

    def test_datos_validos_con_especialidades(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)  # el empleado sí existe

        resultado = Empleados(
            **DATOS_VALIDOS, especialidades=["1", "2"]
        ).actualizar_empleado()

        assert resultado == "Empleado actualizado exitosamente."
        assert llamada_con(cursor, "UPDATE Empleado").args[1] == (
            CARGO_MINIMO,
            NOMBRE_MINIMO,
            APELLIDO_MINIMO,
            CELULAR_ACTUALIZAR,
            CORREO_VALIDO,
            DIRECCION_MINIMA,
            CEDULA_MINIMA,
        )
        assert llamada_con(cursor, "DELETE FROM Capacitacion").args[1] == (
            CEDULA_MINIMA,
        )
        inserts = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Capacitacion" in llamada.args[0]
        ]
        assert inserts == [("1", CEDULA_MINIMA), ("2", CEDULA_MINIMA)]
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 2 operaciones (verificar existencia + UPDATE): cada una cierra su cursor
        cierra_recursos(db, cursor)

    def test_especialidades_vacias_aun_borran_capacitaciones(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        # especialidades por defecto es [], no None: borra las existentes
        resultado = Empleados(**DATOS_VALIDOS).actualizar_empleado()

        assert resultado == "Empleado actualizado exitosamente."
        llamada_con(cursor, "DELETE FROM Capacitacion")
        sin_sentencia(cursor, "INSERT INTO Capacitacion")
        db.commit.assert_called_once()

    def test_especialidades_none_no_toca_capacitaciones(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        empleado = Empleados(**DATOS_VALIDOS)
        empleado.especialidades = None

        resultado = empleado.actualizar_empleado()

        assert resultado == "Empleado actualizado exitosamente."
        sin_sentencia(cursor, "Capacitacion")
        db.commit.assert_called_once()

    def test_valores_minimos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Empleados(**DATOS_VALIDOS).actualizar_empleado()

        assert resultado == "Empleado actualizado exitosamente."
        db.commit.assert_called_once()

    def test_valores_maximos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        resultado = Empleados(
            **datos(
                id_empleado=CEDULA_MAXIMA,
                id_cargo=CARGO_MAXIMO,
                nombre_empleado=NOMBRE_MAXIMO,
                apellido_empleado=APELLIDO_MAXIMO,
                correo_empleado=CORREO_MAXIMO,
                direccion_empleado=DIRECCION_MAXIMA,
            )
        ).actualizar_empleado()

        assert resultado == "Empleado actualizado exitosamente."
        assert llamada_con(cursor, "UPDATE Empleado").args[1] == (
            CARGO_MAXIMO,
            NOMBRE_MAXIMO,
            APELLIDO_MAXIMO,
            CELULAR_ACTUALIZAR,
            CORREO_MAXIMO,
            DIRECCION_MAXIMA,
            CEDULA_MAXIMA,
        )
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "cedula, esperado",
        [
            pytest.param(
                "",
                "El campo Cédula no puede estar vacío.",
                id="vacia",
            ),
            pytest.param(
                "12345",
                "El campo Cédula debe tener al menos 6 dígitos.",
                id="demasiado-corta",
            ),
            pytest.param(
                "1234567890",
                "El campo Cédula no puede tener más de 9 dígitos.",
                id="demasiado-larga",
            ),
            pytest.param(
                "12345a",
                "El campo Cédula solo puede contener números.",
                id="no-numerica",
            ),
        ],
    )
    def test_cedula_invalida_no_toca_la_bd(self, conexion_falsa, cedula, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(id_empleado=cedula)
        ).actualizar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "cargo, esperado",
        [
            pytest.param(
                "",
                "El campo ID del Cargo no puede estar vacío.",
                id="cargo-vacio",
            ),
            pytest.param(
                "12345678901",
                "El campo ID del Cargo no puede tener más de 10 caracteres.",
                id="cargo-demasiado-largo",
            ),
            pytest.param(
                "Cargo#1",
                "El campo ID del Cargo solo puede contener letras, números, acentos y espacios.",
                id="cargo-caracteres-invalidos",
            ),
        ],
    )
    def test_cargo_invalido_no_toca_la_bd(self, conexion_falsa, cargo, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(**datos(id_cargo=cargo)).actualizar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "campo, esperado",
        [
            pytest.param(
                "",
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                "An",
                "El campo Nombre debe tener al menos 3 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                "N" * 31,
                "El campo Nombre no puede tener más de 30 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                "Ana #1",
                "El campo Nombre solo puede contener letras, acentos y espacios.",
                id="nombre-caracteres-invalidos",
            ),
        ],
    )
    def test_nombre_invalido_no_toca_la_bd(self, conexion_falsa, campo, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(nombre_empleado=campo)
        ).actualizar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "campo, esperado",
        [
            pytest.param(
                "",
                "El campo Apellido no puede estar vacío.",
                id="apellido-vacio",
            ),
            pytest.param(
                "Pz",
                "El campo Apellido debe tener al menos 3 caracteres.",
                id="apellido-demasiado-corto",
            ),
            pytest.param(
                "A" * 31,
                "El campo Apellido no puede tener más de 30 caracteres.",
                id="apellido-demasiado-largo",
            ),
            pytest.param(
                "Paz #1",
                "El campo Apellido solo puede contener letras, acentos y espacios.",
                id="apellido-caracteres-invalidos",
            ),
        ],
    )
    def test_apellido_invalido_no_toca_la_bd(self, conexion_falsa, campo, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(apellido_empleado=campo)
        ).actualizar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "celular, esperado",
        [
            pytest.param(
                "123456789",
                "El campo Celular debe tener al menos 10 dígitos.",
                id="demasiado-corto",
            ),
            pytest.param(
                "12345678901",
                "El campo Celular no puede tener más de 10 dígitos.",
                id="demasiado-largo",
            ),
            pytest.param(
                "0412abc123",
                "El campo Celular solo puede contener números.",
                id="no-numerico",
            ),
        ],
    )
    def test_celular_invalido_no_toca_la_bd(self, conexion_falsa, celular, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(celular_empleado=celular)
        ).actualizar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "correo, esperado",
        [
            pytest.param(
                "",
                "El campo correo no puede estar vacío.",
                id="vacio",
            ),
            pytest.param(
                "anaperez.com",
                "El campo correo debe contener el símbolo @.",
                id="sin-arroba",
            ),
            pytest.param(
                "ana@@mail.com",
                "El campo correo debe contener exactamente un símbolo @.",
                id="dos-arrobas",
            ),
            pytest.param(
                "ana@mail",
                "El campo correo debe tener un punto en el dominio (después del @).",
                id="sin-punto-en-dominio",
            ),
        ],
    )
    def test_correo_invalido_no_toca_la_bd(self, conexion_falsa, correo, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(correo_empleado=correo)
        ).actualizar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "direccion, esperado",
        [
            pytest.param(
                "",
                "El campo Dirección no puede estar vacío.",
                id="vacia",
            ),
            pytest.param(
                "A",
                "El campo Dirección debe tener al menos 2 caracteres.",
                id="demasiado-corta",
            ),
            pytest.param(
                "D" * 61,
                "El campo Dirección no puede tener más de 60 caracteres.",
                id="demasiado-larga",
            ),
            pytest.param(
                "Calle #1",
                "El campo Dirección solo puede contener letras, números, acentos y espacios.",
                id="caracteres-invalidos",
            ),
        ],
    )
    def test_direccion_invalida_no_toca_la_bd(
        self, conexion_falsa, direccion, esperado
    ):
        db, cursor = conexion_falsa

        resultado = Empleados(
            **datos(direccion_empleado=direccion)
        ).actualizar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_empleado_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = Empleados(**DATOS_VALIDOS).actualizar_empleado()

        assert resultado == (
            f"El empleado con identificador {CEDULA_MINIMA} no existe."
        )
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Empleados(**DATOS_VALIDOS).actualizar_empleado()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)
        # 1ª llamada: verificar existencia; 2ª: el UPDATE que falla
        cursor.execute.side_effect = [None, Exception("fallo simulado")]

        resultado = Empleados(**DATOS_VALIDOS).actualizar_empleado()

        assert resultado == "Error al actualizar empleado."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarEmpleado:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta: datos del empleado; 2ª: verificación de existencia
        cursor.fetchone.side_effect = [
            {"nombre": "Ana", "apellido": "Pérez"},
            (1,),
        ]

        resultado = Empleados(id_empleado=CEDULA_MINIMA).eliminar_empleado()

        assert resultado == "Empleado eliminado exitosamente."
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        pos_capacitacion = next(
            i for i, sql in enumerate(sentencias) if "DELETE FROM Capacitacion" in sql
        )
        pos_empleado = next(
            i for i, sql in enumerate(sentencias) if "DELETE FROM Empleado" in sql
        )
        assert pos_capacitacion < pos_empleado
        assert llamada_con(cursor, "DELETE FROM Empleado").args[1] == (
            CEDULA_MINIMA,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        # 3 operaciones (consultar, verificar, 2 DELETE): cada una cierra su cursor
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "id_empleado",
        [
            pytest.param(CEDULA_MINIMA, id="id-minimo"),
            pytest.param(CEDULA_MAXIMA, id="id-maximo"),
        ],
    )
    def test_limites_de_id(self, conexion_falsa, id_empleado):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (1,)]

        resultado = Empleados(id_empleado=id_empleado).eliminar_empleado()

        assert resultado == "Empleado eliminado exitosamente."
        assert llamada_con(cursor, "DELETE FROM Empleado").args[1] == (id_empleado,)

    @pytest.mark.parametrize(
        "id_empleado, esperado",
        [
            pytest.param(
                "",
                "El campo ID del Empleado no puede estar vacío.",
                id="vacio",
            ),
            pytest.param(
                "12345",
                "El campo ID del Empleado debe tener al menos 6 dígitos.",
                id="demasiado-corto",
            ),
            pytest.param(
                "1234567890",
                "El campo ID del Empleado no puede tener más de 9 dígitos.",
                id="demasiado-largo",
            ),
            pytest.param(
                "12345678#",
                "El campo ID del Empleado solo puede contener números.",
                id="caracteres-invalidos",
            ),
            pytest.param(
                "abcdef",
                "El campo ID del Empleado solo puede contener números.",
                id="solo-letras",
            ),
        ],
    )
    def test_id_invalido_no_tocan_la_bd(self, conexion_falsa, id_empleado, esperado):
        db, cursor = conexion_falsa

        resultado = Empleados(id_empleado=id_empleado).eliminar_empleado()

        assert resultado == esperado
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_empleado_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        resultado = Empleados(id_empleado=CEDULA_MINIMA).eliminar_empleado()

        assert resultado == (
            f"El empleado con identificador {CEDULA_MINIMA} no existe."
        )
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = Empleados(id_empleado=CEDULA_MINIMA).eliminar_empleado()

        assert resultado == MENSAJE_ERROR_CONEXION

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, (1,)]
        # 1ª: consultar; 2ª: verificar; 3ª: el DELETE que falla
        cursor.execute.side_effect = [None, None, Exception("fallo simulado")]

        resultado = Empleados(id_empleado=CEDULA_MINIMA).eliminar_empleado()

        assert resultado == "Error al eliminar empleado."
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
