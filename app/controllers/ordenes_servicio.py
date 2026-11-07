from flask import Blueprint, jsonify, render_template, request, g
from app.models.empleados import Empleados
from app.models.ordenes_servicio import Orden_servicio as OrdenServicio
from app.models.test import Tests
from app.models.equipo import Equipo
from app.models.clientes import Clientes, Persona_natural, Cliente_juridico
from app.models.productos import Producto
from app.utils.decorators import jwt_required, tiene_permiso
import re
import os
from datetime import datetime

ordenes_servicio_blueprint = Blueprint("ordenes_servicio", __name__)


def _detectar_marca(nombre_modelo: str) -> str:
    n = (nombre_modelo or "").lower()
    if "iphone" in n or "apple" in n:
        return "1"
    if "samsung" in n or "galaxy" in n:
        return "3"
    if "xiaomi" in n or "redmi" in n or "poco" in n:
        return "4"
    if "motorola" in n or "moto" in n:
        return "5"
    if "huawei" in n:
        return "6"
    if "lg" in n:
        return "7"
    return "1"


@ordenes_servicio_blueprint.route("/ordenes-servicio", methods=["POST"])
@jwt_required
def registrar_equipo():
    data = request.get_json(silent=True) or request.form
    id_equipo = data.get("ID_equipo", "").strip()
    color = data.get("Color", "").strip()
    capacidad = data.get("Capacidad", "").strip() or None
    clave = data.get("Clave", "").strip() or None
    patron = data.get("Patron", "").strip()

    if not id_equipo or not color or not patron:
        return jsonify({"success": False, "message": "ID del equipo, color y patron son obligatorios."}), 400

    if not id_equipo.isdigit():
        return jsonify({"success": False, "message": "El ID del equipo debe ser numerico."}), 400
        
    if len(id_equipo) != 15:
        return jsonify({"success": False, "message": "El ID del equipo debe tener 15 digitos."}), 400

    equipo_model = Equipo(
        ID_equipo=id_equipo,
        Color=color,
        Capacidad=capacidad,
        Clave=clave,
        Patron=patron
    )
    mensaje = equipo_model.registrar_equipo()

    if "exitosamente" in mensaje:
        return jsonify({"success": True, "message": mensaje}), 201
    else:
        return jsonify({"success": False, "message": mensaje}), 400


