"""Pruebas unitarias de app/utils/validators.py (sin base de datos).

Documentan el comportamiento acordado tras la unificación de validaciones:
- Solo hay DOS validadores de texto: `validar_texto` (letras) y
  `validar_texto_numero` (letras + números), ambos parametrizables con
  `permitir_espacios`, `caracteres_extra` y `obligatorio`; no existen más
  variantes duplicadas.
- `validar_texto` no acepta valores de solo espacios (bug corregido).
- `validar_email` rechaza dominios con puntos consecutivos o puntos mal ubicados.
- `validar_rif` admite guiones opcionales y minúsculas, y permite limitar las
  letras con `tipos`.
- `validar_decimal` reutiliza normalizar_numero_decimal: acepta "1.234,56" y
  negativos cuando min_valor < 0; el entero 0 ya no se trata como vacío.
"""

import pytest

from app.utils.validators import (
    normalizar_numero_decimal,
    validar_celular_venezolano,
    validar_contraseña,
    validar_decimal,
    validar_email,
    validar_numero,
    validar_rif,
    validar_texto,
    validar_texto_numero,
)


class TestValidarTexto:

    @pytest.mark.parametrize(
        "valor",
        ["Juan", "María José", "Ñandú Ávila", "  Ana  "],
        ids=["simple", "con-espacios", "acento-enie", "con-bordes"],
    )
    def test_validos(self, valor):
        assert validar_texto(valor, 2, 50, "Nombre") is None

    def test_vacio(self):
        assert validar_texto("", 1, 50, "Nombre") == (
            "El campo Nombre no puede estar vacío."
        )

    def test_solo_espacios_es_invalido(self):
        """Bug corregido: antes '   ' pasaba como nombre válido."""
        assert validar_texto("   ", 3, 50, "Nombre") == (
            "El campo Nombre no puede estar vacío."
        )

    def test_salto_de_linea_al_final_se_normaliza(self):
        """El strip del validador elimina el salto de línea final."""
        assert validar_texto("Juan\n", 3, 50, "Nombre") is None

    def test_demasiado_corto(self):
        assert validar_texto("Ju", 3, 50, "Nombre") == (
            "El campo Nombre debe tener al menos 3 caracteres."
        )

    def test_demasiado_largo(self):
        assert validar_texto("A" * 31, 3, 30, "Nombre") == (
            "El campo Nombre no puede tener más de 30 caracteres."
        )

    def test_con_numeros(self):
        assert validar_texto("Juan123", 3, 50, "Nombre") == (
            "El campo Nombre solo puede contener letras, acentos y espacios."
        )

    def test_sin_espacios_una_palabra(self):
        """Unifica a la antigua validar_solo_letras(permitir_espacios=False)."""
        assert validar_texto("María José", 1, 50, "Nombre", permitir_espacios=False) == (
            "El campo Nombre solo puede contener letras, acentos y ñ (sin espacios)."
        )
        assert validar_texto("María", 1, 50, "Nombre", permitir_espacios=False) is None


