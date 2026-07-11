import re

def validar_texto(valor, min_len, max_len, nombre_campo):
    if not valor:
        return f"El campo {nombre_campo} no puede estar vacío."
    if len(valor) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    if len(valor) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."
    if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', valor):
        return f"El campo {nombre_campo} solo puede contener letras, acentos y espacios."
        
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

def validar_texto_numero(valor, min_len, max_len, nombre_campo):
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        return f"El campo {nombre_campo} no puede estar vacío."
    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."
    if not re.match(r'^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s]+$', valor_str):
        return f"El campo {nombre_campo} solo puede contener letras, números, acentos y espacios."
        
    return None

def validar_email(valor):
    valor_str = str(valor).strip() if valor is not None else ""
    if not valor_str:
        return "El campo correo no puede estar vacío."
    if len(valor_str) < 3:
        return "El campo correo debe tener al menos 3 caracteres."
    if len(valor_str) > 60:
        return "El campo correo no puede tener más de 60 caracteres."
    
    # Validación específica para @
    if '@' not in valor_str:
        return "El campo correo debe contener el símbolo @."
    
    # Validar que tenga exactamente un @
    if valor_str.count('@') != 1:
        return "El campo correo debe contener exactamente un símbolo @."
    
    # Validar que tenga un punto después del @
    partes = valor_str.split('@')
    usuario = partes[0]
    dominio = partes[1]
    
    if not usuario:
        return "El campo correo debe tener un usuario antes del @."
    
    if not dominio:
        return "El campo correo debe tener un dominio después del @."
    
    if '.' not in dominio:
        return "El campo correo debe tener un punto en el dominio (después del @)."
    
    # Verificar que el punto no esté al inicio del dominio
    if dominio.startswith('.'):
        return "El campo correo no puede tener un punto al inicio del dominio."
    
    # Verificar que el punto no esté al final del dominio
    if dominio.endswith('.'):
        return "El campo correo no puede tener un punto al final del dominio."
    
    # Validación completa con expresión regular
    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', valor_str):
        return "El campo correo debe ser un correo electrónico válido."
        
    return None


# ==================== NUEVAS FUNCIONES REUTILIZABLES ====================

def validar_solo_letras(valor, min_len=1, max_len=255, nombre_campo="Campo", permitir_espacios=True):
    """
    Valida que el valor contenga solo letras (incluyendo acentos y ñ),
    con posibilidad de permitir o no espacios.
    
    Args:
        valor (str): El valor a validar
        min_len (int): Longitud mínima
        max_len (int): Longitud máxima
        nombre_campo (str): Nombre del campo para el mensaje de error
        permitir_espacios (bool): Si se permiten espacios en blanco
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    if not valor:
        return f"El campo {nombre_campo} no puede estar vacío."
    
    valor_str = str(valor).strip()
    
    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."
    
    # Patrón para letras con acentos y ñ
    if permitir_espacios:
        patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$'
    else:
        patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ]+$'
    
    if not re.match(patron, valor_str):
        if permitir_espacios:
            return f"El campo {nombre_campo} solo puede contener letras, espacios, acentos y ñ."
        else:
            return f"El campo {nombre_campo} solo puede contener letras, acentos y ñ (sin espacios)."
    
    return None


def validar_solo_letras_numeros(valor, min_len=1, max_len=255, nombre_campo="Campo", permitir_espacios=True):
    """
    Valida que el valor contenga solo letras y números,
    con posibilidad de permitir o no espacios.
    
    Args:
        valor (str): El valor a validar
        min_len (int): Longitud mínima
        max_len (int): Longitud máxima
        nombre_campo (str): Nombre del campo para el mensaje de error
        permitir_espacios (bool): Si se permiten espacios en blanco
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    if not valor:
        return f"El campo {nombre_campo} no puede estar vacío."
    
    valor_str = str(valor).strip()
    
    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."
    
    # Patrón para letras (con acentos) y números
    if permitir_espacios:
        patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\d\s]+$'
    else:
        patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\d]+$'
    
    if not re.match(patron, valor_str):
        if permitir_espacios:
            return f"El campo {nombre_campo} solo puede contener letras, números y espacios."
        else:
            return f"El campo {nombre_campo} solo puede contener letras y números (sin espacios)."
    
    return None

