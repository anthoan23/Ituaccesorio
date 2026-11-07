"""Pruebas de integración de la clase Modulo contra MySQL real (BD seguridad)."""
import random

import pytest

from app.models.modulos import Modulo


MODULOS_SEED = {
    "Empleados", "Especialidades", "Cargos", "Catálogo", "Ventas",
    "Productos", "Inventario", "Proveedores", "Trade-in", "Taller",
    "Órdenes de servicio", "Órdenes de compra", "Clientes", "Usuarios",
    "Bitácora", "Personal",
}


def _nombre_modulo_unico() -> str:
    """Nombre de módulo válido (solo letras/números, sin espacios) y único."""
    return f"ModTest{random.randint(100000, 999999)}"


def datos_modulo(**cambios):
    datos = {
        "nombre": _nombre_modulo_unico(),
        "descripcion": "Modulo de prueba",
    }
    datos.update(cambios)
    return datos


def _limpiar_modulo(nombre: str) -> None:
    """Borra el módulo por nombre si existe (evita basura entre tests)."""
    if Modulo(nombre=nombre).verificar_modulo_por_nombre():
        modulo = Modulo(nombre=nombre)
        id_modulo = None
        # obtener_modulo_por_id solo busca por id; hacemos query directa
        from app.models.database import conectar
        db = conectar().conexion2()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("SELECT id FROM modulo WHERE nombre = %s LIMIT 1", (nombre,))
                fila = cursor.fetchone()
                if fila:
                    id_modulo = str(fila[0])
            finally:
                cursor.close()
                db.close()
        if id_modulo:
            Modulo(id=id_modulo).eliminar_modulo()


# ==================== LISTAR ====================

class TestListarModulos:

    def test_devuelve_los_16_modulos_del_seed(self):
        modulos = Modulo().listar_modulos()

        assert modulos is not None
        assert len(modulos) >= 16
        nombres = {m["nombre"] for m in modulos}
        assert MODULOS_SEED.issubset(nombres)

    def test_ordenados_por_nombre(self):
        modulos = Modulo().listar_modulos()
        nombres = [m["nombre"] for m in modulos]
        assert nombres == sorted(nombres)


# ==================== VERIFICAR ====================

class TestVerificarModulo:

    def test_por_id_existente(self):
        # id=1 es Empleados en el seed
        assert Modulo(id="1").verificar_modulo_por_id() is True

    def test_por_id_inexistente(self):
        assert Modulo(id="999999").verificar_modulo_por_id() is False

    def test_por_id_vacio(self):
        assert Modulo(id="").verificar_modulo_por_id() is False

    def test_por_nombre_existente(self):
        assert Modulo(nombre="Empleados").verificar_modulo_por_nombre() is True

    def test_por_nombre_inexistente(self):
        assert Modulo(nombre=_nombre_modulo_unico()).verificar_modulo_por_nombre() is False

    def test_por_nombre_vacio(self):
        assert Modulo(nombre="").verificar_modulo_por_nombre() is False


# ==================== OBTENER ====================

class TestObtenerModuloPorId:

    def test_modulo_existente(self):
        resultado = Modulo(id="1").obtener_modulo_por_id()
        assert resultado is not None
        assert resultado["id"] == 1
        assert resultado["nombre"] == "Empleados"

    def test_modulo_inexistente(self):
        assert Modulo(id="999999").obtener_modulo_por_id() is None

    def test_sin_id(self):
        assert Modulo().obtener_modulo_por_id() is None

    def test_por_parametro(self):
        resultado = Modulo().obtener_modulo_por_id(modulo_id="5")
        assert resultado is not None
        assert resultado["nombre"] == "Ventas"


# ==================== AGREGAR ====================

