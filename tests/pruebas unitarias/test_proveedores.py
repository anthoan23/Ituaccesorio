"""Pruebas unitarias de la clase Proveedores (app.models.proveedores).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.models.proveedores import Proveedores
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ID_MINIMO = 1
ID_MAXIMO = 999999

RIF_VALIDO = "J-12345678-9"
NOMBRE_MINIMO = "Ab"  # 2 caracteres
NOMBRE_MAXIMO = "P" * 100  # 100 caracteres
TIPO_VALIDO = "Mayorista"
CELULAR_VALIDO = "04121234567"
CORREO_VALIDO = "proveedor@mail.com"
DIRECCION_VALIDA = "Av. Principal, local 1"
LIMITE_CERO = 0
LIMITE_MAXIMO = 999999


def resultado_proveedor(id_proveedor=ID_MAXIMO, estado="OK", mensaje=""):
    """Resultado simulado de las variables de salida del procedure."""
    return {
        "id_proveedor": id_proveedor,
        "estado": estado,
        "mensaje": mensaje,
    }


class TestListarProveedores:

    def test_con_datos_existentes(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [
            {
                "id": ID_MINIMO,
                "rif": RIF_VALIDO,
                "nombre": "Distribuidora Uno",
                "tipo": TIPO_VALIDO,
                "celular": CELULAR_VALIDO,
                "correo": CORREO_VALIDO,
                "direccion": DIRECCION_VALIDA,
                "limite_credito": LIMITE_CERO,
            }
        ]
        cursor.fetchall.return_value = filas

        resultado = Proveedores().listar_proveedores()

        assert resultado == filas
        assert "FROM Proveedor" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == ()
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = None

        assert Proveedores().listar_proveedores() == []

    def test_busqueda_agrega_filtro_y_parametros(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Proveedores().listar_proveedores(q="Distri")

        assert "WHERE (Nombre_proveedor LIKE %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            "%Distri%",
            "%Distri%",
            "%Distri%",
        )

    def test_conexion_caida(self, conexion_caída):
        assert Proveedores().listar_proveedores() == []

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        Proveedores().listar_proveedores()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestSiguienteId:

    def test_devuelve_el_siguiente_id(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (ID_MAXIMO,)

        assert Proveedores()._siguiente_id() == ID_MAXIMO
        assert "MAX(ID_proveedor)" in ultima_sentencia(cursor)

    def test_conexion_caida_lanza_error(self, conexion_caída):
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            Proveedores()._siguiente_id()

    def test_cierra_recursos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        Proveedores()._siguiente_id()

        cierra_recursos(db, cursor)


class TestVerificarExistencia:

    def test_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        assert Proveedores(id_proveedor=ID_MAXIMO).verificar_existencia() is True
        assert "FROM Proveedor WHERE ID_proveedor" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_no_existe(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Proveedores(id_proveedor=ID_MAXIMO).verificar_existencia() is False

    def test_id_cero_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Proveedores().verificar_existencia() is False
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Proveedores(id_proveedor=ID_MAXIMO).verificar_existencia() is False


class TestObtenerProveedor:

    def test_proveedor_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        esperado = {"id": ID_MAXIMO, "nombre": "Distribuidora Uno"}
        cursor.fetchone.return_value = esperado

        assert Proveedores(id_proveedor=ID_MAXIMO).obtener_proveedor() == esperado
        assert "WHERE ID_proveedor = %s" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_proveedor_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert Proveedores(id_proveedor=ID_MAXIMO).obtener_proveedor() is None

    def test_id_cero_no_toca_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa

        assert Proveedores().obtener_proveedor() is None
        cursor.execute.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        assert Proveedores(id_proveedor=ID_MAXIMO).obtener_proveedor() is None


class TestObtenerProveedorConProductosProcedure:

    def test_id_cero(self, conexion_falsa):
        resultado = Proveedores().obtener_proveedor_con_productos_procedure()

        assert resultado == {
            "proveedor": None,
            "productos": [],
            "success": False,
            "error": "ID de proveedor no especificado",
        }

    def test_conexion_caida(self, conexion_caída):
        resultado = Proveedores(
            id_proveedor=ID_MAXIMO
        ).obtener_proveedor_con_productos_procedure()

        assert resultado["success"] is False
        assert resultado["error"] == "No se pudo conectar a la BD"

    def test_devuelve_proveedor_y_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        proveedor = {"id": ID_MAXIMO, "nombre": "Distribuidora Uno"}
        productos = [{"id_modelo": "1", "nombre": "Cargador"}]
        res_proveedor = MagicMock()
        res_proveedor.fetchall.return_value = [proveedor]
        res_productos = MagicMock()
        res_productos.fetchall.return_value = productos
        cursor.stored_results.return_value = [res_proveedor, res_productos]

        resultado = Proveedores(
            id_proveedor=ID_MAXIMO
        ).obtener_proveedor_con_productos_procedure()

        assert resultado == {
            "proveedor": proveedor,
            "productos": productos,
            "success": True,
        }
        cursor.callproc.assert_called_once_with(
            "sp_obtener_proveedor_completo", (ID_MAXIMO,)
        )
        cierra_recursos(db, cursor)

    def test_sin_resultados_devuelve_vacios(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.stored_results.return_value = []

        resultado = Proveedores(
            id_proveedor=ID_MAXIMO
        ).obtener_proveedor_con_productos_procedure()

        assert resultado == {"proveedor": None, "productos": [], "success": True}

    def test_varios_proveedores_devuelve_lista(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id": 1}, {"id": 2}]
        res_proveedor = MagicMock()
        res_proveedor.fetchall.return_value = filas
        cursor.stored_results.return_value = [res_proveedor]

        resultado = Proveedores(
            id_proveedor=ID_MAXIMO
        ).obtener_proveedor_con_productos_procedure()

        assert resultado["proveedor"] == filas

    def test_error_de_bd(self, conexion_falsa):
        import mysql.connector

        db, cursor = conexion_falsa
        cursor.callproc.side_effect = mysql.connector.Error("fallo simulado")

        resultado = Proveedores(
            id_proveedor=ID_MAXIMO
        ).obtener_proveedor_con_productos_procedure()

        assert resultado["success"] is False
        assert "fallo simulado" in resultado["error"]


class TestCrearProveedor:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (nombre): no existe; 2ª (RIF): no existe; 3ª: resultado del CALL
        cursor.fetchone.side_effect = [None, None, resultado_proveedor()]
        proveedor = Proveedores(
            rif=RIF_VALIDO,
            nombre=NOMBRE_MINIMO,
            tipo=TIPO_VALIDO,
            celular=CELULAR_VALIDO,
            correo=CORREO_VALIDO,
            direccion=DIRECCION_VALIDA,
            limite_credito=LIMITE_CERO,
        )

        resultado = proveedor.crear_proveedor()

        assert resultado == ID_MAXIMO
        assert proveedor.id_proveedor == ID_MAXIMO
        cursor.callproc.assert_called_once()
        assert cursor.callproc.call_args.args[0] == "sp_registrar_proveedor"
        assert cursor.callproc.call_args.args[1][1] == NOMBRE_MINIMO
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_nombre_vacio(self, conexion_falsa):
        with pytest.raises(ValueError, match="El nombre del proveedor es obligatorio"):
            Proveedores(nombre="").crear_proveedor()

    def test_limite_negativo(self, conexion_falsa):
        with pytest.raises(ValueError, match="no puede ser negativo"):
            Proveedores(nombre=NOMBRE_MINIMO, limite_credito=-1).crear_proveedor()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            Proveedores(nombre=NOMBRE_MINIMO).crear_proveedor()

    def test_nombre_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = (1,)

        with pytest.raises(ValueError, match="Ya existe un proveedor con el nombre"):
            Proveedores(nombre="Distribuidora Uno").crear_proveedor()

        db.commit.assert_not_called()
        db.rollback.assert_called_once()

    def test_rif_duplicado(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (nombre): no existe; 2ª (RIF): sí existe
        cursor.fetchone.side_effect = [None, (1,)]

        with pytest.raises(ValueError, match="Ya existe un proveedor con el RIF"):
            Proveedores(nombre=NOMBRE_MINIMO, rif=RIF_VALIDO).crear_proveedor()

        db.rollback.assert_called_once()

    def test_procedure_no_devuelve_informacion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, None]

        with pytest.raises(RuntimeError, match="no devolvió información"):
            Proveedores(nombre=NOMBRE_MINIMO).crear_proveedor()

        db.rollback.assert_called_once()

    def test_procedure_devuelve_estado_erroneo(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            None,
            resultado_proveedor(estado="ERROR", mensaje="RIF inválido"),
        ]

        with pytest.raises(ValueError, match="RIF inválido"):
            Proveedores(nombre=NOMBRE_MINIMO).crear_proveedor()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [None, resultado_proveedor()]

        with patch("app.models.proveedores.Bitacora") as bitacora:
            Proveedores(
                nombre=NOMBRE_MINIMO, usuario_id="USR-001"
            ).crear_proveedor()

        bitacora.return_value.registrar.assert_called_once()


class TestActualizarProveedor:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = Proveedores(
            id_proveedor=ID_MAXIMO,
            nombre=NOMBRE_MINIMO,
            rif=RIF_VALIDO,
            tipo=TIPO_VALIDO,
            celular=CELULAR_VALIDO,
            correo=CORREO_VALIDO,
            direccion=DIRECCION_VALIDA,
            limite_credito=LIMITE_MAXIMO,
        ).actualizar_proveedor()

        assert resultado is True
        assert "UPDATE Proveedor" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (
            RIF_VALIDO,
            NOMBRE_MINIMO,
            TIPO_VALIDO,
            CELULAR_VALIDO,
            CORREO_VALIDO,
            DIRECCION_VALIDA,
            LIMITE_MAXIMO,
            ID_MAXIMO,
        )
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_sin_filas_afectadas_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        assert Proveedores(
            id_proveedor=ID_MAXIMO, nombre=NOMBRE_MINIMO
        ).actualizar_proveedor() is False

    def test_id_cero(self, conexion_falsa):
        with pytest.raises(ValueError, match="ID del proveedor es requerido"):
            Proveedores(nombre=NOMBRE_MINIMO).actualizar_proveedor()

    def test_nombre_vacio(self, conexion_falsa):
        with pytest.raises(ValueError, match="El nombre del proveedor es obligatorio"):
            Proveedores(id_proveedor=ID_MAXIMO, nombre="").actualizar_proveedor()

    def test_limite_negativo(self, conexion_falsa):
        with pytest.raises(ValueError, match="no puede ser negativo"):
            Proveedores(
                id_proveedor=ID_MAXIMO, nombre=NOMBRE_MINIMO, limite_credito=-5
            ).actualizar_proveedor()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            Proveedores(
                id_proveedor=ID_MAXIMO, nombre=NOMBRE_MINIMO
            ).actualizar_proveedor()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            Proveedores(
                id_proveedor=ID_MAXIMO, nombre=NOMBRE_MINIMO
            ).actualizar_proveedor()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        with patch("app.models.proveedores.Bitacora") as bitacora:
            Proveedores(
                id_proveedor=ID_MAXIMO,
                nombre=NOMBRE_MINIMO,
                usuario_id="USR-001",
            ).actualizar_proveedor()

        bitacora.return_value.registrar.assert_called_once()


class TestEliminarProveedor:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = Proveedores(id_proveedor=ID_MAXIMO).eliminar_proveedor()

        assert resultado is True
        assert ultima_sentencia(cursor) == (
            "DELETE FROM Proveedor WHERE ID_proveedor = %s"
        )
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_sin_filas_afectadas_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        assert Proveedores(id_proveedor=ID_MAXIMO).eliminar_proveedor() is False

    def test_id_cero(self, conexion_falsa):
        with pytest.raises(ValueError, match="ID del proveedor es requerido"):
            Proveedores().eliminar_proveedor()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            Proveedores(id_proveedor=ID_MAXIMO).eliminar_proveedor()

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            Proveedores(id_proveedor=ID_MAXIMO).eliminar_proveedor()

        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestTieneRelacionesActivas:

    def test_id_cero(self, conexion_falsa):
        assert Proveedores().tiene_relaciones_activas() == (
            True,
            "ID de proveedor no especificado",
        )

    def test_conexion_caida(self, conexion_caída):
        assert Proveedores(id_proveedor=ID_MAXIMO).tiene_relaciones_activas() == (
            True,
            "No se pudo conectar a la base de datos",
        )

    def test_tiene_ordenes_de_compra(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = {"total": 3}

        resultado = Proveedores(id_proveedor=ID_MAXIMO).tiene_relaciones_activas()

        assert resultado == (
            True,
            "No se puede eliminar el proveedor porque tiene 3 órdenes de compra asociadas.",
        )
        assert "FROM Orden_compra" in cursor.execute.call_args_list[0].args[0]

    def test_tiene_productos_asociados(self, conexion_falsa):
        db, cursor = conexion_falsa
        # 1ª consulta (órdenes): 0; 2ª (suministros): 2
        cursor.fetchone.side_effect = [{"total": 0}, {"total": 2}]

        resultado = Proveedores(id_proveedor=ID_MAXIMO).tiene_relaciones_activas()

        assert resultado == (
            True,
            "No se puede eliminar el proveedor porque tiene 2 productos asociados.",
        )

    def test_sin_relaciones(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [{"total": 0}, {"total": 0}]

        assert Proveedores(id_proveedor=ID_MAXIMO).tiene_relaciones_activas() == (
            False,
            "",
        )

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Proveedores(id_proveedor=ID_MAXIMO).tiene_relaciones_activas() == (
            True,
            "Error al verificar relaciones del proveedor",
        )


class TestObtenerDetalleRelaciones:

    def test_id_cero(self, conexion_falsa):
        assert Proveedores().obtener_detalle_relaciones() == {}

    def test_conexion_caida(self, conexion_caída):
        assert Proveedores(id_proveedor=ID_MAXIMO).obtener_detalle_relaciones() == {}

    def test_devuelve_ordenes_y_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        ordenes = [{"id": 1, "estado": "Pendiente"}]
        productos = [{"id_modelo": "1", "nombre": "Cargador", "costo": 5}]
        cursor.fetchall.side_effect = [ordenes, productos]

        resultado = Proveedores(id_proveedor=ID_MAXIMO).obtener_detalle_relaciones()

        assert resultado == {"ordenes": ordenes, "productos": productos}
        cierra_recursos(db, cursor)

    def test_sin_relaciones_devuelve_listas_vacias(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.side_effect = [None, None]

        assert Proveedores(id_proveedor=ID_MAXIMO).obtener_detalle_relaciones() == {
            "ordenes": [],
            "productos": [],
        }

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert Proveedores(id_proveedor=ID_MAXIMO).obtener_detalle_relaciones() == {}


class TestListarProductosPorProveedor:

    def test_id_cero(self, conexion_falsa):
        assert Proveedores().listar_productos_por_proveedor() == []

    def test_conexion_caida(self, conexion_caída):
        assert Proveedores(id_proveedor=ID_MAXIMO).listar_productos_por_proveedor() == []

    def test_con_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        filas = [{"id_modelo": "1", "modelo_nombre": "Cargador"}]
        cursor.fetchall.return_value = filas

        assert Proveedores(
            id_proveedor=ID_MAXIMO
        ).listar_productos_por_proveedor() == filas
        assert "FROM Suministra" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO,)

    def test_sin_productos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = None

        assert Proveedores(id_proveedor=ID_MAXIMO).listar_productos_por_proveedor() == []


class TestUpsertProductoProveedor:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = Proveedores(
            id_proveedor=ID_MAXIMO
        ).upsert_producto_proveedor(id_modelo="1", costo=10)

        assert resultado is True
        assert "INSERT INTO Suministra" in ultima_sentencia(cursor)
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO, "1", 10)
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_sin_filas_afectadas_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        assert Proveedores(
            id_proveedor=ID_MAXIMO
        ).upsert_producto_proveedor(id_modelo="1", costo=10) is False

    def test_id_proveedor_cero(self, conexion_falsa):
        with pytest.raises(ValueError, match="ID del proveedor es requerido"):
            Proveedores().upsert_producto_proveedor(id_modelo="1", costo=10)

    def test_id_modelo_vacio(self, conexion_falsa):
        with pytest.raises(ValueError, match="ID del modelo es requerido"):
            Proveedores(id_proveedor=ID_MAXIMO).upsert_producto_proveedor(costo=10)

    def test_costo_negativo(self, conexion_falsa):
        with pytest.raises(ValueError, match="no puede ser negativo"):
            Proveedores(id_proveedor=ID_MAXIMO).upsert_producto_proveedor(
                id_modelo="1", costo=-1
            )

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            Proveedores(id_proveedor=ID_MAXIMO).upsert_producto_proveedor(
                id_modelo="1", costo=10
            )

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            Proveedores(id_proveedor=ID_MAXIMO).upsert_producto_proveedor(
                id_modelo="1", costo=10
            )

        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestEliminarProductoProveedor:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 1

        resultado = Proveedores(
            id_proveedor=ID_MAXIMO
        ).eliminar_producto_proveedor(id_modelo="1")

        assert resultado is True
        assert ultima_sentencia(cursor) == (
            "DELETE FROM Suministra WHERE ID_proveedor = %s AND ID_producto = %s"
        )
        assert cursor.execute.call_args.args[1] == (ID_MAXIMO, "1")
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_sin_filas_afectadas_devuelve_false(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.rowcount = 0

        assert Proveedores(
            id_proveedor=ID_MAXIMO
        ).eliminar_producto_proveedor(id_modelo="1") is False

    def test_id_proveedor_cero(self, conexion_falsa):
        with pytest.raises(ValueError, match="ID del proveedor es requerido"):
            Proveedores().eliminar_producto_proveedor(id_modelo="1")

    def test_id_modelo_vacio(self, conexion_falsa):
        with pytest.raises(ValueError, match="ID del modelo es requerido"):
            Proveedores(id_proveedor=ID_MAXIMO).eliminar_producto_proveedor()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            Proveedores(id_proveedor=ID_MAXIMO).eliminar_producto_proveedor(
                id_modelo="1"
            )

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            Proveedores(id_proveedor=ID_MAXIMO).eliminar_producto_proveedor(
                id_modelo="1"
            )

        db.rollback.assert_called_once()
        db.commit.assert_not_called()


class TestCrearProveedorConProductos:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = Proveedores(
            id_proveedor=ID_MAXIMO,
            rif=RIF_VALIDO,
            nombre=NOMBRE_MINIMO,
            limite_credito=LIMITE_CERO,
        ).crear_proveedor_con_productos(
            [{"id_modelo": "1", "costo": 10}, {"id_modelo": "2", "costo": 20}]
        )

        assert resultado == ID_MAXIMO
        assert "INSERT INTO Proveedor" in cursor.execute.call_args_list[0].args[0]
        assert "INSERT INTO Suministra" in cursor.executemany.call_args.args[0]
        assert cursor.executemany.call_args.args[1] == [
            (ID_MAXIMO, "1", 10),
            (ID_MAXIMO, "2", 20),
        ]
        db.commit.assert_called_once()
        cierra_recursos(db, cursor)

    def test_sin_productos_no_ejecuta_executemany(self, conexion_falsa):
        db, cursor = conexion_falsa

        Proveedores(
            id_proveedor=ID_MAXIMO, nombre=NOMBRE_MINIMO
        ).crear_proveedor_con_productos([])

        cursor.executemany.assert_not_called()
        db.commit.assert_called_once()

    def test_genera_id_si_no_se_indica(self, conexion_falsa):
        db, cursor = conexion_falsa
        proveedor = Proveedores(nombre=NOMBRE_MINIMO)

        with patch.object(
            Proveedores, "_siguiente_id", return_value=ID_MAXIMO
        ) as siguiente:
            assert proveedor.crear_proveedor_con_productos([]) == ID_MAXIMO

        siguiente.assert_called_once()
        assert proveedor.id_proveedor == ID_MAXIMO

    def test_nombre_vacio(self, conexion_falsa):
        with pytest.raises(ValueError, match="El nombre del proveedor es obligatorio"):
            Proveedores().crear_proveedor_con_productos([])

    def test_limite_negativo(self, conexion_falsa):
        with pytest.raises(ValueError, match="no puede ser negativo"):
            Proveedores(
                nombre=NOMBRE_MINIMO, limite_credito=-1
            ).crear_proveedor_con_productos([])

    def test_costo_negativo_de_un_producto(self, conexion_falsa):
        db, cursor = conexion_falsa

        with pytest.raises(ValueError, match="no puede ser negativo"):
            Proveedores(
                id_proveedor=ID_MAXIMO, nombre=NOMBRE_MINIMO
            ).crear_proveedor_con_productos([{"id_modelo": "1", "costo": -1}])

        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        with pytest.raises(RuntimeError, match="No se pudo conectar"):
            Proveedores(nombre=NOMBRE_MINIMO).crear_proveedor_con_productos([])

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            Proveedores(
                id_proveedor=ID_MAXIMO, nombre=NOMBRE_MINIMO
            ).crear_proveedor_con_productos([])

        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_si_hay_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.proveedores.Bitacora") as bitacora:
            Proveedores(
                id_proveedor=ID_MAXIMO,
                nombre=NOMBRE_MINIMO,
                usuario_id="USR-001",
            ).crear_proveedor_con_productos([])

        bitacora.return_value.registrar.assert_called_once()
