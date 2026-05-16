from flask import Blueprint, jsonify, render_template, request, redirect, url_for, make_response
from app.models.usuarios import Usuarios
from app.utils.jwt_utils import create_token

login_blueprint = Blueprint("login", __name__)

@login_blueprint.route("/login", methods=["GET"])
def pagina_login():
    # Servir la vista de login para teléfono en la ruta /login
    return render_template(
        "login_phone.html"
    )

@login_blueprint.route("/api/login", methods=["POST"])
def validar_login():
    datos = request.get_json(silent=True) or {}
    modelo = Usuarios()

    try:
        nombre = datos.get("nombre")
        password = datos.get("password")

        if not nombre or not password:
            return jsonify({"success": False, "error": "El nombre y la contraseña son obligatorios."}), 400

        resultados = modelo.validar(nombre, password)
        if resultados:
            usuario = resultados[0]
            # Create JWT payload
            payload = {
                "usuario_id": usuario.get("id"),
                "usuario_nombre": usuario.get("nombre"),
                "cedula_personal": usuario.get("cedula_personal"),
                "rol_id": usuario.get("rol_id"),
                "nombre_rol": usuario.get("nombre_rol"),
            }
            token = create_token(payload)
            resp = make_response(jsonify({"success": True, "message": "Inicio de sesión exitoso."}))
            resp.set_cookie('access_token', token, httponly=True, samesite='Lax', secure=False, path='/')
            return resp
        else:
            return jsonify({"success": False, "error": "Credenciales inválidas."}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400   



@login_blueprint.route('/logout', methods=['GET'])
def logout():
    resp = redirect(url_for('login.pagina_login'))
    resp.set_cookie('access_token', '', expires=0, path='/')
    return resp