class TestValidarTextoNumero:

    def test_valido(self):
        assert validar_texto_numero("INV123", 1, 20, "Producto") is None

    def test_valido_con_espacios(self):
        assert validar_texto_numero("INV 123", 1, 20, "Producto") is None

    def test_vacio(self):
        assert validar_texto_numero("  ", 1, 20, "Producto") == (
            "El campo Producto no puede estar vacío."
        )

    def test_vacio_opcional(self):
        """Unifica a la antigua validar_sin_caracteres_especiales(min_len=0)."""
        assert validar_texto_numero("", 1, 20, "Dirección", obligatorio=False) is None
        assert validar_texto_numero(None, 1, 20, "Dirección", obligatorio=False) is None

    def test_con_caracteres_especiales(self):
        assert validar_texto_numero("Inv#123", 1, 20, "Producto") == (
            "El campo Producto solo puede contener letras, números, acentos y espacios."
        )

    def test_largo(self):
        assert validar_texto_numero("A" * 21, 1, 20, "Producto") == (
            "El campo Producto no puede tener más de 20 caracteres."
        )

    def test_sin_espacios(self):
        """Unifica a la antigua validar_solo_letras_numeros(permitir_espacios=False)."""
        assert validar_texto_numero(
            "Modulo 1", 1, 50, "Nombre", permitir_espacios=False
        ) == "El campo Nombre solo puede contener letras y números (sin espacios)."
        assert validar_texto_numero(
            "Modulo1", 1, 50, "Nombre", permitir_espacios=False
        ) is None

    def test_caracteres_extra_razon_social(self):
        """Unifica a la antigua validar_solo_letras_numeros(caracteres_extra)."""
        assert validar_texto_numero(
            "Empresa C.A.", 1, 60, "Razón social del cliente", caracteres_extra=".-&"
        ) is None

    def test_caracteres_extra_rechaza_otro_signo(self):
        assert validar_texto_numero(
            "Empresa @ C.A.", 1, 60, "Razón social del cliente",
            caracteres_extra=".-&",
        ) == (
            "El campo Razón social del cliente solo puede contener letras, "
            "números, acentos, espacios, puntos, guiones y ampersand (&)."
        )

    def test_caracteres_extra_nombre_producto(self):
        """Unifica a la antigua validar_nombre_producto."""
        assert validar_texto_numero(
            "Funda (iPhone 13) - negra", 2, 50, "Nombre del producto",
            caracteres_extra="-()",
        ) is None
        assert validar_texto_numero(
            "Funda*", 2, 50, "Nombre del producto", caracteres_extra="-()",
        ) == (
            "El campo Nombre del producto solo puede contener letras, números, "
            "acentos, espacios, guiones y paréntesis."
        )

    def test_caracteres_extra_factura(self):
        """Unifica a la antigua validar_codigo_factura."""
        assert validar_texto_numero(
            "FAC-202601-000001", 1, 20, "Factura",
            permitir_espacios=False, caracteres_extra="-",
        ) is None
        assert validar_texto_numero(
            "FAC_001", 1, 20, "Factura",
            permitir_espacios=False, caracteres_extra="-",
        ) == (
            "El campo Factura solo puede contener letras, números (sin "
            "espacios) y guiones."
        )

    def test_caracteres_extra_direccion(self):
        """Unifica a la antigua validar_direccion_proveedor."""
        patron = "-.,#()/"
        assert validar_texto_numero(
            "Av. Principal, Edif. #5, Piso 2", 1, 100, "Dirección",
            obligatorio=False, caracteres_extra=patron,
        ) is None
        assert validar_texto_numero(
            "Calle 'El Sol'", 1, 100, "Dirección",
            obligatorio=False, caracteres_extra=patron,
        ) == (
            "El campo Dirección solo puede contener letras, números, acentos, "
            "espacios, guiones, puntos, comas, numerales (#), paréntesis y barras (/)."
        )
        assert validar_texto_numero(
            "", 1, 100, "Dirección", obligatorio=False, caracteres_extra=patron,
        ) is None


class TestValidarNumero:

    def test_valido(self):
        assert validar_numero("12345678", 6, 8, "Cédula") is None

    def test_vacio(self):
        assert validar_numero("", 1, 10, "Rol") == (
            "El campo Rol no puede estar vacío."
        )

    def test_vacio_opcional(self):
        """Unifica a la antigua validar_celular(obligatorio=False)."""
        assert validar_numero("", 11, 11, "Teléfono", obligatorio=False) is None
        assert validar_numero(None, 11, 11, "Teléfono", obligatorio=False) is None

    def test_telefono_11_digitos(self):
        """Unifica a la antigua validar_celular: misma regla, mismos mensajes."""
        assert validar_numero("04121234567", 11, 11, "Celular") is None

    def test_telefono_corto(self):
        assert validar_numero("0412123456", 11, 11, "Celular") == (
            "El campo Celular debe tener al menos 11 dígitos."
        )

    def test_telefono_largo(self):
        assert validar_numero("041212345678", 11, 11, "Celular") == (
            "El campo Celular no puede tener más de 11 dígitos."
        )

    def test_telefono_no_numerico(self):
        assert validar_numero("0412abc4567", 11, 11, "Celular") == (
            "El campo Celular solo puede contener números."
        )

    def test_corto(self):
        assert validar_numero("123", 6, 8, "Cédula") == (
            "El campo Cédula debe tener al menos 6 dígitos."
        )

    def test_largo(self):
        assert validar_numero("123456789", 6, 8, "Cédula") == (
            "El campo Cédula no puede tener más de 8 dígitos."
        )

    def test_no_numerico(self):
        assert validar_numero("12a456", 6, 8, "Cédula") == (
            "El campo Cédula solo puede contener números."
        )

    def test_negativo_rechazado(self):
        assert validar_numero("-5", 1, 10, "Cantidad") == (
            "El campo Cantidad solo puede contener números."
        )


