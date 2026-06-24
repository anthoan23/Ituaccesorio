import re

def validar_texto(valor, min_len, max_len, nombre_campo):
    if not valor:
        return f"El campo {nombre_campo} no puede estar vacío."
    if len(valor) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    if len(valor) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."
    if not re.match(r'^[A-Za-z\s]+$', valor):
        return f"El campo {nombre_campo} solo puede contener letras y espacios."
    return None

def validar_numero(valor, min_len, max_len, nombre_campo):
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        return f"El campo {nombre_campo} no puede estar vacío."
    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} dígitos."
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} dígitos."
    if not re.match(r'^[0-9]+$', valor_str):
        return f"El campo {nombre_campo} solo puede contener números."
    return None