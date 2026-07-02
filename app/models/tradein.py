from app.models.database import conectar
from typing import Any, cast, Optional, Dict, List
from decimal import Decimal
from app.models.bitacora import Bitacora


class TradeIn(conectar):
    """Modelo para cotizaciones de Trade-in (solo cálculo, no guarda en BD)"""
    
    FALLAS_COTIZACION = [
        {"clave": "power", "etiqueta": "Botón de power", "busqueda": "power"},
        {"clave": "cornetas", "etiqueta": "Cornetas", "busqueda": "cornetas"},
        {"clave": "mica", "etiqueta": "Mica", "busqueda": "mica"},
        {"clave": "lcd", "etiqueta": "LCD", "busqueda": "lcd"},
        {"clave": "tactil", "etiqueta": "Táctil", "busqueda": "tactil"},
        {"clave": "botones_laterales", "etiqueta": "Botones laterales", "busqueda": "boton"},
        {"clave": "botones_inferiores", "etiqueta": "Botones inferiores", "busqueda": "boton"},
        {"clave": "puerto_carga", "etiqueta": "Puerto de carga", "busqueda": "carga"},
        {"clave": "wifi", "etiqueta": "WiFi", "busqueda": "wifi"},
        {"clave": "camara_trasera", "etiqueta": "Cámara trasera", "busqueda": "camara"},
        {"clave": "camara_delantera", "etiqueta": "Cámara delantera", "busqueda": "camara"},
        {"clave": "flash", "etiqueta": "Flash", "busqueda": "flash"},
        {"clave": "senal_auricular", "etiqueta": "Señal auricular", "busqueda": "auricular"},
        {"clave": "microfono", "etiqueta": "Micrófono", "busqueda": "microfono"},
        {"clave": "sensor_proximidad", "etiqueta": "Sensor de proximidad", "busqueda": "proximidad"},
        {"clave": "caja", "etiqueta": "Caja", "busqueda": "caja"},
        {"clave": "cargador", "etiqueta": "Cargador", "busqueda": "cargador"},
        {"clave": "cable", "etiqueta": "Cable", "busqueda": "cable"},
        {"clave": "audifonos", "etiqueta": "Audífonos", "busqueda": "audifonos"},
        {"clave": "manuales", "etiqueta": "Manuales", "busqueda": "manual"},
    ]

    def __init__(self, usuario_id: str = None):
        super().__init__()
        self.usuario_id = usuario_id

    def _obtener_config_falla(self, clave_falla: str) -> Optional[Dict[str, str]]:
        """Obtiene la configuración de una falla por su clave"""
        for falla in self.FALLAS_COTIZACION:
            if falla["clave"] == clave_falla:
                return falla
        return None

    def consultar_equipos(self) -> List[Dict[str, Any]]:
        """
        Consulta equipos disponibles para trade-in.
        En lugar de filtrar solo iPhone, devuelve todos los productos con existencia > 0.
        """
        db = self.conexion1()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    e.ID_inventario AS ID_producto,
                    e.Costo_venta,
                    p.Nombre_producto AS N_modelo,
                    e.Existencia
                FROM Existencias_productos e
                INNER JOIN Producto p ON p.ID_producto = e.ID_producto
                WHERE e.Existencia > 0
                ORDER BY p.Nombre_producto ASC
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            
            # Convertir Decimal a float para serialización JSON
            for fila in filas:
                if isinstance(fila.get("Costo_venta"), Decimal):
                    fila["Costo_venta"] = float(fila["Costo_venta"])
            
            return [cast(Dict[str, Any], fila) for fila in filas] if filas else []
        finally:
            cursor.close()
            db.close()

    def consultar_equipo_por_id(self, id_producto: str) -> Optional[Dict[str, Any]]:
        """Consulta un equipo específico por ID de inventario"""
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
                    e.ID_inventario AS ID_producto,
                    e.Costo_venta,
                    p.Nombre_producto AS N_modelo,
                    e.Existencia
                FROM Existencias_productos e
                INNER JOIN Producto p ON p.ID_producto = e.ID_producto
                WHERE e.ID_inventario = %s
                LIMIT 1
            """
            cursor.execute(query, (id_producto_str,))
            fila = cursor.fetchone()
            
            if fila and isinstance(fila.get("Costo_venta"), Decimal):
                fila["Costo_venta"] = float(fila["Costo_venta"])
            
            return cast(Dict[str, Any], fila) if fila else None
        finally:
            cursor.close()
            db.close()

    def calcular_cotizacion(self, id_producto, fallas_seleccionadas) -> Dict[str, Any]:
        """
        Calcula la cotización de un equipo.
        
        Args:
            id_producto: ID del producto (ID_inventario)
            fallas_seleccionadas: Lista de claves de fallas seleccionadas
        
        Returns:
            Dict con resultado de la cotización
        """
        # Validaciones
        if not id_producto:
            return {
                "success": False,
                "error": "El ID del producto no puede estar vacío.",
            }
        
        id_producto_str = str(id_producto).strip()
        
        equipo = self.consultar_equipo_por_id(id_producto_str)
        if not equipo:
            return {
                "success": False,
                "error": f"No se encontró el equipo con ID '{id_producto_str}'.",
            }

        nombre_modelo = str(equipo["N_modelo"] or "")
        precio_base = float(equipo["Costo_venta"] or 0)
        
        if precio_base <= 0:
            return {
                "success": False,
                "error": f"El equipo '{nombre_modelo}' no tiene un precio base válido.",
            }
        
        # Procesar fallas seleccionadas
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

        # Calcular deducciones
        detalles_fallas = []
        advertencias = []
        costo_total_repuestos = 0.0

        # Porcentaje de deducción por falla (aproximado, ya que no hay tabla de repuestos)
        # En una implementación real, consultarías una tabla de costos por falla/modelo
        DEDUCCION_POR_FALLA = 0.05  # 5% de deducción por cada falla
        
        for falla in fallas_validas:
            # Calcular deducción como porcentaje del precio base
            deduccion = round(precio_base * DEDUCCION_POR_FALLA, 2)
            costo_total_repuestos += deduccion
            
            detalles_fallas.append({
                "clave": falla["clave"],
                "etiqueta": falla["etiqueta"],
                "costo": deduccion,
            })
            
            advertencias.append(
                f"Se aplicó {DEDUCCION_POR_FALLA * 100}% de deducción por {falla['etiqueta']}."
            )

        monto_estimado = max(precio_base - costo_total_repuestos, 0)
        
        # Registrar en bitácora (opcional)
        if self.usuario_id:
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
                usuario_id=self.usuario_id,
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