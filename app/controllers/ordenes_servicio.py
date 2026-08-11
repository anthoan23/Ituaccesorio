from flask import Blueprint, jsonify, render_template, request, g
from app.models.empleados import Empleados
from app.models.ordenes_servicio import Orden_servicio as OrdenServicio
from app.models.test import Tests
from app.models.equipo import Equipo
from app.models.clientes import Clientes, Persona_natural
from app.models.productos import Producto
from app.utils.decorators import jwt_required, tiene_permiso
import re
import os
from datetime import datetime

ordenes_servicio_blueprint = Blueprint("ordenes_servicio", __name__)


def _validar_email(email):
    """Valida un correo electrónico"""
    patron = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(patron, email) is not None


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
        return jsonify({"success": False, "message": "ID del equipo, color y patrón son obligatorios."}), 400

    # CORRECCIÓN: No convertir id_equipo ni patron a int, se envían como strings al modelo
    if not id_equipo.isdigit():
        return jsonify({"success": False, "message": "El ID del equipo debe ser numérico."}), 400
        
    if len(id_equipo) != 15:
        return jsonify({"success": False, "message": "El ID del equipo debe tener 15 dígitos."}), 400

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


def _obtener_nombre_cliente(cliente_id):
    """Obtiene el nombre de un cliente por su ID"""
    try:
        orden = OrdenServicio()
        ordenes = orden.listado_ordenes_servicio()
        for o in ordenes:
            if o.get("ID_cliente") == cliente_id:
                return o.get("Nombre_cliente", str(cliente_id))
    except Exception:
        pass
    return str(cliente_id)


