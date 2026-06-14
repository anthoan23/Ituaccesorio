from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from datetime import datetime
from typing import Dict, Any, Optional, List


class EntregaModel:
    """Modelo para operaciones de entregas"""
    
    def __init__(self, entrega_id: str = None, factura_id: str = None, 
                 cedula_delivery: str = None, direccion: str = None, 
                 estado: int = 0, usuario_id: str = None):
        self.entrega_id = entrega_id
        self.factura_id = factura_id
        self.cedula_delivery = cedula_delivery
        self.direccion = direccion
        self.estado = estado
        self.usuario_id = usuario_id
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
    
    def obtener_entrega_por_id(self, entrega_id: str = None) -> Optional[Dict[str, Any]]:
        """Obtiene una entrega por su ID"""
        entrega = entrega_id or self.entrega_id
        if not entrega:
            return None
        
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
            """, (entrega,))
            
            resultado = cursor.fetchone()
            if resultado:
                estado_val = resultado.get("estado", 0)
                if estado_val == 0:
                    resultado["estado_texto"] = "Pendiente"
                    resultado["estado_clase"] = "estado-pendiente"
                elif estado_val == 1:
                    resultado["estado_texto"] = "En camino"
                    resultado["estado_clase"] = "estado-camino"
                elif estado_val == 2:
                    resultado["estado_texto"] = "Entregado"
                    resultado["estado_clase"] = "estado-entregado"
                elif estado_val == 3:
                    resultado["estado_texto"] = "Cancelado"
                    resultado["estado_clase"] = "estado-cancelado"
                else:
                    resultado["estado_texto"] = "Programado"
                    resultado["estado_clase"] = "estado-programado"
            
            return resultado
        finally:
            cursor.close()
            db.close()
    
    def registrar_entrega(self) -> str:
        """Registra una nueva entrega"""
        if not self.factura_id:
            raise ValueError("La factura es obligatoria")
        if not self.cedula_delivery:
            raise ValueError("El delivery es obligatorio")
        if not self.direccion:
            raise ValueError("La dirección es obligatoria")
        
        db = self.__conexion_bd.conexion1()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos")
        
        entrega_id = self._generar_id_entrega()
        fecha_entrega = datetime.now()
        
        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Venta WHERE ID_factura = %s", (self.factura_id,))
            if not cursor.fetchone():
                raise ValueError(f"La factura {self.factura_id} no existe")
            
            cursor.execute("SELECT 1 FROM Personal_delivery WHERE Cedula_delivery = %s", (self.cedula_delivery,))
            if not cursor.fetchone():
                raise ValueError(f"El delivery con cédula {self.cedula_delivery} no existe")
            
            cursor.execute("""
                INSERT INTO Entrega (ID_entrega, ID_factura, Cedula_delivery, Estado_entrega, Direccion_entrega, Fecha_entrega)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (entrega_id, self.factura_id, self.cedula_delivery, self.estado, self.direccion, fecha_entrega))
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Registrar entrega",
                    descripcion=f"Se registró la entrega ID: {entrega_id} para factura: {self.factura_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                )
                bitacora.registrar()
            
            self.entrega_id = entrega_id
            return entrega_id
        except Exception as e:
            db.rollback()
            raise
        finally:
            cursor.close()
            db.close()
    
    def actualizar_entrega(self) -> str:
        """Actualiza una entrega existente"""
        if not self.entrega_id:
            return "ID de entrega no especificado"
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos"
        
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE Entrega 
                SET Direccion_entrega = %s, Estado_entrega = %s
                WHERE ID_entrega = %s
            """, (self.direccion, self.estado, self.entrega_id))
            
            if cursor.rowcount == 0:
                return "Entrega no encontrada"
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar entrega",
                    descripcion=f"Se actualizó la entrega ID: {self.entrega_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                )
                bitacora.registrar()
            
            return "Entrega actualizada exitosamente"
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_entrega: {e}")
            return f"Error al actualizar: {e}"
        finally:
            cursor.close()
            db.close()
    
    def eliminar_entrega(self) -> str:
        """Elimina una entrega"""
        if not self.entrega_id:
            return "ID de entrega no especificado"
        
        db = self.__conexion_bd.conexion1()
        if not db:
            return "Error al conectar a la base de datos"
        
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM Entrega WHERE ID_entrega = %s", (self.entrega_id,))
            
            if cursor.rowcount == 0:
                return "Entrega no encontrada"
            
            db.commit()
            
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar entrega",
                    descripcion=f"Se eliminó la entrega ID: {self.entrega_id}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Entregas"
                )
                bitacora.registrar()
            
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