def validar_decimal(valor, nombre_campo="Valor", max_decimales=2, min_valor=0, max_valor=None):
    """
    Valida que el valor sea un número decimal válido.
    
    Args:
        valor (str): El valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
        max_decimales (int): Número máximo de decimales permitidos
        min_valor (float): Valor mínimo permitido (por defecto 0)
        max_valor (float): Valor máximo permitido (opcional)
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    if not valor or not str(valor).strip():
        return f"El campo {nombre_campo} no puede estar vacío."
    
    valor_str = str(valor).strip()
    
    # Permitir formato con coma o punto decimal
    valor_str = valor_str.replace(',', '.')
    
    # Validar formato: números opcionalmente con un punto decimal
    if not re.match(r'^\d+(\.\d{1,' + str(max_decimales) + r'})?$', valor_str):
        if max_decimales == 0:
            return f"El campo {nombre_campo} debe ser un número entero válido."
        else:
            return f"El campo {nombre_campo} debe ser un número decimal válido con hasta {max_decimales} decimales."
    
    try:
        valor_float = float(valor_str)
        
        # Validar valor mínimo
        if min_valor is not None and valor_float < min_valor:
            return f"El campo {nombre_campo} debe ser mayor o igual a {min_valor}."
        
        # Validar valor máximo
        if max_valor is not None and valor_float > max_valor:
            return f"El campo {nombre_campo} debe ser menor o igual a {max_valor}."
        
        # Validar que no tenga más decimales de los permitidos
        if max_decimales >= 0:
            decimales = len(valor_str.split('.')[1]) if '.' in valor_str else 0
            if decimales > max_decimales:
                return f"El campo {nombre_campo} no puede tener más de {max_decimales} decimales."
        
    except ValueError:
        return f"El campo {nombre_campo} debe ser un número válido."
    
    return None


def validar_decimal_positivo(valor, nombre_campo="Valor", max_decimales=2):
    """
    Valida que el valor sea un número decimal positivo.
    
    Args:
        valor (str): El valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
        max_decimales (int): Número máximo de decimales permitidos
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    return validar_decimal(valor, nombre_campo, max_decimales, min_valor=0)


