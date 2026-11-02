"""Pruebas unitarias de la clase TradeIn (app.models.tradein).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.

TradeIn es un modelo de cálculo: consulta equipos y costos de repuestos,
pero no escribe en la base de datos (la bitácora se delega a Bitacora).
"""
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models.tradein import TradeIn
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

# ==================== Datos de frontera ====================
ID_PRODUCTO = "INV-01"  # ID de inventario del equipo
ID_PRODUCTO_BASE = "P001"  # ID del producto base (para buscar repuestos)
PRECIO_BASE = 500.0

FALLA_CONOCIDA = "power"
FALLA_DESCONOCIDA = "no_existe"


def equipo_base(**cambios):
    """Devuelve un equipo de trade-in válido con los campos cambiados."""
    equipo = {
        "ID_producto": ID_PRODUCTO,
        "Costo_venta": PRECIO_BASE,
        "N_modelo": "iPhone 13",
        "Existencia": 1,
        "Marca": "Apple",
        "Clase": "Telefono",
        "ID_producto_base": ID_PRODUCTO_BASE,
    }
    return {**equipo, **cambios}


class TestObtenerConfigFalla:

    def test_falla_existente(self):
        config = TradeIn()._obtener_config_falla("power")

        assert config == {
            "clave": "power",
            "etiqueta": "Botón de power",
            "busqueda": "power",
        }

    @pytest.mark.parametrize(
        "clave",
        [
            pytest.param("", id="clave-vacia"),
            pytest.param(FALLA_DESCONOCIDA, id="clave-inexistente"),
            pytest.param("Power", id="clave-con-mayuscula"),
        ],
    )
    def test_falla_inexistente(self, clave):
        assert TradeIn()._obtener_config_falla(clave) is None

    def test_todas_las_fallas_tienen_mapeo_de_repuesto(self):
        for falla in TradeIn.FALLAS_COTIZACION:
            assert falla["clave"] in TradeIn.MAPEO_FALLA_REPUESTO


class TestObtenerDescripcionFalla:

    def test_falla_conocida(self):
        descripcion = TradeIn()._obtener_descripcion_falla("power")

        assert descripcion == (
            "El botón de encendido no responde o funciona de manera intermitente."
        )

    def test_falla_desconocida_usa_descripcion_generica(self):
        descripcion = TradeIn()._obtener_descripcion_falla(FALLA_DESCONOCIDA)

        assert descripcion == (
            "Esta falla requiere revisión técnica para determinar el costo exacto."
        )

    def test_todas_las_fallas_tienen_descripcion_propia(self):
        descripcion_generica = (
            "Esta falla requiere revisión técnica para determinar el costo exacto."
        )
        trade_in = TradeIn()

        for falla in TradeIn.FALLAS_COTIZACION:
            descripcion = trade_in._obtener_descripcion_falla(falla["clave"])
            assert descripcion != descripcion_generica


