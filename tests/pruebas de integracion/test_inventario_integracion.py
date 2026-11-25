"""Pruebas de integración del módulo Inventario contra MySQL real.

El módulo Inventario es de lectura más una sola
operación de escritura. A diferencia de Proveedores o Productos, **no tiene
`registrar_*` ni `eliminar_*`**: el registro de existencias lo hace el flujo de
abastecimiento de órdenes de compra (`app/models/ordenes_entregas.py`, que hace
el INSERT en `Existencias_productos`) y el borrado lo hace `Producto.eliminar_producto()`
en cascada. Por eso estas pruebas cubren lo que el modelo sí expone:

    - listar inventario (con JOIN a producto, marca y clase);
    - aumentar_stock (la única escritura del módulo);
    - y la relación Producto → Existencias (al eliminar el producto, su
      inventario desaparece en cascada).

Para crear/borrar la existencia temporal (que no tiene método en el modelo) se
usa SQL directo vía `conectar()`, igual que la limpieza de los catálogos.
"""
from app.models.database import conectar
from app.models.inventario import Inventario
from app.models.productos import ClaseProducto, MarcaProducto, Producto

# Datos temporales de la prueba (zona que no interfiere con el seed).
NOMBRE_CLASE = "Clase Temporal Inventario"
NOMBRE_MARCA = "Marca Temporal Inventario"
NOMBRE_PRODUCTO = "Producto Temporal Inventario"
DESCRIPCION_PRODUCTO = "Producto temporal de inventario"
ID_INVENTARIO_TEMPORAL = "INV999999"
EXISTENCIA_INICIAL = 3
AUMENTO = 5

# Datos sembrados directamente en la BD de prueba
# (bd/tests/ituaccesoriobd.sql): existencia del seed "Seed iPhone 13".
ID_INVENTARIO_SEED = "INV000901"


def _ejecutar_sql(sql, params=()):
    """Ejecuta una sentencia contra la BD principal y confirma la transacción."""
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute(sql, params)
        db.commit()
    finally:
        cursor.close()
        db.close()


def _crear_existencia(id_producto, id_inventario, existencia, costo_venta=10.00):
    """Crea una fila de Existencias_productos (no existe método en el modelo)."""
    _ejecutar_sql(
        "INSERT INTO Existencias_productos (ID_inventario, ID_producto, Existencia, Costo_venta) "
        "VALUES (%s, %s, %s, %s)",
        (id_inventario, id_producto, existencia, costo_venta),
    )


def _crear_producto_temporal():
    """Registra clase, marca y producto temporales; devuelve (id_clase, id_marca, id_producto)."""
    id_clase = ClaseProducto(nombre=NOMBRE_CLASE).registrar_clase()
    id_marca = MarcaProducto(nombre=NOMBRE_MARCA).registrar_marca()
    id_producto = Producto(
        id_clase=id_clase,
        id_marca=id_marca,
        nombre=NOMBRE_PRODUCTO,
        descripcion=DESCRIPCION_PRODUCTO,
    ).registrar_producto()
    return id_clase, id_marca, id_producto


def _existencia_de(id_inventario):
    """Devuelve la existencia de una fila del inventario, o None si no existe."""
    for item in Inventario().listar_inventario():
        if item["id_inventario"] == id_inventario:
            return item["existencia"]
    return None


def limpiar_datos_temporales():
    """Elimina los registros temporales (de esta corrida o de una previa abortada)."""
    # 1. Existencia temporal (por si quedó de una corrida abortada).
    _ejecutar_sql(
        "DELETE FROM Existencias_productos WHERE ID_inventario = %s",
        (ID_INVENTARIO_TEMPORAL,),
    )
    # 2. Producto temporal (elimina también sus existencias en cascada).
    for producto in Producto().listar_productos(q=NOMBRE_PRODUCTO):
        if producto.get("nombre") == NOMBRE_PRODUCTO:
            Producto(id_producto=producto["id"]).eliminar_producto()
    # 3. Marca y clase temporales (catálogos sin método de borrado).
    _ejecutar_sql(
        "DELETE FROM Marca_producto WHERE Nombre_marca = %s", (NOMBRE_MARCA,)
    )
    _ejecutar_sql(
        "DELETE FROM Clase_producto WHERE Nombre_Clase = %s", (NOMBRE_CLASE,)
    )


def test_listar_inventario_con_relaciones():
    # La consulta resuelve el JOIN con producto, marca y clase sobre el seed.
    inventario = Inventario().listar_inventario()
    assert inventario

    seed = next(
        (item for item in inventario if item["id_inventario"] == ID_INVENTARIO_SEED),
        None,
    )
    assert seed is not None
    # El punto del test son las relaciones (JOIN), no el valor exacto del stock,
    # que puede variar si otra prueba o el flujo de abastecimiento lo modifica.
    assert seed["nombre_producto"] == "Seed iPhone 13"
    assert seed["nombre_marca"] == "Iphone"
    assert seed["nombre_clase"] == "Telefono"
    assert seed["existencia"] >= 0


def test_aumentar_stock():
    limpiar_datos_temporales()
    try:
        _, _, id_producto = _crear_producto_temporal()
        _crear_existencia(id_producto, ID_INVENTARIO_TEMPORAL, EXISTENCIA_INICIAL)

        assert _existencia_de(ID_INVENTARIO_TEMPORAL) == EXISTENCIA_INICIAL

        # La única escritura del módulo: aumentar el stock.
        assert (
            Inventario(id_inventario=ID_INVENTARIO_TEMPORAL).aumentar_stock(AUMENTO)
            is True
        )
        assert _existencia_de(ID_INVENTARIO_TEMPORAL) == EXISTENCIA_INICIAL + AUMENTO
    finally:
        limpiar_datos_temporales()


def test_eliminar_producto_elimina_inventario():
    limpiar_datos_temporales()
    try:
        _, _, id_producto = _crear_producto_temporal()
        _crear_existencia(id_producto, ID_INVENTARIO_TEMPORAL, EXISTENCIA_INICIAL)

        assert _existencia_de(ID_INVENTARIO_TEMPORAL) == EXISTENCIA_INICIAL

        # Al eliminar el producto, su inventario desaparece en cascada.
        assert Producto(id_producto=id_producto).eliminar_producto() is True
        assert _existencia_de(ID_INVENTARIO_TEMPORAL) is None
    finally:
        limpiar_datos_temporales()
