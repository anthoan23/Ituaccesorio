from app.models.database import conectar
import mysql.connector
from typing import Any, cast
from app.models.bitacora import registrar_en_bitacora


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

    def _obtener_config_falla(self, clave_falla):
        for falla in self.FALLAS_COTIZACION:
            if falla["clave"] == clave_falla:
                return falla
        return None

    def _consulta_equipos_base(self):
        return (
            "SELECT stock.ID_producto, stock.ID_modelo, stock.Existencia, stock.Costo_venta, "
            "COALESCE(modelo_producto.N_modelo, CONCAT('Producto #', stock.ID_producto)) AS N_modelo "
            "FROM stock "
            "LEFT JOIN modelo_producto ON stock.ID_modelo = modelo_producto.ID_modelo"
        )

    def _es_modelo_iphone(self, nombre_modelo: str) -> bool:
        if not nombre_modelo:
            return False
        return "iphone" in nombre_modelo.lower()

    def consultar_equipos(self):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            # Listar solo modelos que contengan 'iPhone' (case-insensitive)
            query = (
                self._consulta_equipos_base()
                + " WHERE LOWER(COALESCE(modelo_producto.N_modelo, '')) LIKE %s"
                + " ORDER BY N_modelo ASC, stock.ID_producto ASC"
            )
            cursor.execute(query, ("%iphone%",))
            filas = cursor.fetchall()
            return [cast(dict[str, Any], fila) for fila in filas]
        finally:
            cursor.close()
            db.close()

    def consultar_equipo_por_id(self, id_producto):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            query = self._consulta_equipos_base() + " WHERE stock.ID_producto = %s LIMIT 1"
            cursor.execute(query, (id_producto,))
            fila = cursor.fetchone()
            return cast(dict[str, Any], fila) if fila else None
        finally:
            cursor.close()
            db.close()

    def consultar_costo_repuesto(self, nombre_modelo, nombre_falla):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT Costo_r FROM repuesto "
                "WHERE Nombre_r LIKE %s AND Nombre_r LIKE %s "
                "ORDER BY Costo_r ASC LIMIT 1",
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
        equipo = self.consultar_equipo_por_id(id_producto)
        if not equipo:
            return {
                "success": False,
                "error": "No se encontró el equipo seleccionado.",
            }

        nombre_modelo = str(equipo["N_modelo"] or "")
        if not self._es_modelo_iphone(nombre_modelo):
            return {
                "success": False,
                "error": "Lo sentimos, solo se aceptan iPhones para cotización.",
            }
        precio_base = int(equipo["Costo_venta"] or 0)
        fallas_validas = []
        for clave_falla in fallas_seleccionadas or []:
            config = self._obtener_config_falla(str(clave_falla))
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
        descripcion_bitacora = (
            f"Cotización Trade-in | Modelo: {nombre_modelo} | Base: {precio_base} | "
            f"Deducción: {costo_total_repuestos} | Estimado: {monto_estimado}"
        )
        if detalles_fallas:
            fallas_texto = ", ".join(detalle["etiqueta"] for detalle in detalles_fallas)
            descripcion_bitacora = f"{descripcion_bitacora} | Fallas: {fallas_texto}"

        registro_bitacora = registrar_en_bitacora(
            "Cotización Trade-in",
            descripcion_bitacora,
            usuario_id="CLIENTE",
            modulo_nombre="Trade-in",
        )
        if not registro_bitacora.get("success") and registro_bitacora.get("warning"):
            advertencias.append(registro_bitacora["warning"])

        return {
            "success": True,
            "equipo": equipo,
            "precio_base": precio_base,
            "costo_total_repuestos": costo_total_repuestos,
            "monto_estimado": monto_estimado,
            "detalles_fallas": detalles_fallas,
            "advertencias": advertencias,
        }
