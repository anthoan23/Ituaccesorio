"""Pruebas de integración de la clase Proveedores contra MySQL real."""
import pytest

from app.models.proveedores import Proveedores
from seed_helpers import (
    crear_producto_temporal,
    eliminar_producto_temporal,
)

CLASE_TELEFONO = "1"
MARCA_SEED = "3"

# Datos fijos por prueba (rangos reservados para este módulo).
RIF_LISTADO = "J-81000101-1"
RIF_CREADO = "J-81000102-1"
RIF_DUPLICADO = "J-81000103-1"
RIF_OTRO = "J-81000104-1"
RIF_ACTUALIZADO = "J-81000105-1"
RIF_LIMITE = "J-81000106-1"
RIF_CON_PRODUCTOS = "J-81000107-1"
RIF_LIMITE_MENOR = "J-81000108-1"
RIF_DUMMY = "J-81000109-1"      # para validaciones que nunca insertan


# ==================== HELPERS LOCALES (solo para este módulo) ====================


def _crear_proveedor(nombre: str, rif: str = None, limite_credito=None) -> int:
    from app.models.database import conectar

    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(ID_proveedor), 0) + 1 FROM Proveedor")
        id_proveedor = int(cursor.fetchone()[0])
        cursor.execute(
            "INSERT INTO Proveedor (ID_proveedor, Rif_proveedor, Nombre_proveedor, Tipo_proveedor, "
            "Celular_proveedor, Correo_proveedor, Direccion_proveedor, Limite_credito) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                id_proveedor,
                rif or "J-99999999-9",
                nombre,
                "Importador",
                "04141234567",
                "proveedor@mail.com",
                "Barquisimeto",
                limite_credito,
            ),
        )
        db.commit()
        return id_proveedor
    finally:
        cursor.close()
        db.close()


def _eliminar_proveedor(id_proveedor: int) -> None:
    from app.models.database import conectar

    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Suministra WHERE ID_proveedor = %s", (id_proveedor,))
        cursor.execute("DELETE FROM Proveedor WHERE ID_proveedor = %s", (id_proveedor,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


def _asignar_costo(id_proveedor: int, id_producto: str, costo: float) -> None:
    from app.models.database import conectar

    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto) "
            "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Costo_producto = VALUES(Costo_producto)",
            (id_proveedor, id_producto, costo),
        )
        db.commit()
    finally:
        cursor.close()
        db.close()


def _quitar_costo(id_proveedor: int, id_producto: str) -> None:
    from app.models.database import conectar

    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute(
            "DELETE FROM Suministra WHERE ID_proveedor = %s AND ID_producto = %s",
            (id_proveedor, id_producto),
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


class TestListarProveedores:

    def test_incluye_proveedor_temporal(self):
        nombre = "Proveedor Integra Listado"
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor(nombre, rif=RIF_LISTADO)

            proveedores = Proveedores().listar_proveedores()
            fila = next((p for p in proveedores if p["id"] == id_proveedor), None)

            assert fila is not None
            assert fila["nombre"] == nombre
            assert fila["tipo"] == "Importador"
            assert fila["celular"] == "04141234567"
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_filtro_de_busqueda_por_nombre(self):
        nombre = "Proveedor Integra Busqueda XYZ"
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor(nombre, rif=RIF_DUMMY)

            resultado = Proveedores().listar_proveedores(q="Busqueda XYZ")

            assert [p["id"] for p in resultado] == [id_proveedor]
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)