@ordenes_servicio_blueprint.route("/ordenes-servicio", methods=["GET"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'consultar')
def pagina_ordenes_servicio():
    return render_template(
        "ordenes_servicio.html",
        show_navbar=True,
        show_notifications=True,
        active_page="ordenes_servicio",
    )


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/tecnicos", methods=["GET"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'consultar')
def listar_tecnicos():
    modelo = Empleados()
    tecnicos = modelo.listar_tecnicos()
    if isinstance(tecnicos, str):
        return jsonify({"success": False, "error": tecnicos}), 503
    return jsonify({"success": True, "tecnicos": tecnicos or []})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/tecnicos/<int:id_empleado>/ordenes", methods=["GET"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'consultar')
def listar_ordenes_tecnico(id_empleado):
    modelo = OrdenServicio()
    modelo.ID_empleado = id_empleado
    ordenes = modelo.ordenes_asignadas_tecnico() or []
    return jsonify({"success": True, "ordenes": ordenes})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/equipo/<string:id_equipo>", methods=["GET"])
@jwt_required
def verificar_equipo(id_equipo):
    if not id_equipo or not id_equipo.isdigit():
        return jsonify({"success": False, "error": "IMEI invalido."}), 400
    
    if len(id_equipo) != 15:
        return jsonify({"success": False, "error": "El IMEI debe tener 15 digitos."}), 400
    
    modelo = Equipo()
    modelo.ID_equipo = id_equipo
    equipo = modelo.Consultar_equipo_por_id()
    
    if equipo:
        return jsonify({
            "success": True,
            "exists": True,
            "equipo": {
                "id": equipo.get("ID_equipo"),
                "id_modelo": equipo.get("ID_producto"),
                "color": equipo.get("Color"),
                "capacidad": equipo.get("Capacidad"),
                "clave": equipo.get("Clave"),
                "patron": equipo.get("Patron"),
                "nombre_producto": equipo.get("Nombre_producto"),
                "marca": equipo.get("Nombre_marca"),
                "clase": equipo.get("Nombre_Clase"),
            }
        })
    else:
        return jsonify({"success": True, "exists": False})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes", methods=["GET"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'consultar')
def listar_ordenes_servicio():
    estado = (request.args.get("estado") or "").strip()
    
    if ',' in estado:
        estados = [s.strip() for s in estado.split(',') if s.strip()]
    else:
        estados = [s.strip() for s in estado.split(",") if s.strip()] if estado else []
    
    if estados:
        normalizadas = []
        for st in estados:
            st_lower = st.lower()
            if st_lower in ("pendiente", "pendient"): normalizadas.append("Pendiente")
            elif st_lower in ("asignada", "asignado"): normalizadas.append("Asignada")
            elif st_lower in ("en proceso", "en_proceso", "proceso", "enproceso"): normalizadas.append("En proceso")
            elif st_lower in ("reparada", "reparado"): normalizadas.append("Reparada")
            else: normalizadas.append(st)
        
        estados = list(dict.fromkeys(normalizadas))

    modelo = OrdenServicio()
    try:
        ordenes = modelo.listado_ordenes_servicio(estados if estados else None) or []
        return jsonify({"success": True, "ordenes": ordenes})
    except Exception as error:
        print(f"[ERROR] Error al listar ordenes: {error}")
        return jsonify({"success": False, "error": str(error)}), 500


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/modelos", methods=["GET"])
@jwt_required
def listar_modelos():
    try:
        orden_model = OrdenServicio()
        modelos = orden_model.listar_modelos_telefonos()
        
        if not modelos:
            return jsonify({"success": True, "modelos": [], "message": "No se encontraron modelos de telefonos."})
        
        return jsonify({"success": True, "modelos": modelos})
    except Exception as e:
        print(f"[ERROR] Error al listar modelos: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ordenes_servicio_blueprint.route("/api/ordenes-servicio", methods=["POST"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'registrar')
def crear_orden_servicio():
    datos = request.get_json(silent=True) or {}
    
    id_cliente = datos.get("id_cliente")
    imei = (datos.get("id_equipo") or "").strip()
    id_modelo = datos.get("id_modelo")
    modelo_custom = (datos.get("modelo_custom") or "").strip()
    color = (datos.get("color") or "").strip()
    capacidad = (datos.get("capacidad") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    nota = (datos.get("nota") or "").strip() or None
    patron = (datos.get("patron") or "").strip()
    
    nombre_cliente = (datos.get("nombre") or "").strip()
    apellido_cliente = (datos.get("apellido") or "").strip()
    celular_cliente = (datos.get("celular") or "").strip()
    correo_cliente = (datos.get("correo") or "").strip()
    direccion_cliente = (datos.get("direccion") or "").strip()
    tipo_cliente = (datos.get("tipo") or "natural").strip()

    usuario_id = g.user.get("cedula") if isinstance(g.user, dict) else getattr(g.user, "cedula", None)
    
    # 1. Validar/Registrar Cliente (si aplica)
    cliente_model = Clientes(usuario_id=usuario_id)
    cliente_existente = None
    
    id_cliente_buscar = str(id_cliente).strip() if id_cliente else ""
    if tipo_cliente == "juridico" and id_cliente_buscar:
        id_cliente_buscar = id_cliente_buscar.replace("-", "").upper()
    
    if id_cliente_buscar:
        cliente_existente = cliente_model.obtener_datos_cliente_completo(id_cliente_buscar)
    
    if not cliente_existente and tipo_cliente == "juridico" and '-' not in id_cliente_buscar:
        if len(id_cliente_buscar) == 10 and id_cliente_buscar[0] in 'JE':
            id_con_guiones = f"{id_cliente_buscar[0]}-{id_cliente_buscar[1:9]}-{id_cliente_buscar[9]}"
            cliente_existente = cliente_model.obtener_datos_cliente_completo(id_con_guiones)
    
    if not cliente_existente:
        if tipo_cliente == "natural":
            if not nombre_cliente or not apellido_cliente or not celular_cliente:
                return jsonify({"success": False, "error": "Faltan datos del cliente para registrarlo."}), 400
            
            persona = Persona_natural(
                Cedula_cliente=id_cliente_buscar, Nombre_cliente=nombre_cliente, Apellido_cliente=apellido_cliente,
                Telefono_cliente=celular_cliente, Correo_cliente=correo_cliente, Direccion_cliente=direccion_cliente,
                usuario_id=usuario_id
            )
            resultado_cliente = persona.registrar_persona_natural()
            if "exitosamente" not in resultado_cliente.lower():
                return jsonify({"success": False, "error": f"Error al registrar cliente: {resultado_cliente}"}), 400
        else:
            if not celular_cliente:
                return jsonify({"success": False, "error": "Faltan datos de la empresa para registrarla."}), 400
            
            id_cliente_juridico = id_cliente_buscar.replace("-", "").upper()
            
            juridico_model = Cliente_juridico(
                Id_cliente=id_cliente_juridico, Razon_social=nombre_cliente or "Cliente Juridico",
                Rif_cliente=id_cliente_buscar, Direccion_cliente=direccion_cliente,
                Telefono_cliente=celular_cliente, Correo_cliente=correo_cliente, usuario_id=usuario_id
            )
            resultado_cliente = juridico_model.registrar_cliente_juridico()
            if "exitosamente" not in resultado_cliente.lower():
                return jsonify({"success": False, "error": f"Error al registrar cliente juridico: {resultado_cliente}"}), 400

    # 2. Validar/Registrar Equipo (si aplica)
    equipo_model = Equipo()
    equipo_model.ID_equipo = imei
    equipo_existente = equipo_model.Consultar_equipo_por_id()
    
    id_producto_final = id_modelo
    
    if imei and not equipo_existente:
        if modelo_custom and not id_modelo:
            id_marca_detectada = _detectar_marca(modelo_custom)
            producto = Producto(
                nombre=modelo_custom, id_clase="1", id_marca=id_marca_detectada, descripcion=modelo_custom, usuario_id=usuario_id
            )
            try:
                id_producto_final = producto.registrar_producto()
            except Exception as e:
                msg = str(e).lower()
                if "ya existe" in msg or "duplicate" in msg:
                    existente = producto.buscar_por_nombre_clase_marca(modelo_custom, "1", id_marca_detectada)
                    if existente:
                        id_producto_final = existente
                    else:
                        return jsonify({"success": False, "error": f"El producto ya existe pero no se pudo recuperar: {str(e)}"}), 400
                else:
                    return jsonify({"success": False, "error": f"Error al registrar modelo: {str(e)}"}), 400
        
        if id_producto_final:
            equipo_model.ID_producto = str(id_producto_final)
            equipo_model.Color = color
            equipo_model.Capacidad = capacidad
            equipo_model.Patron = patron
            
            resultado_equipo = equipo_model.registrar_equipo()
            if "exitosamente" not in resultado_equipo.lower():
                return jsonify({"success": False, "error": resultado_equipo}), 400

    # 3. Crear Orden (El modelo validará el resto de reglas de negocio)
    id_empleado = usuario_id
    orden_model = OrdenServicio()
    orden_model.ID_empleado = id_empleado
    
    id_cliente_final = id_cliente_buscar
    if tipo_cliente == "juridico":
        id_cliente_final = id_cliente_buscar.replace("-", "").upper()
    
    try:
        nueva_id = orden_model.crear_orden(
            id_cliente=id_cliente_final,
            id_equipo=imei,
            id_modelo=id_producto_final,
            descripcion=descripcion,
            nota=nota,
            modelo_custom=modelo_custom,
            color=color,
            capacidad=capacidad,
            tipo_cliente=tipo_cliente
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    
    if not nueva_id:
        return jsonify({"success": False, "error": "No se pudo crear la orden de servicio."}), 500

    # 4. Registrar tests iniciales
    incluir_tests = datos.get("incluir_tests", False)
    tests_data = datos.get("tests", [])
    
    if incluir_tests and tests_data:
        try:
            tests_filtrados = [t for t in tests_data if t.get('nombre') != 'Observaciones']
            observaciones = next((t.get('resultado') for t in tests_data if t.get('nombre') == 'Observaciones'), "")
            
            if tests_filtrados or observaciones:
                lista_tests = [{"nombre": t.get('nombre', ''), "resultado": t.get('resultado', 'Funciona')} for t in tests_filtrados]
                if observaciones: lista_tests.append({"nombre": "Observaciones", "resultado": observaciones})
                
                test_model = Tests(usuario_id=usuario_id)
                test_model.ID_orden = nueva_id
                test_model.ID_empleado = id_empleado
                test_model.Numero_test = 1
                test_model.lista_tests = lista_tests
                test_model.registrar_revision_test()
        except Exception as e:
            print(f"[ERROR] Error al registrar tests iniciales: {e}")

    return jsonify({
        "success": True,
        "id": nueva_id,
        "equipo": imei,
        "tests_registrados": len(tests_data) if incluir_tests and tests_data else 0,
        "mensaje": "Orden de servicio creada exitosamente" + (" con revision inicial" if incluir_tests and tests_data else "")
    })


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>", methods=["GET"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'consultar')
def detalle_orden_servicio(id_orden):
    ordenes = OrdenServicio()
    tests = Tests()
    detalle = ordenes.detalles_orden(id_orden)
    if not detalle:
        return jsonify({"success": False, "error": "Orden no encontrada."}), 404
    fotos = ordenes.fotos_orden(id_orden) or []
    tests_orden = tests.buscar_test_por_orden(id_orden) or []
    empleados = ordenes.empleados_asignados(id_orden) or []
    return jsonify({
        "success": True, "detalle_orden": detalle, "fotos_orden": fotos, "test_orden": tests_orden, "empleados_orden": empleados,
    })


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>/test/<string:num_test>", methods=["GET"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'consultar')
def detalle_test_orden(id_orden, num_test):
    try:
        tests_model = Tests()
        componentes = tests_model.obtener_test_por_orden_y_numero(id_orden, num_test)
        if not componentes:
            return jsonify({"success": False, "error": "No se encontraron componentes."}), 404
        return jsonify({"success": True, "componentes": componentes, "id_orden": id_orden, "num_test": num_test})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>/asignar", methods=["POST"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'modificar')
def asignar_orden_servicio(id_orden):
    datos = request.get_json(silent=True) or {}
    id_empleado = datos.get("id_empleado")
    
    try:
        id_empleado_val = int(id_empleado)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "ID de empleado invalido."}), 400

    modelo = OrdenServicio()
    detalle = modelo.detalles_orden(id_orden)
    if not detalle:
        return jsonify({"success": False, "error": f"La orden #{id_orden} no existe."}), 404
    
    estado_actual = detalle.get("Estado", "")
    if estado_actual.lower() != "pendiente":
        return jsonify({"success": False, "error": f"La orden esta en estado '{estado_actual}'. Solo se pueden asignar en 'Pendiente'."}), 400

    empleado_model = Empleados(id_empleado=str(id_empleado_val))
    empleado = empleado_model.consultar_empleado()

    if isinstance(empleado, str):
        return jsonify({"success": False, "error": empleado}), 503

    if not empleado:
        return jsonify({"success": False, "error": f"El tecnico con ID {id_empleado_val} no existe."}), 400

    modelo.ID_orden_servicio = id_orden
    modelo.ID_empleado = id_empleado_val
    
    ok = modelo.asignar_orden_empleado()
    if not ok:
        return jsonify({"success": False, "error": "Error desconocido al asignar."}), 400
    
    return jsonify({"success": True, "message": f"Orden #{id_orden} asignada al tecnico {id_empleado_val}"})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>/revision", methods=["POST"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'modificar')
def registrar_test_orden(id_orden):
    datos = request.get_json() or {}
    empleado_id = g.user.get("cedula")
    
    campos = ['ID_em', 'Num_test', 'Botón Power','Botón Vol','Cornetas','Mica','LCD','Tactil','Wifi',
        'Puerto_carga','Cámara posterior','Cámara delantera','Microfono','Flash','Botón Silencio','Auricular',
        'Senal','Sensor_proximidad','Face_id','Bluetooth','Observaciones']

    valores = []
    for campo in campos:
        if campo == 'ID_em':
            valores.append(empleado_id)
            continue
        if campo in datos:
            v = datos.get(campo)
            if v is None or v == '': valores.append(None)
            else:
                if campo == 'Observaciones': valores.append(str(v))
                else:
                    try: valores.append(int(v))
                    except Exception: valores.append(None)
        else:
            valores.append(None)

    test_model = Tests()
    ok = test_model.registrar_test(tuple(valores), id_orden)
    
    return jsonify({"ok": bool(ok)})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>/estado", methods=["PUT"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'modificar')
def actualizar_estado_orden(id_orden):
    datos = request.get_json(silent=True) or {}
    nuevo_estado = datos.get("estado", "").strip()
    if not nuevo_estado:
        return jsonify({"success": False, "error": "El estado es obligatorio."}), 400
    if OrdenServicio().actualizar_estado(id_orden, nuevo_estado):
        return jsonify({"success": True, "message": "Estado actualizado"})
    return jsonify({"success": False, "error": "No se pudo actualizar el estado."}), 400


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'eliminar')
def eliminar_orden_servicio(id_orden):
    if OrdenServicio().eliminar_orden(id_orden):
        return jsonify({"success": True, "message": "Orden eliminada"})
    return jsonify({"success": False, "error": "No se pudo eliminar la orden."}), 400


@ordenes_servicio_blueprint.route("/api/taller/ordenes/<string:id_orden>/fotos", methods=["POST"])
@jwt_required
@tiene_permiso('Ordenes de servicio', 'modificar')
def subir_fotos_orden(id_orden):
    try:
        archivos = request.files.getlist('fotos')
        if not archivos or all(f.filename == '' for f in archivos):
            return jsonify({"ok": False, "message": "No se seleccionaron archivos."}), 400
        
        modelo = OrdenServicio()
        modelo.ID_orden_servicio = id_orden
        
        db = modelo._conexion.conexion1()
        if not db:
            return jsonify({"ok": False, "message": "Error de conexion."}), 500
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MAX(ID_foto_orden_servicio) FROM Fotos_orden_servicio")
            row = cursor.fetchone()
            ultimo_id = row[0] if row else None
            nuevo_num = int(ultimo_id[3:]) + 1 if ultimo_id else 1
        finally:
            cursor.close()
        
        fotos_guardadas = []
        for archivo in archivos:
            if archivo.filename == '': continue
            
            extension = os.path.splitext(archivo.filename)[1]
            nombre_archivo = f"orden_{id_orden}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nuevo_num}{extension}"
            ruta_destino = os.path.join('app', 'static', 'img', 'evidencias', 'orden_servicio')
            os.makedirs(ruta_destino, exist_ok=True)
            
            ruta_completa = os.path.join(ruta_destino, nombre_archivo)
            archivo.save(ruta_completa)
            
            id_foto = f"FOS{str(nuevo_num).zfill(6)}"
            ruta_relativa = f"/static/img/evidencias/orden_servicio/{nombre_archivo}"
            
            modelo.ID_foto_orden_servicio = id_foto
            modelo.Foto_orden_servicio = ruta_relativa
            
            if "exitosamente" in modelo.agregar_foto_orden_servicio():
                fotos_guardadas.append({"id": id_foto, "ruta": ruta_relativa})
                nuevo_num += 1
        
        if fotos_guardadas:
            return jsonify({"ok": True, "fotos": fotos_guardadas, "message": "Fotos subidas"})
        else:
            return jsonify({"ok": False, "message": "No se pudieron guardar."}), 400
        
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500