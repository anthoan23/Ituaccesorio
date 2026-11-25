"""Pruebas de integración del módulo Productos contra MySQL real.

Escenario: se registra la clase y la marca (padres)
y luego un producto (hijo) que usa ambas, verificando
la relación en la BD; y se verifica que no se pueda eliminar un registro "en
uso" (una clase con productos, y un producto con stock en inventario).

La jerarquía del módulo es:
    Clase_producto / Marca_producto  (padres)
            └── Producto             (hijo, referencia a ambos)
                    └── Existencias_productos  (inventario / stock)

Nota: `ClaseProducto` y `MarcaProducto` solo tienen `registrar_*` y `listar_*`
(no existe `eliminar_*` en el modelo), por eso la limpieza de esos catálogos
se hace con SQL directo vía `conectar()`.
"""
import mysql.connector
import pytest

from app.models.database import conectar
from app.models.productos import ClaseProducto, MarcaProducto, Producto

# Datos temporales de la prueba (zona que no interfiere con el seed).
NOMBRE_CLASE = "Clase Temporal Integracion"
NOMBRE_MARCA = "Marca Temporal Integracion"
NOMBRE_PRODUCTO = "Producto Temporal Integracion"
DESCRIPCION_PRODUCTO = "Producto temporal de integración"

# Datos sembrados directamente en la BD de prueba
# (bd/tests/ituaccesoriobd.sql):
#   - clase '1' (Telefono): en uso por varios productos del seed.
#   - producto '102' (Producto En Uso Carrito): con stock (Existencia = 5).
ID_CLASE_EN_USO = "1"
ID_PRODUCTO_CON_STOCK = "102"


def _borrar_catalogo(tabla, columna, nombre):
    """Elimina filas de un catálogo (clase/marca) por nombre usando SQL directo."""
    db = conectar().conexion1()
    if not db:
        return
    cursor = db.cursor()
    try:
        cursor.execute(f"DELETE FROM {tabla} WHERE {columna} = %s", (nombre,))
        db.commit()
    finally:
        cursor.close()
        db.close()


def limpiar_datos_temporales():
    """Elimina los registros temporales (de esta corrida o de una previa abortada)."""
    # 1. Producto temporal (por nombre). Primero, porque la FK restringiría
    #    borrar la clase/marca mientras el producto las referencie.
    for producto in Producto().listar_productos(q=NOMBRE_PRODUCTO):
        if producto.get("nombre") == NOMBRE_PRODUCTO:
            Producto(id_producto=producto["id"]).eliminar_producto()

    # 2. Marca y clase temporales (catálogos sin método de borrado en el modelo).
    _borrar_catalogo("Marca_producto", "Nombre_marca", NOMBRE_MARCA)
    _borrar_catalogo("Clase_producto", "Nombre_Clase", NOMBRE_CLASE)


def test_registrar_clase_marca_y_producto():
    limpiar_datos_temporales()
    try:
        # 1. Registrar la clase y la marca (padres).
        id_clase = ClaseProducto(nombre=NOMBRE_CLASE).registrar_clase()
        assert id_clase
        id_marca = MarcaProducto(nombre=NOMBRE_MARCA).registrar_marca()
        assert id_marca

        # 2. Registrar un producto (hijo) que usa esa clase y marca.
        id_producto = Producto(
            id_clase=id_clase,
            id_marca=id_marca,
            nombre=NOMBRE_PRODUCTO,
            descripcion=DESCRIPCION_PRODUCTO,
        ).registrar_producto()
        assert id_producto

        assert Producto(id_producto=id_producto).verificar_producto() is True

        # La relación se refleja en la consulta (JOIN con clase y marca).
        consulta = Producto(id_producto=id_producto).obtener_producto()
        assert consulta is not None
        assert consulta["nombre"] == NOMBRE_PRODUCTO
        assert consulta["clase_nombre"] == NOMBRE_CLASE
        assert consulta["marca_nombre"] == NOMBRE_MARCA

        assert any(
            producto["id"] == id_producto
            for producto in Producto().listar_productos(q=NOMBRE_PRODUCTO)
        )

        # 3. Eliminar el producto (hijo) y verificar que ya no existe.
        assert Producto(id_producto=id_producto).eliminar_producto() is True
        assert Producto(id_producto=id_producto).verificar_producto() is False
    finally:
        limpiar_datos_temporales()


def test_no_se_puede_eliminar_clase_con_productos():
    # La clase '1' (Telefono) está en uso por productos del seed.
    productos = Producto().listar_productos(id_clase=ID_CLASE_EN_USO)
    assert productos, "El seed debería tener productos que usan la clase '1'"

    # La FK Producto_ibfk_1 (RESTRICT) impide borrar la clase en uso.
    db = conectar().conexion1()
    cursor = db.cursor()
    try:
        with pytest.raises(mysql.connector.IntegrityError):
            cursor.execute(
                "DELETE FROM Clase_producto WHERE ID_Clase = %s", (ID_CLASE_EN_USO,)
            )
    finally:
        db.rollback()
        cursor.close()
        db.close()

    # La clase sigue intacta.
    assert ClaseProducto(id_clase=ID_CLASE_EN_USO).verificar_clase() is True


def test_no_se_puede_eliminar_producto_con_stock():
    # Producto '102' con stock en inventario (Existencia = 5).
    modelo = Producto(id_producto=ID_PRODUCTO_CON_STOCK)

    assert modelo.verificar_producto() is True
    assert modelo.verificar_stock_asociado() is True
    assert modelo.obtener_stock_producto() == 5

    # El controlador usa esta verificación para impedir borrar un producto
    # con stock (regla de negocio de api_eliminar_modelo).
    resultado = modelo.verificar_stock_procedure()
    assert resultado["success"] is True
    assert resultado["tiene_stock"] is True
    assert resultado["stock_total"] == 5
