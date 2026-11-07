from app.utils.validators import validar_limite_credito


def test_validar_limite_credito_permite_formatos_locales():
    assert validar_limite_credito("1000") is None
    assert validar_limite_credito("1000.00") is None
    assert validar_limite_credito("1000,00") is None
    assert validar_limite_credito("1.000,00") is None


def test_validar_limite_credito_rechaza_negativos():
    assert "no puede ser negativo" in validar_limite_credito("-1")
    assert "no puede ser negativo" in validar_limite_credito("-1,00")
