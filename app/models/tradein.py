from decimal import Decimal
from typing import Any, cast

from app.models.bitacora import Bitacora
from app.models.database import conectar


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

    # Mapeo de fallas a productos/repuestos en la BD
    # Esto relaciona cada falla con un producto de repuesto
    MAPEO_FALLA_REPUESTO = {
        "power": "boton_power",
        "cornetas": "corneta",
        "mica": "mica",
        "lcd": "pantalla",
        "tactil": "touch",
        "botones_laterales": "boton_volumen",
        "botones_inferiores": "boton_home",
        "puerto_carga": "puerto_carga",
        "wifi": "modulo_wifi",
        "camara_trasera": "camara_trasera",
        "camara_delantera": "camara_frontal",
        "flash": "flash",
        "senal_auricular": "auricular",
        "microfono": "microfono",
        "sensor_proximidad": "sensor_prox",
        "caja": "caja",
        "cargador": "cargador",
        "cable": "cable_usb",
        "audifonos": "audifonos",
        "manuales": "manuales",
    }

    def __init__(self, usuario_id: str = None):
        super().__init__()
        self.usuario_id = usuario_id

    def _obtener_config_falla(self, clave_falla: str) -> dict[str, str] | None:
        """Obtiene la configuración de una falla por su clave"""
        for falla in self.FALLAS_COTIZACION:
            if falla["clave"] == clave_falla:
                return falla
        return None

    def _obtener_descripcion_falla(self, clave_falla: str) -> str:
        """Obtiene una descripción detallada de cada falla"""
        descripciones = {
            "power": "El botón de encendido no responde o funciona de manera intermitente.",
            "cornetas": "El altavoz superior no reproduce sonido o suena distorsionado.",
            "mica": "El vidrio protector de la pantalla tiene rayones, grietas o está roto.",
            "lcd": "La pantalla muestra líneas, manchas, colores distorsionados o está completamente negra.",
            "tactil": "El panel táctil no responde al tacto o responde de manera errática.",
            "botones_laterales": "Los botones de volumen no funcionan correctamente.",
            "botones_inferiores": "El botón de inicio o los botones inferiores no responden.",
            "puerto_carga": "El puerto de carga no reconoce el cable o no carga correctamente.",
            "wifi": "El WiFi no se conecta o se desconecta constantemente.",
            "camara_trasera": "La cámara trasera no enfoca, toma fotos borrosas o no funciona.",
            "camara_delantera": "La cámara frontal no funciona o toma fotos de baja calidad.",
            "flash": "El flash no enciende o funciona de manera intermitente.",
            "senal_auricular": "El sonido del auricular es bajo, distorsionado o no se escucha.",
            "microfono": "El micrófono no capta la voz correctamente o produce ruido.",
            "sensor_proximidad": "El sensor de proximidad no apaga la pantalla durante las llamadas.",
            "caja": "La caja del dispositivo no está en buen estado o falta.",
            "cargador": "El cargador no funciona correctamente.",
            "cable": "El cable USB está dañado o no funciona.",
            "audifonos": "Los audífonos no funcionan o tienen mala calidad de sonido.",
            "manuales": "Los manuales o documentación no están completos.",
        }
        return descripciones.get(clave_falla, "Esta falla requiere revisión técnica para determinar el costo exacto.")

    def _obtener_costo_repuesto(self, id_producto_equipo: str, falla_clave: str) -> float:
        """
        Obtiene el costo de un repuesto desde la base de datos.
        Busca en Suministra el costo del repuesto relacionado con la falla.
        """
        db = self.conexion1()
        if not db:
            return 0.00  # Valor por defecto si no hay conexión

        cursor = db.cursor(dictionary=True)
        try:
            # Buscar el repuesto relacionado con la falla
            # Primero, obtener el ID_producto del repuesto basado en el mapeo
            nombre_repuesto = self.MAPEO_FALLA_REPUESTO.get(falla_clave, falla_clave)
            
            # Buscar el producto repuesto
            query_repuesto = """
                SELECT ID_producto 
                FROM Producto 
                WHERE LOWER(Nombre_producto) LIKE %s 
                    AND ID_Clase = '7'  -- Clase Repuesto
                LIMIT 1
            """
            cursor.execute(query_repuesto, (f'%{nombre_repuesto}%',))
            repuesto = cursor.fetchone()
            
            if not repuesto:
                return 0.00  # Valor por defecto si no encuentra el repuesto
            
            id_repuesto = repuesto['ID_producto']
            
            # Obtener el costo del repuesto desde Suministra (tomar el más bajo)
            query_costo = """
                SELECT MIN(Costo_producto) as costo
                FROM Suministra
                WHERE ID_producto = %s
            """
            cursor.execute(query_costo, (id_repuesto,))
            resultado = cursor.fetchone()
            
            if resultado and resultado['costo'] is not None:
                return float(resultado['costo'])
            
            # Si no tiene costo en Suministra, buscar en Existencias_productos
            query_existencia = """
                SELECT Costo_venta
                FROM Existencias_productos
                WHERE ID_producto = %s
                LIMIT 1
            """
            cursor.execute(query_existencia, (id_repuesto,))
            existencia = cursor.fetchone()
            
            if existencia and existencia['Costo_venta'] is not None:
                return float(existencia['Costo_venta'])
            
            return 0.00  # Valor por defecto
            
        except Exception as e:
            print(f"Error al obtener costo de repuesto: {e}")
            return 0.00
        finally:
            cursor.close()
            db.close()

    def consultar_equipos(self) -> list[dict[str, Any]]:
        """
        Consulta equipos disponibles para trade-in.
        Solo muestra equipos Apple de la clase Teléfono (iPhone).
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
                    e.Existencia,
                    m.Nombre_marca AS Marca,
                    c.Nombre_Clase AS Clase
                FROM Existencias_productos e
                INNER JOIN Producto p ON p.ID_producto = e.ID_producto
                INNER JOIN Marca_producto m ON m.ID_marca = p.ID_marca
                INNER JOIN Clase_producto c ON c.ID_Clase = p.ID_Clase
                WHERE e.Existencia > 0
                    AND m.Nombre_marca = 'Apple'
                    AND c.Nombre_Clase = 'Telefono'
                ORDER BY p.Nombre_producto ASC
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            
            for fila in filas:
                if isinstance(fila.get("Costo_venta"), Decimal):
                    fila["Costo_venta"] = float(fila["Costo_venta"])
            
            return [cast(dict[str, Any], fila) for fila in filas] if filas else []
        finally:
            cursor.close()
            db.close()

    def consultar_equipo_por_id(self, id_producto: str) -> dict[str, Any] | None:
        """
        Consulta un equipo específico por ID de inventario.
        Solo equipos Apple de la clase Teléfono (iPhone).
        """
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
                    e.Existencia,
                    m.Nombre_marca AS Marca,
                    c.Nombre_Clase AS Clase,
                    p.ID_producto AS ID_producto_base
                FROM Existencias_productos e
                INNER JOIN Producto p ON p.ID_producto = e.ID_producto
                INNER JOIN Marca_producto m ON m.ID_marca = p.ID_marca
                INNER JOIN Clase_producto c ON c.ID_Clase = p.ID_Clase
                WHERE e.ID_inventario = %s
                    AND m.Nombre_marca = 'Apple'
                    AND c.Nombre_Clase = 'Telefono'
                LIMIT 1
            """
            cursor.execute(query, (id_producto_str,))
            fila = cursor.fetchone()
            
            if fila and isinstance(fila.get("Costo_venta"), Decimal):
                fila["Costo_venta"] = float(fila["Costo_venta"])
            
            return cast(dict[str, Any], fila) if fila else None
        finally:
            cursor.close()
            db.close()

    def calcular_cotizacion(self, id_producto, fallas_seleccionadas) -> dict[str, Any]:
       
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
        id_producto_base = equipo.get("ID_producto_base", "")
        
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

        # Calcular deducciones con costos reales desde la BD
        detalles_fallas = []
        advertencias = []
        costo_total_repuestos = 0.0

        for falla in fallas_validas:
            # Obtener costo del repuesto desde la base de datos
            costo = self._obtener_costo_repuesto(id_producto_base, falla["clave"])
            costo_total_repuestos += costo
            
            detalles_fallas.append({
                "clave": falla["clave"],
                "etiqueta": falla["etiqueta"],
                "costo": round(costo, 2),
                "descripcion": self._obtener_descripcion_falla(falla["clave"]),
            })
            
            advertencias.append(
                f"Se aplicó ${costo:.2f} por {falla['etiqueta']}."
            )

        if len(fallas_validas) >= 5:
            descuento_adicional = costo_total_repuestos * 0.10
            costo_total_repuestos += descuento_adicional
            advertencias.append(
                f"Se aplicó un 10% de descuento adicional por múltiples fallas (${descuento_adicional:.2f})."
            )

        monto_estimado = max(precio_base - costo_total_repuestos, 0)
        
        # Registrar en bitácora
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
            "precio_base": round(precio_base, 2),
            "costo_total_repuestos": round(costo_total_repuestos, 2),
            "monto_estimado": round(monto_estimado, 2),
            "detalles_fallas": detalles_fallas,
            "advertencias": advertencias,
            "total_fallas": len(fallas_validas),
        }