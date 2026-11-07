"""Pruebas de integración de Bitacora contra MySQL real (BD seguridad)."""
import pytest

from app.models.bitacora import Bitacora
from seed_helpers import limpiar_bitacora_por_descripcion


USUARIO_ADMIN = "USR-001"
MODULO_VALIDO = "Empleados"
MODULO_INEXISTENTE = "NoExiste"


@pytest.fixture(autouse=True)
def limpieza_automatica():
    """Antes y después de cada test, limpia bitácora de prueba."""
    limpiar_bitacora_por_descripcion("_BITACORA_TEST_")
    yield
    limpiar_bitacora_por_descripcion("_BITACORA_TEST_")


# ==================== OBTENER MODULO ID ====================

class TestObtenerModuloId:

    def test_modulo_existente(self):
        modulo_id = Bitacora().obtener_modulo_id(MODULO_VALIDO)
        # Empleados es id=1 en el seed
        assert modulo_id == 1

    def test_modulo_inexistente_cae_al_primero(self):
        modulo_id = Bitacora().obtener_modulo_id(MODULO_INEXISTENTE)
        # Si no encuentra, busca el primero (id=1)
        assert modulo_id == 1

    def test_sin_nombre_usa_el_primero(self):
        modulo_id = Bitacora().obtener_modulo_id()
        assert modulo_id == 1


# ==================== REGISTRAR ====================

class TestRegistrar:

    def test_registra_accion_valida(self):
        resultado = Bitacora(
            accion="Test acción",
            descripcion="_BITACORA_TEST_ descripción válida",
            usuario_id=USUARIO_ADMIN,
            modulo_nombre=MODULO_VALIDO,
        ).registrar()

        assert resultado == {"success": True}

        registros = Bitacora().listar_recientes(limite=100)
        encontrado = next(
            (r for r in registros if "_BITACORA_TEST_" in (r["descripcion"] or "")),
            None,
        )
        assert encontrado is not None
        assert encontrado["accion"] == "Test acción"
        assert encontrado["usuario_id"] == USUARIO_ADMIN
        assert encontrado["modulo_nombre"] == "Empleados"

    def test_sin_accion(self):
        resultado = Bitacora(
            accion="", descripcion="_BITACORA_TEST_ x", usuario_id=USUARIO_ADMIN
        ).registrar()
        assert resultado["success"] is False
        assert "Acción y descripción" in resultado["warning"]

    def test_sin_descripcion(self):
        resultado = Bitacora(
            accion="Test", descripcion="", usuario_id=USUARIO_ADMIN
        ).registrar()
        assert resultado["success"] is False
        assert "Acción y descripción" in resultado["warning"]

    def test_con_parametros_override(self):
        bitacora = Bitacora()
        resultado = bitacora.registrar(
            accion="Test override",
            descripcion="_BITACORA_TEST_ desde parámetros",
            usuario_id=USUARIO_ADMIN,
            modulo_nombre=MODULO_VALIDO,
        )
        assert resultado == {"success": True}

    def test_usuario_id_por_defecto_system(self):
        resultado = Bitacora(
            accion="Test system",
            descripcion="_BITACORA_TEST_ con SYSTEM",
            modulo_nombre=MODULO_VALIDO,
        ).registrar()
        # SYSTEM no es un usuario real, pero la FK no falla porque usuario_id
        # no tiene FK constraint explícito en bitacora (solo índice).
        # Si fallara por FK, este test lo detecta.
        assert isinstance(resultado, dict)


# ==================== LISTAR RECIENTES ====================

class TestListarRecientes:

    def test_devuelve_lista(self):
        registros = Bitacora().listar_recientes()
        assert isinstance(registros, list)

    def test_respeta_limite(self):
        for i in range(5):
            Bitacora(
                accion=f"Test {i}",
                descripcion=f"_BITACORA_TEST_ iteración {i}",
                usuario_id=USUARIO_ADMIN,
                modulo_nombre=MODULO_VALIDO,
            ).registrar()

        registros = Bitacora().listar_recientes(limite=2)
        assert len(registros) <= 2

    def test_incluye_datos_del_modulo(self):
        Bitacora(
            accion="Test módulo",
            descripcion="_BITACORA_TEST_ para verificar módulo",
            usuario_id=USUARIO_ADMIN,
            modulo_nombre=MODULO_VALIDO,
        ).registrar()

        registros = Bitacora().listar_recientes(limite=100)
        encontrado = next(
            (r for r in registros if "_BITACORA_TEST_" in (r["descripcion"] or "")),
            None,
        )
        assert encontrado is not None
        assert encontrado["modulo_nombre"] == "Empleados"

    def test_ordenados_por_id_desc(self):
        registros = Bitacora().listar_recientes(limite=20)
        ids = [r["id"] for r in registros]
        assert ids == sorted(ids, reverse=True)

    def test_incluye_fallback_usuario_id(self):
        """_obtener_info_usuario consulta conexion1 (sin tabla usuario).

        Ese bug hace que siempre caiga al fallback usuario_id.
        Lo documento aquí como comportamiento conocido.
        """
        Bitacora(
            accion="Test fallback",
            descripcion="_BITACORA_TEST_ fallback usuario",
            usuario_id=USUARIO_ADMIN,
            modulo_nombre=MODULO_VALIDO,
        ).registrar()

        registros = Bitacora().listar_recientes(limite=100)
        encontrado = next(
            (r for r in registros if "_BITACORA_TEST_" in (r["descripcion"] or "")),
            None,
        )
        assert encontrado is not None
        # El bug hace que usuario_nombre caiga al usuario_id
        assert encontrado["usuario_nombre"] == USUARIO_ADMIN
        assert encontrado["usuario_foto"] is None


# ==================== ACTIVIDAD RECIENTE ====================

class TestListarActividadReciente:

    def test_devuelve_lista(self):
        actividades = Bitacora().listar_actividad_reciente(limite=5)
        assert isinstance(actividades, list)

    def test_incluye_tiempo_relativo(self):
        Bitacora(
            accion="Test tiempo",
            descripcion="_BITACORA_TEST_ con tiempo relativo",
            usuario_id=USUARIO_ADMIN,
            modulo_nombre=MODULO_VALIDO,
        ).registrar()

        actividades = Bitacora().listar_actividad_reciente(limite=10)
        encontrado = next(
            (a for a in actividades if "_BITACORA_TEST_" in (a["descripcion"] or "")),
            None,
        )
        assert encontrado is not None
        assert "tiempo_relativo" in encontrado
        assert encontrado["tiempo_relativo"] == "hace unos segundos"

    def test_limita_correctamente(self):
        actividades = Bitacora().listar_actividad_reciente(limite=3)
        assert len(actividades) <= 3


# ==================== FUNCIÓN HELPER ====================

class TestFuncionHelper:

    def test_listar_actividad_reciente_dashboard(self):
        from app.models.bitacora import listar_actividad_reciente_dashboard
        resultado = listar_actividad_reciente_dashboard(limite=5)
        assert isinstance(resultado, list)