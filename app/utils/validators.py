"""
Validadores reutilizables de entrada (única fuente de verdad).

Convenciones:
- Cada validador devuelve None si el valor es válido, o un mensaje de error
  en español listo para mostrar al usuario.
- Los campos opcionales aceptan None/"" como válidos (parametro `obligatorio=False`
  o comportamiento documentado en cada función).
- Todos los patrones se comparan con `re.fullmatch` para evitar que un
  salto de línea final ("Juan\\n") pase la validación.
"""

import re
from decimal import Decimal, InvalidOperation


# ==================== NORMALIZACIÓN ====================

def normalizar_numero_decimal(valor):
    """Convierte "1.234,56", "1,56", "-5" y similares en Decimal.

    Devuelve None si el valor no representa un número válido.
    """
    if valor in (None, ""):
        return None

    valor_str = str(valor).strip().replace(" ", "")
    if not valor_str:
        return None

    negativo = valor_str.startswith("-")
    if valor_str.startswith(("+", "-")):
        valor_str = valor_str[1:]

    if "," in valor_str and "." in valor_str:
        if valor_str.rfind(",") > valor_str.rfind("."):
            valor_str = valor_str.replace(".", "").replace(",", ".")
        else:
            valor_str = valor_str.replace(",", "")
    elif "," in valor_str:
        valor_str = valor_str.replace(",", ".")
    elif "." in valor_str and valor_str.count(".") > 1:
        valor_str = valor_str.replace(".", "")

    if not re.fullmatch(r"\d+(\.\d+)?", valor_str):
        return None

    try:
        numero = Decimal(valor_str)
    except InvalidOperation:
        return None

    if negativo:
        numero = -numero

    return numero


# ==================== VALIDADORES BÁSICOS ====================

def validar_texto(valor, min_len, max_len, nombre_campo, permitir_espacios=True):
    """
    Valida texto: solo letras (incluye acentos, ü y ñ). No acepta vacío.

    `permitir_espacios=False` restringe a una sola palabra (sin espacios).
    `min_len` y `max_len` son obligatorios: cada módulo pasa sus límites.
    """
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        return f"El campo {nombre_campo} no puede estar vacío."
    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."
    if permitir_espacios:
        patron = r'[A-Za-zÁÉÍÓÚáéíóúÜÑñ\s]+'
    else:
        patron = r'[A-Za-zÁÉÍÓÚáéíóúÜÑñ]+'
    if not re.fullmatch(patron, valor_str):
        if permitir_espacios:
            return f"El campo {nombre_campo} solo puede contener letras, acentos y espacios."
        return f"El campo {nombre_campo} solo puede contener letras, acentos y ñ (sin espacios)."
    return None


def validar_numero(valor, min_len, max_len, nombre_campo, obligatorio=True):
    """
    Valida un número entero escrito como dígitos (sin signos ni separadores).

    Con `obligatorio=False`, un valor vacío (None/"") es válido.
    """
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        if obligatorio:
            return f"El campo {nombre_campo} no puede estar vacío."
        return None
    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} dígitos."
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} dígitos."
    if not re.fullmatch(r'[0-9]+', valor_str):
        return f"El campo {nombre_campo} solo puede contener números."
    return None


