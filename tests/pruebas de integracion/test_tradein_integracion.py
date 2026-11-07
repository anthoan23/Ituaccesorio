"""Pruebas de integración de TradeIn (cotizador) contra MySQL real."""
import pytest

from app.models.tradein import TradeIn
from seed_helpers import (
    crear_producto_temporal,
    eliminar_producto_temporal,
    limpiar_bitacora_por_descripcion,
)


CLASE_TELEFONO = "1"
CLASE_REPUESTO = "7"
MARCA_IPHONE = "1"
USUARIO_ADMIN = "USR-001"


def _crear_repuesto_con_costo(nombre: str, costo: float) -> tuple[str, str]:
    """Crea Proveedor + Producto (clase Repuesto) + Suministra. Devuelve (id_producto, id_proveedor)."""
    from app.models.database import conectar
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        # Crear Proveedor
        cursor.execute("SELECT COALESCE(MAX(ID_proveedor), 0) + 1 FROM Proveedor")
        id_proveedor = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO Proveedor (ID_proveedor, Nombre_proveedor) VALUES (%s, %s)",
            (id_proveedor, f"Proveedor Test {id_proveedor}"),
        )
        # Crear Producto (clase Repuesto)
        cursor.execute(
            "SELECT COALESCE(MAX(CAST(ID_producto AS UNSIGNED)), 0) + 1 FROM Producto"
        )
        id_producto = str(cursor.fetchone()[0])
        cursor.execute(
            "INSERT INTO Producto (ID_producto, ID_Clase, ID_marca, Nombre_producto) "
            "VALUES (%s, %s, %s, %s)",
            (id_producto, CLASE_REPUESTO, MARCA_IPHONE, nombre),
        )
        # Crear Suministra
        cursor.execute(
            "INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto) "
            "VALUES (%s, %s, %s)",
            (id_proveedor, id_producto, costo),
        )
        db.commit()
        return id_producto, id_proveedor
    finally:
        cursor.close()
        db.close()


