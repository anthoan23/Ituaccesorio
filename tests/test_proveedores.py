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
