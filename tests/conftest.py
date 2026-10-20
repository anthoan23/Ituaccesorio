from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def db_falsa():
    """Crea (db, cursor) simulados sin tocar la base de datos real."""
    db = MagicMock()
    cursor = MagicMock()
    cursor.nextset.return_value = False
    db.cursor.return_value = cursor
    return db, cursor


@pytest.fixture
def conexion_falsa(db_falsa):
    """Simula la base de datos sin tocar la real.

    Parchea los métodos de la clase base `conectar`, así sirve para
    cualquier modelo que herede de ella (no hay que redefinir el fixture
    en cada archivo de prueba). Devuelve (db, cursor).
    """
    db, cursor = db_falsa
    with patch("app.models.database.conectar.conexion1", return_value=db), patch(
        "app.models.database.conectar.conexion2", return_value=db
    ):
        yield db, cursor


@pytest.fixture
def conexion_caída():
    """Simula que la base de datos no responde: conexion1() devuelve None."""
    with patch("app.models.database.conectar.conexion1", return_value=None), patch(
        "app.models.database.conectar.conexion2", return_value=None
    ):
        yield