def validar_texto_numero(valor, min_len, max_len, nombre_campo,
                         permitir_espacios=True, caracteres_extra="", obligatorio=True):
    """
    Valida texto alfanumérico: letras (con acentos, ü y ñ), números y,
    opcionalmente, espacios y caracteres extra.

    Args:
        valor: El valor a validar
        min_len: Longitud mínima (obligatorio; 0 no es válido, usa `obligatorio=False`)
        max_len: Longitud máxima (obligatorio)
        nombre_campo: Nombre del campo para el mensaje de error
        permitir_espacios: Si se permiten espacios en blanco
        caracteres_extra: Caracteres adicionales aceptados (p. ej. ".-&"
            para razones sociales, "-()" para nombres de producto,
            "-.,#()/" para direcciones)
        obligatorio: Si False, un valor vacío (None/"") es válido
    """
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        if obligatorio:
            return f"El campo {nombre_campo} no puede estar vacío."
        return None
    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."

    if permitir_espacios:
        clase = rf'[A-Za-zÁÉÍÓÚáéíóúÜÑñ\d\s{re.escape(caracteres_extra)}]'
    else:
        clase = rf'[A-Za-zÁÉÍÓÚáéíóúÜÑñ\d{re.escape(caracteres_extra)}]'

    if not re.fullmatch(clase + '+', valor_str):
        # Mensaje generado a partir de los parámetros de la llamada
        nombres_caracteres = {
            ".": "puntos", "-": "guiones", "_": "guiones bajos",
            "&": "ampersand (&)", "/": "barras (/)", "#": "numerales (#)",
            "(": "paréntesis", ")": "paréntesis", ",": "comas",
            ":": "dos puntos (:)", "+": "signos más (+)",
            "%": "porcentajes (%)", "@": "arrobas (@)",
        }
        if permitir_espacios:
            elementos = ["letras", "números", "acentos", "espacios"]
        else:
            elementos = ["letras", "números (sin espacios)"]
        vistos = []
        for caracter in caracteres_extra:
            nombre = nombres_caracteres.get(caracter, f"'{caracter}'")
            if nombre not in vistos:
                vistos.append(nombre)
        elementos.extend(vistos)
        if len(elementos) == 1:
            union = elementos[0]
        else:
            union = ", ".join(elementos[:-1]) + " y " + elementos[-1]
        return f"El campo {nombre_campo} solo puede contener {union}."

    return None


def validar_email(valor, nombre_campo="correo", max_len=50, obligatorio=False):
    """
    Valida un correo electrónico.

    Por defecto es opcional (None/"" → None); pasa `obligatorio=True` cuando
    el campo es requerido. El dominio exige al menos dos etiquetas y una
    terminación TLD de 2+ letras, sin puntos consecutivos ni puntos mal
    ubicados ("a@b..com" y ".a@b.com" son inválidos).
    """
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        if obligatorio:
            return f"El campo {nombre_campo} no puede estar vacío."
        return None

    if len(valor_str) < 3:
        return f"El campo {nombre_campo} debe tener al menos 3 caracteres."
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."

    # Mensajes específicos para dar mejor retroalimentación al usuario
    if '@' not in valor_str:
        return f"El campo {nombre_campo} debe contener el símbolo @."

    if valor_str.count('@') != 1:
        return f"El campo {nombre_campo} debe contener exactamente un símbolo @."

    usuario, dominio = valor_str.split('@')

    if not usuario:
        return f"El campo {nombre_campo} debe tener un usuario antes del @."

    if not dominio:
        return f"El campo {nombre_campo} debe tener un dominio después del @."

    if '.' not in dominio:
        return f"El campo {nombre_campo} debe tener un punto en el dominio (después del @)."

    # Puntos mal ubicados (inicio/fin de usuario, puntos consecutivos,
    # inicio/fin del dominio)
    if (usuario.startswith('.') or usuario.endswith('.') or '..' in usuario
            or dominio.startswith('.') or dominio.endswith('.') or '..' in dominio):
        return f"El campo {nombre_campo} debe ser un correo electrónico válido."

    if not re.fullmatch(r'[A-Za-z0-9._%+-]+', usuario):
        return f"El campo {nombre_campo} debe ser un correo electrónico válido."

    # Dominio: etiquetas de letras/dígitos/guiones separadas por puntos,
    # con TLD final de 2+ letras
    if not re.fullmatch(r'[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+', dominio) or \
            not re.fullmatch(r'[A-Za-z]{2,}', dominio.rsplit('.', 1)[1]):
        return f"El campo {nombre_campo} debe ser un correo electrónico válido."

    return None