class TestAgregarModulo:

    def test_datos_validos(self):
        datos = datos_modulo()
        try:
            resultado = Modulo(**datos).agregar_modulo()
            assert resultado == "Módulo agregado exitosamente."

            modulo = Modulo(nombre=datos["nombre"])
            assert modulo.verificar_modulo_por_nombre() is True
        finally:
            _limpiar_modulo(datos["nombre"])

    def test_modulo_duplicado(self):
        datos = datos_modulo()
        try:
            Modulo(**datos).agregar_modulo()

            resultado = Modulo(**datos).agregar_modulo()
            assert resultado == f"El módulo '{datos['nombre']}' ya existe."
        finally:
            _limpiar_modulo(datos["nombre"])

    @pytest.mark.parametrize(
        "cambios, esperado",
        [
            pytest.param(
                {"nombre": ""},
                "El campo Nombre no puede estar vacío.",
                id="nombre-vacio",
            ),
            pytest.param(
                {"nombre": "N" * 51},
                "El campo Nombre no puede tener más de 50 caracteres.",
                id="nombre-demasiado-largo",
            ),
            pytest.param(
                {"nombre": "Mod Test"},
                "El campo Nombre solo puede contener letras y números (sin espacios).",
                id="nombre-con-espacios",
            ),
            pytest.param(
                {"nombre": "Mod#Test"},
                "El campo Nombre solo puede contener letras y números (sin espacios).",
                id="nombre-con-caracteres-invalidos",
            ),
            pytest.param(
                {"descripcion": "D" * 256},
                "El campo Descripción no puede tener más de 255 caracteres.",
                id="descripcion-demasiado-larga",
            ),
            pytest.param(
                {"descripcion": "Desc @#$"},
                "El campo Descripción no puede contener caracteres especiales.",
                id="descripcion-caracteres-invalidos",
            ),
        ],
    )
    def test_datos_invalidos(self, cambios, esperado):
        resultado = Modulo(**datos_modulo(**cambios)).agregar_modulo()
        assert resultado == esperado


# ==================== ACTUALIZAR ====================

class TestActualizarModulo:

    def test_actualiza_nombre_y_descripcion(self):
        datos = datos_modulo()
        nuevo_nombre = _nombre_modulo_unico()
        try:
            Modulo(**datos).agregar_modulo()
            modulo = Modulo(nombre=datos["nombre"])
            # Obtener el id recién creado
            from app.models.database import conectar
            db = conectar().conexion2()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM modulo WHERE nombre = %s LIMIT 1", (datos["nombre"],))
            id_modulo = str(cursor.fetchone()[0])
            cursor.close()
            db.close()

            resultado = Modulo(
                id=id_modulo, nombre=nuevo_nombre, descripcion="Actualizado"
            ).actualizar_modulo()

            assert resultado == "Módulo actualizado exitosamente."
            consultado = Modulo().obtener_modulo_por_id(modulo_id=id_modulo)
            assert consultado["nombre"] == nuevo_nombre
            assert consultado["descripcion"] == "Actualizado"
        finally:
            _limpiar_modulo(datos["nombre"])
            _limpiar_modulo(nuevo_nombre)

    def test_modulo_inexistente(self):
        resultado = Modulo(
            id="999999", nombre=_nombre_modulo_unico()
        ).actualizar_modulo()
        assert resultado.startswith("El módulo con ID 999999 no existe.")

    def test_sin_id(self):
        resultado = Modulo(nombre=_nombre_modulo_unico()).actualizar_modulo()
        assert resultado == "El ID del módulo es obligatorio."


# ==================== ELIMINAR ====================

class TestEliminarModulo:

    def test_elimina_modulo_sin_permisos(self):
        datos = datos_modulo()
        try:
            Modulo(**datos).agregar_modulo()

            from app.models.database import conectar
            db = conectar().conexion2()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM modulo WHERE nombre = %s LIMIT 1", (datos["nombre"],))
            id_modulo = str(cursor.fetchone()[0])
            cursor.close()
            db.close()

            resultado = Modulo(id=id_modulo).eliminar_modulo()

            assert resultado == "Módulo eliminado exitosamente."
            assert Modulo(id=id_modulo).verificar_modulo_por_id() is False
        finally:
            _limpiar_modulo(datos["nombre"])

    def test_modulo_inexistente(self):
        resultado = Modulo(id="999999").eliminar_modulo()
        assert resultado == "El módulo con identificador 999999 no existe."

    @pytest.mark.parametrize(
        "modulo_id, esperado",
        [
            pytest.param("", "El identificador del módulo no puede estar vacío.", id="vacio"),
            pytest.param(
                "12345678901",
                "El campo Módulo no puede tener más de 10 dígitos.",
                id="demasiado-largo",
            ),
            pytest.param(
                "abc",
                "El campo Módulo solo puede contener números.",
                id="no-numerico",
            ),
        ],
    )
    def test_id_invalido(self, modulo_id, esperado):
        assert Modulo(id=modulo_id).eliminar_modulo() == esperado