def _limpiar_repuesto(id_producto: str, id_proveedor: str) -> None:
    from app.models.database import conectar
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Suministra WHERE ID_producto = %s", (id_producto,))
        cursor.execute("DELETE FROM Producto WHERE ID_producto = %s", (id_producto,))
        cursor.execute("DELETE FROM Proveedor WHERE ID_proveedor = %s", (id_proveedor,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cursor.close()
        db.close()


@pytest.fixture
def iphone_con_repuestos():
    """Crea un iPhone + repuestos con costos reales. Limpia al final."""
    id_iphone = None
    ids_repuestos = []
    try:
        id_iphone = crear_producto_temporal(
            nombre="iPhone Cotizador", clase=CLASE_TELEFONO, marca=MARCA_IPHONE
        )
        # Crear existencias para el iPhone (con costo 1000)
        from app.models.database import conectar
        db = conectar().conexion1()
        cursor = db.cursor()
        cursor.execute(
            "SELECT CONCAT('INV', LPAD(COALESCE(MAX(CAST(SUBSTRING(ID_inventario, 4) AS UNSIGNED)), 0) + 1, 6, '0')) FROM Existencias_productos"
        )
        id_inventario = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO Existencias_productos (ID_inventario, ID_producto, Existencia, Costo_venta, ID_categoria) "
            "VALUES (%s, %s, %s, %s, NULL)",
            (id_inventario, id_iphone, 5, 1000.0),
        )
        db.commit()
        cursor.close()
        db.close()

        # Crear repuestos para fallas específicas
        repuestos = [
            ("pantalla", 200.0),
            ("mica", 30.0),
            ("power", 50.0),
        ]
        for nombre, costo in repuestos:
            id_rep, id_prov = _crear_repuesto_con_costo(nombre, costo)
            ids_repuestos.append((id_rep, id_prov))

        yield {"id_inventario": id_inventario, "id_producto": id_iphone}
    finally:
        if id_iphone:
            eliminar_producto_temporal(id_iphone)
        for id_rep, id_prov in ids_repuestos:
            _limpiar_repuesto(id_rep, id_prov)
        limpiar_bitacora_por_descripcion("Cotización")


# ==================== CONSULTAR EQUIPOS ====================

class TestConsultarEquipos:

    def test_devuelve_lista(self):
        assert isinstance(TradeIn().consultar_equipos(), list)

    def test_incluye_iphone_con_stock(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        equipos = TradeIn().consultar_equipos()

        equipo = next(
            (e for e in equipos if e["ID_producto"] == info["id_inventario"]), None
        )
        assert equipo is not None
        assert equipo["N_modelo"] == "iPhone Cotizador"
        assert equipo["Costo_venta"] == 1000.0
        assert isinstance(equipo["Costo_venta"], float)


class TestConsultarEquipoPorId:

    def test_equipo_existente(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        equipo = TradeIn().consultar_equipo_por_id(info["id_inventario"])

        assert equipo is not None
        assert equipo["ID_producto"] == info["id_inventario"]
        assert equipo["N_modelo"] == "iPhone Cotizador"
        assert equipo["ID_producto_base"] == info["id_producto"]

    def test_equipo_inexistente(self):
        assert TradeIn().consultar_equipo_por_id("INV999999") is None

    def test_sin_id(self):
        assert TradeIn().consultar_equipo_por_id("") is None


# ==================== CALCULAR COTIZACIÓN ====================

class TestCalcularCotizacion:

    def test_sin_id_producto(self):
        resultado = TradeIn().calcular_cotizacion("", [])
        assert resultado == {
            "success": False,
            "error": "El ID del producto no puede estar vacío.",
        }

    def test_equipo_inexistente(self):
        resultado = TradeIn().calcular_cotizacion("INV999999", [])
        assert resultado == {
            "success": False,
            "error": "No se encontró el equipo con ID 'INV999999'.",
        }

    def test_sin_fallas_devuelve_precio_base(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        resultado = TradeIn().calcular_cotizacion(info["id_inventario"], [])

        assert resultado["success"] is True
        assert resultado["precio_base"] == 1000.0
        assert resultado["costo_total_repuestos"] == 0.0
        assert resultado["monto_estimado"] == 1000.0
        assert resultado["total_fallas"] == 0
        assert resultado["detalles_fallas"] == []

    def test_falla_individual_con_costo_real(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        resultado = TradeIn().calcular_cotizacion(
            info["id_inventario"], ["mica"]
        )

        assert resultado["success"] is True
        assert resultado["costo_total_repuestos"] == 30.0
        assert resultado["monto_estimado"] == 970.0
        assert resultado["total_fallas"] == 1
        assert resultado["detalles_fallas"][0]["costo"] == 30.0

    def test_multiples_fallas_sin_descuento_adicional(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        resultado = TradeIn().calcular_cotizacion(
            info["id_inventario"], ["mica", "power"]
        )

        assert resultado["success"] is True
        assert resultado["costo_total_repuestos"] == 80.0  # 30 + 50
        assert resultado["monto_estimado"] == 920.0
        assert resultado["total_fallas"] == 2

    def test_cinco_o_mas_fallas_aplica_10_por_ciento(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        fallas = ["mica", "power", "lcd", "tactil", "cornetas"]
        resultado = TradeIn().calcular_cotizacion(info["id_inventario"], fallas)

        assert resultado["success"] is True
        assert resultado["total_fallas"] == 5
        # 30 + 50 + 0 + 0 + 0 = 80 (solo mica y power tienen costo)
        # + 10% = 88
        assert resultado["costo_total_repuestos"] == 88.0
        assert resultado["monto_estimado"] == 912.0

    def test_falla_duplicada_se_ignora(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        resultado = TradeIn().calcular_cotizacion(
            info["id_inventario"], ["mica", "mica", "mica"]
        )
        assert resultado["total_fallas"] == 1
        assert resultado["costo_total_repuestos"] == 30.0

    def test_falla_invalida_se_ignora(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        resultado = TradeIn().calcular_cotizacion(
            info["id_inventario"], ["falla_inexistente", "mica"]
        )
        assert resultado["total_fallas"] == 1

    def test_fallas_no_es_lista(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        resultado = TradeIn().calcular_cotizacion(info["id_inventario"], "mica")
        assert resultado == {
            "success": False,
            "error": "Las fallas seleccionadas deben ser una lista.",
        }

    def test_monto_no_baja_de_cero(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        # Aplicar todas las fallas posibles para exceder el precio base
        todas = [f["clave"] for f in TradeIn.FALLAS_COTIZACION]
        resultado = TradeIn().calcular_cotizacion(info["id_inventario"], todas)

        assert resultado["success"] is True
        assert resultado["monto_estimado"] >= 0.0

    def test_registra_en_bitacora(self, iphone_con_repuestos):
        info = iphone_con_repuestos
        TradeIn(usuario_id=USUARIO_ADMIN).calcular_cotizacion(
            info["id_inventario"], ["mica"]
        )

        from app.models.bitacora import Bitacora
        registros = Bitacora().listar_recientes(limite=10)

        encontrado = any(
            "Cotización Trade-in" in r["accion"] and "iPhone Cotizador" in (r["descripcion"] or "")
            for r in registros
        )
        assert encontrado
        limpiar_bitacora_por_descripcion("Cotización")


# ==================== MAPEO DE FALLAS ====================

class TestMapeoFallas:

    def test_config_falla_existente(self):
        config = TradeIn()._obtener_config_falla("mica")
        assert config is not None
        assert config["etiqueta"] == "Mica"

    def test_config_falla_inexistente(self):
        assert TradeIn()._obtener_config_falla("no_existe") is None

    def test_descripcion_falla_existente(self):
        descripcion = TradeIn()._obtener_descripcion_falla("mica")
        assert "vidrio" in descripcion.lower()

    def test_descripcion_falla_inexistente(self):
        descripcion = TradeIn()._obtener_descripcion_falla("no_existe")
        assert "revisión técnica" in descripcion.lower()