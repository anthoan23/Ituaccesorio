"""Pruebas unitarias de la clase ValidacionPagosModel
(app.models.validacion_pagos).

Los fixtures `conexion_falsa` y `conexion_caída` viven en
tests/pruebas unitarias/conftest.py y los helpers en
tests/pruebas unitarias/helpers.py.
"""
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.models.validacion_pagos import ValidacionPagosModel
from helpers import cierra_recursos, sin_sentencia, ultima_sentencia

MENSAJE_ERROR_CONEXION = "Error al conectar a la base de datos."

# ==================== Datos de frontera ====================
FACTURA_VALIDA = "FAC-202611-ABC123"
EMPLEADO_VALIDO = "12345678"  # 8 dígitos (máximo)
EMPLEADO_MINIMO = "123456"  # 6 dígitos (mínimo)
FECHA_FIJA = datetime(2026, 11, 2, 10, 30, 0)
MOTIVO_VALIDO = "Comprobante inválido"


def llamada_con(cursor, fragmento):
    """Devuelve la llamada a execute cuya sentencia contiene el fragmento."""
    return next(
        llamada
        for llamada in cursor.execute.call_args_list
        if fragmento in llamada.args[0]
    )


class TestObtenerPagosPendientes:

    def test_con_pagos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "factura_id": FACTURA_VALIDA,
                "Monto": Decimal("25.50"),
                "estado": "pendiente",
            },
        ]

        resultado = ValidacionPagosModel().obtener_pagos_pendientes()

        assert resultado[0]["Monto"] == 25.5
        assert "LOWER(TRIM(mp.Estado_pago)) = 'pendiente'" in ultima_sentencia(
            cursor
        )
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_pagos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert ValidacionPagosModel().obtener_pagos_pendientes() == []

    def test_conexion_caida(self, conexion_caída):
        assert ValidacionPagosModel().obtener_pagos_pendientes() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert ValidacionPagosModel().obtener_pagos_pendientes() == []
        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        ValidacionPagosModel().obtener_pagos_pendientes()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerPagosAprobados:

    def test_con_pagos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "factura_id": FACTURA_VALIDA,
                "Monto": Decimal("10.00"),
                "estado": "aprobado",
            },
        ]

        resultado = ValidacionPagosModel().obtener_pagos_aprobados()

        assert resultado[0]["Monto"] == 10.0
        assert "LOWER(TRIM(mp.Estado_pago)) = 'aprobado'" in ultima_sentencia(
            cursor
        )
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_pagos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert ValidacionPagosModel().obtener_pagos_aprobados() == []

    def test_conexion_caida(self, conexion_caída):
        assert ValidacionPagosModel().obtener_pagos_aprobados() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert ValidacionPagosModel().obtener_pagos_aprobados() == []
        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        ValidacionPagosModel().obtener_pagos_aprobados()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestObtenerPagosRechazados:

    def test_con_pagos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "factura_id": FACTURA_VALIDA,
                "Monto": Decimal("5.75"),
                "estado": "rechazado",
                "Motivo_rechazo": "Comprobante inválido",
            },
        ]

        resultado = ValidacionPagosModel().obtener_pagos_rechazados()

        assert resultado[0]["Monto"] == 5.75
        assert "LOWER(TRIM(mp.Estado_pago)) = 'rechazado'" in ultima_sentencia(
            cursor
        )
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_pagos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        assert ValidacionPagosModel().obtener_pagos_rechazados() == []

    def test_conexion_caida(self, conexion_caída):
        assert ValidacionPagosModel().obtener_pagos_rechazados() == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        assert ValidacionPagosModel().obtener_pagos_rechazados() == []
        cursor.close.assert_called_once()
        db.close.assert_called_once()

    def test_no_modifica_la_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        ValidacionPagosModel().obtener_pagos_rechazados()

        sin_sentencia(cursor, "INSERT")
        sin_sentencia(cursor, "UPDATE")
        sin_sentencia(cursor, "DELETE")
        db.commit.assert_not_called()


