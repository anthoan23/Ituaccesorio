from flask import Blueprint, jsonify, request
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.james import James
from app.services.james import IAService

james_blueprint = Blueprint("james", __name__)
ia_service = IAService()

@james_blueprint.route("/james", methods=["POST"])
def consultar_informacion_orden():
    data = request.get_json(silent=True) or request.form
    ID_orden = data.get("ID_orden", "").strip()

    if not ID_orden:
        return jsonify({"success": False, "message": "El ID de la orden es obligatorio."}), 400

    james_model = James(ID_orden=ID_orden)
    resultado = james_model.consultar_informacion_orden()
    personales = james_model.consultar_tecnicos_con_especialidades_y_ordenes()

    if isinstance(resultado, str):
        return jsonify({"success": False, "message": resultado}), 404

    # --- LÓGICA DE IA ---
    decision_ia = ia_service.determinar_tecnico_ideal(resultado, personales)
    
    # Verificar si la IA tuvo error
    if decision_ia.get('error', False):
        # Si falla la IA, usar fallback
        decision_ia = ia_service.determinar_tecnico_ideal_fallback(personales)
    # --------------------

    # RETORNAR SOLO LA DECISIÓN DE LA IA
    return jsonify({
        "success": True,
        "decision": decision_ia
    }), 200