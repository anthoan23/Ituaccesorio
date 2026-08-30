from flask import Blueprint, render_template, redirect, url_for, g, jsonify
from app.models.inventario import Inventario
from app.models.database import conectar
from datetime import datetime, timedelta

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/')
def home():
    try:
        usuario = getattr(g, "user", None)
        
        
        if not usuario:
            print("[DEBUG] Home - No hay usuario, redirigiendo a login")
            return redirect(url_for("login.pagina_login"))
        
        if isinstance(usuario, dict):
            nombre_rol = usuario.get("rol_nombre", "")
            if not nombre_rol:
                nombre_rol = getattr(g, "nombre_rol", "")
        else:
            nombre_rol = getattr(usuario, "rol_nombre", "")
            if not nombre_rol:
                nombre_rol = getattr(g, "nombre_rol", "")
        
        
        nombre_rol_str = str(nombre_rol).strip().lower() if nombre_rol else ""
        
        if nombre_rol_str == "admin" or nombre_rol_str == "administrador":
            return render_template(
                'index.html', 
                show_navbar=True, 
                show_notifications=True, 
                active_page='dashboard'
            )
        
        return redirect(url_for("ventas.pagina_catalogo"))
        
    except Exception as e:
        print(f"[ERROR] Home: {e}")
        traceback.print_exc()
        return redirect(url_for("login.pagina_login"))


@home_blueprint.route('/inventario')
def inventario():
    return render_template('inventario.html', show_navbar=True, show_notifications=True, active_page='inventario')


