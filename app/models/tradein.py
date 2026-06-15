from app.models.database import conectar
import mysql.connector
from typing import Any, cast
from app.models.bitacora import Bitacora


class TradeIn(conectar):
    FALLAS_COTIZACION = [
        {"clave": "power", "etiqueta": "Botón de power", "busqueda": "Power"},
        {"clave": "cornetas", "etiqueta": "Cornetas", "busqueda": "Cornetas"},
        {"clave": "mica", "etiqueta": "Mica", "busqueda": "Mica"},
        {"clave": "lcd", "etiqueta": "LCD", "busqueda": "LCD"},
        {"clave": "tactil", "etiqueta": "Táctil", "busqueda": "Tactil"},
        {"clave": "botones_laterales", "etiqueta": "Botones laterales", "busqueda": "Boton"},
        {"clave": "botones_inferiores", "etiqueta": "Botones inferiores", "busqueda": "Boton"},
        {"clave": "puerto_carga", "etiqueta": "Puerto de carga", "busqueda": "Puerto de carga"},
        {"clave": "wifi", "etiqueta": "WiFi", "busqueda": "Wifi"},
        {"clave": "camara_trasera", "etiqueta": "Cámara trasera", "busqueda": "Camara trasera"},
        {"clave": "camara_delantera", "etiqueta": "Cámara delantera", "busqueda": "Camara delantera"},
        {"clave": "flash", "etiqueta": "Flash", "busqueda": "Flash"},
        {"clave": "senal_auricular", "etiqueta": "Señal auricular", "busqueda": "Auricular"},
        {"clave": "microfono", "etiqueta": "Micrófono", "busqueda": "Microfono"},
        {"clave": "sensor_proximidad", "etiqueta": "Sensor de proximidad", "busqueda": "Proximidad"},
        {"clave": "caja", "etiqueta": "Caja", "busqueda": "Caja"},
        {"clave": "cargador", "etiqueta": "Cargador", "busqueda": "Cargador"},
        {"clave": "cable", "etiqueta": "Cable", "busqueda": "Cable"},
        {"clave": "audifonos", "etiqueta": "Audífonos", "busqueda": "Audifonos"},
        {"clave": "manuales", "etiqueta": "Manuales", "busqueda": "Manual"},
    ]

    def __init__(self, usuario_id: str = None):
        super().__init__()
        self.usuario_id = usuario_id

    def _obtener_config_falla(self, clave_falla):
        for falla in self.FALLAS_COTIZACION:
            if falla["clave"] == clave_falla:
                return falla
        return None

    def consultar_equipos(self):
        """Consulta equipos disponibles para trade-in (solo iPhone)"""
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    i.ID_inventario AS ID_producto,
                    i.Costo_venta,
                    p.Nombre_producto AS N_modelo
                FROM Inventario i
                INNER JOIN Producto p ON p.ID_producto = i.ID_producto
                WHERE LOWER(p.Nombre_producto) LIKE '%iphone%'
                ORDER BY p.Nombre_producto ASC
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            return [cast(dict[str, Any], fila) for fila in filas] if filas else []
        finally:
            cursor.close()
            db.close()

    def consultar_equipo_por_id(self, id_producto):
        """Consulta un equipo específico por ID"""
        if not id_producto:
            return None
        
        id_producto_str = str(id_producto).strip()
        
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    i.ID_inventario AS ID_producto,
                    i.Costo_venta,
                    p.Nombre_producto AS N_modelo,
                    i.Existencia
                FROM Inventario i
                INNER JOIN Producto p ON p.ID_producto = i.ID_producto
                WHERE i.ID_inventario = %s
                LIMIT 1
            """
            cursor.execute(query, (id_producto_str,))
            fila = cursor.fetchone()
            return cast(dict[str, Any], fila) if fila else None
        finally:
            cursor.close()
            db.close()

    def consultar_costo_repuesto(self, nombre_modelo, nombre_falla):
        """Consulta el costo de un repuesto para un modelo específico"""
        if not nombre_modelo or not nombre_falla:
            return None
        
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                """SELECT Precio_venta FROM Inventario i
                INNER JOIN Producto p ON p.ID_producto = i.ID_producto
                WHERE p.Nombre_producto LIKE %s 
                AND p.Nombre_producto LIKE %s 
                AND i.Costo_venta > 0
                LIMIT 1""",
                (f"%{nombre_falla}%", f"%{nombre_modelo}%"),
            )
            fila = cursor.fetchone()
            if not fila:
                return None
            costo = cast(tuple[Any, ...], fila)[0]
            return int(str(costo)) if costo is not None else None
        except mysql.connector.Error:
            return None
        finally:
            cursor.close()
            db.close()

    def calcular_cotizacion(self, id_producto, fallas_seleccionadas):
        """Calcula la cotización de un equipo"""
        if not id_producto:
            return {
                "success": False,
                "error": "El ID del producto no puede estar vacío.",
            }
        
        id_producto_str = str(id_producto).strip()
        
        if not id_producto_str.isdigit():
            return {
                "success": False,
                "error": "El ID del producto debe contener solo números.",
            }
        
        if len(id_producto_str) > 15:
            return {
                "success": False,
                "error": "El ID del producto no puede exceder los 15 caracteres.",
            }
        
        equipo = self.consultar_equipo_por_id(id_producto_str)
        if not equipo:
            return {
                "success": False,
                "error": f"No se encontró el equipo con ID '{id_producto_str}'.",
            }

        nombre_modelo = str(equipo["N_modelo"] or "")
        if "iphone" not in nombre_modelo.lower():
            return {
                "success": False,
                "error": "Lo sentimos, solo se aceptan iPhones para cotización.",
            }
        
        precio_base = int(equipo["Costo_venta"] or 0)
        
        if precio_base <= 0:
            return {
                "success": False,
                "error": f"El equipo '{nombre_modelo}' no tiene un precio base válido.",
            }
        
        # Validar fallas seleccionadas
        fallas_validas = []
        if fallas_seleccionadas:
            if not isinstance(fallas_seleccionadas, (list, tuple)):
                return {
                    "success": False,
                    "error": "Las fallas seleccionadas deben ser una lista.",
                }
            
            for falla in fallas_seleccionadas:
                falla_str = str(falla).strip()
                config = self._obtener_config_falla(falla_str)
                if config and config not in fallas_validas:
                    fallas_validas.append(config)

        detalles_fallas = []
        advertencias = []
        costo_total_repuestos = 0

        for falla in fallas_validas:
            costo = self.consultar_costo_repuesto(nombre_modelo, falla["busqueda"])
            if costo is None:
                advertencias.append(
                    f"No se encontró un repuesto para {falla['etiqueta']} en el modelo seleccionado."
                )
                costo = 0

            costo_total_repuestos += int(costo)
            detalles_fallas.append({
                "clave": falla["clave"],
                "etiqueta": falla["etiqueta"],
                "costo": int(costo),
            })

        monto_estimado = max(precio_base - costo_total_repuestos, 0)
        
        # Registrar en bitácora
        descripcion_bitacora = (
            f"Cotización Trade-in | Modelo: {nombre_modelo} | Base: {precio_base} | "
            f"Deducción: {costo_total_repuestos} | Estimado: {monto_estimado}"
        )
        if detalles_fallas:
            fallas_texto = ", ".join(detalle["etiqueta"] for detalle in detalles_fallas)
            descripcion_bitacora = f"{descripcion_bitacora} | Fallas: {fallas_texto}"

        bitacora = Bitacora(
            accion="Cotización Trade-in",
            descripcion=descripcion_bitacora,
            usuario_id=self.usuario_id or "ANONIMO",
            modulo_nombre="Trade-in"
        )
        resultado_bitacora = bitacora.registrar()
        
        if not resultado_bitacora.get("success") and resultado_bitacora.get("warning"):
            advertencias.append(resultado_bitacora["warning"])

        return {
            "success": True,
            "equipo": equipo,
            "precio_base": precio_base,
            "costo_total_repuestos": costo_total_repuestos,
            "monto_estimado": monto_estimado,
            "detalles_fallas": detalles_fallas,
            "advertencias": advertencias,
        }