class TestVerificarObtenerProveedor:

    def test_verificar_existencia(self):
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor("Proveedor Integra Existente")
            assert Proveedores(id_proveedor=id_proveedor).verificar_existencia() is True
            assert Proveedores(id_proveedor=999999).verificar_existencia() is False
            assert Proveedores().verificar_existencia() is False
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_obtener_proveedor(self):
        nombre = "Proveedor Integra Obtenido"
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor(
                nombre, rif=RIF_CREADO, limite_credito=1000.0
            )
            proveedor = Proveedores(id_proveedor=id_proveedor).obtener_proveedor()

            assert proveedor["id"] == id_proveedor
            assert proveedor["nombre"] == nombre
            assert proveedor["rif"] == RIF_CREADO
            assert float(proveedor["limite_credito"]) == 1000.0
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_obtener_proveedor_inexistente(self):
        assert Proveedores(id_proveedor=999999).obtener_proveedor() is None
        assert Proveedores().obtener_proveedor() is None


class TestCrearProveedor:

    def test_datos_validos(self):
        nombre = "Proveedor Integra Creado"
        id_proveedor = None
        try:
            id_proveedor = Proveedores(
                rif=RIF_CREADO,
                nombre=nombre,
                tipo="Importador",
                celular="04141234567",
                correo="creado@mail.com",
                direccion="Barquisimeto",
                limite_credito=5000,
            ).crear_proveedor()

            assert id_proveedor > 0
            assert Proveedores(id_proveedor=id_proveedor).verificar_existencia() is True
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_nombre_duplicado(self):
        nombre = "Proveedor Integra Duplicado"
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor(nombre, rif=RIF_DUPLICADO)
            with pytest.raises(ValueError) as exc:
                Proveedores(rif=RIF_OTRO, nombre=nombre).crear_proveedor()

            assert str(exc.value) == f"Ya existe un proveedor con el nombre '{nombre}'."
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_rif_duplicado(self):
        nombre = "Proveedor Integra Rif Dup"
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor(nombre, rif=RIF_DUPLICADO)
            with pytest.raises(ValueError) as exc:
                Proveedores(
                    rif=RIF_DUPLICADO, nombre="Proveedor Integra Otro"
                ).crear_proveedor()

            assert str(exc.value) == f"Ya existe un proveedor con el RIF '{RIF_DUPLICADO}'."
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"nombre": ""},
                "El campo Nombre del proveedor no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"nombre": "P"},
                "El campo Nombre del proveedor debe tener al menos 2 caracteres.",
                id="nombre-demasiado-corto",
            ),
            pytest.param(
                {"nombre": "P" * 61},
                "El campo Nombre del proveedor no puede tener más de 60 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"nombre": "Proveedor #1"},
                "El campo Nombre del proveedor solo puede contener letras, números y espacios.",
                id="nombre-caracteres-invalidos",
            ),
            pytest.param(
                {"rif": "12345678"},
                "El campo RIF debe tener formato válido. Ejemplo: J-12345678-9, E-12345678-9 o V-12345678-9.",
                id="rif-sin-formato",
            ),
            pytest.param(
                {"rif": "J-1234567-9"},
                "El campo RIF debe tener formato válido. Ejemplo: J-12345678-9, E-12345678-9 o V-12345678-9.",
                id="rif-digitos-incompletos",
            ),
            pytest.param(
                {"celular": "0414123456"},
                "El campo Teléfono debe tener exactamente 11 dígitos.",
                id="telefono-demasiado-corto",
            ),
            pytest.param(
                {"celular": "03121234567"},
                "El campo Teléfono debe comenzar con un prefijo válido: "
                "0412, 0414, 0416, 0422, 0424 o 0426.",
                id="telefono-prefijo-invalido",
            ),
            pytest.param(
                {"correo": "correo-sin-arroba"},
                "El campo correo debe contener el símbolo @.",
                id="correo-sin-arroba",
            ),
            pytest.param(
                {"direccion": "D" * 101},
                "El campo Dirección no puede tener más de 100 caracteres.",
                id="direccion-demasiado-larga",
            ),
            pytest.param(
                {"direccion": "Dirección @#"},
                "El campo Dirección solo puede contener letras, números, espacios y signos básicos.",
                id="direccion-caracteres-invalidos",
            ),
            pytest.param(
                {"limite_credito": "abc"},
                "El límite de crédito debe ser numérico.",
                id="limite-no-numerico",
            ),
            pytest.param(
                {"limite_credito": -5},
                "El límite de crédito no puede ser negativo.",
                id="limite-negativo",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        datos = {
            "rif": RIF_DUMMY,
            "nombre": "Proveedor Integra Invalido",
            "tipo": "Importador",
            "celular": "04141234567",
            "correo": "proveedor@mail.com",
            "direccion": "Barquisimeto",
            "limite_credito": 1000,
        }
        datos.update(cambios)
        with pytest.raises(ValueError) as exc:
            Proveedores(**datos).crear_proveedor()

        assert str(exc.value) == esperado


class TestActualizarProveedor:

    def test_datos_validos(self):
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor(
                "Proveedor Integra Original", limite_credito=1000.0
            )

            resultado = Proveedores(
                id_proveedor=id_proveedor,
                rif=RIF_ACTUALIZADO,
                nombre="Proveedor Integra Actualizado",
                tipo="Nacional",
                celular="04241234567",
                correo="actualizado@mail.com",
                direccion="Caracas",
                limite_credito=2000,
            ).actualizar_proveedor()

            assert resultado is True
            proveedor = Proveedores(id_proveedor=id_proveedor).obtener_proveedor()
            assert proveedor["nombre"] == "Proveedor Integra Actualizado"
            assert proveedor["tipo"] == "Nacional"
            assert float(proveedor["limite_credito"]) == 2000.0
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_limite_menor_que_costo_del_producto(self):
        id_proveedor = None
        id_producto = None
        try:
            id_proveedor = _crear_proveedor(
                "Proveedor Integra Limite Bajo", rif=RIF_LIMITE_MENOR,
                limite_credito=1000.0,
            )
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Proveedor Costo",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _asignar_costo(id_proveedor, id_producto, costo=800.0)

            with pytest.raises(ValueError) as exc:
                Proveedores(
                    id_proveedor=id_proveedor,
                    rif=RIF_LIMITE_MENOR,
                    nombre="Proveedor Integra Limite Bajo",
                    limite_credito=500,
                ).actualizar_proveedor()

            assert str(exc.value) == (
                "El nuevo límite de crédito (500 Bs) no puede ser menor que el costo "
                "del producto más caro que ya tiene asignado (800 Bs). "
                "Reduzca los costos primero o elimine productos."
            )
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_sin_id(self):
        with pytest.raises(ValueError) as exc:
            Proveedores(nombre="Proveedor Integra Sin ID").actualizar_proveedor()

        assert str(exc.value) == "ID del proveedor es requerido para actualizar."


class TestEliminarProveedor:

    def test_datos_validos(self):
        id_proveedor = _crear_proveedor("Proveedor Integra Eliminable")
        resultado = Proveedores(id_proveedor=id_proveedor).eliminar_proveedor()

        assert resultado is True
        assert Proveedores(id_proveedor=id_proveedor).verificar_existencia() is False

    def test_segunda_eliminacion_devuelve_false(self):
        id_proveedor = _crear_proveedor("Proveedor Integra Segunda Vez")
        Proveedores(id_proveedor=id_proveedor).eliminar_proveedor()
        resultado = Proveedores(id_proveedor=id_proveedor).eliminar_proveedor()

        assert resultado is False

    def test_sin_id(self):
        with pytest.raises(ValueError) as exc:
            Proveedores().eliminar_proveedor()

        assert str(exc.value) == "ID del proveedor es requerido para eliminar."


class TestRelacionesProveedor:

    def test_sin_productos_no_tiene_relaciones(self):
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor("Proveedor Integra Sin Relaciones")

            tiene, mensaje = Proveedores(
                id_proveedor=id_proveedor
            ).tiene_relaciones_activas()

            assert tiene is False
            assert mensaje == ""
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_con_producto_asociado(self):
        id_proveedor = None
        id_producto = None
        try:
            id_proveedor = _crear_proveedor(
                "Proveedor Integra Relaciones", rif=RIF_LIMITE
            )
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Relacion",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _asignar_costo(id_proveedor, id_producto, costo=250.0)

            tiene, mensaje = Proveedores(
                id_proveedor=id_proveedor
            ).tiene_relaciones_activas()

            assert tiene is True
            assert mensaje == (
                "No se puede eliminar el proveedor porque tiene 1 productos asociados."
            )

            detalle = Proveedores(id_proveedor=id_proveedor).obtener_detalle_relaciones()
            assert detalle["ordenes"] == []
            assert len(detalle["productos"]) == 1
            assert str(detalle["productos"][0]["id_modelo"]) == id_producto
            assert float(detalle["productos"][0]["costo"]) == 250.0
        finally:
            if id_producto:
                _quitar_costo(id_proveedor, id_producto)
                eliminar_producto_temporal(id_producto)
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_sin_id(self):
        tiene, mensaje = Proveedores().tiene_relaciones_activas()

        assert tiene is True
        assert mensaje == "ID de proveedor no especificado"


class TestProductosDelProveedor:

    def test_listar_productos_por_proveedor(self):
        id_proveedor = None
        id_producto = None
        try:
            id_proveedor = _crear_proveedor("Proveedor Integra Productos")
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Listado Prov",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _asignar_costo(id_proveedor, id_producto, costo=300.0)

            productos = Proveedores(
                id_proveedor=id_proveedor
            ).listar_productos_por_proveedor()
            fila = next(
                (p for p in productos if str(p["id_modelo"]) == id_producto), None
            )

            assert fila is not None
            assert float(fila["costo"]) == 300.0
            assert fila["clase_nombre"] == "Telefono"
        finally:
            if id_producto:
                _quitar_costo(id_proveedor, id_producto)
                eliminar_producto_temporal(id_producto)
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_upsert_producto_inserta_y_actualiza(self):
        id_proveedor = None
        id_producto = None
        try:
            id_proveedor = _crear_proveedor(
                "Proveedor Integra Upsert", limite_credito=5000.0
            )
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Upsert",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            modelo = Proveedores(id_proveedor=id_proveedor)

            assert modelo.upsert_producto_proveedor(id_producto, 400) is True
            productos = modelo.listar_productos_por_proveedor()
            assert float(
                next(p for p in productos if str(p["id_modelo"]) == id_producto)["costo"]
            ) == 400.0

            assert modelo.upsert_producto_proveedor(id_producto, 450) is True
            productos = modelo.listar_productos_por_proveedor()
            assert float(
                next(p for p in productos if str(p["id_modelo"]) == id_producto)["costo"]
            ) == 450.0
        finally:
            if id_producto:
                _quitar_costo(id_proveedor, id_producto)
                eliminar_producto_temporal(id_producto)
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_upsert_costo_superior_al_limite(self):
        id_proveedor = None
        try:
            id_proveedor = _crear_proveedor(
                "Proveedor Integra Costo Alto", limite_credito=1000.0
            )
            with pytest.raises(ValueError) as exc:
                Proveedores(id_proveedor=id_proveedor).upsert_producto_proveedor(
                    "999999", 2000
                )

            assert str(exc.value) == (
                "El costo del producto (2000 Bs) no puede superar el límite de "
                "crédito del proveedor (1000 Bs)."
            )
        finally:
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    @pytest.mark.parametrize(
        "id_proveedor, id_modelo, costo, esperado",
        [
            pytest.param(
                0,
                "1",
                100,
                "ID del proveedor es requerido",
                id="sin-proveedor",
            ),
            pytest.param(
                999999,
                "",
                100,
                "El modelo es obligatorio.",
                id="sin-modelo",
            ),
            pytest.param(
                999999,
                "1",
                "abc",
                "El costo debe ser numérico.",
                id="costo-no-numerico",
            ),
            pytest.param(
                999999,
                "1",
                -5,
                "El costo no puede ser negativo.",
                id="costo-negativo",
            ),
        ],
    )
    def test_upsert_validaciones(self, id_proveedor, id_modelo, costo, esperado):
        with pytest.raises(ValueError) as exc:
            Proveedores(id_proveedor=id_proveedor).upsert_producto_proveedor(
                id_modelo, costo
            )

        assert str(exc.value) == esperado

    def test_eliminar_producto_del_proveedor(self):
        id_proveedor = None
        id_producto = None
        try:
            id_proveedor = _crear_proveedor("Proveedor Integra Quitar")
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Quitar",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            _asignar_costo(id_proveedor, id_producto, costo=100.0)

            assert (
                Proveedores(id_proveedor=id_proveedor).eliminar_producto_proveedor(
                    id_producto
                )
                is True
            )
            assert (
                Proveedores(id_proveedor=id_proveedor).eliminar_producto_proveedor(
                    id_producto
                )
                is False
            )
        finally:
            if id_producto:
                _quitar_costo(id_proveedor, id_producto)
                eliminar_producto_temporal(id_producto)
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_eliminar_producto_sin_modelo(self):
        with pytest.raises(ValueError) as exc:
            Proveedores(id_proveedor=1).eliminar_producto_proveedor()

        assert str(exc.value) == "ID del modelo es requerido"


class TestCrearProveedorConProductos:

    def test_datos_validos(self):
        id_producto = None
        id_proveedor = None
        try:
            id_producto = crear_producto_temporal(
                nombre="Prod Integra Con Productos",
                clase=CLASE_TELEFONO,
                marca=MARCA_SEED,
            )
            id_proveedor = Proveedores(
                rif=RIF_CON_PRODUCTOS,
                nombre="Proveedor Integra Con Productos",
                limite_credito=5000,
            ).crear_proveedor_con_productos(
                [{"id_modelo": id_producto, "costo": 700}]
            )

            assert id_proveedor > 0
            productos = Proveedores(
                id_proveedor=id_proveedor
            ).listar_productos_por_proveedor()
            assert len(productos) == 1
            assert float(productos[0]["costo"]) == 700.0
        finally:
            if id_producto:
                eliminar_producto_temporal(id_producto)
            if id_proveedor:
                _eliminar_proveedor(id_proveedor)

    def test_costo_superior_al_limite(self):
        # La validación es en memoria (contra limite_credito): no toca la BD.
        with pytest.raises(ValueError) as exc:
            Proveedores(
                rif=RIF_DUMMY,
                nombre="Proveedor Integra Limite",
                limite_credito=1000,
            ).crear_proveedor_con_productos(
                [{"id_modelo": "999999", "costo": 1500}]
            )

        assert str(exc.value) == (
            "El costo del producto ID '999999' (1500 Bs) no puede superar "
            "el límite de crédito del proveedor (1000 Bs)."
        )

    @pytest.mark.parametrize(
        "productos, esperado",
        [
            pytest.param(
                "no-soy-lista",
                "Productos debe ser una lista.",
                id="no-es-lista",
            ),
            pytest.param(
                [{"costo": 100}],
                "id_modelo es obligatorio en productos.",
                id="sin-id-modelo",
            ),
            pytest.param(
                [{"id_modelo": "1", "costo": "abc"}],
                "El costo debe ser numérico.",
                id="costo-no-numerico",
            ),
            pytest.param(
                [{"id_modelo": "1", "costo": -10}],
                "El costo del producto '1' no puede ser negativo.",
                id="costo-negativo",
            ),
        ],
    )
    def test_productos_invalidos(self, productos, esperado):
        with pytest.raises(ValueError) as exc:
            Proveedores(
                rif=RIF_DUMMY,
                nombre="Proveedor Integra Productos Invalidos",
            ).crear_proveedor_con_productos(productos)

        assert str(exc.value) == esperado
