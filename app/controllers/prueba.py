from flask import Blueprint, jsonify, render_template, request
from app.models.prueba import Prueba_bd

prueba_blueprint = Blueprint("prueba", __name__)
@prueba_blueprint.route("/prueba", methods=["GET"])
def pagina_prueba():
    return render_template(
        "prueba.html"
    )


@prueba_blueprint.route("/api/prueba", methods=["GET"])
def obtener_prueba_json():
    modelo = Prueba_bd()
    resultados_bd1 = modelo.prueba_consultar_bd1() or []
    resultados_bd2 = modelo.prueba_consultar_bd2() or []
    return jsonify({
        "success": True,
        "resultados_bd1": resultados_bd1,
        "resultados_bd2": resultados_bd2
    })


@prueba_blueprint.route("/api/prueba/cliente", methods=["POST"])
def agregar_cliente():
    datos = request.get_json(silent=True) or {}
    modelo = Prueba_bd()

    try:
        id_cliente = datos.get("id_cliente")
        if id_cliente in (None, ""):
            return jsonify({"success": False, "error": "El ID del cliente es obligatorio."}), 400

        exitoso = modelo.prueba_agregar_bd1(
            int(id_cliente),
            datos.get("nombre_cliente"),
            datos.get("apellido_cliente"),
            datos.get("celular_cliente"),
            datos.get("correo_cliente"),
            datos.get("direccion_cliente"),
            datos.get("tipo_cliente"),
        )
        return jsonify({"success": exitoso})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@prueba_blueprint.route("/api/prueba/modulo", methods=["POST"])
def agregar_modulo():
    datos = request.get_json(silent=True) or {}
    modelo = Prueba_bd()

    try:
        exitoso = modelo.prueba_agregar_bd2(
            datos.get("nombre_modulo"),
            datos.get("descripcion_modulo"),
        )
        return jsonify({"success": exitoso})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@prueba_blueprint.route("/api/prueba/cliente/<int:id_cliente>", methods=["PUT"])
def editar_cliente(id_cliente):
    datos = request.get_json(silent=True) or {}
    modelo = Prueba_bd()

    try:
        exitoso = modelo.prueba_editar_bd1(
            id_cliente,
            datos.get("nombre_cliente"),
            datos.get("apellido_cliente"),
            datos.get("celular_cliente"),
            datos.get("correo_cliente"),
            datos.get("direccion_cliente"),
            datos.get("tipo_cliente"),
        )
        return jsonify({"success": exitoso})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@prueba_blueprint.route("/api/prueba/cliente/<int:id_cliente>", methods=["DELETE"])
def eliminar_cliente(id_cliente):
    modelo = Prueba_bd()

    try:
        exitoso = modelo.prueba_eliminar_bd1(id_cliente)
        return jsonify({"success": exitoso})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@prueba_blueprint.route("/api/prueba/modulo/<int:id_modulo>", methods=["PUT"])
def editar_modulo(id_modulo):
    datos = request.get_json(silent=True) or {}
    modelo = Prueba_bd()

    try:
        exitoso = modelo.prueba_editar_bd2(
            id_modulo,
            datos.get("nombre_modulo"),
            datos.get("descripcion_modulo"),
        )
        return jsonify({"success": exitoso})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@prueba_blueprint.route("/api/prueba/modulo/<int:id_modulo>", methods=["DELETE"])
def eliminar_modulo(id_modulo):
    modelo = Prueba_bd()

    try:
        exitoso = modelo.prueba_eliminar_bd2(id_modulo)
        return jsonify({"success": exitoso})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400
