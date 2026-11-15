"""Pruebas de integración de la clase Orden_servicio contra MySQL real."""
import pytest

from app.models.ordenes_servicio import Orden_servicio
from app.models.database import conectar
from seed_helpers import (
    crear_cliente_temporal,
    crear_existencia_temporal,
    crear_producto_temporal,
    eliminar_cliente_temporal,
    eliminar_existencia_temporal,
    eliminar_producto_temporal,
)

EMPLEADO_ADMIN = "12345678"
CLASE_TELEFONO = "1"
MARCA_SEED = "3"

# Datos fijos por prueba (rangos reservados para este módulo).
CEDULA_CLIENTE = "82000001"
CEDULA_CLIENTE_INEXISTENTE = "82999999"
IMEI_EQUIPO = "861000000000001"
IMEI_INEXISTENTE = "861999999999999"
ID_FOTO = "FOT9000001"
ID_FOTO_INEXISTENTE = "FOT999999"


# ==================== HELPERS LOCALES (solo para este módulo) ====================


def _crear_equipo(
    id_producto: str, imei: str, color: str = "Negro", capacidad: str = "128GB"
) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Equipo (ID_equipo, ID_producto, Color, Capacidad, Clave, Patron) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (imei, id_producto, color, capacidad, 1234, "1-2-3-4"),
        )
        db.commit()
        return imei
    finally:
        cursor.close()
        db.close()