class TestObtenerCostoRepuesto:

    def test_costo_desde_suministra(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_producto": "REP-01"},
            {"costo": Decimal("12.50")},
        ]

        resultado = TradeIn()._obtener_costo_repuesto(ID_PRODUCTO_BASE, "power")

        assert resultado == 12.5
        assert isinstance(resultado, float)
        assert cursor.execute.call_args_list[0].args[1] == ("%boton_power%",)
        assert cursor.execute.call_args_list[1].args[1] == ("REP-01",)
        cierra_recursos(db, cursor)

    def test_falla_sin_mapeo_busca_por_su_clave(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_producto": "REP-02"},
            {"costo": Decimal("1.00")},
        ]

        TradeIn()._obtener_costo_repuesto(ID_PRODUCTO_BASE, FALLA_DESCONOCIDA)

        assert cursor.execute.call_args_list[0].args[1] == (f"%{FALLA_DESCONOCIDA}%",)

    def test_sin_repuesto_devuelve_cero(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = TradeIn()._obtener_costo_repuesto(ID_PRODUCTO_BASE, "power")

        assert resultado == 0.00
        assert cursor.execute.call_count == 1
        cierra_recursos(db, cursor)

    def test_sin_costo_en_suministra_usa_existencia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_producto": "REP-01"},
            {"costo": None},
            {"Costo_venta": Decimal("9.99")},
        ]

        resultado = TradeIn()._obtener_costo_repuesto(ID_PRODUCTO_BASE, "power")

        assert resultado == 9.99
        assert "Existencias_productos" in cursor.execute.call_args_list[2].args[0]

    def test_sin_costo_en_existencia_devuelve_cero(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_producto": "REP-01"},
            {"costo": None},
            {"Costo_venta": None},
        ]

        resultado = TradeIn()._obtener_costo_repuesto(ID_PRODUCTO_BASE, "power")

        assert resultado == 0.00

    def test_conexion_caida_devuelve_cero(self, conexion_caída):
        resultado = TradeIn()._obtener_costo_repuesto(ID_PRODUCTO_BASE, "power")

        assert resultado == 0.00

    def test_error_de_bd_devuelve_cero(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = TradeIn()._obtener_costo_repuesto(ID_PRODUCTO_BASE, "power")

        assert resultado == 0.00
        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            {"ID_producto": "REP-01"},
            {"costo": Decimal("3.00")},
        ]

        TradeIn()._obtener_costo_repuesto(ID_PRODUCTO_BASE, "power")

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestConsultarEquipos:

    def test_con_equipos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "ID_producto": ID_PRODUCTO,
                "Costo_venta": Decimal("349.99"),
                "N_modelo": "iPhone 13",
                "Existencia": 2,
                "Marca": "Apple",
                "Clase": "Telefono",
            },
            {
                "ID_producto": "INV-02",
                "Costo_venta": 210.0,
                "N_modelo": "iPhone 11",
                "Existencia": 1,
                "Marca": "Apple",
                "Clase": "Telefono",
            },
        ]

        resultado = TradeIn().consultar_equipos()

        assert len(resultado) == 2
        assert resultado[0]["Costo_venta"] == 349.99
        assert isinstance(resultado[0]["Costo_venta"], float)
        assert resultado[1]["Costo_venta"] == 210.0
        assert "Nombre_marca = 'Apple'" in ultima_sentencia(cursor)

    def test_sin_equipos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert TradeIn().consultar_equipos() == []

    def test_conexion_caida(self, conexion_caída):
        assert TradeIn().consultar_equipos() == []

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        TradeIn().consultar_equipos()

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        TradeIn().consultar_equipos()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_error_de_bd_se_propaga(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        # consultar_equipos no captura la excepción, solo cierra recursos
        with pytest.raises(Exception, match="fallo simulado"):
            TradeIn().consultar_equipos()

        cierra_recursos(db, cursor)


class TestConsultarEquipoPorId:

    def test_equipo_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = equipo_base(Costo_venta=Decimal("349.99"))

        resultado = TradeIn().consultar_equipo_por_id(ID_PRODUCTO)

        assert resultado["N_modelo"] == "iPhone 13"
        assert resultado["Costo_venta"] == 349.99
        assert isinstance(resultado["Costo_venta"], float)
        assert cursor.execute.call_args.args[1] == (ID_PRODUCTO,)
        db.cursor.assert_called_once_with(dictionary=True)

    def test_id_con_espacios_se_limpia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = equipo_base()

        TradeIn().consultar_equipo_por_id(f"  {ID_PRODUCTO}  ")

        assert cursor.execute.call_args.args[1] == (ID_PRODUCTO,)

    @pytest.mark.parametrize(
        "id_producto",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_sin_id_no_toca_la_bd(self, conexion_falsa, id_producto):
        db, cursor = conexion_falsa

        assert TradeIn().consultar_equipo_por_id(id_producto) is None
        cursor.execute.assert_not_called()

    def test_equipo_no_encontrado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        assert TradeIn().consultar_equipo_por_id(ID_PRODUCTO) is None

    def test_conexion_caida(self, conexion_caída):
        assert TradeIn().consultar_equipo_por_id(ID_PRODUCTO) is None

    def test_cierra_cursor_y_conexion(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        TradeIn().consultar_equipo_por_id(ID_PRODUCTO)

        cierra_recursos(db, cursor)

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = equipo_base()

        TradeIn().consultar_equipo_por_id(ID_PRODUCTO)

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()

    def test_error_de_bd_se_propaga(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        with pytest.raises(Exception, match="fallo simulado"):
            TradeIn().consultar_equipo_por_id(ID_PRODUCTO)

        cierra_recursos(db, cursor)


class TestCalcularCotizacion:

    @pytest.mark.parametrize(
        "id_producto",
        [
            pytest.param(None, id="none"),
            pytest.param("", id="vacio"),
        ],
    )
    def test_id_producto_vacio(self, conexion_falsa, id_producto):
        db, cursor = conexion_falsa

        resultado = TradeIn().calcular_cotizacion(id_producto, [])

        assert resultado == {
            "success": False,
            "error": "El ID del producto no puede estar vacío.",
        }
        cursor.execute.assert_not_called()

    def test_equipo_inexistente(self):
        with patch.object(TradeIn, "consultar_equipo_por_id", return_value=None):
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, [])

        assert resultado == {
            "success": False,
            "error": f"No se encontró el equipo con ID '{ID_PRODUCTO}'.",
        }

    @pytest.mark.parametrize(
        "precio",
        [
            pytest.param(0, id="cero"),
            pytest.param(None, id="none"),
            pytest.param(-100.0, id="negativo"),
        ],
    )
    def test_precio_base_invalido(self, precio):
        with patch.object(
            TradeIn,
            "consultar_equipo_por_id",
            return_value=equipo_base(Costo_venta=precio),
        ):
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, [])

        assert resultado == {
            "success": False,
            "error": (
                "El equipo 'iPhone 13' no tiene un precio base válido."
            ),
        }

    @pytest.mark.parametrize(
        "fallas",
        [
            pytest.param("power", id="string"),
            pytest.param({"power": True}, id="diccionario"),
            pytest.param(123, id="numero"),
        ],
    )
    def test_fallas_que_no_son_lista(self, fallas):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ):
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, fallas)

        assert resultado == {
            "success": False,
            "error": "Las fallas seleccionadas deben ser una lista.",
        }

    def test_sin_fallas(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ):
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, [])

        assert resultado["success"] is True
        assert resultado["equipo"] == equipo_base()
        assert resultado["precio_base"] == PRECIO_BASE
        assert resultado["costo_total_repuestos"] == 0.0
        assert resultado["monto_estimado"] == PRECIO_BASE
        assert resultado["detalles_fallas"] == []
        assert resultado["advertencias"] == []
        assert resultado["total_fallas"] == 0

    def test_una_falla(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(
            TradeIn, "_obtener_costo_repuesto", return_value=25.0
        ) as costo_mock:
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, ["power"])

        assert resultado["success"] is True
        assert resultado["precio_base"] == 500.0
        assert resultado["costo_total_repuestos"] == 25.0
        assert resultado["monto_estimado"] == 475.0
        assert resultado["total_fallas"] == 1
        assert resultado["detalles_fallas"] == [
            {
                "clave": "power",
                "etiqueta": "Botón de power",
                "costo": 25.0,
                "descripcion": (
                    "El botón de encendido no responde o funciona "
                    "de manera intermitente."
                ),
            }
        ]
        assert resultado["advertencias"] == [
            "Se aplicó $25.00 por Botón de power."
        ]
        costo_mock.assert_called_once_with(ID_PRODUCTO_BASE, "power")

    def test_cuatro_fallas_sin_descuento_adicional(self):
        fallas = ["power", "cornetas", "mica", "lcd"]
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(
            TradeIn, "_obtener_costo_repuesto", return_value=10.0
        ):
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, fallas)

        assert resultado["total_fallas"] == 4
        assert resultado["costo_total_repuestos"] == 40.0
        assert resultado["monto_estimado"] == 460.0
        assert not any(
            "descuento adicional" in advertencia
            for advertencia in resultado["advertencias"]
        )

    def test_cinco_fallas_aplica_diez_por_ciento(self):
        fallas = ["power", "cornetas", "mica", "lcd", "tactil"]
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(
            TradeIn, "_obtener_costo_repuesto", return_value=10.0
        ):
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, fallas)

        assert resultado["total_fallas"] == 5
        assert resultado["costo_total_repuestos"] == 55.0
        assert resultado["monto_estimado"] == 445.0
        assert (
            "Se aplicó un 10% de descuento adicional por múltiples fallas "
            "($5.00)."
        ) in resultado["advertencias"]

    def test_fallas_invalidas_se_ignoran(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(
            TradeIn, "_obtener_costo_repuesto", return_value=10.0
        ) as costo_mock:
            resultado = TradeIn().calcular_cotizacion(
                ID_PRODUCTO, [FALLA_DESCONOCIDA, "power", None, 123]
            )

        assert resultado["total_fallas"] == 1
        assert resultado["detalles_fallas"][0]["clave"] == "power"
        costo_mock.assert_called_once_with(ID_PRODUCTO_BASE, "power")

    def test_fallas_duplicadas_se_ignoran(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(
            TradeIn, "_obtener_costo_repuesto", return_value=10.0
        ) as costo_mock:
            resultado = TradeIn().calcular_cotizacion(
                ID_PRODUCTO, ["power", "power", " power "]
            )

        assert resultado["total_fallas"] == 1
        assert resultado["costo_total_repuestos"] == 10.0
        costo_mock.assert_called_once()

    def test_tuplas_son_aceptadas(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(TradeIn, "_obtener_costo_repuesto", return_value=5.0):
            resultado = TradeIn().calcular_cotizacion(
                ID_PRODUCTO, ("power", "mica")
            )

        assert resultado["success"] is True
        assert resultado["total_fallas"] == 2

    def test_monto_estimado_nunca_es_negativo(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(TradeIn, "_obtener_costo_repuesto", return_value=600.0):
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, ["power"])

        assert resultado["monto_estimado"] == 0
        assert resultado["costo_total_repuestos"] == 600.0

    def test_precio_base_se_redondea(self):
        with patch.object(
            TradeIn,
            "consultar_equipo_por_id",
            return_value=equipo_base(Costo_venta=349.996),
        ), patch.object(TradeIn, "_obtener_costo_repuesto", return_value=0.0):
            resultado = TradeIn().calcular_cotizacion(ID_PRODUCTO, [])

        assert resultado["precio_base"] == 350.0

    def test_registra_bitacora_con_usuario(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(
            TradeIn, "_obtener_costo_repuesto", return_value=20.0
        ), patch(
            "app.models.tradein.Bitacora"
        ) as bitacora_clase:
            resultado = TradeIn(usuario_id="7").calcular_cotizacion(
                ID_PRODUCTO, ["power"]
            )

        assert resultado["success"] is True
        bitacora_clase.assert_called_once_with(
            accion="Cotización Trade-in",
            descripcion=(
                "Cotización Trade-in | Modelo: iPhone 13 | Base: 500.0 | "
                "Deducción: 20.0 | Estimado: 480.0 | Fallas: Botón de power"
            ),
            usuario_id="7",
            modulo_nombre="Trade-in",
        )
        bitacora_clase.return_value.registrar.assert_called_once()

    def test_bitacora_sin_fallas_no_incluye_texto_de_fallas(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch("app.models.tradein.Bitacora") as bitacora_clase:
            TradeIn(usuario_id="7").calcular_cotizacion(ID_PRODUCTO, [])

        descripcion = bitacora_clase.call_args.kwargs["descripcion"]
        assert descripcion == (
            "Cotización Trade-in | Modelo: iPhone 13 | Base: 500.0 | "
            "Deducción: 0.0 | Estimado: 500.0"
        )

    def test_advertencia_de_bitacora_se_agrega(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(
            TradeIn, "_obtener_costo_repuesto", return_value=10.0
        ), patch(
            "app.models.tradein.Bitacora"
        ) as bitacora_clase:
            bitacora_clase.return_value.registrar.return_value = {
                "success": False,
                "warning": "No se pudo registrar la bitácora: sin conexión.",
            }
            resultado = TradeIn(usuario_id="7").calcular_cotizacion(
                ID_PRODUCTO, ["power"]
            )

        assert resultado["advertencias"][-1] == (
            "No se pudo registrar la bitácora: sin conexión."
        )

    def test_sin_usuario_no_registra_bitacora(self):
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(
            TradeIn, "_obtener_costo_repuesto", return_value=10.0
        ), patch(
            "app.models.tradein.Bitacora"
        ) as bitacora_clase:
            TradeIn().calcular_cotizacion(ID_PRODUCTO, ["power"])

        bitacora_clase.assert_not_called()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        with patch.object(
            TradeIn, "consultar_equipo_por_id", return_value=equipo_base()
        ), patch.object(TradeIn, "_obtener_costo_repuesto", return_value=10.0):
            TradeIn().calcular_cotizacion(ID_PRODUCTO, ["power"])

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()
