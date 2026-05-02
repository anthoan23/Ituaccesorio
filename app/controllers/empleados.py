from flask import Blueprint, jsonify, render_template, request, Response

from app.models.empleados import Empleados

empleados_blueprint = Blueprint("empleados", __name__)


@empleados_blueprint.route("/empleados", methods=["GET"])
def pagina_empleados():
    return render_template("empleados.html")


@empleados_blueprint.route("/api/empleados", methods=["GET"])
def api_listar_empleados():
    modelo = Empleados()
    empleados = modelo.listar_empleados() or []
    return jsonify({"success": True, "empleados": empleados})


@empleados_blueprint.route("/api/empleados/recientes", methods=["GET"])
def api_empleados_recientes():
    limite = request.args.get("limit", default=5, type=int)
    limite = max(1, min(limite or 5, 20))

    modelo = Empleados()
    recientes = modelo.obtener_empleados_recientes(limite) or []

    logs = []
    for emp in recientes:
        nombre = f"{emp.get('nombre', '')} {emp.get('apellido', '')}".strip() or "Empleado"
        logs.append({
            "linea": f"{nombre} registrado (Cédula {emp.get('cedula', '')})",
            "meta": f"Rol: {emp.get('rol') or '—'}",
        })

    return jsonify({"success": True, "logs": logs})


@empleados_blueprint.route("/api/empleados", methods=["POST"])
def api_crear_empleado():
    datos = request.get_json(silent=True) or {}
    modelo = Empleados()

    try:
        cedula = datos.get("cedula")
        if cedula in (None, ""):
            return jsonify({"success": False, "error": "La cédula es obligatoria."}), 400

        exitoso = modelo.crear_empleado(
            int(cedula),
            datos.get("nombre"),
            datos.get("apellido"),
            datos.get("celular"),
            datos.get("correo"),
            datos.get("direccion"),
            datos.get("rol"),
        )

        return jsonify({"success": bool(exitoso)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@empleados_blueprint.route("/api/empleados/<int:cedula>", methods=["PUT"])
def api_actualizar_empleado(cedula: int):
    datos = request.get_json(silent=True) or {}
    modelo = Empleados()

    try:
        exitoso = modelo.actualizar_empleado(
            cedula,
            datos.get("nombre"),
            datos.get("apellido"),
            datos.get("celular"),
            datos.get("correo"),
            datos.get("direccion"),
            datos.get("rol"),
        )
        return jsonify({"success": bool(exitoso)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@empleados_blueprint.route("/api/empleados/<int:cedula>", methods=["DELETE"])
def api_eliminar_empleado(cedula: int):
    modelo = Empleados()

    try:
        exitoso = modelo.eliminar_empleado(cedula)
        return jsonify({"success": bool(exitoso)})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 400


@empleados_blueprint.route("/api/empleados/reporte", methods=["GET"])
def api_reporte_empleados():
    modelo = Empleados()
    filas = modelo.listar_empleados() or []

    def csv_escape(value):
        text = "" if value is None else str(value)
        if any(ch in text for ch in [",", "\n", "\r", '"']):
            return '"' + text.replace('"', '""') + '"'
        return text

    encabezado = ["cedula", "nombre", "apellido", "rol", "celular", "correo", "direccion"]
    lines = [",".join(encabezado)]
    for row in filas:
        lines.append(",".join([
            csv_escape(row.get("cedula")),
            csv_escape(row.get("nombre")),
            csv_escape(row.get("apellido")),
            csv_escape(row.get("rol")),
            csv_escape(row.get("celular")),
            csv_escape(row.get("correo")),
            csv_escape(row.get("direccion")),
        ]))

    csv_text = "\n".join(lines) + "\n"
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=empleados.csv"},
    )