class TestValidarEmail:

    @pytest.mark.parametrize(
        "correo",
        ["ana.perez@mail.com", "a+b%c@sub.dominio.com", "ana@mail.com.ve"],
        ids=["simple", "con-signos", "multi-etiqueta"],
    )
    def test_validos(self, correo):
        assert validar_email(correo) is None

    def test_vacio_opcional(self):
        assert validar_email("") is None
        assert validar_email(None) is None

    def test_vacio_obligatorio(self):
        assert validar_email("", obligatorio=True) == (
            "El campo correo no puede estar vacío."
        )

    def test_sin_arroba(self):
        assert validar_email("anamail.com") == (
            "El campo correo debe contener el símbolo @."
        )

    def test_dos_arrobas(self):
        assert validar_email("dos@@mail.com") == (
            "El campo correo debe contener exactamente un símbolo @."
        )

    def test_sin_dominio(self):
        assert validar_email("cliente@") == (
            "El campo correo debe tener un dominio después del @."
        )

    def test_dominio_sin_punto(self):
        assert validar_email("ana@mail") == (
            "El campo correo debe tener un punto en el dominio (después del @)."
        )

    def test_doble_punto_en_dominio_es_invalido(self):
        """Bug corregido: antes 'a@b..com' pasaba como válido."""
        assert validar_email("ana@mail..com") == (
            "El campo correo debe ser un correo electrónico válido."
        )

    def test_punto_al_inicio_del_usuario_es_invalido(self):
        assert validar_email(".ana@mail.com") == (
            "El campo correo debe ser un correo electrónico válido."
        )

    def test_punto_al_final_del_usuario_es_invalido(self):
        assert validar_email("ana.@mail.com") == (
            "El campo correo debe ser un correo electrónico válido."
        )

    def test_tld_muy_corto_es_invalido(self):
        assert validar_email("ana@mail.c") == (
            "El campo correo debe ser un correo electrónico válido."
        )

    def test_nombre_campo_personalizado(self):
        assert validar_email("malo", nombre_campo="Correo del proveedor") == (
            "El campo Correo del proveedor debe contener el símbolo @."
        )


class TestValidarContraseña:

    def test_valida(self):
        assert validar_contraseña("clave123") is None

    def test_vacia(self):
        assert validar_contraseña("   ") == (
            "El campo Contraseña no puede estar vacío."
        )

    def test_corta(self):
        assert validar_contraseña("12345") == (
            "El campo Contraseña debe tener al menos 6 caracteres."
        )

    def test_larga(self):
        assert validar_contraseña("P" * 51) == (
            "El campo Contraseña no puede tener más de 50 caracteres."
        )

    def test_espacios_internos(self):
        assert validar_contraseña("abc 123") == (
            "El campo Contraseña no puede contener espacios."
        )

    def test_espacios_en_bordes_rechazados(self):
        """Ya no se hace strip: lo validado es exactamente lo que se guarda."""
        assert validar_contraseña("  clave123  ") == (
            "El campo Contraseña no puede contener espacios."
        )


class TestValidarRif:

    @pytest.mark.parametrize(
        "rif",
        ["J-12345678-9", "J123456789", "E-12345678-9", "V-12345678-9", "v123456789"],
        ids=["j-guiones", "j-sin-guiones", "e", "v", "minusculas"],
    )
    def test_validos(self, rif):
        assert validar_rif(rif) is None

    def test_vacio_opcional(self):
        assert validar_rif("") is None

    def test_vacio_obligatorio(self):
        assert validar_rif("", obligatorio=True) == (
            "El campo RIF no puede estar vacío."
        )

    def test_tipos_limita_letras(self):
        assert validar_rif("V-12345678-9", tipos="JE") == (
            "El campo RIF debe tener formato válido. "
            "Ejemplo: J-12345678-9 o E-12345678-9."
        )

    def test_formato_invalido(self):
        assert validar_rif("J-1234567-9", tipos="JE") == (
            "El campo RIF debe tener formato válido. "
            "Ejemplo: J-12345678-9 o E-12345678-9."
        )

    def test_muy_corto(self):
        assert validar_rif("J-1234") == (
            "El campo RIF debe tener al menos 8 caracteres."
        )

    def test_muy_largo(self):
        assert validar_rif("J" * 16) == (
            "El campo RIF no puede tener más de 15 caracteres."
        )


