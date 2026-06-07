from __future__ import annotations
from app.models.database import conectar
from datetime import datetime
from typing import Dict, Any, Optional, List


class EntregaModel:
    """Modelo para operaciones de entregas"""
    
    def __init__(self):
        self.__conexion_bd = conectar()
    
    def _generar_id_entrega(self) -> str:
        db = self.__conexion_bd.conexion1()
        if not db:
            return "ENT0000001"
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT MAX(ID_entrega) FROM Entrega")
            row = cursor.fetchone()
            ultimo_id = row[0] if row else None
            
            if ultimo_id and ultimo_id.startswith('ENT'):
                num = int(ultimo_id[3:]) + 1
            else:
                num = 1
            
            return f"ENT{num:07d}"
        finally:
            cursor.close()
            db.close()
    
    def listar_entregas(self, estado: int = None) -> List[Dict[str, Any]]:
        """Lista todas las entregas, opcionalmente filtradas por estado"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            where = []
            params = []
            
            if estado is not None:
                where.append("e.Estado_entrega = %s")
                params.append(estado)
            
            where_sql = f"WHERE {' AND '.join(where)}" if where else ""
            
            cursor.execute(f"""
                SELECT 
                    e.ID_entrega AS id_entrega,
                    e.ID_factura AS factura_id,
                    e.Cedula_delivery AS cedula_delivery,
                    e.Estado_entrega AS estado,
                    e.Direccion_entrega AS direccion,
                    e.Fecha_entrega AS fecha_entrega,
                    pd.Nombre_delivery AS delivery_nombre,
                    pd.Apellido_delivery AS delivery_apellido,
                    CONCAT(pd.Nombre_delivery, ' ', pd.Apellido_delivery) AS delivery_nombre_completo,
                    v.ID_cliente AS cliente_id,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Direccion_cliente AS cliente_direccion
                FROM Entrega e
                LEFT JOIN Personal_delivery pd ON e.Cedula_delivery = pd.Cedula_delivery
                LEFT JOIN Venta v ON e.ID_factura = v.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                {where_sql}
                ORDER BY e.Fecha_entrega DESC
            """, tuple(params))
            
            entregas = cursor.fetchall()
            
            # Convertir estado a texto para mostrar
            for entrega in entregas:
                estado_val = entrega.get("estado", 0)
                if estado_val == 0:
                    entrega["estado_texto"] = "⏳ Pendiente"
                elif estado_val == 1:
                    entrega["estado_texto"] = "🚚 En camino"
                elif estado_val == 2:
                    entrega["estado_texto"] = "✅ Entregado"
                elif estado_val == 3:
                    entrega["estado_texto"] = "❌ Cancelado"
                else:
                    entrega["estado_texto"] = "📋 Programado"
            
            return entregas
        finally:
            cursor.close()
            db.close()
    
    def obtener_entrega(self, entrega_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una entrega por su ID"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_entrega AS id_entrega,
                    e.ID_factura AS factura_id,
                    e.Cedula_delivery AS cedula_delivery,
                    e.Estado_entrega AS estado,
                    e.Direccion_entrega AS direccion,
                    e.Fecha_entrega AS fecha_entrega,
                    pd.Nombre_delivery AS delivery_nombre,
                    pd.Apellido_delivery AS delivery_apellido,
                    v.ID_cliente AS cliente_id,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Direccion_cliente AS cliente_direccion,
                    c.Correo_cliente AS cliente_correo
                FROM Entrega e
                LEFT JOIN Personal_delivery pd ON e.Cedula_delivery = pd.Cedula_delivery
                LEFT JOIN Venta v ON e.ID_factura = v.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE e.ID_entrega = %s
            """, (entrega_id,))
            
            entrega = cursor.fetchone()
            if entrega:
                estado_val = entrega.get("estado", 0)
                if estado_val == 0:
                    entrega["estado_texto"] = "⏳ Pendiente"
                elif estado_val == 1:
                    entrega["estado_texto"] = "🚚 En camino"
                elif estado_val == 2:
                    entrega["estado_texto"] = "✅ Entregado"
                elif estado_val == 3:
                    entrega["estado_texto"] = "❌ Cancelado"
                else:
                    entrega["estado_texto"] = "📋 Programado"
            
            return entrega
        finally:
            cursor.close()
            db.close()
    
    def registrar_entrega(
        self,
        factura_id: str,
        cedula_delivery: str,
        direccion: str,
        estado: int = 0
    ) -> str:
        """Registra una nueva entrega"""
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        entrega_id = self._generar_id_entrega()
        fecha_entrega = datetime.now()
        
        cursor = db.cursor()
        try:
            # Verificar que la factura existe
            cursor.execute("SELECT 1 FROM Venta WHERE ID_factura = %s", (factura_id,))
            if not cursor.fetchone():
                raise ValueError(f"La factura {factura_id} no existe")
            
            # Verificar que el delivery existe
            cursor.execute("SELECT 1 FROM Personal_delivery WHERE Cedula_delivery = %s", (cedula_delivery,))
            if not cursor.fetchone():
                raise ValueError(f"El delivery con cédula {cedula_delivery} no existe")
            
            # Verificar que no exista una entrega para esta factura
            cursor.execute(
                "SELECT 1 FROM Entrega WHERE ID_factura = %s LIMIT 1",
                (factura_id,)
            )
            if cursor.fetchone():
                raise ValueError(f"Ya existe una entrega para la factura {factura_id}")
            
            cursor.execute("""
                INSERT INTO Entrega (ID_entrega, ID_factura, Cedula_delivery, Estado_entrega, Direccion_entrega, Fecha_entrega)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (entrega_id, factura_id, cedula_delivery, estado, direccion, fecha_entrega))
            
            db.commit()
            return entrega_id
        except Exception:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def actualizar_estado(self, entrega_id: str, nuevo_estado: int) -> Dict[str, Any]:
        """Actualiza el estado de una entrega"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Entrega 
                SET Estado_entrega = %s 
                WHERE ID_entrega = %s
            """, (nuevo_estado, entrega_id))
            
            if cursor.rowcount == 0:
                return {"success": False, "error": "Entrega no encontrada"}
            
            db.commit()
            return {"success": True, "message": "Estado actualizado correctamente"}
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_estado: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    def actualizar_direccion(self, entrega_id: str, direccion: str) -> Dict[str, Any]:
        """Actualiza la dirección de una entrega"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return {"success": False, "error": "Error de conexión"}
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Entrega 
                SET Direccion_entrega = %s 
                WHERE ID_entrega = %s
            """, (direccion, entrega_id))
            
            if cursor.rowcount == 0:
                return {"success": False, "error": "Entrega no encontrada"}
            
            db.commit()
            return {"success": True, "message": "Dirección actualizada correctamente"}
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_direccion: {e}")
            return {"success": False, "error": str(e)}
        finally:
            cursor.close()
            db.close()
    
    def obtener_facturas_pendientes_entrega(self) -> List[Dict[str, Any]]:
        """Obtiene las facturas que no tienen entrega registrada"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    v.ID_factura AS factura_id,
                    v.ID_cliente AS cliente_id,
                    v.Fecha_venta,
                    COALESCE(pn.Nombre_cliente, '') AS cliente_nombre,
                    COALESCE(pn.Apellido_cliente, '') AS cliente_apellido,
                    c.Celular_cliente AS cliente_celular,
                    c.Direccion_cliente AS cliente_direccion,
                    c.Correo_cliente AS cliente_correo
                FROM Venta v
                LEFT JOIN Entrega e ON v.ID_factura = e.ID_factura
                LEFT JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                LEFT JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE e.ID_entrega IS NULL
                  AND v.ID_empleado IS NOT NULL
                ORDER BY v.Fecha_venta DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()