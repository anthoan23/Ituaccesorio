from app.utils.validators import validar_limite_credito, validar_rif


def test_validar_limite_credito_permite_formatos_locales():
    assert validar_limite_credito("1000") is None
    assert validar_limite_credito("1000.00") is None
    assert validar_limite_credito("1000,00") is None
    assert validar_limite_credito("1.000,00") is None


def test_validar_limite_credito_rechaza_negativos():
    assert "no puede ser negativo" in validar_limite_credito("-1")
    assert "no puede ser negativo" in validar_limite_credito("-1,00")


def test_validar_rif_permite_je_v_y_rechaza_otros():
    assert validar_rif("J-12345678-9") is None
    assert validar_rif("E-12345678-9") is None
    assert validar_rif("V-12345678-9") is None
    assert "formato válido" in validar_rif("X-12345678-9")
    assert "formato válido" in validar_rif("T-12345678-9")
