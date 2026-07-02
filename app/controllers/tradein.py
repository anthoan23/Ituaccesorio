from flask import Blueprint, jsonify, render_template, request, g
from app.models.tradein import TradeIn

tradein_blueprint = Blueprint("tradein", __name__)


# ==================== FUNCIONES AUXILIARES ====================

def _obtener_usuario_actual():
    """Obtiene el ID del usuario actual (si está logueado) o None si no"""
    user = getattr(g, 'user', None)
    if not user:
        return None
    if isinstance(user, dict):
        return str(user.get("usuario_id") or user.get("id") or user.get("cedula"))
    return str(getattr(user, "usuario_id", None) or getattr(user, "id", None) or getattr(user, "cedula", None))


# ==================== VALIDACIONES ====================

def _validar_cotizacion_data(data):
    """
    Función auxiliar para validar los datos de cotización de trade-in.
    
    Args:
        data (dict): Datos del formulario de cotización
    
    Returns:
        tuple: (error_mensaje, error_codigo) o (None, None) si es válido
    """
    # Validar equipo
    id_producto = data.get("id_producto")
    if not id_producto:
        return "Debes seleccionar un equipo para cotizar.", 400
    
    # Validar que el ID del producto sea válido (solo números)
    try:
        id_producto = str(id_producto).strip()
        if not id_producto.isdigit():
            return "El ID del equipo debe ser un número válido.", 400
    except (ValueError, TypeError):
        return "El ID del equipo debe ser un número válido.", 400
    
    # Validar liberación del equipo
    liberado = str(data.get("liberado", "")).strip().lower()
    valores_liberado = ("si", "s", "sí", "1", "true", "on", "yes")
    if liberado not in valores_liberado:
        return "Lo sentimos, el equipo debe estar liberado para calificar.", 400
    
    # Validar fallas (si se proporcionan)
    fallas = data.get("fallas") or []
    if not isinstance(fallas, list):
        return "El formato de fallas no es válido.", 400
    
    # Validar cada falla
    fallas_validas = [f["clave"] for f in TradeIn.FALLAS_COTIZACION]
    for falla in fallas:
        falla_str = str(falla).strip()
        if not falla_str:
            return "No se permiten fallas vacías.", 400
        if not falla_str.isdigit():
            return f"El formato de la falla '{falla_str}' no es válido.", 400
        # Si el modelo valida existencia, esto se verifica allá
        if falla_str not in fallas_validas:
            # Si no está en la lista de fallas válidas, permitimos que el modelo lo maneje
            # pero podríamos pasar una advertencia
            pass
    
    return None, 200


# ==================== PÁGINAS ====================

@tradein_blueprint.route("/trade-in", methods=["GET"])
def pagina_tradein():
    """Página principal de Trade-in - acceso público"""
    modelo = TradeIn()
    equipos = modelo.consultar_equipos() or []
    
    return render_template(
        "tradein.html",
        show_navbar=True,
        show_notifications=True,
        active_page="tradein",
        equipos=equipos,
        fallas=TradeIn.FALLAS_COTIZACION,
    )


# ==================== APIS PÚBLICAS ====================

@tradein_blueprint.route("/api/trade-in", methods=["GET"])
def obtener_tradein_json():
    """API para obtener datos de Trade-in - acceso público"""
    try:
        modelo = TradeIn()
        return jsonify({
            "success": True,
            "equipos": modelo.consultar_equipos() or [],
            "fallas": TradeIn.FALLAS_COTIZACION,
        })
    except Exception as e:
        print(f"Error en obtener_tradein_json: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_blueprint.route("/api/trade-in/cotizar", methods=["POST"])
def cotizar_tradein():
    """API para calcular cotización - acceso público"""
    try:
        datos = request.get_json(silent=True) or {}
        
        # Validar datos de cotización
        error, status = _validar_cotizacion_data(datos)
        if error:
            return jsonify({"success": False, "error": error}), status
        
        # Obtener usuario actual (puede ser None para usuarios no autenticados)
        usuario_id = _obtener_usuario_actual()
        
        id_producto = datos.get("id_producto")
        fallas = datos.get("fallas") or []
        
        # Crear instancia del modelo con el usuario_id
        modelo = TradeIn(usuario_id=usuario_id)
        
        resultado = modelo.calcular_cotizacion(id_producto, fallas)
        estado = 200 if resultado.get("success") else 400
        return jsonify(resultado), estado
        
    except Exception as e:
        print(f"Error en cotizar_tradein: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@tradein_blueprint.route("/api/trade-in/equipos", methods=["GET"])
def obtener_equipos():
    """API para obtener solo la lista de equipos"""
    try:
        modelo = TradeIn()
        return jsonify({
            "success": True,
            "equipos": modelo.consultar_equipos() or []
        })
    except Exception as e:
        print(f"Error en obtener_equipos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500