def _eliminar_equipo(imei: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Equipo WHERE ID_equipo = %s", (imei,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _siguiente_id_orden_servicio(cursor) -> str:
    cursor.execute("SELECT MAX(ID_orden_servicio) FROM Orden_servicio")
    ultimo = cursor.fetchone()[0]
    if not ultimo or not str(ultimo).startswith("OS"):
        numero = 0
    else:
        try:
            numero = int(str(ultimo)[2:])
        except ValueError:
            numero = 0
    return f"OS{str(numero + 1).zfill(7)}"


def _siguiente_id_interaccion(cursor) -> str:
    cursor.execute("SELECT MAX(ID_interaccion) FROM Interaccion")
    ultimo = cursor.fetchone()[0]
    if not ultimo or not str(ultimo).startswith("INT"):
        numero = 0
    else:
        try:
            numero = int(str(ultimo)[3:])
        except ValueError:
            numero = 0
    return f"INT{str(numero + 1).zfill(6)}"


def _crear_orden_servicio(
    id_cliente: str,
    id_equipo: str,
    descripcion: str = "Pantalla rota de prueba",
    estado: str = "Pendiente",
) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        id_orden = _siguiente_id_orden_servicio(cursor)
        cursor.execute(
            "INSERT INTO Orden_servicio (ID_orden_servicio, ID_equipo, ID_cliente, "
            "Estado_orden_servicio, Descripcion_reparacion, Nota_orden_servicio, Fecha_entrada) "
            "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (id_orden, id_equipo, id_cliente, estado, descripcion, None),
        )
        cursor.execute(
            "INSERT INTO Interaccion (ID_interaccion, ID_orden_servicio, ID_empleado, Accion) "
            "VALUES (%s, %s, %s, %s)",
            (_siguiente_id_interaccion(cursor), id_orden, EMPLEADO_ADMIN, estado),
        )
        db.commit()
        return id_orden
    finally:
        cursor.close()
        db.close()


def _eliminar_orden_servicio(id_orden: str) -> None:
    """Borra tests, interacciones, fotos, repuestos y la orden."""
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE tri FROM Test_realizados_interaccion tri "
            "INNER JOIN Interaccion i ON tri.ID_interaccion = i.ID_interaccion "
            "WHERE i.ID_orden_servicio = %s",
            (id_orden,),
        )
        cursor.execute(
            "DELETE t FROM Test t "
            "INNER JOIN Test_realizados_interaccion tri ON t.ID_test = tri.ID_test "
            "INNER JOIN Interaccion i ON tri.ID_interaccion = i.ID_interaccion "
            "WHERE i.ID_orden_servicio = %s",
            (id_orden,),
        )
        cursor.execute(
            "DELETE ru FROM Repuestos_usados ru WHERE ru.ID_orden_servicio = %s",
            (id_orden,),
        )
        cursor.execute(
            "DELETE FROM Interaccion WHERE ID_orden_servicio = %s", (id_orden,)
        )
        cursor.execute(
            "DELETE FROM Fotos_orden_servicio WHERE ID_orden_servicio = %s",
            (id_orden,),
        )
        cursor.execute(
            "DELETE FROM Orden_servicio WHERE ID_orden_servicio = %s", (id_orden,)
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _estado_de_orden(id_orden: str) -> str:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT Estado_orden_servicio FROM Orden_servicio WHERE ID_orden_servicio = %s",
            (id_orden,),
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        db.close()


def _quitar_repuesto_usado(id_inventario: str) -> None:
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Repuestos_usados WHERE ID_inventario = %s",
            (id_inventario,),
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


@pytest.fixture
def taller():
    """Cliente + producto + equipo (IMEI fijo). Limpia al final."""
    id_producto = None
    try:
        crear_cliente_temporal(
            CEDULA_CLIENTE, nombre="Cliente", apellido="Taller"
        )
        id_producto = crear_producto_temporal(
            nombre="Prod Integra Taller", clase=CLASE_TELEFONO, marca=MARCA_SEED
        )
        imei = _crear_equipo(id_producto, IMEI_EQUIPO)
        yield {"cliente_id": CEDULA_CLIENTE, "id_producto": id_producto, "imei": imei}
    finally:
        _eliminar_equipo(IMEI_EQUIPO)
        if id_producto:
            eliminar_producto_temporal(id_producto)
        eliminar_cliente_temporal(CEDULA_CLIENTE)


@pytest.fixture
def orden_taller(taller):
    """Orden de servicio pendiente lista para operar."""
    info = taller
    id_orden = _crear_orden_servicio(info["cliente_id"], info["imei"])
    yield {**info, "id_orden": id_orden}
    _eliminar_orden_servicio(id_orden)


class TestListarModelosTelefonos:

    def test_incluye_producto_temporal_de_clase_telefono(self, taller):
        info = taller
        modelos = Orden_servicio().listar_modelos_telefonos()
        fila = next(
            (m for m in modelos if str(m["id"]) == info["id_producto"]), None
        )

        assert fila is not None
        assert fila["nombre"] == "Prod Integra Taller"
        assert fila["clase_nombre"] == "Telefono"


class TestCrearOrden:

    def test_datos_validos(self, taller):
        info = taller
        id_orden = None
        try:
            id_orden = Orden_servicio(ID_empleado=int(EMPLEADO_ADMIN)).crear_orden(
                id_cliente=info["cliente_id"],
                id_equipo=info["imei"],
                id_modelo=info["id_producto"],
                descripcion="Pantalla rota de prueba",
                nota="Sin nota",
                color="Negro",
                capacidad="128GB",
            )

            assert id_orden.startswith("OS")
            orden = Orden_servicio(ID_orden_servicio=id_orden).consultar_orden()
            assert orden["Estado"] == "Pendiente"
            assert orden["Descripcion"] == "Pantalla rota de prueba"
            assert orden["nombre_cliente"] == "Cliente Taller"
        finally:
            if id_orden:
                _eliminar_orden_servicio(id_orden)

    def test_registra_interaccion_inicial(self, orden_taller):
        info = orden_taller
        empleados = Orden_servicio().empleados_asignados(info["id_orden"])

        assert len(empleados) == 1
        assert str(empleados[0]["ID_empleado"]) == EMPLEADO_ADMIN
        assert empleados[0]["Accion"] == "Pendiente"

    def test_cliente_inexistente(self, taller):
        info = taller
        with pytest.raises(Exception) as exc:
            Orden_servicio(ID_empleado=int(EMPLEADO_ADMIN)).crear_orden(
                id_cliente=CEDULA_CLIENTE_INEXISTENTE,
                id_equipo=info["imei"],
                id_modelo=info["id_producto"],
                descripcion="Pantalla rota",
                color="Negro",
                capacidad="128GB",
            )

        assert "no existe en la base de datos" in str(exc.value)

    def test_equipo_inexistente(self, taller):
        info = taller
        with pytest.raises(Exception) as exc:
            Orden_servicio(ID_empleado=int(EMPLEADO_ADMIN)).crear_orden(
                id_cliente=info["cliente_id"],
                id_equipo=IMEI_INEXISTENTE,
                id_modelo=info["id_producto"],
                descripcion="Pantalla rota",
                color="Negro",
                capacidad="128GB",
            )

        assert str(exc.value) == (
            f"El equipo con IMEI {IMEI_INEXISTENTE} no existe en la base de datos."
        )

    def test_modelo_inexistente(self, taller):
        info = taller
        with pytest.raises(Exception) as exc:
            Orden_servicio(ID_empleado=int(EMPLEADO_ADMIN)).crear_orden(
                id_cliente=info["cliente_id"],
                id_equipo=info["imei"],
                id_modelo="999999",
                descripcion="Pantalla rota",
                color="Negro",
                capacidad="128GB",
            )

        assert str(exc.value) == "El modelo con ID 999999 no existe en la base de datos."

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"id_cliente": ""},
                "El ID del cliente es obligatorio.",
                id="cliente-vacio",
            ),
            pytest.param(
                {"id_cliente": "12345a"},
                "La cédula debe contener solo números.",
                id="cedula-no-numerica",
            ),
            pytest.param(
                {"id_cliente": "12345"},
                "La cédula debe tener 7 u 8 dígitos.",
                id="cedula-demasiado-corta",
            ),
            pytest.param(
                {"id_cliente": "123456789"},
                "La cédula debe tener 7 u 8 dígitos.",
                id="cedula-demasiado-larga",
            ),
            pytest.param(
                {"descripcion": ""},
                "La descripción del problema es obligatoria.",
                id="descripcion-vacia",
            ),
            pytest.param(
                {"descripcion": "D" * 301},
                "La descripción no puede exceder 300 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                {"id_equipo": ""},
                "El IMEI del equipo es obligatorio.",
                id="imei-vacio",
            ),
            pytest.param(
                {"id_equipo": "12345abc"},
                "El IMEI debe ser un número.",
                id="imei-no-numerico",
            ),
            pytest.param(
                {"id_equipo": "12345"},
                "El IMEI debe tener exactamente 15 dígitos.",
                id="imei-demasiado-corto",
            ),
            pytest.param(
                {"id_equipo": "1234567890123456"},
                "El IMEI debe tener exactamente 15 dígitos.",
                id="imei-demasiado-largo",
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
                {"id_modelo": "", "modelo_custom": None},
                "Debes seleccionar un modelo o escribir uno personalizado.",
                id="sin-modelo",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        datos = {
            "id_cliente": CEDULA_CLIENTE,
            "id_equipo": "123456789012345",
            "id_modelo": "1",
            "descripcion": "Pantalla rota",
            "color": "Negro",
            "capacidad": "128GB",
        }
        datos.update(cambios)
        with pytest.raises(Exception) as exc:
            Orden_servicio(ID_empleado=int(EMPLEADO_ADMIN)).crear_orden(**datos)

        assert str(exc.value) == esperado


class TestConsultarOrden:

    def test_orden_existente(self, orden_taller):
        info = orden_taller
        orden = Orden_servicio(ID_orden_servicio=info["id_orden"]).consultar_orden()

        assert orden["ID_orden_servicio"] == info["id_orden"]
        assert orden["Estado"] == "Pendiente"
        assert orden["nombre_cliente"] == "Cliente Taller"
        assert orden["Modelo"] == "Prod Integra Taller"
        assert orden["fotos"] == []

    def test_orden_inexistente(self):
        assert Orden_servicio(ID_orden_servicio="OS9999999").consultar_orden() is None

    @pytest.mark.parametrize(
        "id_orden, esperado",
        [
            pytest.param(
                "",
                "El campo ID dela orden no puede estar vacío.",
                id="id-vacio",
            ),
            pytest.param(
                "OS 12345#",
                "El campo ID dela orden solo puede contener letras, números, acentos y espacios.",
                id="id-caracteres-invalidos",
            ),
            pytest.param(
                "O" * 11,
                "El campo ID dela orden no puede tener más de 10 caracteres.",
                id="id-demasiado-largo",
            ),
        ],
    )
    def test_id_invalido(self, id_orden, esperado):
        assert Orden_servicio(ID_orden_servicio=id_orden).consultar_orden() == esperado

    def test_detalles_orden(self, orden_taller):
        info = orden_taller
        detalles = Orden_servicio().detalles_orden(info["id_orden"])

        assert detalles["ID_orden"] == info["id_orden"]
        assert detalles["Nombre_completo"] == "Cliente Taller"
        assert detalles["Modelo"] == "Prod Integra Taller"
        assert detalles["Equipo"] == IMEI_EQUIPO
        assert detalles["Color"] == "Negro"

    def test_detalles_orden_inexistente(self):
        assert Orden_servicio().detalles_orden("OS9999999") is None


class TestListadoOrdenesServicio:

    def test_incluye_orden_pendiente_con_filtro(self, orden_taller):
        info = orden_taller
        listado = Orden_servicio().listado_ordenes_servicio(estados=["Pendiente"])
        fila = next(
            (o for o in listado if o["ID_orden"] == info["id_orden"]), None
        )

        assert fila is not None
        assert fila["Nombre_completo"] == "Cliente Taller"
        assert fila["Modelo"] == "Prod Integra Taller"

    def test_excluye_orden_con_otro_estado(self, orden_taller):
        info = orden_taller
        listado = Orden_servicio().listado_ordenes_servicio(estados=["Completada"])

        assert all(o["ID_orden"] != info["id_orden"] for o in listado)

    def test_sin_filtro_incluye_todos_los_estados(self, orden_taller):
        info = orden_taller
        listado = Orden_servicio().listado_ordenes_servicio()

        assert any(o["ID_orden"] == info["id_orden"] for o in listado)


class TestActualizarEstado:

    def test_datos_validos(self, orden_taller):
        info = orden_taller
        assert (
            Orden_servicio().actualizar_estado(info["id_orden"], "En proceso")
            is True
        )
        assert _estado_de_orden(info["id_orden"]) == "En proceso"

    def test_orden_inexistente(self):
        assert Orden_servicio().actualizar_estado("OS9999999", "En proceso") is False


class TestAsignacion:

    def test_asignar_orden(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"], ID_empleado=int(EMPLEADO_ADMIN)
        )
        assert modelo.asignar_orden_empleado() is True

        assert _estado_de_orden(info["id_orden"]) == "Asignada"

        empleados = Orden_servicio().empleados_asignados(info["id_orden"])
        asignaciones = [e for e in empleados if e["Accion"] == "Asignada"]
        assert len(asignaciones) == 1
        assert str(asignaciones[0]["ID_empleado"]) == EMPLEADO_ADMIN

        tecnicos = Orden_servicio(ID_empleado=int(EMPLEADO_ADMIN)).listar_ordenes_tecnico()
        assert any(o["id_orden"] == info["id_orden"] for o in tecnicos)

        asignadas = Orden_servicio(
            ID_empleado=int(EMPLEADO_ADMIN)
        ).ordenes_asignadas_tecnico()
        assert any(o["ID_orden"] == info["id_orden"] for o in asignadas)

    def test_asignar_orden_ya_asignada_falla(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"], ID_empleado=int(EMPLEADO_ADMIN)
        )
        modelo.asignar_orden_empleado()

        # El SP rechaza la segunda asignación
        assert modelo.asignar_orden_empleado() is False

    def test_liberar_orden(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"], ID_empleado=int(EMPLEADO_ADMIN)
        )
        modelo.asignar_orden_empleado()

        assert modelo.liberar_orden_empleado() is True

        assert _estado_de_orden(info["id_orden"]) == "En proceso"

        # Ya no aparece en las órdenes asignadas al técnico
        tecnicos = Orden_servicio(ID_empleado=int(EMPLEADO_ADMIN)).listar_ordenes_tecnico()
        assert all(o["id_orden"] != info["id_orden"] for o in tecnicos)

        asignadas = Orden_servicio(
            ID_empleado=int(EMPLEADO_ADMIN)
        ).ordenes_asignadas_tecnico()
        assert all(o["ID_orden"] != info["id_orden"] for o in asignadas)

    def test_liberar_orden_no_asignada_falla(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"], ID_empleado=int(EMPLEADO_ADMIN)
        )
        # La orden está Pendiente: el SP exige estado Asignada
        assert modelo.liberar_orden_empleado() is False


class TestFotos:

    def test_agregar_y_eliminar_foto(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"],
            ID_foto_orden_servicio=ID_FOTO,
            Foto_orden_servicio="/static/img/evidencias/taller/prueba.jpg",
        )

        assert modelo.agregar_foto_orden_servicio() == (
            f"Foto registrada exitosamente con ID {ID_FOTO}"
        )
        assert modelo.verificar_foto_existe_por_id() is True

        fotos = Orden_servicio().fotos_orden(info["id_orden"])
        assert any(f["id"] == ID_FOTO for f in fotos)

        resultado = modelo.eliminar_foto_orden_servicio()
        assert resultado["success"] is True
        assert resultado["id_orden"] == info["id_orden"]
        assert modelo.verificar_foto_existe_por_id() is False

    def test_eliminar_foto_inexistente(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"],
            ID_foto_orden_servicio=ID_FOTO_INEXISTENTE,
        )
        resultado = modelo.eliminar_foto_orden_servicio()

        assert resultado["success"] is False
        assert resultado["error"] == (
            f"No se encontró una foto con ID {ID_FOTO_INEXISTENTE}"
        )

    def test_eliminar_foto_sin_id(self):
        resultado = Orden_servicio().eliminar_foto_orden_servicio()

        assert resultado == {"success": False, "error": "El ID de la foto es obligatorio"}

    def test_registrar_fotos_con_procedure(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"],
            Foto_orden_servicio=[
                "/static/img/evidencias/taller/a.jpg",
                "/static/img/evidencias/taller/b.jpg",
            ],
        )
        resultado = modelo.registrar_fotos()

        assert resultado["success"] is True
        assert resultado["mensaje"] == "2 fotos registradas exitosamente"

        fotos = Orden_servicio().fotos_orden(info["id_orden"])
        assert len(fotos) == 2

    def test_registrar_fotos_vacias_falla(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"],
            Foto_orden_servicio=[],
        )
        resultado = modelo.registrar_fotos()

        assert resultado["success"] is False
        assert "No se proporcionaron fotos para registrar" in resultado["error"]


class TestRegistrarReparacion:

    def test_datos_validos(self, orden_taller):
        info = orden_taller
        Orden_servicio(
            ID_orden_servicio=info["id_orden"], ID_empleado=int(EMPLEADO_ADMIN)
        ).asignar_orden_empleado()

        resultado = Orden_servicio(
            ID_orden_servicio=info["id_orden"],
            ID_empleado=int(EMPLEADO_ADMIN),
            Descripcion_reparacion="Se cambió la pantalla",
        ).registrar_reparacion()

        assert resultado["success"] is True
        assert resultado["mensaje"] == "Orden reparada exitosamente"
        assert _estado_de_orden(info["id_orden"]) == "Reparada"

        orden = Orden_servicio(ID_orden_servicio=info["id_orden"]).consultar_orden()
        assert orden["Descripcion"] == "Se cambió la pantalla"
        assert orden["Fecha_salida"] is not None

    def test_con_repuestos(self, orden_taller):
        info = orden_taller
        id_inventario = crear_existencia_temporal(
            info["id_producto"], existencia=5, costo=100.0
        )
        try:
            Orden_servicio(
                ID_orden_servicio=info["id_orden"],
                ID_empleado=int(EMPLEADO_ADMIN),
            ).asignar_orden_empleado()

            resultado = Orden_servicio(
                ID_orden_servicio=info["id_orden"],
                ID_empleado=int(EMPLEADO_ADMIN),
                Descripcion_reparacion="Cambio de módulo",
                lista_repuestos=[{"id_inventario": id_inventario, "cantidad": 2}],
            ).registrar_reparacion()

            assert resultado["success"] is True

            db = conectar().conexion1()
            cursor = db.cursor()
            try:
                cursor.execute(
                    "SELECT Cantidad_usada FROM Repuestos_usados "
                    "WHERE ID_orden_servicio = %s AND ID_inventario = %s",
                    (info["id_orden"], id_inventario),
                )
                assert cursor.fetchone()[0] == 2
                cursor.execute(
                    "SELECT Existencia FROM Existencias_productos WHERE ID_inventario = %s",
                    (id_inventario,),
                )
                assert cursor.fetchone()[0] == 3
            finally:
                cursor.close()
                db.close()
        finally:
            # Repuestos_usados referencia la existencia: borrarla antes.
            _quitar_repuesto_usado(id_inventario)
            eliminar_existencia_temporal(id_inventario)

    def test_stock_insuficiente(self, orden_taller):
        info = orden_taller
        id_inventario = crear_existencia_temporal(
            info["id_producto"], existencia=1, costo=100.0
        )
        try:
            Orden_servicio(
                ID_orden_servicio=info["id_orden"],
                ID_empleado=int(EMPLEADO_ADMIN),
            ).asignar_orden_empleado()

            resultado = Orden_servicio(
                ID_orden_servicio=info["id_orden"],
                ID_empleado=int(EMPLEADO_ADMIN),
                Descripcion_reparacion="Cambio de módulo",
                lista_repuestos=[{"id_inventario": id_inventario, "cantidad": 99}],
            ).registrar_reparacion()

            assert "Stock insuficiente" in resultado["error"]
        finally:
            _quitar_repuesto_usado(id_inventario)
            eliminar_existencia_temporal(id_inventario)

    def test_descripcion_vacia(self, orden_taller):
        info = orden_taller
        resultado = Orden_servicio(
            ID_orden_servicio=info["id_orden"],
            ID_empleado=int(EMPLEADO_ADMIN),
            Descripcion_reparacion="",
        ).registrar_reparacion()

        assert resultado == {
            "success": False,
            "error": "El campo Desdescripcion  no puede estar vacío.",
        }

    def test_orden_no_asignada(self, orden_taller):
        info = orden_taller
        resultado = Orden_servicio(
            ID_orden_servicio=info["id_orden"],
            ID_empleado=int(EMPLEADO_ADMIN),
            Descripcion_reparacion="Cambio de módulo",
        ).registrar_reparacion()

        assert "La orden debe estar en estado Asignada o En proceso" in resultado["error"]


class TestEliminarOrden:

    def test_orden_pendiente(self, orden_taller):
        info = orden_taller
        assert Orden_servicio().eliminar_orden(info["id_orden"]) is True

        assert (
            Orden_servicio(ID_orden_servicio=info["id_orden"]).consultar_orden()
            is None
        )
        assert Orden_servicio().empleados_asignados(info["id_orden"]) == []

    def test_orden_en_proceso_no_se_elimina(self, orden_taller):
        info = orden_taller
        modelo = Orden_servicio(
            ID_orden_servicio=info["id_orden"], ID_empleado=int(EMPLEADO_ADMIN)
        )
        modelo.asignar_orden_empleado()
        modelo.liberar_orden_empleado()

        assert Orden_servicio().eliminar_orden(info["id_orden"]) is False
        assert _estado_de_orden(info["id_orden"]) == "En proceso"

    def test_orden_inexistente(self):
        assert Orden_servicio().eliminar_orden("OS9999999") is False