def validar_numero_entero(valor, nombre_campo="Valor", min_valor=0, max_valor=None):
    """
    Valida que el valor sea un número entero válido.
    
    Args:
        valor (str): El valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
        min_valor (int): Valor mínimo permitido
        max_valor (int): Valor máximo permitido (opcional)
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    # Usar validar_decimal con 0 decimales
    error = validar_decimal(valor, nombre_campo, max_decimales=0, min_valor=min_valor, max_valor=max_valor)
    if error:
        return error
    

    
    return None

def validar_contraseña(password, min_len=6, max_len=50, nombre_campo="Contraseña"):
    """
    Valida que la contraseña cumpla con los requisitos mínimos.
    
    Args:
        password (str): La contraseña a validar
        min_len (int): Longitud mínima
        max_len (int): Longitud máxima
        nombre_campo (str): Nombre del campo para el mensaje de error
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    if not password or not password.strip():
        return f"El campo {nombre_campo} no puede estar vacío."
    
    password_str = str(password).strip()
    
    if len(password_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    
    if len(password_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."
    
    # Verificar que no tenga espacios
    if re.search(r'\s', password_str):
        return f"El campo {nombre_campo} no puede contener espacios."
    
    return None


def validar_cedula_venezolana(cedula, nombre_campo="Cédula"):
    """
    Valida que la cédula sea un número de 6 a 8 dígitos.
    (Formato común en Venezuela)
    
    Args:
        cedula (str): La cédula a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    if not cedula:
        return f"El campo {nombre_campo} no puede estar vacío."
    
    cedula_str = str(cedula).strip()
    
    # Eliminar espacios y guiones
    cedula_limpia = re.sub(r'[\s\-]', '', cedula_str)
    
    if not re.match(r'^\d+$', cedula_limpia):
        return f"El campo {nombre_campo} solo puede contener números."
    
    if len(cedula_limpia) < 6 or len(cedula_limpia) > 8:
        return f"El campo {nombre_campo} debe tener entre 6 y 8 dígitos."
    
    return None


def validar_sin_espacios(valor, nombre_campo="Campo"):
    """
    Valida que el valor no contenga espacios.
    
    Args:
        valor (str): El valor a validar
        nombre_campo (str): Nombre del campo para el mensaje de error
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    if not valor:
        return f"El campo {nombre_campo} no puede estar vacío."
    
    valor_str = str(valor).strip()
    
    if not valor_str:
        return f"El campo {nombre_campo} no puede estar vacío."
    
    if re.search(r'\s', valor_str):
        return f"El campo {nombre_campo} no puede contener espacios."
    
    return None


def validar_sin_caracteres_especiales(valor, min_len=0, max_len=255, nombre_campo="Campo", permitir_espacios=True):
    """
    Valida que el valor no contenga caracteres especiales (solo letras, números y espacios).
    
    Args:
        valor (str): El valor a validar
        min_len (int): Longitud mínima
        max_len (int): Longitud máxima
        nombre_campo (str): Nombre del campo para el mensaje de error
        permitir_espacios (bool): Si se permiten espacios en blanco
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    if not valor and min_len > 0:
        return f"El campo {nombre_campo} no puede estar vacío."
    
    if valor is None:
        return None  # No hay valor, pero no es requerido (si min_len=0)
    
    valor_str = str(valor).strip()
    
    # Si no hay valor y min_len=0, es válido
    if not valor_str and min_len == 0:
        return None
    
    if len(valor_str) < min_len:
        return f"El campo {nombre_campo} debe tener al menos {min_len} caracteres."
    
    if len(valor_str) > max_len:
        return f"El campo {nombre_campo} no puede tener más de {max_len} caracteres."
    
    # Verificar que no tenga caracteres especiales (solo letras, números y espacios)
    if permitir_espacios:
        patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\d\s]+$'
    else:
        patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\d]+$'
    
    if not re.match(patron, valor_str):
        return f"El campo {nombre_campo} no puede contener caracteres especiales."
    
    return None


def validar_campo_comun(valor, tipo, nombre_campo="Campo", **kwargs):
    """
    Validador genérico para diferentes tipos de campos.
    
    Args:
        valor: El valor a validar
        tipo (str): Tipo de validación ('texto', 'numero', 'email', 'telefono', 'cedula', 'password', 'solo_letras', 'solo_letras_numeros', 'sin_espacios', 'sin_caracteres_especiales')
        nombre_campo (str): Nombre del campo para mensajes de error
        **kwargs: Argumentos adicionales específicos del tipo
    
    Returns:
        str or None: Mensaje de error o None si es válido
    """
    if valor is None:
        valor = ""
    
    if tipo == 'texto':
        return validar_texto(
            valor,
            kwargs.get('min_len', 1),
            kwargs.get('max_len', 255),
            nombre_campo
        )
    
    elif tipo == 'numero':
        return validar_numero(
            valor,
            kwargs.get('min_len', 1),
            kwargs.get('max_len', 20),
            nombre_campo
        )
    
    elif tipo == 'solo_letras':
        return validar_solo_letras(
            valor,
            kwargs.get('min_len', 1),
            kwargs.get('max_len', 255),
            nombre_campo,
            kwargs.get('permitir_espacios', True)
        )
    
    elif tipo == 'solo_letras_numeros':
        return validar_solo_letras_numeros(
            valor,
            kwargs.get('min_len', 1),
            kwargs.get('max_len', 255),
            nombre_campo,
            kwargs.get('permitir_espacios', True)
        )
    
    elif tipo == 'password':
        return validar_contraseña(
            valor,
            kwargs.get('min_len', 6),
            kwargs.get('max_len', 50),
            nombre_campo
        )
    
    elif tipo == 'cedula':
        return validar_cedula_venezolana(valor, nombre_campo)
    
    elif tipo == 'sin_espacios':
        return validar_sin_espacios(valor, nombre_campo)
    
    elif tipo == 'sin_caracteres_especiales':
        return validar_sin_caracteres_especiales(
            valor,
            kwargs.get('min_len', 0),
            kwargs.get('max_len', 255),
            nombre_campo,
            kwargs.get('permitir_espacios', True)
        )
    
    else:
        return f"Tipo de validación '{tipo}' no soportado."