def validar_contraseña(password, min_len=6, max_len=50, nombre_campo="Contraseña"):
    """
    Valida la contraseña sin alterar el valor original (no hace strip):
    así lo que se valida es exactamente lo que se va a guardar/hashear.
    """
    if not password or not str(password).strip():
        return f"El campo {nombre_campo} no puede estar vacío."

    password_str = str(password)

    if len(password_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."

    if len(password_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."

    # Verificar que no tenga espacios (incluye espacios al inicio o al final)
    if re.search(r'\s', password_str):
        return f"El campo {nombre_campo} no puede contener espacios."

    return None


# ==================== IDENTIFICACIÓN VENEZOLANA ====================

def validar_rif(valor, min_len=8, max_len=15, nombre_campo="RIF", tipos="JEV", obligatorio=False):
    """
    Valida un RIF venezolano: letra (J/E/V según `tipos`) + 8 dígitos +
    dígito verificador, con guiones opcionales ("J-12345678-9" o "J123456789").
    No valida el dígito verificador.

    `tipos` limita las letras aceptadas (p. ej. "JE" para clientes jurídicos).
    """
    valor_str = str(valor).strip().upper() if valor is not None else ""
    if not valor_str:
        if obligatorio:
            return f"El campo {nombre_campo} no puede estar vacío."
        return None

    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."

    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."

    letras = "".join(tipos)
    if not re.fullmatch(rf'[{letras}]-?\d{{8}}-?\d', valor_str):
        partes = [f"{t}-12345678-9" for t in tipos]
        if len(partes) > 1:
            ejemplo = ", ".join(partes[:-1]) + " o " + partes[-1]
        else:
            ejemplo = partes[0]
        return f"El campo {nombre_campo} debe tener formato válido. Ejemplo: {ejemplo}."

    return None


def validar_celular_venezolano(valor, nombre_campo="Celular", obligatorio=True):
    """
    Valida un celular móvil venezolano: 11 dígitos con prefijo válido.
    Prefijos permitidos: 0412, 0414, 0416, 0422, 0424 y 0426.
    """
    valor_str = str(valor).strip() if valor is not None else ""

    if not valor_str:
        if obligatorio:
            return f"El campo {nombre_campo} no puede estar vacío."
        return None

    if not re.fullmatch(r'\d+', valor_str):
        return f"El campo {nombre_campo} solo puede contener números."

    if len(valor_str) != 11:
        return f"El campo {nombre_campo} debe tener exactamente 11 dígitos."

    if not re.fullmatch(r'(0412|0414|0416|0422|0424|0426)\d{7}', valor_str):
        return (
            f"El campo {nombre_campo} debe comenzar con un prefijo válido: "
            "0412, 0414, 0416, 0422, 0424 o 0426."
        )

    return None


# ==================== OTROS CAMPOS ====================


def validar_decimal(valor, nombre_campo, max_decimales, min_valor, max_valor=None, obligatorio=True):
    """
    Valida que el valor sea un número decimal válido.

    Acepta coma o punto como separador decimal y formatos mixtos
    ("1.234,56") mediante `normalizar_numero_decimal`. Con `min_valor` menor
    que 0 admite negativos. Con `obligatorio=False`, un valor vacío es válido.

    Args:
        valor: El valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
        max_decimales (int): Número máximo de decimales permitidos (obligatorio)
        min_valor: Valor mínimo permitido (obligatorio; None para no limitar)
        max_valor: Valor máximo permitido (None para no limitar)
        obligatorio: Si False, un valor vacío (None/"") es válido
    """
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        if obligatorio:
            return f"El campo {nombre_campo} no puede estar vacío."
        return None

    numero = normalizar_numero_decimal(valor_str)
    if numero is None:
        if max_decimales == 0:
            return f"El campo {nombre_campo} debe ser un número entero válido."
        return (
            f"El campo {nombre_campo} debe ser un número decimal válido "
            f"con hasta {max_decimales} decimales."
        )

    if min_valor is not None and numero < Decimal(str(min_valor)):
        return f"El campo {nombre_campo} debe ser mayor o igual a {min_valor}."

    if max_valor is not None and numero > Decimal(str(max_valor)):
        return f"El campo {nombre_campo} debe ser menor o igual a {max_valor}."

    if max_decimales is not None and max_decimales >= 0:
        decimales = max(0, -numero.as_tuple().exponent)
        if decimales > max_decimales:
            if max_decimales == 0:
                return f"El campo {nombre_campo} debe ser un número entero válido."
            return f"El campo {nombre_campo} no puede tener más de {max_decimales} decimales."

    return None


def normalizar_celular(valor):
    """Limpia espacios, guiones, paréntesis y '+' de un teléfono.

    La limpieza vivía en controllers (login.py); ahora el modelo normaliza
    ANTES de validar, así cualquier llamador puede pasar el dato crudo.
    """
    return re.sub(r'[\s\-\(\)\+]', '', str(valor or "")).strip()
