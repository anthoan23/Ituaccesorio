"""Pruebas de integración de la clase conectar (app/models/database.py)."""
from app.models.database import conectar


def test_conexion1_responde():
    conexion = conectar()
    db = conexion.conexion1()

    assert db is not None
    assert db.is_connected()

    cursor = db.cursor()
    try:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)
    finally:
        conexion.cerrar_conexion(cursor, db)

    assert not db.is_connected()


def test_conexion2_responde():
    conexion = conectar()
    db = conexion.conexion2()

    assert db is not None
    assert db.is_connected()

    cursor = db.cursor()
    try:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)
    finally:
        conexion.cerrar_conexion(cursor, db)

    assert not db.is_connected()
