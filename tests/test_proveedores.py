from unittest.mock import MagicMock, patch

import pytest

from app.models.proveedores import Proveedores


class TestValidacionModeloProveedores:
    def test_crear_proveedor_rechaza_nombre_invalido_en_modelo(self):
        db = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        db.cursor.return_value = cursor

        with patch("app.models.database.conectar.conexion1", return_value=db):
            proveedor = Proveedores(
                rif="J-12345678-9",
                nombre="@@",
                tipo="Nacional",
                celular="04141234567",
                correo="proveedor@test.com",
                direccion="Av. Principal",
                limite_credito=500,
            )

            with pytest.raises(ValueError, match="Nombre del proveedor"):
                proveedor.crear_proveedor()

    def test_validacion_celular_rechaza_prefijos_no_permitidos(self):
        proveedor = Proveedores(
            rif="J-12345678-9",
            nombre="Proveedor Demo",
            tipo="Nacional",
            celular="04101234567",
            correo="proveedor@test.com",
            direccion="Av. Principal",
            limite_credito=500,
        )

        with pytest.raises(ValueError, match="prefijo válido|0412, 0414, 0416, 0422, 0424 o 0426"):
            proveedor._validar_datos_basicos()

    def test_validacion_celular_permite_vacio_en_proveedor(self):
        proveedor = Proveedores(
            rif="J-12345678-9",
            nombre="Proveedor Demo",
            tipo="Nacional",
            celular="",
            correo="proveedor@test.com",
            direccion="Av. Principal",
            limite_credito=500,
        )

        proveedor._validar_datos_basicos()