@ordenes_servicio_blueprint.route("/ordenes-servicio", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def pagina_ordenes_servicio():
    return render_template(
        "ordenes_servicio.html",
        show_navbar=True,
        show_notifications=True,
        active_page="ordenes_servicio",
    )


# ============================================
# RUTAS API - ORDEN DE LAS RUTAS IMPORTANTE
# ============================================

# Primero las rutas más específicas
@ordenes_servicio_blueprint.route("/api/ordenes-servicio/tecnicos", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def listar_tecnicos():
    modelo = Empleados()
    tecnicos = modelo.listar_tecnicos() or []
    return jsonify({"success": True, "tecnicos": tecnicos})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/tecnicos/<int:id_empleado>/ordenes", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def listar_ordenes_tecnico(id_empleado):
    modelo = OrdenServicio()
    modelo.ID_empleado = id_empleado
    ordenes = modelo.ordenes_asignadas_tecnico() or []
    return jsonify({"success": True, "ordenes": ordenes})


@ordenes_servicio_blueprint.route("/api/ordenes-servicio/equipo/<string:id_equipo>", methods=["GET"])
@jwt_required
def verificar_equipo(id_equipo):
    """Verifica si un equipo existe por su ID (IMEI)"""
    if not id_equipo or not id_equipo.isdigit():
        return jsonify({"success": False, "error": "IMEI inválido."}), 400
    
    if len(id_equipo) != 15:
        return jsonify({"success": False, "error": "El IMEI debe tener 15 dígitos."}), 400
    
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
@tiene_permiso('Órdenes de servicio', 'consultar')
def listar_ordenes_servicio():
    estado = (request.args.get("estado") or "").strip()
    
    # Si el estado contiene comas, dividirlo en múltiples estados
    if ',' in estado:
        estados = [s.strip() for s in estado.split(',') if s.strip()]
    else:
        estados = [s.strip() for s in estado.split(",") if s.strip()] if estado else []
    
    print(f"[DEBUG] Estados recibidos: {estados}")
    
    if estados:
        normalizadas = []
        for st in estados:
            st_lower = st.lower()
            if st_lower in ("pendiente", "pendient"):
                normalizadas.append("Pendiente")
            elif st_lower in ("asignada", "asignado"):
                normalizadas.append("Asignada")
            elif st_lower in ("revisado", "revisada", "en revision", "en revisión"):
                normalizadas.append("Revisado")
            elif st_lower in ("reparada", "reparado"):
                normalizadas.append("Reparada")
            else:
                # Si no coincide con ningún estado conocido, guardar el original
                normalizadas.append(st)
        
        # Eliminar duplicados manteniendo el orden
        estados = list(dict.fromkeys(normalizadas))
        print(f"[DEBUG] Estados normalizados: {estados}")

    modelo = OrdenServicio()
    try:
        ordenes = modelo.listado_ordenes_servicio(estados if estados else None) or []
        print(f"[DEBUG] Órdenes encontradas: {len(ordenes)}")
        return jsonify({"success": True, "ordenes": ordenes})
    except Exception as error:
        print(f"[ERROR] Error al listar órdenes: {error}")
        return jsonify({"success": False, "error": str(error)}), 500


# Ruta para crear una nueva orden (POST)
@ordenes_servicio_blueprint.route("/api/ordenes-servicio", methods=["POST"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'registrar')
def crear_orden_servicio():
    datos = request.get_json(silent=True) or {}
    
    print("=" * 60)
    print("CREANDO ORDEN DE SERVICIO")
    print("=" * 60)
    print(f"Datos recibidos: {datos}")
    
    # =============================================
    # 1. OBTENER DATOS DEL REQUEST
    # =============================================
    id_cliente = datos.get("id_cliente")
    imei = (datos.get("id_equipo") or "").strip()
    id_modelo = datos.get("id_modelo")
    modelo_custom = (datos.get("modelo_custom") or "").strip()
    color = (datos.get("color") or "").strip()
    capacidad = (datos.get("capacidad") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    nota = (datos.get("nota") or "").strip() or None
    patron = (datos.get("patron") or "").strip() # CORRECCIÓN: Obtenemos el patrón
    
    # Datos del cliente (por si hay que registrarlo)
    nombre_cliente = (datos.get("nombre") or "").strip()
    apellido_cliente = (datos.get("apellido") or "").strip()
    celular_cliente = (datos.get("celular") or "").strip()
    correo_cliente = (datos.get("correo") or "").strip()
    direccion_cliente = (datos.get("direccion") or "").strip()

    print(f"[DEBUG] id_cliente: {id_cliente}")
    print(f"[DEBUG] imei: {imei}")
    print(f"[DEBUG] id_modelo: {id_modelo}")
    print(f"[DEBUG] modelo_custom: {modelo_custom}")

    # =============================================
    # 2. VALIDACIONES INICIALES
    # =============================================
    if not id_cliente:
        print("ERROR: ID cliente vacío")
        return jsonify({"success": False, "error": "El ID del cliente es obligatorio."}), 400
    
    if not descripcion:
        print("ERROR: Descripción vacía")
        return jsonify({"success": False, "error": "La descripción del problema es obligatoria."}), 400
    
    if not imei:
        print("ERROR: IMEI vacío")
        return jsonify({"success": False, "error": "El IMEI del equipo es obligatorio."}), 400
    
    if not color:
        print("ERROR: Color vacío")
        return jsonify({"success": False, "error": "El color del equipo es obligatorio."}), 400
    
    if not capacidad:
        print("ERROR: Capacidad vacía")
        return jsonify({"success": False, "error": "La capacidad del equipo es obligatoria."}), 400
    
    if not id_modelo and not modelo_custom:
        print("ERROR: No hay modelo seleccionado ni personalizado")
        return jsonify({"success": False, "error": "Debes seleccionar un modelo o escribir uno personalizado."}), 400

    try:
        id_cliente_val = int(id_cliente)
        print(f"id_cliente_val convertido: {id_cliente_val}")
    except (ValueError, TypeError):
        print(f"ERROR: ID cliente no es numérico: {id_cliente}")
        return jsonify({"success": False, "error": "El ID del cliente debe ser un número."}), 400

    if not imei.isdigit():
        print(f"ERROR: IMEI no es numérico: {imei}")
        return jsonify({"success": False, "error": "El IMEI debe ser un número."}), 400
    
    if len(imei) != 15:
        print(f"ERROR: IMEI longitud incorrecta: {len(imei)}")
        return jsonify({"success": False, "error": "El IMEI debe tener exactamente 15 dígitos."}), 400

    print("Validaciones iniciales superadas correctamente")

    # =============================================
    # 3. VALIDAR/REGISTRAR CLIENTE
    # =============================================
    print("--- Validando/registrando cliente ---")
    usuario_id = g.user.get("cedula") if isinstance(g.user, dict) else getattr(g.user, "cedula", None)
    print(f"usuario_id: {usuario_id}")
    
    cliente_model = Clientes(usuario_id=usuario_id)
    cliente_existente = cliente_model.obtener_cliente_por_id(str(id_cliente_val))
    
    if not cliente_existente:
        print(f"Cliente {id_cliente_val} no existe, registrando...")
        if not nombre_cliente:
            print("ERROR: Nombre cliente vacío")
            return jsonify({"success": False, "error": "El nombre del cliente es obligatorio para registrarlo."}), 400
        
        if not apellido_cliente:
            print("ERROR: Apellido cliente vacío")
            return jsonify({"success": False, "error": "El apellido del cliente es obligatorio para registrarlo."}), 400
        
        if not celular_cliente:
            print("ERROR: Celular cliente vacío")
            return jsonify({"success": False, "error": "El celular del cliente es obligatorio para registrarlo."}), 400
        
        if not celular_cliente.isdigit():
            print(f"ERROR: Celular no es numérico: {celular_cliente}")
            return jsonify({"success": False, "error": "El celular debe contener solo números."}), 400
        
        if len(celular_cliente) != 11:
            print(f"ERROR: Celular longitud incorrecta: {len(celular_cliente)}")
            return jsonify({"success": False, "error": "El celular debe tener exactamente 11 dígitos."}), 400
        
        if correo_cliente and not _validar_email(correo_cliente):
            print(f"ERROR: Correo inválido: {correo_cliente}")
            return jsonify({"success": False, "error": "El correo electrónico no es válido."}), 400
        
        persona = Persona_natural(
            Cedula_cliente=str(id_cliente_val),
            Nombre_cliente=nombre_cliente,
            Apellido_cliente=apellido_cliente,
            Telefono_cliente=celular_cliente,
            Correo_cliente=correo_cliente,
            Direccion_cliente=direccion_cliente,
            usuario_id=usuario_id
        )
        resultado_cliente = persona.registrar_persona_natural()
        print(f"Resultado registro cliente: {resultado_cliente}")
        if "exitosamente" not in resultado_cliente.lower():
            return jsonify({"success": False, "error": f"Error al registrar cliente: {resultado_cliente}"}), 400
    else:
        print(f"Cliente {id_cliente_val} ya existe")

    # =============================================
    # 4. VALIDAR/REGISTRAR EQUIPO
    # =============================================
    print("--- Validando/registrando equipo ---")
    equipo_model = Equipo()
    equipo_model.ID_equipo = imei
    equipo_existente = equipo_model.Consultar_equipo_por_id()
    
    id_producto_final = id_modelo
    
    if not equipo_existente:
        print(f"Equipo {imei} no existe, registrando...")
        
        if modelo_custom and not id_modelo:
            print(f"Creando modelo personalizado: {modelo_custom}")
            producto = Producto(
                nombre=modelo_custom,
                id_clase="1",
                id_marca="1",
                descripcion=modelo_custom,
                usuario_id=usuario_id
            )
            try:
                id_producto_final = producto.registrar_producto()
                print(f"ID producto personalizado creado: {id_producto_final}")
            except Exception as e:
                print(f"ERROR al registrar producto personalizado: {e}")
                return jsonify({"success": False, "error": f"Error al registrar modelo personalizado: {str(e)}"}), 400
        
        if not id_producto_final:
            print("ERROR: ID de modelo inválido")
            return jsonify({"success": False, "error": "ID de modelo inválido."}), 400
        
        equipo_model.ID_producto = str(id_producto_final)
        equipo_model.Color = color
        equipo_model.Capacidad = capacidad
        equipo_model.Patron = patron # CORRECCIÓN: Asignamos el patrón al modelo
        
        print(f"Registrando equipo con:")
        print(f"  ID_producto: {equipo_model.ID_producto}")
        print(f"  Color: {equipo_model.Color}")
        print(f"  Capacidad: {equipo_model.Capacidad}")
        print(f"  Patron: {equipo_model.Patron}")
        
        resultado_equipo = equipo_model.registrar_equipo()
        print(f"Resultado registro equipo: {resultado_equipo}")
        if "exitosamente" not in resultado_equipo.lower():
            return jsonify({"success": False, "error": resultado_equipo}), 400
    else:
        print(f"Equipo {imei} ya existe")

    # =============================================
    # 5. CREAR LA ORDEN DE SERVICIO
    # =============================================
    print("--- Creando orden de servicio ---")
    print(f"Datos para crear orden:")
    print(f"  id_cliente: {id_cliente_val}")
    print(f"  id_equipo: {imei}")
    print(f"  id_modelo: {id_producto_final}")
    print(f"  descripcion: {descripcion}")
    print(f"  nota: {nota}")
    
    id_empleado = usuario_id
       
    orden_model = OrdenServicio()
    orden_model.ID_empleado = id_empleado
    
    nueva_id = orden_model.crear_orden(
        id_cliente=str(id_cliente_val),
        id_equipo=imei,
        id_modelo=id_producto_final,
        descripcion=descripcion,
        nota=nota,
        modelo_custom=modelo_custom,
    )
    
    print(f"ID de orden creada: {nueva_id}")
    
    if not nueva_id:
        print("ERROR: No se pudo crear la orden de servicio")
        return jsonify({"success": False, "error": "No se pudo crear la orden de servicio."}), 500

    print("=" * 60)
    print(f"ORDEN CREADA EXITOSAMENTE: {nueva_id}")
    print("=" * 60)

    return jsonify({
        "success": True,
        "id": nueva_id,
        "equipo": imei,
        "mensaje": "Orden de servicio creada exitosamente"
    })


# Ruta para obtener detalle de una orden específica
@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>", methods=["GET"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'consultar')
def detalle_orden_servicio(id_orden):
    ordenes = OrdenServicio()
    tests = Tests()
    detalle = ordenes.detalles_orden(id_orden)
    if not detalle:
        return jsonify({"success": False, "error": "Orden no encontrada."}), 404
    fotos = ordenes.fotos_orden(id_orden) or []
    tests_orden = tests.buscar_test_por_orden(id_orden) or []
    empleados = ordenes.empleados_asignados(id_orden) or []
    return jsonify(
        {
            "success": True,
            "detalle_orden": detalle,
            "fotos_orden": fotos,
            "test_orden": tests_orden,
            "empleados_orden": empleados,
        }
    )


# Ruta para asignar una orden
@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>/asignar", methods=["POST"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'modificar')
def asignar_orden_servicio(id_orden):
    datos = request.get_json(silent=True) or {}
    id_empleado = datos.get("id_empleado")
    
    print(f"[DEBUG] === ASIGNANDO ORDEN ===")
    print(f"[DEBUG] ID Orden: {id_orden} (type: {type(id_orden)})")
    print(f"[DEBUG] ID Empleado: {id_empleado} (type: {type(id_empleado)})")
    
    try:
        id_empleado_val = int(id_empleado)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "ID de empleado inválido. Debe ser un número."}), 400

    modelo = OrdenServicio()
    detalle = modelo.detalles_orden(id_orden)
    if not detalle:
        return jsonify({"success": False, "error": f"La orden #{id_orden} no existe."}), 404
    
    estado_actual = detalle.get("Estado", "")
    print(f"[DEBUG] Estado actual de la orden: '{estado_actual}'")
    
    if estado_actual.lower() != "pendiente":
        return jsonify({
            "success": False, 
            "error": f"La orden está en estado '{estado_actual}'. Solo se pueden asignar órdenes en estado 'Pendiente'."
        }), 400

    empleado_model = Empleados(id_empleado=str(id_empleado_val))
    empleado = empleado_model.consultar_empleado()

    if not empleado:
        return jsonify({"success": False, "error": f"El técnico con ID {id_empleado_val} no existe."}), 400

    modelo.ID_orden_servicio = id_orden
    modelo.ID_empleado = id_empleado_val
    
    ok = modelo.asignar_orden_empleado()
    
    if not ok:
        error_msg = getattr(modelo, '_ultimo_error', 'Error desconocido al asignar la orden.')
        print(f"[ERROR] Falló la asignación: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 400
    
    return jsonify({
        "success": True, 
        "message": f"Orden #{id_orden} asignada correctamente al técnico {id_empleado_val}"
    })


# Ruta para registrar una revisión
@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>/revision", methods=["POST"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'modificar')
def registrar_test_orden(id_orden):
    datos = request.get_json() or {}
    
    empleado_id = g.user.get("cedula")
    
    campos = [
        'ID_em', 'Num_test', 'Btn_power','Btn_vol','Cornetas','Mica','LCD','Tactil','Wifi',
        'Puerto_carga','Cam_pos','Cam_del','Microfono','Flash','Btn_sil','Auricular',
        'Senal','Sensor_proximidad','Face_id','Bluetooth','Observaciones'
    ]

    valores = []
    for campo in campos:
        if campo == 'ID_em':
            valores.append(empleado_id)
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
    
    return jsonify({"ok": bool(ok)})


# Ruta para actualizar estado
@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>/estado", methods=["PUT"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'modificar')
def actualizar_estado_orden(id_orden):
    datos = request.get_json(silent=True) or {}
    nuevo_estado = datos.get("estado", "").strip()
    
    if not nuevo_estado:
        return jsonify({"success": False, "error": "El estado es obligatorio."}), 400
    
    modelo = OrdenServicio()
    ok = modelo.actualizar_estado(id_orden, nuevo_estado)
    
    if not ok:
        return jsonify({"success": False, "error": "No se pudo actualizar el estado."}), 400
    
    return jsonify({"success": True, "message": "Estado actualizado"})


# Ruta para eliminar orden
@ordenes_servicio_blueprint.route("/api/ordenes-servicio/ordenes/<string:id_orden>", methods=["DELETE"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'eliminar')
def eliminar_orden_servicio(id_orden):
    modelo = OrdenServicio()
    ok = modelo.eliminar_orden(id_orden)
    if not ok:
        return jsonify({"success": False, "error": "No se pudo eliminar la orden."}), 400
    return jsonify({"success": True, "message": "Orden eliminada"})


@ordenes_servicio_blueprint.route("/api/productos/modelos", methods=["GET"])
@jwt_required
def listar_modelos():
    from app.models.database import conectar
    db = conectar().conexion1()
    if not db:
        return jsonify({"success": False, "error": "Error de conexión"}), 500

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                p.ID_producto AS id,
                p.Nombre_producto AS nombre,
                mp.Nombre_marca AS marca_nombre,
                cp.Nombre_Clase AS clase_nombre
            FROM Producto p
            LEFT JOIN Marca_producto mp ON p.ID_marca = mp.ID_marca
            LEFT JOIN Clase_producto cp ON p.ID_Clase = cp.ID_Clase
            ORDER BY mp.Nombre_marca, p.Nombre_producto
        """)
        modelos = cursor.fetchall()
        return jsonify({"success": True, "modelos": modelos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        db.close()


@ordenes_servicio_blueprint.route("/api/taller/ordenes/<string:id_orden>/fotos", methods=["POST"])
@jwt_required
@tiene_permiso('Órdenes de servicio', 'modificar')
def subir_fotos_orden(id_orden):
    try:
        archivos = request.files.getlist('fotos')
        if not archivos or all(f.filename == '' for f in archivos):
            return jsonify({"ok": False, "message": "No se seleccionaron archivos."}), 400
        
        modelo = OrdenServicio()
        modelo.ID_orden_servicio = id_orden
        
        db = modelo._conexion.conexion1()
        if not db:
            return jsonify({"ok": False, "message": "Error de conexión a la base de datos."}), 500
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MAX(ID_foto_orden_servicio) FROM Fotos_orden_servicio")
            row = cursor.fetchone()
            ultimo_id = row[0] if row else None
            if not ultimo_id:
                nuevo_num = 1
            else:
                nuevo_num = int(ultimo_id[3:]) + 1
        finally:
            cursor.close()
        
        fotos_guardadas = []
        for archivo in archivos:
            if archivo.filename == '':
                continue
            
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
            resultado = modelo.agregar_foto_orden_servicio()
            
            if "exitosamente" in resultado:
                fotos_guardadas.append({"id": id_foto, "ruta": ruta_relativa})
                nuevo_num += 1
        
        if fotos_guardadas:
            return jsonify({"ok": True, "fotos": fotos_guardadas, "message": "Fotos subidas correctamente"})
        else:
            return jsonify({"ok": False, "message": "No se pudieron guardar las fotos."}), 400
        
    except Exception as e:
        print(f"Error al subir fotos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "message": str(e)}), 500