class TestValidarCelularVenezolano:

    @pytest.mark.parametrize(
        "prefijo", ["0412", "0414", "0416", "0422", "0424", "0426"]
    )
    def test_prefijos_validos(self, prefijo):
        assert validar_celular_venezolano(prefijo + "1234567") is None

    def test_vacio_obligatorio(self):
        assert validar_celular_venezolano("") == (
            "El campo Celular no puede estar vacío."
        )

    def test_vacio_opcional(self):
        assert validar_celular_venezolano("", obligatorio=False) is None

    def test_longitud_incorrecta(self):
        assert validar_celular_venezolano("0412123456") == (
            "El campo Celular debe tener exactamente 11 dígitos."
        )

    def test_prefijo_invalido(self):
        assert validar_celular_venezolano("04151234567") == (
            "El campo Celular debe comenzar con un prefijo válido: "
            "0412, 0414, 0416, 0422, 0424 o 0426."
        )


class TestValidarDecimal:

    def test_valido(self):
        assert validar_decimal("10.50", "Monto", max_decimales=2, min_valor=0) is None

    def test_valido_con_coma(self):
        assert validar_decimal("10,50", "Monto", max_decimales=2, min_valor=0) is None

    def test_valido_formato_mixto(self):
        """Ahora acepta "1.234,56" vía normalizar_numero_decimal."""
        assert validar_decimal("1.234,56", "Monto", max_decimales=2, min_valor=0) is None

    def test_vacio(self):
        assert validar_decimal("", "Monto", max_decimales=2, min_valor=0) == (
            "El campo Monto no puede estar vacío."
        )

    def test_vacio_opcional(self):
        """Unifica a la antigua validar_limite_credito (campo opcional)."""
        assert validar_decimal("", "Límite de crédito", max_decimales=2,
                               min_valor=0, obligatorio=False) is None
        assert validar_decimal(None, "Límite de crédito", max_decimales=2,
                               min_valor=0, obligatorio=False) is None

    def test_cero_es_valido(self):
        """Bug corregido: antes el entero 0 se trataba como vacío."""
        assert validar_decimal(0, "Estado", max_decimales=0, min_valor=None) is None

    def test_no_numerico(self):
        assert validar_decimal("abc", "Monto", max_decimales=2, min_valor=0) == (
            "El campo Monto debe ser un número decimal válido con hasta 2 decimales."
        )

    def test_negativo_con_min_cero(self):
        assert validar_decimal("-5", "Valor pagado", max_decimales=2, min_valor=0) == (
            "El campo Valor pagado debe ser mayor o igual a 0."
        )

    def test_negativo_permitido(self):
        assert validar_decimal("-5.25", "Ajuste", max_decimales=2, min_valor=-100) is None

    def test_maximo_excedido(self):
        assert validar_decimal("10000000000", "Monto", max_decimales=2, min_valor=0,
                               max_valor=9999999999.99) == (
            "El campo Monto debe ser menor o igual a 9999999999.99."
        )

    def test_limite_maximo_exacto(self):
        assert validar_decimal("9999999999.99", "Monto", max_decimales=2, min_valor=0,
                               max_valor=9999999999.99) is None

    def test_demasiados_decimales(self):
        assert validar_decimal("1.234", "Monto", max_decimales=2, min_valor=0) == (
            "El campo Monto no puede tener más de 2 decimales."
        )

    def test_con_decimales_entero(self):
        """Unifica a la antigua validar_numero_entero."""
        assert validar_decimal("2.5", "Estado", max_decimales=0, min_valor=None) == (
            "El campo Estado debe ser un número entero válido."
        )

    def test_no_numerico_entero(self):
        assert validar_decimal("abc", "Estado", max_decimales=0, min_valor=None) == (
            "El campo Estado debe ser un número entero válido."
        )


class TestNormalizarNumeroDecimal:

    @pytest.mark.parametrize(
        "valor, esperado",
        [
            ("1.234,56", "1234.56"),
            ("1,5", "1.5"),
            ("-5", "-5"),
            ("+3", "3"),
            ("1.2.3", "123"),
            ("  2.50  ", "2.50"),
        ],
        ids=["mixto", "coma", "negativo", "positivo", "multi-punto", "bordes"],
    )
    def test_conversion(self, valor, esperado):
        assert str(normalizar_numero_decimal(valor)) == esperado

    @pytest.mark.parametrize("valor", ["", None, "abc", "1,2,3,4"], ids=["vacio", "nulo", "texto", "comas-multiples"])
    def test_invalidos(self, valor):
        assert normalizar_numero_decimal(valor) is None
