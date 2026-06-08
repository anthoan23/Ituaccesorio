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
                try:
                    num = int(ultimo_id[3:]) + 1
                except ValueError:
                    num = 1
            else:
                num = 1
            
            return f"ENT{num:07d}"
        finally:
            cursor.close()
            db.close()
    
    def listar_entregas(self) -> List[Dict[str, Any]]:
        """Lista todas las entregas"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_entrega AS id,
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
                ORDER BY e.Fecha_entrega DESC
            """)
            
            entregas = cursor.fetchall()
            
            # Convertir estado a texto para mostrar
            for entrega in entregas:
                estado_val = entrega.get("estado", 0)
                if estado_val == 0:
                    entrega["estado_texto"] = "Pendiente"
                    entrega["estado_clase"] = "estado-pendiente"
                elif estado_val == 1:
                    entrega["estado_texto"] = "En camino"
                    entrega["estado_clase"] = "estado-camino"
                elif estado_val == 2:
                    entrega["estado_texto"] = "Entregado"
                    entrega["estado_clase"] = "estado-entregado"
                elif estado_val == 3:
                    entrega["estado_texto"] = "Cancelado"
                    entrega["estado_clase"] = "estado-cancelado"
                else:
                    entrega["estado_texto"] = "Programado"
                    entrega["estado_clase"] = "estado-programado"
            
            return entregas
        except Exception as e:
            print(f"Error en listar_entregas: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def obtener_entrega_por_id(self, entrega_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una entrega por su ID"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return None
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    e.ID_entrega AS id,
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
                    entrega["estado_texto"] = "Pendiente"
                    entrega["estado_clase"] = "estado-pendiente"
                elif estado_val == 1:
                    entrega["estado_texto"] = "En camino"
                    entrega["estado_clase"] = "estado-camino"
                elif estado_val == 2:
                    entrega["estado_texto"] = "Entregado"
                    entrega["estado_clase"] = "estado-entregado"
                elif estado_val == 3:
                    entrega["estado_texto"] = "Cancelado"
                    entrega["estado_clase"] = "estado-cancelado"
                else:
                    entrega["estado_texto"] = "Programado"
                    entrega["estado_clase"] = "estado-programado"
            
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
            cursor.execute("SELECT 1 FROM Venta WHERE ID_factura = %s", (factura_id,))
            if not cursor.fetchone():
                raise ValueError(f"La factura {factura_id} no existe")
            
            cursor.execute("SELECT 1 FROM Personal_delivery WHERE Cedula_delivery = %s", (cedula_delivery,))
            if not cursor.fetchone():
                raise ValueError(f"El delivery con cédula {cedula_delivery} no existe")
            
            cursor.execute("""
                INSERT INTO Entrega (ID_entrega, ID_factura, Cedula_delivery, Estado_entrega, Direccion_entrega, Fecha_entrega)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (entrega_id, factura_id, cedula_delivery, estado, direccion, fecha_entrega))
            
            db.commit()
            return entrega_id
        except Exception as e:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def actualizar_entrega(self, entrega_id: str, direccion: str, estado: int) -> str:
        """Actualiza una entrega existente"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos"
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Entrega 
                SET Direccion_entrega = %s, Estado_entrega = %s
                WHERE ID_entrega = %s
            """, (direccion, estado, entrega_id))
            
            if cursor.rowcount == 0:
                return "Entrega no encontrada"
            
            db.commit()
            return "Entrega actualizada exitosamente"
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_entrega: {e}")
            return f"Error al actualizar: {e}"
        finally:
            cursor.close()
            db.close()
    
    def eliminar_entrega(self, entrega_id: str) -> str:
        """Elimina una entrega"""
        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos"
        
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Entrega WHERE ID_entrega = %s", (entrega_id,))
            
            if cursor.rowcount == 0:
                return "Entrega no encontrada"
            
            db.commit()
            return "Entrega eliminada exitosamente"
        except Exception as e:
            db.rollback()
            print(f"Error en eliminar_entrega: {e}")
            return f"Error al eliminar: {e}"
        finally:
            cursor.close()
            db.close()
    
    def obtener_facturas_pendientes(self) -> List[Dict[str, Any]]:
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
                    c.Direccion_cliente AS cliente_direccion
                FROM Venta v
                LEFT JOIN Entrega e ON v.ID_factura = e.ID_factura
                INNER JOIN Persona_natural pn ON v.ID_cliente = pn.ID_cliente
                INNER JOIN Cliente c ON v.ID_cliente = c.ID_cliente
                WHERE e.ID_entrega IS NULL
                ORDER BY v.Fecha_venta DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_facturas_pendientes: {e}")
            return []
        finally:
            cursor.close()
            db.close()