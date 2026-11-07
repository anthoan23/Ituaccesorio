"""Configuración de las pruebas de integración."""
from pathlib import Path

import pytest
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session", autouse=True)
def entorno_prueba():
    """Carga las credenciales de las BD de prueba."""
    load_dotenv(RAIZ / ".env.test", override=True)