class TestAprobarPago:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]

        with patch("app.models.validacion_pagos.datetime") as datetime_mock:
            datetime_mock.now.return_value = FECHA_FIJA
            resultado = ValidacionPagosModel().aprobar_pago(
                factura_id=FACTURA_VALIDA,
                empleado_id=EMPLEADO_MINIMO,
            )

        assert resultado == {
            "success": True,
            "message": "Pago aprobado exitosamente.",
        }
        update = llamada_con(cursor, "UPDATE Metodo_pago")
        assert "Estado_pago = 'aprobado'" in update.args[0]
        assert update.args[1] == (
            EMPLEADO_MINIMO,
            FECHA_FIJA,
            FACTURA_VALIDA,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    def test_usa_factura_y_empleado_de_la_instancia(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]

        resultado = ValidacionPagosModel(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
        ).aprobar_pago()

        assert resultado["success"] is True
        assert (
            llamada_con(cursor, "UPDATE Metodo_pago").args[1][0]
            == EMPLEADO_VALIDO
        )

    def test_pago_sin_registro_se_considera_pendiente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), (1,), None]

        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
        )

        assert resultado["success"] is True
        db.commit.assert_called_once()

    @pytest.mark.parametrize(
        "factura, esperado",
        [
            pytest.param(
                "",
                "El ID de la factura no puede estar vacío.",
                id="factura-vacia",
            ),
            pytest.param(
                "FAC#1",
                "El campo Factura solo puede contener letras, números y guiones.",
                id="factura-caracteres-invalidos",
            ),
            pytest.param(
                "FAC-202611-ABCDEFGHIJ",
                "El campo Factura no puede tener más de 20 caracteres.",
                id="factura-demasiado-larga",
            ),
        ],
    )
    def test_factura_invalida(self, conexion_falsa, factura, esperado):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=factura,
            empleado_id=EMPLEADO_VALIDO,
        )

        assert resultado == {"success": False, "error": esperado}
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "empleado, esperado",
        [
            pytest.param(
                "",
                "El ID del empleado no puede estar vacío.",
                id="empleado-vacio",
            ),
            pytest.param(
                "12345",
                "El campo Empleado debe tener al menos 6 dígitos.",
                id="empleado-demasiado-corto",
            ),
            pytest.param(
                "123456789",
                "El campo Empleado no puede tener más de 8 dígitos.",
                id="empleado-demasiado-largo",
            ),
            pytest.param(
                "12345a",
                "El campo Empleado solo puede contener números.",
                id="empleado-no-numerico",
            ),
        ],
    )
    def test_empleado_invalido(self, conexion_falsa, empleado, esperado):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=empleado,
        )

        assert resultado == {"success": False, "error": esperado}
        cursor.execute.assert_not_called()

    def test_factura_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
        )

        assert resultado == {
            "success": False,
            "error": f"La factura '{FACTURA_VALIDA}' no existe.",
        }
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_empleado_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), None]

        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
        )

        assert resultado == {
            "success": False,
            "error": f"El empleado con ID {EMPLEADO_VALIDO} no existe.",
        }
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_pago_ya_procesado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "aprobado"},
        ]

        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
        )

        assert resultado == {
            "success": False,
            "error": "El pago no está pendiente o ya fue procesado.",
        }
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_conexion_caida_despues_de_validar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]
        with patch(
            "app.models.database.conectar.conexion1",
            side_effect=[db, db, db, None],
        ):
            resultado = ValidacionPagosModel().aprobar_pago(
                factura_id=FACTURA_VALIDA,
                empleado_id=EMPLEADO_VALIDO,
            )

        assert resultado == {"success": False, "error": MENSAJE_ERROR_CONEXION}

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]
        # 3 verificaciones + UPDATE que falla
        cursor.execute.side_effect = [
            None,
            None,
            None,
            Exception("fallo simulado"),
        ]

        resultado = ValidacionPagosModel().aprobar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
        )

        assert resultado == {
            "success": False,
            "error": "Error al aprobar pago: fallo simulado",
        }
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]

        with patch(
            "app.models.validacion_pagos.Bitacora"
        ) as bitacora_clase:
            ValidacionPagosModel(usuario_id="7").aprobar_pago(
                factura_id=FACTURA_VALIDA,
                empleado_id=EMPLEADO_VALIDO,
            )

        bitacora_clase.assert_called_once_with(
            accion="Aprobar pago",
            descripcion=(
                f"Se aprobó el pago de la factura ID: {FACTURA_VALIDA}"
            ),
            usuario_id="7",
            modulo_nombre="Validación Pagos",
        )
        bitacora_clase.return_value.registrar.assert_called_once()


