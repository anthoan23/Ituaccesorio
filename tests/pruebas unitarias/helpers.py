"""Utilidades compartidas por las pruebas unitarias."""


def sin_sentencia(cursor, verbo):
    """Comprueba que no se ejecutó ninguna sentencia con ese verbo."""
    verbo = verbo.upper()
    ejecutadas = [llamada.args[0].upper() for llamada in cursor.execute.call_args_list]
    assert not any(verbo in sql for sql in ejecutadas), (
        f"No debía ejecutarse '{verbo}', pero se ejecutó: {ejecutadas}"
    )


def ultima_sentencia(cursor):
    """Devuelve la última consulta SQL ejecutada en el cursor."""
    return cursor.execute.call_args_list[-1].args[0]


def cierra_recursos(db, cursor):
    """Comprueba que se cerraron cursor y conexión (cada operación cierra los suyos)."""
    cursor.close.assert_called()
    db.close.assert_called()
