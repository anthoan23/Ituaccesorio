from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for
from app.models.usuarios import Usuarios

login_blueprint = Blueprint("login", __name__)
@login_blueprint.route("/login", methods=["GET"])
def pagina_login():
    return render_template(
        "login.html"
    )

@login_blueprint.route("/api/consultar/login", methods=["GET"])
def consultar_usurios():
    modelo = Usuarios()
    resultados = modelo.consultar_usuario()
    return jsonify({"success": True, "data": resultados})

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
            session.clear()
            session["autenticado"] = True
            session["usuario_id"] = usuario.get("id")
            session["usuario_nombre"] = usuario.get("nombre")
            session["cedula_personal"] = usuario.get("cedula_personal")
            session["rol_id"] = usuario.get("rol_id")
            session["nombre_rol"] = usuario.get("nombre_rol")
            return jsonify({"success": True, "message": "Inicio de sesión exitoso."})
        else:
            return jsonify({"success": False, "error": "Credenciales inválidas."}), 401
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400   



@login_blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('home.home'))