# ============================================================
# 1. INGRESOS VS GASTOS (GRÁFICO PRINCIPAL)
# ============================================================
@home_blueprint.route('/api/dashboard/ingresos-gastos', methods=['GET'])
def api_ingresos_gastos():
    """API para el gráfico de Ingresos vs Gastos - últimos 7 días"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener últimos 7 días
        fechas = []
        for i in range(6, -1, -1):
            fecha = datetime.now() - timedelta(days=i)
            fechas.append(fecha.strftime('%Y-%m-%d'))
        
        etiquetas = []
        ingresos = []
        gastos = []
        
        for fecha_str in fechas:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
            etiquetas.append(fecha_obj.strftime('%a'))
            
            # --- INGRESOS: Sumar montos de Metodo_pago con estado 'aprobado' ---
            cursor.execute("""
                SELECT COALESCE(SUM(mp.Monto), 0) as total
                FROM Metodo_pago mp
                INNER JOIN Venta v ON mp.ID_factura = v.ID_factura
                WHERE mp.Estado_pago = 'aprobado'
                AND DATE(v.Fecha_venta) = %s
            """, (fecha_str,))
            result = cursor.fetchone()
            ingresos.append(float(result['total']) if result else 0)
            
            # --- GASTOS: Sumar órdenes de compra completadas ---
            cursor.execute("""
                SELECT COALESCE(SUM(d.Cantidad_producto * s.Costo_producto), 0) as total
                FROM Orden_compra o
                INNER JOIN Detalle_orden d ON o.ID_orden_compra = d.ID_orden_compra
                INNER JOIN Suministra s ON d.ID_producto = s.ID_producto AND o.ID_proveedor = s.ID_proveedor
                WHERE o.Estado_orden_compra = 'Completada'
                AND DATE(o.Fecha_orden_compra) = %s
            """, (fecha_str,))
            result = cursor.fetchone()
            gastos.append(float(result['total']) if result else 0)
        
        conn.close()
        
        return jsonify({
            "success": True,
            "etiquetas": etiquetas,
            "ingresos": ingresos,
            "gastos": gastos
        })
        
    except Exception as e:
        print(f"Error en api_ingresos_gastos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# 2. VENTAS HOY
# ============================================================
@home_blueprint.route('/api/dashboard/ventas-hoy', methods=['GET'])
def api_ventas_hoy():
    """API para obtener las ventas de hoy"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(mp.Monto), 0) as total,
                'VES' as moneda
            FROM Metodo_pago mp
            INNER JOIN Venta v ON mp.ID_factura = v.ID_factura
            WHERE mp.Estado_pago = 'aprobado'
            AND DATE(v.Fecha_venta) = %s
        """, (hoy,))
        
        result = cursor.fetchone()
        conn.close()
        
        total = float(result['total']) if result else 0
        
        return jsonify({
            "success": True,
            "total": total,
            "total_formateado": f"{total:,.2f}",
            "simbolo": "Bs"
        })
        
    except Exception as e:
        print(f"Error en api_ventas_hoy: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# 3. ÓRDENES ACTIVAS
# ============================================================
@home_blueprint.route('/api/dashboard/ordenes-servicio', methods=['GET'])
def api_ordenes_servicio():
    """API para obtener órdenes de servicio activas"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Orden_servicio
            WHERE Estado_orden_servicio IN ('Asignada', 'En proceso')
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return jsonify({
            "success": True,
            "total": result['total'] if result else 0
        })
        
    except Exception as e:
        print(f"Error en api_ordenes_servicio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# 4. EQUIPOS REPARADOS (MES)
# ============================================================
@home_blueprint.route('/api/dashboard/reparados-mes', methods=['GET'])
def api_reparados_mes():
    """API para obtener equipos reparados en el mes"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        mes_actual = datetime.now().strftime('%Y-%m')
        
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Orden_servicio
            WHERE Estado_orden_servicio = 'Reparada'
            AND DATE_FORMAT(Fecha_salida, '%%Y-%%m') = %s
        """, (mes_actual,))
        
        result = cursor.fetchone()
        conn.close()
        
        return jsonify({
            "success": True,
            "total": result['total'] if result else 0
        })
        
    except Exception as e:
        print(f"Error en api_reparados_mes: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# 5. INGRESOS MENSUALES
# ============================================================
@home_blueprint.route('/api/dashboard/ingresos-mensuales', methods=['GET'])
def api_ingresos_mensuales():
    """API para obtener ingresos del mes actual"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        mes_actual = datetime.now().strftime('%Y-%m')
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(mp.Monto), 0) as total
            FROM Metodo_pago mp
            INNER JOIN Venta v ON mp.ID_factura = v.ID_factura
            WHERE mp.Estado_pago = 'aprobado'
            AND DATE_FORMAT(v.Fecha_venta, '%%Y-%%m') = %s
        """, (mes_actual,))
        
        result = cursor.fetchone()
        conn.close()
        
        total = float(result['total']) if result else 0
        
        return jsonify({
            "success": True,
            "total": total,
            "total_formateado": f"{total:,.2f}",
            "simbolo": "Bs"
        })
        
    except Exception as e:
        print(f"Error en api_ingresos_mensuales: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# 6. PRODUCTOS BAJO STOCK
# ============================================================
@home_blueprint.route('/api/dashboard/bajo-stock', methods=['GET'])
def api_bajo_stock():
    """API para obtener productos con bajo stock (<=10)"""
    try:
        inventario = Inventario()
        productos = inventario.obtener_productos_bajo_stock(limite=10)
        return jsonify({"success": True, "productos": productos})
    except Exception as e:
        print(f"Error en api_bajo_stock: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@home_blueprint.route('/api/dashboard/sin-stock', methods=['GET'])
def api_sin_stock():
    """API para obtener productos sin stock (=0)"""
    try:
        inventario = Inventario()
        productos = inventario.obtener_productos_sin_stock()
        return jsonify({"success": True, "productos": productos})
    except Exception as e:
        print(f"Error en api_sin_stock: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# 7. ACTIVIDAD RECIENTE
# ============================================================
@home_blueprint.route('/api/dashboard/actividad-reciente', methods=['GET'])
def api_actividad_reciente():
    """API para obtener actividad reciente de la bitácora"""
    try:
        db = conectar()
        conn = db.conexion2()  # Base de datos 'seguridad'
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                b.id,
                b.usuario_id,
                b.accion,
                b.descripcion,
                b.fecha_hora,
                m.nombre as modulo_nombre,
                TIMESTAMPDIFF(MINUTE, b.fecha_hora, NOW()) as minutos_pasados
            FROM bitacora b
            LEFT JOIN modulo m ON b.modulo_id = m.id
            ORDER BY b.fecha_hora DESC
            LIMIT 10
        """)
        
        actividades = cursor.fetchall()
        conn.close()
        
        # Procesar tiempo relativo
        for act in actividades:
            minutos = act.get('minutos_pasados', 0)
            if minutos < 1:
                act['tiempo_relativo'] = 'Ahora mismo'
            elif minutos < 60:
                act['tiempo_relativo'] = f'Hace {minutos} min'
            elif minutos < 1440:
                horas = minutos // 60
                act['tiempo_relativo'] = f'Hace {horas} h'
            else:
                dias = minutos // 1440
                act['tiempo_relativo'] = f'Hace {dias} d'
        
        return jsonify({
            "success": True,
            "actividades": actividades
        })
        
    except Exception as e:
        print(f"Error en api_actividad_reciente: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": True, "actividades": []})


# ============================================================
# 8. TÉCNICOS ACTIVOS
# ============================================================
@home_blueprint.route('/api/dashboard/tecnicos-activos', methods=['GET'])
def api_tecnicos_activos():
    """API para obtener número de técnicos activos"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        # Técnicos son empleados con cargo 'Técnico' (CRG0000006)
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Empleado
            WHERE ID_cargo = 'CRG0000006'
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return jsonify({
            "success": True,
            "total": result['total'] if result else 0
        })
        
    except Exception as e:
        print(f"Error en api_tecnicos_activos: {e}")
        return jsonify({"success": True, "total": 0})

        # ============================================================
# 9. VENTAS DE LA SEMANA
# ============================================================
@home_blueprint.route('/api/dashboard/ventas-semana', methods=['GET'])
def api_ventas_semana():
    """API para obtener las ventas de la última semana"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        # Fecha de hace 7 días
        semana_atras = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(mp.Monto), 0) as total
            FROM Metodo_pago mp
            INNER JOIN Venta v ON mp.ID_factura = v.ID_factura
            WHERE mp.Estado_pago = 'aprobado'
            AND DATE(v.Fecha_venta) >= %s
        """, (semana_atras,))
        
        result = cursor.fetchone()
        conn.close()
        
        total = float(result['total']) if result else 0
        
        return jsonify({
            "success": True,
            "total": total,
            "total_formateado": f"{total:,.2f}",
            "simbolo": "Bs"
        })
        
    except Exception as e:
        print(f"Error en api_ventas_semana: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================
# 10. INCREMENTO DE REPARACIONES (SEMANA ACTUAL vs ANTERIOR)
# ============================================================
@home_blueprint.route('/api/dashboard/incremento-reparaciones', methods=['GET'])
def api_incremento_reparaciones():
    """API para calcular el incremento de reparaciones esta semana vs la anterior"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        # Semana actual (últimos 7 días)
        semana_atras = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Semana anterior (días 8-14 atrás)
        dos_semanas_atras = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        
        # Reparaciones de la semana actual (ordenes reparadas en los últimos 7 días)
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Orden_servicio
            WHERE Estado_orden_servicio = 'Reparada'
            AND DATE(Fecha_salida) >= %s
        """, (semana_atras,))
        result_actual = cursor.fetchone()
        total_actual = result_actual['total'] if result_actual else 0
        
        # Reparaciones de la semana anterior (días 8-14 atrás)
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM Orden_servicio
            WHERE Estado_orden_servicio = 'Reparada'
            AND DATE(Fecha_salida) >= %s
            AND DATE(Fecha_salida) < %s
        """, (dos_semanas_atras, semana_atras))
        result_anterior = cursor.fetchone()
        total_anterior = result_anterior['total'] if result_anterior else 0
        
        conn.close()
        
        # Calcular incremento
        if total_anterior > 0:
            incremento = total_actual - total_anterior
            texto = f"{'+' if incremento >= 0 else ''}{incremento} esta semana"
        else:
            texto = f"{total_actual} esta semana"
        
        return jsonify({
            "success": True,
            "total_actual": total_actual,
            "total_anterior": total_anterior,
            "incremento": total_actual - total_anterior,
            "texto": texto
        })
        
    except Exception as e:
        print(f"Error en api_incremento_reparaciones: {e}")
        return jsonify({"success": True, "total_actual": 0, "total_anterior": 0, "incremento": 0, "texto": "0 esta semana"})


# ============================================================
# 11. INCREMENTO DE VENTAS (SEMANA ACTUAL vs ANTERIOR)
# ============================================================
@home_blueprint.route('/api/dashboard/incremento-ventas', methods=['GET'])
def api_incremento_ventas():
    """API para calcular el incremento de ventas esta semana vs la anterior"""
    try:
        db = conectar()
        conn = db.conexion1()
        cursor = conn.cursor(dictionary=True)
        
        semana_atras = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        dos_semanas_atras = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        
        # Ventas de la semana actual
        cursor.execute("""
            SELECT COALESCE(SUM(mp.Monto), 0) as total
            FROM Metodo_pago mp
            INNER JOIN Venta v ON mp.ID_factura = v.ID_factura
            WHERE mp.Estado_pago = 'aprobado'
            AND DATE(v.Fecha_venta) >= %s
        """, (semana_atras,))
        result_actual = cursor.fetchone()
        total_actual = float(result_actual['total']) if result_actual else 0
        
        # Ventas de la semana anterior
        cursor.execute("""
            SELECT COALESCE(SUM(mp.Monto), 0) as total
            FROM Metodo_pago mp
            INNER JOIN Venta v ON mp.ID_factura = v.ID_factura
            WHERE mp.Estado_pago = 'aprobado'
            AND DATE(v.Fecha_venta) >= %s
            AND DATE(v.Fecha_venta) < %s
        """, (dos_semanas_atras, semana_atras))
        result_anterior = cursor.fetchone()
        total_anterior = float(result_anterior['total']) if result_anterior else 0
        
        conn.close()
        
        # Calcular porcentaje de incremento
        if total_anterior > 0:
            porcentaje = ((total_actual - total_anterior) / total_anterior) * 100
            texto = f"{'+' if porcentaje >= 0 else ''}{porcentaje:.1f}%"
            tendencia = "up" if porcentaje >= 0 else "down"
        else:
            porcentaje = 0
            texto = "+0%"
            tendencia = "up" if total_actual > 0 else "neutral"
        
        return jsonify({
            "success": True,
            "total_actual": total_actual,
            "total_anterior": total_anterior,
            "porcentaje": round(porcentaje, 1),
            "texto": texto,
            "tendencia": tendencia
        })
        
    except Exception as e:
        print(f"Error en api_incremento_ventas: {e}")
        return jsonify({"success": True, "total_actual": 0, "total_anterior": 0, "porcentaje": 0, "texto": "+0%", "tendencia": "neutral"})