class TestRechazarPago:

    def test_datos_validos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]

        with patch("app.models.validacion_pagos.datetime") as datetime_mock:
            datetime_mock.now.return_value = FECHA_FIJA
            resultado = ValidacionPagosModel().rechazar_pago(
                factura_id=FACTURA_VALIDA,
                empleado_id=EMPLEADO_VALIDO,
                motivo=MOTIVO_VALIDO,
            )

        assert resultado == {
            "success": True,
            "message": "Pago rechazado exitosamente.",
        }
        update = llamada_con(cursor, "UPDATE Metodo_pago")
        assert "Estado_pago = 'rechazado'" in update.args[0]
        assert update.args[1] == (
            MOTIVO_VALIDO,
            EMPLEADO_VALIDO,
            FECHA_FIJA,
            FACTURA_VALIDA,
        )
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "motivo, esperado",
        [
            pytest.param(
                "",
                "El motivo de rechazo no puede estar vacío.",
                id="motivo-vacio",
            ),
            pytest.param(
                "abc",
                "El campo Motivo del rechazo debe tener al menos 5 caracteres.",
                id="motivo-demasiado-corto",
            ),
            pytest.param(
                "M" * 256,
                "El campo Motivo del rechazo no puede tener más de 255 caracteres.",
                id="motivo-demasiado-largo",
            ),
            pytest.param(
                "motivo#1",
                "El campo Motivo del rechazo no puede contener caracteres especiales.",
                id="motivo-caracteres-invalidos",
            ),
        ],
    )
    def test_motivo_invalido(self, conexion_falsa, motivo, esperado):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel().rechazar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
            motivo=motivo,
        )

        assert resultado == {"success": False, "error": esperado}
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.parametrize(
        "factura, empleado, esperado",
        [
            pytest.param(
                "",
                EMPLEADO_VALIDO,
                "El ID de la factura no puede estar vacío.",
                id="factura-vacia",
            ),
            pytest.param(
                FACTURA_VALIDA,
                "12345",
                "El campo Empleado debe tener al menos 6 dígitos.",
                id="empleado-corto",
            ),
        ],
    )
    def test_factura_o_empleado_invalidos(
        self, conexion_falsa, factura, empleado, esperado
    ):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel().rechazar_pago(
            factura_id=factura,
            empleado_id=empleado,
            motivo=MOTIVO_VALIDO,
        )

        assert resultado == {"success": False, "error": esperado}
        cursor.execute.assert_not_called()

    def test_factura_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.return_value = None

        resultado = ValidacionPagosModel().rechazar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
            motivo=MOTIVO_VALIDO,
        )

        assert resultado == {
            "success": False,
            "error": f"La factura '{FACTURA_VALIDA}' no existe.",
        }
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_empleado_inexistente(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [(1,), None]

        resultado = ValidacionPagosModel().rechazar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
            motivo=MOTIVO_VALIDO,
        )

        assert resultado == {
            "success": False,
            "error": f"El empleado con ID {EMPLEADO_VALIDO} no existe.",
        }
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_pago_ya_procesado(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "rechazado"},
        ]

        resultado = ValidacionPagosModel().rechazar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
            motivo=MOTIVO_VALIDO,
        )

        assert resultado == {
            "success": False,
            "error": "El pago no está pendiente o ya fue procesado.",
        }
        sin_sentencia(cursor, "UPDATE")
        db.commit.assert_not_called()

    def test_conexion_caida_despues_de_validar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]
        with patch(
            "app.models.database.conectar.conexion1",
            side_effect=[db, db, db, None],
        ):
            resultado = ValidacionPagosModel().rechazar_pago(
                factura_id=FACTURA_VALIDA,
                empleado_id=EMPLEADO_VALIDO,
                motivo=MOTIVO_VALIDO,
            )

        assert resultado == {"success": False, "error": MENSAJE_ERROR_CONEXION}

    def test_error_de_bd_hace_rollback(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]
        cursor.execute.side_effect = [
            None,
            None,
            None,
            Exception("fallo simulado"),
        ]

        resultado = ValidacionPagosModel().rechazar_pago(
            factura_id=FACTURA_VALIDA,
            empleado_id=EMPLEADO_VALIDO,
            motivo=MOTIVO_VALIDO,
        )

        assert resultado == {
            "success": False,
            "error": "Error al rechazar pago: fallo simulado",
        }
        db.rollback.assert_called_once()
        db.commit.assert_not_called()

    def test_registra_bitacora_con_usuario(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchone.side_effect = [
            (1,),
            (1,),
            {"Estado_pago": "pendiente"},
        ]

        with patch(
            "app.models.validacion_pagos.Bitacora"
        ) as bitacora_clase:
            ValidacionPagosModel(usuario_id="7").rechazar_pago(
                factura_id=FACTURA_VALIDA,
                empleado_id=EMPLEADO_VALIDO,
                motivo=MOTIVO_VALIDO,
            )

        bitacora_clase.assert_called_once_with(
            accion="Rechazar pago",
            descripcion=(
                f"Se rechazó el pago de la factura ID: {FACTURA_VALIDA} "
                f"- Motivo: {MOTIVO_VALIDO}"
            ),
            usuario_id="7",
            modulo_nombre="Validación Pagos",
        )
        bitacora_clase.return_value.registrar.assert_called_once()


class TestObtenerDetalleVenta:

    def test_con_items(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "ID_inventario": "1",
                "Cantidad_articulo": Decimal("2"),
                "Costo_venta": Decimal("10.50"),
                "Nombre_producto": "Cable USB",
                "marca": "Genérica",
                "clase": "Accesorios",
            },
        ]

        resultado = ValidacionPagosModel().obtener_detalle_venta(
            factura_id=FACTURA_VALIDA
        )

        assert resultado[0]["Costo_venta"] == 10.5
        assert resultado[0]["Cantidad_articulo"] == 2
        assert resultado[0]["Nombre_producto"] == "Cable USB"
        assert cursor.execute.call_args.args[1] == (FACTURA_VALIDA,)
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_factura(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel().obtener_detalle_venta()

        assert resultado == []
        cursor.execute.assert_not_called()

    @pytest.mark.parametrize(
        "factura",
        [
            pytest.param("   ", id="factura-en-blanco"),
            pytest.param("FAC#1", id="factura-caracteres-invalidos"),
        ],
    )
    def test_factura_invalida(self, conexion_falsa, factura):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel().obtener_detalle_venta(
            factura_id=factura
        )

        assert resultado == []
        cursor.execute.assert_not_called()

    def test_sin_items(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        resultado = ValidacionPagosModel().obtener_detalle_venta(
            factura_id=FACTURA_VALIDA
        )

        assert resultado == []
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = ValidacionPagosModel().obtener_detalle_venta(
            factura_id=FACTURA_VALIDA
        )

        assert resultado == []

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = ValidacionPagosModel().obtener_detalle_venta(
            factura_id=FACTURA_VALIDA
        )

        assert resultado == []
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestObtenerReportesPagos:

    def test_con_filtros_y_resumen(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "factura_id": FACTURA_VALIDA,
                "monto_pagado": Decimal("10.50"),
                "estado": "pendiente",
            },
            {
                "factura_id": "FAC-202611-DEF456",
                "monto_pagado": Decimal("5.25"),
                "estado": "aprobado",
            },
        ]

        resultado = ValidacionPagosModel().obtener_reportes_pagos(
            {
                "q": "ana",
                "estado": "pendiente",
                "metodo_pago": "zelle",
                "fecha_desde": "2026-01-01",
                "fecha_hasta": "2026-01-31",
            }
        )

        assert resultado["success"] is True
        assert resultado["total"] == 2
        assert resultado["total_monto"] == pytest.approx(15.75)
        assert resultado["pagos"][0]["monto_pagado"] == 10.5
        consulta = llamada_con(cursor, "FROM Venta v")
        assert consulta.args[1] == (
            "%ana%",
            "%ana%",
            "%ana%",
            "pendiente",
            "zelle",
            "2026-01-01",
            "2026-01-31",
        )
        db.commit.assert_not_called()
        cierra_recursos(db, cursor)

    def test_sin_datos(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        resultado = ValidacionPagosModel().obtener_reportes_pagos({})

        assert resultado == {
            "success": True,
            "pagos": [],
            "total": 0,
            "total_monto": 0,
        }
        assert llamada_con(cursor, "FROM Venta v").args[1] == ()

    @pytest.mark.parametrize(
        "filtros, esperado",
        [
            pytest.param(
                {"q": "Bus#1"},
                "El campo Búsqueda no puede contener caracteres especiales.",
                id="busqueda-invalida",
            ),
            pytest.param(
                {"fecha_desde": "2026/01/01"},
                "Formato de fecha inválido. Use YYYY-MM-DD.",
                id="fecha-invalida",
            ),
            pytest.param(
                {"monto_min": "100", "monto_max": "50"},
                "El monto mínimo no puede ser mayor que el monto máximo.",
                id="rango-de-montos-invertido",
            ),
        ],
    )
    def test_filtros_invalidos_no_tocan_la_bd(
        self, conexion_falsa, filtros, esperado
    ):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel().obtener_reportes_pagos(filtros)

        assert resultado == {
            "success": False,
            "error": esperado,
            "pagos": [],
            "total": 0,
        }
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = ValidacionPagosModel().obtener_reportes_pagos({})

        assert resultado == {
            "success": False,
            "error": "Error al conectar a la base de datos.",
            "pagos": [],
            "total": 0,
        }

    def test_error_de_bd(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = ValidacionPagosModel().obtener_reportes_pagos({})

        assert resultado == {
            "success": False,
            "error": "fallo simulado",
            "pagos": [],
            "total": 0,
        }
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestActualizarFechaPago:

    def test_actualiza_la_fecha(self, conexion_falsa):
        db, cursor = conexion_falsa

        with patch("app.models.validacion_pagos.datetime") as datetime_mock:
            datetime_mock.now.return_value = FECHA_FIJA
            resultado = ValidacionPagosModel(
                factura_id=FACTURA_VALIDA
            ).actualizar_fecha_pago()

        assert resultado is None
        update = llamada_con(cursor, "UPDATE Metodo_pago")
        assert "SET Fecha_pago = %s" in update.args[0]
        assert update.args[1] == (FECHA_FIJA, FACTURA_VALIDA)
        db.commit.assert_called_once()
        db.rollback.assert_not_called()
        cierra_recursos(db, cursor)

    @pytest.mark.parametrize(
        "factura",
        [
            pytest.param(None, id="sin-factura"),
            pytest.param("", id="factura-vacia"),
            pytest.param("FAC#1", id="factura-invalida"),
        ],
    )
    def test_sin_factura_valida_no_toca_la_bd(self, conexion_falsa, factura):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel(
            factura_id=factura
        ).actualizar_fecha_pago()

        assert resultado is None
        cursor.execute.assert_not_called()
        db.commit.assert_not_called()

    def test_conexion_caida(self, conexion_caída):
        resultado = ValidacionPagosModel(
            factura_id=FACTURA_VALIDA
        ).actualizar_fecha_pago()

        assert resultado is None

    def test_error_de_bd_hace_rollback_sin_propagar(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.execute.side_effect = Exception("fallo simulado")

        resultado = ValidacionPagosModel(
            factura_id=FACTURA_VALIDA
        ).actualizar_fecha_pago()

        assert resultado is None
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        cursor.close.assert_called_once()
        db.close.assert_called_once()


class TestObtenerReporteDetalleVentas:

    def test_con_detalle(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = [
            {
                "ID_inventario": "1",
                "Cantidad_articulo": Decimal("2"),
                "Costo_venta": Decimal("10.00"),
            },
        ]

        resultado = ValidacionPagosModel(
            factura_id=FACTURA_VALIDA
        ).obtener_reporte_detalle_ventas()

        assert resultado["success"] is True
        assert resultado["detalle"][0]["Costo_venta"] == 10.0
        assert resultado["detalle"][0]["Cantidad_articulo"] == 2

    def test_sin_detalle(self, conexion_falsa):
        db, cursor = conexion_falsa
        cursor.fetchall.return_value = []

        resultado = ValidacionPagosModel(
            factura_id=FACTURA_VALIDA
        ).obtener_reporte_detalle_ventas()

        assert resultado == {
            "success": False,
            "error": "No se encontró detalle para la venta",
        }

    def test_conexion_caida(self, conexion_caída):
        resultado = ValidacionPagosModel(
            factura_id=FACTURA_VALIDA
        ).obtener_reporte_detalle_ventas()

        assert resultado == {
            "success": False,
            "error": "No se encontró detalle para la venta",
        }

    def test_factura_invalida(self, conexion_falsa):
        db, cursor = conexion_falsa

        resultado = ValidacionPagosModel(
            factura_id="FAC#1"
        ).obtener_reporte_detalle_ventas()

        assert resultado == {
            "success": False,
            "error": "No se encontró detalle para la venta",
        }
        cursor.execute.assert_not_called()


class TestObtenerMetodosPagoDisponibles:

    def test_metodos_pago_disponibles(self):
        esperado = [
            "pago_movil",
            "zelle",
            "binance",
            "efectivo_usd",
            "efectivo_bs",
        ]

        assert (
            ValidacionPagosModel().obtener_metodos_pago_disponibles()
            == esperado
        )


class TestObtenerMonedasDisponibles:

    def test_monedas_disponibles(self):
        assert ValidacionPagosModel().obtener_monedas_disponibles() == [
            "USD",
            "VES",
            "USDT",
        ]
