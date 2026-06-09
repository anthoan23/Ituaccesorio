import os
from uuid import uuid4

from flask import Blueprint, jsonify, render_template, request, current_app, g
from werkzeug.utils import secure_filename
from app.utils.decorators import jwt_required, tiene_permiso
from app.models.bitacora import registrar_en_bitacora
from app.models.ordenes_servicio import Orden_servicio
from app.models.test import Tests
from app.models.inventario import Inventario

taller_blueprint = Blueprint("taller", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _is_allowed_image(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@taller_blueprint.route("/taller", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def pagina_taller():
    return render_template(
        "taller.html",
        active_page="taller",
        show_navbar=True,
        show_notifications=True,
    )


@taller_blueprint.route("/api/taller/ordenes", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def obtener_ordenes_taller():
    ordenes = Orden_servicio()
    resultado = ordenes.listar_ordenes_taller()
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/reparaciones-asignadas", methods=["GET"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def obtener_reparaciones_asignadas():
    # Obtener ID del empleado desde g.user
    usuario_id = g.user.get("cedula_personal") if isinstance(g.user, dict) else getattr(g.user, "cedula_personal", None)
    try:
        id_empleado = int(usuario_id) if usuario_id else 32014004
    except (ValueError, TypeError):
        id_empleado = 32014004
    
    ordenes = Orden_servicio(ID_empleado=id_empleado)
    resultado = ordenes.listar_ordenes_tecnico()
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/detalle-orden", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def obtener_detalles_orden():
    ordenes = Orden_servicio(
        ID_orden_e=request.json.get("id_orden")
    )
    test = Tests()
    
    detalle_orden = ordenes.consultar_orden()
    fotos_orden = ordenes.fotos_orden()
    test_orden = test.buscar_test()
    empleados_orden = ordenes.empleados_asignados()

    resultado = {
        "detalle_orden": detalle_orden,
        "fotos_orden": fotos_orden,
        "test_orden": test_orden,
        "empleados_orden": empleados_orden
    }

    return jsonify(resultado)


@taller_blueprint.route("/api/taller/asignar/<int:id_orden>/<int:id_empleado>/estado", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'modificar')
def asignar_estado_orden(id_orden, id_empleado):
    # Obtener ID del empleado desde g.user
    usuario_id = g.user.get("cedula_personal") if isinstance(g.user, dict) else getattr(g.user, "cedula_personal", None)
    try:
        empleado_id = int(usuario_id) if usuario_id else 1004
    except (ValueError, TypeError):
        empleado_id = 1004
    
    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    
    ordenes = Orden_servicio()
    resultado = ordenes.asignar_orden_empleado(id_orden, empleado_id)
    
    if resultado:
        registrar_en_bitacora(
            accion="Asignar orden taller",
            descripcion=f"Se asignó la orden ID: {id_orden} al técnico ID: {empleado_id}",
            usuario_id=usuario_actual_id,
            modulo_nombre="Taller"
        )
    
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/liberar/<int:id_orden>/<int:id_empleado>/estado", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'modificar')
def liberar_estado_orden(id_orden, id_empleado):
    # Obtener ID del empleado desde g.user
    usuario_id = g.user.get("cedula_personal") if isinstance(g.user, dict) else getattr(g.user, "cedula_personal", None)
    try:
        empleado_id = int(usuario_id) if usuario_id else 1004
    except (ValueError, TypeError):
        empleado_id = 1004
    
    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    
    ordenes = Orden_servicio()
    resultado = ordenes.liberar_orden(id_orden, empleado_id)
    
    if resultado:
        registrar_en_bitacora(
            accion="Liberar orden taller",
            descripcion=f"Se liberó la orden ID: {id_orden} por el técnico ID: {empleado_id}",
            usuario_id=usuario_actual_id,
            modulo_nombre="Taller"
        )
    
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/ordenes/<int:id_orden>/fotos", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'modificar')
def registrar_fotos_orden(id_orden):
    files = request.files.getlist("fotos")
    if not files:
        return jsonify({"ok": False, "message": "No se recibieron fotos."}), 400

    base_dir = os.path.join(current_app.static_folder, "img", "evidencias", "taller", str(id_orden))
    os.makedirs(base_dir, exist_ok=True)

    rutas_guardadas = []
    rutas_locales = []
    for file in files:
        if not file or not file.filename:
            continue
        if not _is_allowed_image(file.filename):
            return jsonify({"ok": False, "message": f"Archivo no permitido: {file.filename}"}), 400

        nombre_seguro = secure_filename(file.filename)
        ext = nombre_seguro.rsplit(".", 1)[1].lower() if "." in nombre_seguro else "jpg"
        nombre_final = f"{uuid4().hex}.{ext}"
        ruta_fs = os.path.join(base_dir, nombre_final)
        file.save(ruta_fs)
        rutas_locales.append(ruta_fs)
        rutas_guardadas.append(f"/static/img/evidencias/taller/{id_orden}/{nombre_final}")

    ordenes = Orden_servicio()
    if not ordenes.registrar_fotos_orden(id_orden, rutas_guardadas):
        for ruta_local in rutas_locales:
            if os.path.exists(ruta_local):
                os.remove(ruta_local)
        return jsonify({"ok": False, "message": "No se pudieron registrar las fotos."}), 500

    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    
    registrar_en_bitacora(
        accion="Registrar fotos orden taller",
        descripcion=f"Se registraron {len(rutas_guardadas)} fotos para la orden ID: {id_orden}",
        usuario_id=usuario_actual_id,
        modulo_nombre="Taller"
    )

    return jsonify({"ok": True, "message": "Fotos registradas correctamente.", "fotos": rutas_guardadas})


@taller_blueprint.route("/api/taller/ordenes/<int:id_orden>/test", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'modificar')
def registrar_test_orden(id_orden):
    datos = request.get_json() or {}

    # Obtener ID del empleado desde g.user
    usuario_id = g.user.get("cedula_personal") if isinstance(g.user, dict) else getattr(g.user, "cedula_personal", None)
    try:
        id_empleado = int(usuario_id) if usuario_id else 1004
    except (ValueError, TypeError):
        id_empleado = 1004

    campos = [
        'ID_em', 'Num_test', 'Btn_power','Btn_vol','Cornetas','Mica','LCD','Tactil','Wifi',
        'Puerto_carga','Cam_pos','Cam_del','Microfono','Flash','Btn_sil','Auricular',
        'Senal','Sensor_proximidad','Face_id','Bluetooth','Observaciones'
    ]

    valores = []
    for campo in campos:
        if campo == 'ID_em':
            valores.append(id_empleado)
            continue

        if campo in datos:
            v = datos.get(campo)
            if v is None or v == '':
                valores.append(None)
            else:
                if campo == 'Observaciones':
                    valores.append(str(v))
                else:
                    try:
                        valores.append(int(v))
                    except Exception:
                        valores.append(None)
        else:
            valores.append(None)

    test_model = Tests()
    ok = test_model.registrar_test(tuple(valores), id_orden)
    
    if ok:
        # Obtener usuario actual para bitácora
        usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Registrar test orden taller",
            descripcion=f"Se registró test para la orden ID: {id_orden}",
            usuario_id=usuario_actual_id,
            modulo_nombre="Taller"
        )
    
    return jsonify({"ok": bool(ok)})


@taller_blueprint.route("/api/taller/inventario/<string:N_modelo>", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'consultar')
def obtener_inventarios(N_modelo):
    inventario = Inventario()
    inventario_taller = inventario.listar_inventario()
    inventario_modelo = inventario.listar_inventario_modelo(N_modelo)
    resultado = {
        "inventario_taller": inventario_taller,
        "inventario_modelo": inventario_modelo
    }
    return jsonify(resultado)


@taller_blueprint.route("/api/taller/reparacion/<int:id_orden>", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'modificar')
def registrar_reparacion_orden(id_orden):
    datos = request.get_json() or {}
    id_productos = datos.get('id_productos')
    cantidades = datos.get('cantidades')
    id_empleado = datos.get('id_empleado', 1004)
    reparacion = datos.get('reparacion')

    if not isinstance(id_productos, (list, tuple)) or not isinstance(cantidades, (list, tuple)):
        return jsonify({"ok": False, "message": "id_productos y cantidades deben ser arrays."}), 400
    if len(id_productos) != len(cantidades):
        return jsonify({"ok": False, "message": "Las longitudes de id_productos y cantidades deben coincidir."}), 400

    try:
        ids = [int(x) for x in id_productos]
        qts = [int(x) for x in cantidades]
        id_empleado = int(id_empleado)
    except Exception:
        return jsonify({"ok": False, "message": "Valores inválidos en id_productos o cantidades."}), 400

    if reparacion is None:
        reparacion_val = None
    else:
        reparacion_val = str(reparacion)

    ordenes = Orden_servicio()
    ok = ordenes.Orden_reparada(id_orden, ids, qts, id_empleado, reparacion_val)
    
    if ok:
        # Obtener usuario actual para bitácora
        usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Registrar reparación orden",
            descripcion=f"Se registró reparación para la orden ID: {id_orden} - Productos usados: {len(ids)}",
            usuario_id=usuario_actual_id,
            modulo_nombre="Taller"
        )
        return jsonify({"ok": True})
    
    return jsonify({"ok": False, "message": "No se pudo registrar la reparación."}), 500


@taller_blueprint.route("/api/taller/fotos/<int:id_evidencia>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Taller', 'modificar')
def eliminar_foto_orden(id_evidencia):
    ordenes = Orden_servicio()
    
    if not ordenes.eliminar_foto_orden(id_evidencia):
        return jsonify({"ok": False, "message": "No se pudo eliminar la imagen."}), 404

    # Obtener usuario actual para bitácora
    usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
    
    registrar_en_bitacora(
        accion="Eliminar foto orden taller",
        descripcion=f"Se eliminó la foto ID: {id_evidencia}",
        usuario_id=usuario_actual_id,
        modulo_nombre="Taller"
    )

    return jsonify({"ok": True, "message": "Imagen eliminada correctamente."})


@taller_blueprint.route("/api/taller/ordenes/<int:id_orden>/finalizar", methods=["POST"])
@jwt_required
@tiene_permiso('Taller', 'modificar')
def finalizar_orden_taller(id_orden):
    """Finaliza una orden de taller (marca como completada)"""
    ordenes = Orden_servicio()
    resultado = ordenes.finalizar_orden(id_orden)
    
    if resultado:
        # Obtener usuario actual para bitácora
        usuario_actual_id = g.user.get("id") if isinstance(g.user, dict) else getattr(g.user, "id", "SYSTEM")
        
        registrar_en_bitacora(
            accion="Finalizar orden taller",
            descripcion=f"Se finalizó la orden de taller ID: {id_orden}",
            usuario_id=usuario_actual_id,
            modulo_nombre="Taller"
        )
        return jsonify({"ok": True, "message": "Orden finalizada correctamente."})
    
    return jsonify({"ok": False, "message": "No se pudo finalizar la orden."}), 500