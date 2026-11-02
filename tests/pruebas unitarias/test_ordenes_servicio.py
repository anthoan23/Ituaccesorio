"""Pruebas unitarias de la clase Orden_servicio
(app.models.ordenes_servicio).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.models.ordenes_servicio import Orden_servicio
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ID_ORDEN = "OS0000001"
ID_ORDEN_MAXIMO = "OS9999999"
ID_EMPLEADO = "123456"
ID_FOTO = "FOT000001"
RUTA_FOTO = "/static/img/evidencias/taller/OS0000001/foto1.jpg"

CEDULA_MINIMA = "1234567"  # 7 dígitos (mínimo)
CEDULA_MAXIMA = "12345678"  # 8 dígitos (máximo)
RIF_VALIDO = "J-12345678-9"
RIF_SIN_GUIONES = "J123456789"

IMEI = "123456789012345"  # 15 dígitos (exacto)

DESCRIPCION_MINIMA = "Pantalla rota"
DESCRIPCION_MAXIMA = "D" * 300  # 300 caracteres (máximo)
COLOR = "Negro"
CAPACIDAD = "128GB"
ID_MODELO = "1"


def crear_orden_valida(**cambios):
    """Crea una orden con datos válidos y permite sobreescribir campos."""
    datos = {
        "id_cliente": CEDULA_MAXIMA,
        "id_equipo": IMEI,
        "id_modelo": ID_MODELO,
        "descripcion": DESCRIPCION_MINIMA,
        "nota": "Cliente reporta falla",
        "color": COLOR,
        "capacidad": CAPACIDAD,
    }
    datos.update(cambios)
    return Orden_servicio(ID_empleado=ID_EMPLEADO).crear_orden(**datos)


class TestValidarEmail:

    @pytest.mark.parametrize(
        "email",
        [
            pytest.param(None, id="nulo"),
            pytest.param("", id="vacio"),
            pytest.param("cliente@mail.com", id="valido"),
        ],
    )
    def test_correos_aceptados(self, email):
        assert Orden_servicio._validar_email(email) is None

    @pytest.mark.parametrize(
        "email",
        [
            pytest.param("sin-arroba", id="sin-arroba"),
            pytest.param("dos@@mail.com", id="dos-arroba"),
            pytest.param("cliente@", id="sin-dominio"),
        ],
    )
    def test_correos_invalidos(self, email):
        assert Orden_servicio._validar_email(email) == (
            "El correo electrónico no es válido."
        )


class TestValidarRif:

    @pytest.mark.parametrize(
        "rif",
        [
            pytest.param(RIF_VALIDO, id="con-guiones"),
            pytest.param(RIF_SIN_GUIONES, id="sin-guiones"),
            pytest.param("e-12345678-9", id="minusculas"),
        ],
    )
    def test_rif_valido(self, rif):
        assert Orden_servicio._validar_rif(rif) is None

    @pytest.mark.parametrize(
        "rif",
        [
            pytest.param(None, id="nulo"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_rif_obligatorio(self, rif):
        assert Orden_servicio._validar_rif(rif) == "El RIF es obligatorio."

    @pytest.mark.parametrize(
        "rif",
        [
            pytest.param("V-12345678-9", id="letra-invalida"),
            pytest.param("J-1234", id="muy-corto"),
            pytest.param("J-1234567890", id="muy-largo"),
        ],
    )
    def test_rif_con_formato_invalido(self, rif):
        assert Orden_servicio._validar_rif(rif) == (
            "El RIF debe tener el formato J-12345678-9 o E-12345678-9."
        )


class TestListarModelosTelefonos:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": "1", "nombre": "iPhone 13", "clase_nombre": "Telefono"}]
        cursor.fetchall.return_value = filas

        assert Orden_servicio().listar_modelos_telefonos() == filas
        assert "FROM Producto p" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Orden_servicio().listar_modelos_telefonos() == []

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().listar_modelos_telefonos() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio().listar_modelos_telefonos() == []

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Orden_servicio().listar_modelos_telefonos()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestListarOrdenesServicio:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id_orden": ID_ORDEN, "estado": "Pendiente"}]
        cursor.fetchall.return_value = filas

        assert Orden_servicio().listar_ordenes_servicio() == filas
        assert "FROM Orden_servicio os" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Orden_servicio().listar_ordenes_servicio() == []

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().listar_ordenes_servicio() == (
            "Error al conectar con la base de datos."
        )

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio().listar_ordenes_servicio() == []


class TestListarOrdenesTaller:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id_orden": ID_ORDEN, "estado": "En proceso"}]
        cursor.fetchall.return_value = filas

        assert Orden_servicio().listar_ordenes_taller() == filas
        assert "Estado_orden_servicio IN ('Pendiente', 'En proceso')" in (
            ultima_sentencia(cursor)
        )
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Orden_servicio().listar_ordenes_taller() == []

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().listar_ordenes_taller() == (
            "Error al conectar con la base de datos."
        )

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio().listar_ordenes_taller() == []


class TestListarOrdenesTecnico:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id_orden": ID_ORDEN, "modelo": "iPhone 13"}]
        cursor.fetchall.return_value = filas

        resultado = Orden_servicio(ID_empleado=ID_EMPLEADO).listar_ordenes_tecnico()

        assert resultado == filas
        assert cursor.execute.call_args.args[1] == (ID_EMPLEADO,)
        assert "i.ID_empleado = %s" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Orden_servicio(ID_empleado=ID_EMPLEADO).listar_ordenes_tecnico() == []

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(
            ID_empleado=ID_EMPLEADO
        ).listar_ordenes_tecnico() == "Error al conectar con la base de datos."

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio(ID_empleado=ID_EMPLEADO).listar_ordenes_tecnico() == []


class TestConsultarOrden:

    def test_orden_encontrada_con_fotos(self, conexion_falsa):
        db, cursor = conexion_falsa
        orden = {"ID_orden_servicio": ID_ORDEN, "Estado": "Pendiente"}
        fotos = [{"ID_foto_orden_servicio": ID_FOTO}]
        cursor.fetchone.return_value = orden
        cursor.fetchall.return_value = fotos

        resultado = Orden_servicio(ID_orden_servicio=ID_ORDEN).consultar_orden()

        assert resultado == {**orden, "fotos": fotos}
        assert cursor.execute.call_args_list[0].args[1] == (ID_ORDEN,)
        cierra_recursos(db, cursor)

    def test_orden_sin_fotos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"ID_orden_servicio": ID_ORDEN}
        cursor.fetchall.return_value = None

        resultado = Orden_servicio(ID_orden_servicio=ID_ORDEN).consultar_orden()

        assert resultado["fotos"] == []

    def test_orden_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Orden_servicio(
            ID_orden_servicio=ID_ORDEN
        ).consultar_orden() is None

    @pytest.mark.parametrize(
        "orden, esperado",
        [
            pytest.param(
                "",
                "El campo ID dela orden no puede estar vacío.",
                id="vacia",
            ),
            pytest.param(
                "OS000000001",
                "El campo ID dela orden no puede tener más de 10 caracteres.",
                id="demasiado-larga",
            ),
            pytest.param(
                "OS#1",
                "El campo ID dela orden solo puede contener letras, números, "
                "acentos y espacios.",
                id="caracteres-invalidos",
            ),
        ],
    )
    def test_id_invalido_no_toca_la_bd(self, conexion_falsa, orden, esperado):
        db, cursor = conexion_falsa

        assert Orden_servicio(
            ID_orden_servicio=orden
        ).consultar_orden() == esperado
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(ID_orden_servicio=ID_ORDEN).consultar_orden() is None

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio(ID_orden_servicio=ID_ORDEN).consultar_orden() is None


class TestEmpleadosAsignados:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"Accion": "Asignada", "ID_empleado": ID_EMPLEADO}]
        cursor.fetchall.return_value = filas

        resultado = Orden_servicio().empleados_asignados(ID_ORDEN)

        assert resultado == filas
        assert cursor.execute.call_args.args[1] == (ID_ORDEN,)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Orden_servicio().empleados_asignados(ID_ORDEN) == []

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().empleados_asignados(ID_ORDEN) is None

    def test_error_de_bd_se_propaga(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            Orden_servicio().empleados_asignados(ID_ORDEN)


class TestVerificarFotoExistePorId:

    def test_sin_id_foto(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Orden_servicio().verificar_foto_existe_por_id() is False
        cursor.execute.assert_not_called()

    def test_foto_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Orden_servicio(
            ID_foto_orden_servicio=f"  {ID_FOTO}  "
        ).verificar_foto_existe_por_id() is True
        assert cursor.execute.call_args.args[1] == (ID_FOTO,)
        cierra_recursos(db, cursor)

    def test_foto_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO
        ).verificar_foto_existe_por_id() is False

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO
        ).verificar_foto_existe_por_id() is False

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO
        ).verificar_foto_existe_por_id() is False


class TestEliminarFotoOrdenServicio:

    def test_sin_id_foto(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Orden_servicio().eliminar_foto_orden_servicio() == {
            "success": False,
            "error": "El ID de la foto es obligatorio",
        }
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO
        ).eliminar_foto_orden_servicio() == {
            "success": False,
            "error": "Error al conectar con la base de datos.",
        }

    def test_foto_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO
        ).eliminar_foto_orden_servicio() == {
            "success": False,
            "error": f"No se encontró una foto con ID {ID_FOTO}",
        }

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {
            "Foto_orden_servicio": RUTA_FOTO,
            "ID_orden_servicio": ID_ORDEN,
        }

        resultado = Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO
        ).eliminar_foto_orden_servicio()

        assert resultado == {
            "success": True,
            "mensaje": f"La foto con ID {ID_FOTO} se eliminó exitosamente",
            "ruta_foto": RUTA_FOTO,
            "id_orden": ID_ORDEN,
        }
        assert "DELETE FROM Fotos_orden_servicio" in ultima_sentencia(cursor)
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO
        ).eliminar_foto_orden_servicio()

        assert resultado == {
            "success": False,
            "error": "Error al eliminar la foto: fallo simulado",
        }
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestRegistrarFotos:

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(
            ID_orden_servicio=ID_ORDEN, Foto_orden_servicio=[RUTA_FOTO]
        ).registrar_fotos() == {
            "success": False,
            "error": "Error al conectar con la base de datos.",
        }

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        resultado_bd = MagicMock()
        resultado_bd.fetchall.return_value = [{"resultado": "ok"}]
        cursor.stored_results.return_value = [resultado_bd]
        rutas = [RUTA_FOTO, "/static/img/foto2.jpg"]

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, Foto_orden_servicio=rutas
        ).registrar_fotos()

        assert resultado == {
            "success": True,
            "mensaje": "2 fotos registradas exitosamente",
            "data": [{"resultado": "ok"}],
        }
        cursor.callproc.assert_called_once_with(
            "sp_registrar_fotos_orden",
            (ID_ORDEN, '["/static/img/evidencias/taller/OS0000001/foto1.jpg", '
             '"/static/img/foto2.jpg"]'),
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_resultados_del_procedure(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.stored_results.return_value = []

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, Foto_orden_servicio=[]
        ).registrar_fotos()

        assert resultado["success"] is True
        assert resultado["data"] is None

    def test_extrae_mensaje_de_error_de_mysql(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.callproc.side_effect = Exception(
            "1644 (45000): MESSAGE_TEXT: La orden no existe, algo mas"
        )

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, Foto_orden_servicio=[RUTA_FOTO]
        ).registrar_fotos()

        assert resultado == {
            "success": False,
            "error": "Error al registrar fotos: La orden no existe",
        }
        db.rollback.assert_called_once()

    def test_error_generico_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.callproc.side_effect = Exception("fallo simulado")

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, Foto_orden_servicio=[]
        ).registrar_fotos()

        assert resultado == {
            "success": False,
            "error": "Error al registrar fotos: fallo simulado",
        }


class TestAsignarOrdenEmpleado:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.nextset.return_value = False

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, ID_empleado=ID_EMPLEADO
        ).asignar_orden_empleado()

        assert resultado is True
        assert ultima_sentencia(cursor) == "CALL sp_asignar_orden_servicio(%s, %s);"
        assert cursor.execute.call_args.args[1] == (ID_ORDEN, ID_EMPLEADO)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(
            ID_orden_servicio=ID_ORDEN, ID_empleado=ID_EMPLEADO
        ).asignar_orden_empleado() is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, ID_empleado=ID_EMPLEADO
        ).asignar_orden_empleado()

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestLiberarOrdenEmpleado:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.nextset.return_value = False

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, ID_empleado=ID_EMPLEADO
        ).liberar_orden_empleado()

        assert resultado is True
        assert ultima_sentencia(cursor) == "CALL sp_liberar_orden_servicio(%s, %s);"
        assert cursor.execute.call_args.args[1] == (ID_ORDEN, ID_EMPLEADO)
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(
            ID_orden_servicio=ID_ORDEN, ID_empleado=ID_EMPLEADO
        ).liberar_orden_empleado() is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, ID_empleado=ID_EMPLEADO
        ).liberar_orden_empleado()

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestRegistrarReparacion:

    def test_descripcion_vacia(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, Descripcion_reparacion=""
        ).registrar_reparacion()

        assert resultado == {
            "success": False,
            "error": "El campo Desdescripcion  no puede estar vacío.",
        }
        cursor.execute.assert_not_called()

    def test_descripcion_con_caracteres_invalidos(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN, Descripcion_reparacion="Cambio #"
        ).registrar_reparacion()

        assert resultado["success"] is False
        assert "solo puede contener letras" in resultado["error"]
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(
            ID_orden_servicio=ID_ORDEN,
            Descripcion_reparacion=DESCRIPCION_MINIMA,
        ).registrar_reparacion() == {
            "error": "Error de conexión a la base de datos"
        }

    def test_resultado_exitoso(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"mensaje": "Reparación registrada exitosamente"}
        cursor.nextset.return_value = False

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN,
            ID_empleado=ID_EMPLEADO,
            Descripcion_reparacion=DESCRIPCION_MINIMA,
            lista_repuestos=[{"id": "1", "cantidad": 1}],
        ).registrar_reparacion()

        assert resultado["success"] is True
        assert resultado["mensaje"] == "Reparación registrada exitosamente"
        assert cursor.execute.call_args.args[1] == (
            ID_ORDEN,
            ID_EMPLEADO,
            DESCRIPCION_MINIMA,
            [{"id": "1", "cantidad": 1}],
        )
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_resultado_con_mensaje_de_error(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"mensaje": "La orden ya está cerrada"}
        cursor.nextset.return_value = False

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN,
            Descripcion_reparacion=DESCRIPCION_MINIMA,
        ).registrar_reparacion()

        assert resultado == {
            "error": "La orden ya está cerrada",
            "data": {"mensaje": "La orden ya está cerrada"},
        }

    def test_sin_resultado_devuelve_exito_por_defecto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None
        cursor.nextset.return_value = False

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN,
            Descripcion_reparacion=DESCRIPCION_MINIMA,
        ).registrar_reparacion()

        assert resultado == {
            "success": True,
            "mensaje": "Reparación registrada exitosamente",
        }

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Orden_servicio(
            ID_orden_servicio=ID_ORDEN,
            Descripcion_reparacion=DESCRIPCION_MINIMA,
        ).registrar_reparacion()

        assert resultado == {"error": "Error en la base de datos: fallo simulado"}
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestCrearOrden:

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"id_cliente": ""},
                "El ID del cliente es obligatorio.",
                id="cliente-vacio",
            ),
            pytest.param(
                {"id_cliente": "1234abc"},
                "La cédula debe contener solo números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"id_cliente": "123456"},
                "La cédula debe tener 7 u 8 dígitos.",
                id="cedula-corta",
            ),
            pytest.param(
                {"id_cliente": "123456789"},
                "La cédula debe tener 7 u 8 dígitos.",
                id="cedula-larga",
            ),
            pytest.param(
                {"id_cliente": "V-12345678-9", "tipo_cliente": "juridico"},
                "El RIF debe tener el formato J-12345678-9 o E-12345678-9.",
                id="rif-invalido",
            ),
            pytest.param(
                {"descripcion": ""},
                "La descripción del problema es obligatoria.",
                id="descripcion-vacia",
            ),
            pytest.param(
                {"descripcion": "D" * 301},
                "La descripción no puede exceder 300 caracteres.",
                id="descripcion-larga",
            ),
            pytest.param(
                {"id_equipo": ""},
                "El IMEI del equipo es obligatorio.",
                id="imei-vacio",
            ),
            pytest.param(
                {"id_equipo": "12345abcde12345"},
                "El IMEI debe ser un número.",
                id="imei-no-numerico",
            ),
            pytest.param(
                {"id_equipo": "12345678901234"},
                "El IMEI debe tener exactamente 15 dígitos.",
                id="imei-corto",
            ),
            pytest.param(
                {"color": ""},
                "El color del equipo es obligatorio.",
                id="color-vacio",
            ),
            pytest.param(
                {"capacidad": ""},
                "La capacidad del equipo es obligatoria.",
                id="capacidad-vacia",
            ),
            pytest.param(
                {"id_modelo": "", "modelo_custom": ""},
                "Debes seleccionar un modelo o escribir uno personalizado.",
                id="sin-modelo",
            ),
        ],
    )
    def test_validaciones_de_negocio(self, conexion_falsa, cambios, esperado):
        db, cursor = conexion_falsa

        with pytest.raises(Exception, match=esperado):
            crear_orden_valida(**cambios)

        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(Exception, match="Error al conectar con la base de datos."):
            crear_orden_valida()

    def test_cliente_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        with pytest.raises(Exception, match="no existe en la base de datos"):
            crear_orden_valida()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_equipo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_cliente": CEDULA_MAXIMA},  # cliente existe
            None,  # equipo no existe
        ]

        with pytest.raises(
            Exception, match=f"El equipo con IMEI {IMEI} no existe"
        ):
            crear_orden_valida()

    def test_modelo_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_cliente": CEDULA_MAXIMA},
            {"ID_equipo": IMEI},
            None,
        ]

        with pytest.raises(Exception, match=f"El modelo con ID {ID_MODELO} no existe"):
            crear_orden_valida()

    def test_orden_creada_con_primeros_consecutivos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_cliente": CEDULA_MAXIMA},
            {"ID_equipo": IMEI},
            {"ID_producto": ID_MODELO},
            {"max_id": None},
            {"max_id": None},
        ]

        resultado = crear_orden_valida()

        assert resultado == "OS0000001"
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any("INSERT INTO Orden_servicio" in sql for sql in sentencias)
        assert any("INSERT INTO Interaccion" in sql for sql in sentencias)
        insert_interaccion = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Interaccion" in llamada.args[0]
        )
        assert insert_interaccion == (
            "INT000001",
            "OS0000001",
            ID_EMPLEADO,
            "Pendiente",
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_orden_creada_incrementa_consecutivos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_cliente": CEDULA_MAXIMA},
            {"ID_equipo": IMEI},
            {"ID_producto": ID_MODELO},
            {"max_id": "OS0000005"},
            {"max_id": "INT000010"},
        ]

        resultado = crear_orden_valida()

        assert resultado == "OS0000006"
        insert_interaccion = next(
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
            if "INSERT INTO Interaccion" in llamada.args[0]
        )
        assert insert_interaccion[0] == "INT000011"

    def test_cliente_con_rif_con_guiones(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_cliente": RIF_VALIDO},
            {"ID_equipo": IMEI},
            {"ID_producto": ID_MODELO},
            {"max_id": None},
            {"max_id": None},
        ]

        resultado = crear_orden_valida(
            id_cliente=RIF_VALIDO, tipo_cliente="juridico"
        )

        assert resultado == "OS0000001"
        primera = cursor.execute.call_args_list[0]
        assert primera.args[1] == (RIF_VALIDO, RIF_SIN_GUIONES)

    def test_cliente_rif_sin_guiones(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_cliente": RIF_VALIDO},
            {"ID_equipo": IMEI},
            {"ID_producto": ID_MODELO},
            {"max_id": None},
            {"max_id": None},
        ]

        crear_orden_valida(id_cliente=RIF_SIN_GUIONES, tipo_cliente="juridico")

        primera = cursor.execute.call_args_list[0]
        assert primera.args[1] == (RIF_SIN_GUIONES, RIF_VALIDO)

    def test_busca_en_cliente_juridico_si_no_esta_en_cliente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,  # no está en Cliente
            {"ID_cliente": CEDULA_MAXIMA},  # sí en Cliente_juridico
            {"ID_equipo": IMEI},
            {"ID_producto": ID_MODELO},
            {"max_id": None},
            {"max_id": None},
        ]

        resultado = crear_orden_valida()

        assert resultado == "OS0000001"
        assert "FROM Cliente_juridico" in cursor.execute.call_args_list[1].args[0]

    def test_modelo_personalizado_no_verifica_producto(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_cliente": CEDULA_MAXIMA},
            {"ID_equipo": IMEI},
            {"max_id": None},
            {"max_id": None},
        ]

        resultado = crear_orden_valida(id_modelo="", modelo_custom="Otro modelo")

        assert resultado == "OS0000001"
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert not any("FROM Producto WHERE ID_producto" in sql for sql in sentencias)

    def test_error_de_bd_hace_rollback_y_propaga(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_cliente": CEDULA_MAXIMA},
            {"ID_equipo": IMEI},
            {"ID_producto": ID_MODELO},
            {"max_id": None},
            {"max_id": None},
        ]
        cursor.execute.side_effect = [
            None,  # cliente
            None,  # equipo
            None,  # producto
            None,  # MAX orden
            Exception("fallo simulado"),  # INSERT orden
        ]

        with pytest.raises(Exception, match="fallo simulado"):
            crear_orden_valida()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestListadoOrdenesServicio:

    def test_sin_filtro_de_estados(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"ID_orden": ID_ORDEN}]
        cursor.fetchall.return_value = filas

        resultado = Orden_servicio().listado_ordenes_servicio()

        assert resultado == filas
        assert "WHERE os.Estado_orden_servicio IN" not in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == []
        cierra_recursos(db, cursor)

    def test_con_filtro_de_estados(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Orden_servicio().listado_ordenes_servicio(["Pendiente", "En proceso"])

        assert (
            "WHERE os.Estado_orden_servicio IN (%s,%s)" in ultima_sentencia(cursor)
        )
        assert cursor.execute.call_args.args[1] == ["Pendiente", "En proceso"]

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Orden_servicio().listado_ordenes_servicio() == []

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().listado_ordenes_servicio() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio().listado_ordenes_servicio() == []


class TestDetallesOrden:

    def test_orden_encontrada(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"ID_orden": ID_ORDEN, "Estado": "Pendiente"}
        cursor.fetchone.return_value = esperado

        assert Orden_servicio().detalles_orden(ID_ORDEN) == esperado
        assert cursor.execute.call_args.args[1] == (ID_ORDEN,)
        cierra_recursos(db, cursor)

    def test_orden_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Orden_servicio().detalles_orden(ID_ORDEN) is None

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().detalles_orden(ID_ORDEN) is None

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio().detalles_orden(ID_ORDEN) is None


class TestFotosOrden:

    def test_con_fotos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": ID_FOTO, "foto": RUTA_FOTO}]
        cursor.fetchall.return_value = filas

        assert Orden_servicio().fotos_orden(ID_ORDEN) == filas
        assert cursor.execute.call_args.args[1] == (ID_ORDEN,)
        cierra_recursos(db, cursor)

    def test_sin_fotos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Orden_servicio().fotos_orden(ID_ORDEN) == []

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().fotos_orden(ID_ORDEN) == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio().fotos_orden(ID_ORDEN) == []


class TestActualizarEstado:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = Orden_servicio().actualizar_estado(ID_ORDEN, "En proceso")

        assert resultado is True
        assert ultima_sentencia(cursor) == (
            "UPDATE Orden_servicio SET Estado_orden_servicio = %s "
            "WHERE ID_orden_servicio = %s"
        )
        assert cursor.execute.call_args.args[1] == ("En proceso", ID_ORDEN)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_filas_afectadas(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        assert Orden_servicio().actualizar_estado(ID_ORDEN, "En proceso") is False

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().actualizar_estado(ID_ORDEN, "En proceso") is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Orden_servicio().actualizar_estado(ID_ORDEN, "En proceso")

        assert resultado is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarOrden:

    def test_orden_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Orden_servicio().eliminar_orden(ID_ORDEN) is False
        db.commit.assert_not_called()

    def test_orden_pendiente_se_elimina(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("Pendiente",)

        resultado = Orden_servicio().eliminar_orden(ID_ORDEN)

        assert resultado is True
        sentencias = [llamada.args[0] for llamada in cursor.execute.call_args_list]
        assert any("DELETE FROM Fotos_orden_servicio" in sql for sql in sentencias)
        assert any("DELETE FROM Interaccion" in sql for sql in sentencias)
        assert any("DELETE FROM Orden_servicio" in sql for sql in sentencias)
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_estado_en_minusculas_tambien_es_pendiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = ("pendiente",)

        assert Orden_servicio().eliminar_orden(ID_ORDEN) is True

    def test_estado_en_diccionario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"Estado_orden_servicio": "Pendiente"}

        assert Orden_servicio().eliminar_orden(ID_ORDEN) is True

    @pytest.mark.parametrize(
        "estado",
        [
            pytest.param("Completada", id="completada"),
            pytest.param("En proceso", id="en-proceso"),
            pytest.param("Asignada", id="asignada"),
        ],
    )
    def test_orden_no_pendiente_no_se_elimina(self, conexion_falsa, estado):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (estado,)

        assert Orden_servicio().eliminar_orden(ID_ORDEN) is False
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio().eliminar_orden(ID_ORDEN) is False

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio().eliminar_orden(ID_ORDEN) is False
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestAgregarFotoOrdenServicio:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO,
            ID_orden_servicio=ID_ORDEN,
            Foto_orden_servicio=RUTA_FOTO,
        ).agregar_foto_orden_servicio()

        assert resultado == f"Foto registrada exitosamente con ID {ID_FOTO}"
        assert "INSERT INTO Fotos_orden_servicio" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_FOTO, ID_ORDEN, RUTA_FOTO)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO,
            ID_orden_servicio=ID_ORDEN,
            Foto_orden_servicio=RUTA_FOTO,
        ).agregar_foto_orden_servicio() == "Error al conectar con la base de datos."

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = Orden_servicio(
            ID_foto_orden_servicio=ID_FOTO,
            ID_orden_servicio=ID_ORDEN,
            Foto_orden_servicio=RUTA_FOTO,
        ).agregar_foto_orden_servicio()

        assert resultado == "Error al registrar la foto: fallo simulado"
        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestOrdenesAsignadasTecnico:

    def test_con_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"ID_orden": ID_ORDEN, "Accion": "Asignada"}]
        cursor.fetchall.return_value = filas

        resultado = Orden_servicio(
            ID_empleado=ID_EMPLEADO
        ).ordenes_asignadas_tecnico()

        assert resultado == filas
        assert cursor.execute.call_args.args[1] == (ID_EMPLEADO,)
        assert "i.ID_empleado = %s" in ultima_sentencia(cursor)
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert Orden_servicio(ID_empleado=ID_EMPLEADO).ordenes_asignadas_tecnico() == []

    def test_conexion_caida(self, conexion_caída):
        assert Orden_servicio(ID_empleado=ID_EMPLEADO).ordenes_asignadas_tecnico() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Orden_servicio(ID_empleado=ID_EMPLEADO).ordenes_asignadas_tecnico() == []
