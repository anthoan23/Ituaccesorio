from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import (
    validar_numero,
    validar_texto_numero,
    validar_sin_caracteres_especiales,
    validar_codigo_factura,
    validar_numero_entero,
)
from datetime import datetime
from typing import Dict, Any, Optional, List


class EntregaModel:
    """Modelo para operaciones de entregas"""

    ESTADOS_VALIDOS = (0, 1, 2, 3)  # Pendiente, En camino, Entregado, Cancelado

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

    # ==================== VALIDACIONES ====================

    def _validar_estado(self) -> Optional[str]:
        if self.estado is None:
            return "El estado es obligatorio."
        # Entrega.Estado_entrega int
        error = validar_numero_entero(self.estado, "Estado", min_valor=0, max_valor=3)
        if error:
            return error
        try:
            estado_int = int(self.estado)
        except (ValueError, TypeError):
            return "El estado debe ser un número entero válido."
        if estado_int not in self.ESTADOS_VALIDOS:
            return "El estado debe ser 0 (Pendiente), 1 (En camino), 2 (Entregado) o 3 (Cancelado)."
        self.estado = estado_int
        return None

    def _validar_datos_registro(self) -> Optional[str]:
        """Valida los datos para registrar una entrega nueva."""
        factura_id = str(self.factura_id).strip() if self.factura_id is not None else ""
        if not factura_id:
            return "La factura es obligatoria."
        # Entrega.ID_factura varchar(20); formato FAC-YYYYMM-XXXXXX
        error = validar_codigo_factura(factura_id, 1, 20, "Factura")
        if error:
            return error
        self.factura_id = factura_id

        cedula_delivery = str(self.cedula_delivery).strip() if self.cedula_delivery is not None else ""
        if not cedula_delivery:
            return "El delivery es obligatorio."
        # Entrega.Cedula_delivery varchar(15)
        error = validar_numero(cedula_delivery, 6, 15, "Cédula del delivery")
        if error:
            return error
        self.cedula_delivery = cedula_delivery

        direccion = str(self.direccion).strip() if self.direccion is not None else ""
        if not direccion:
            return "La dirección es obligatoria."
        # Entrega.Direccion_entrega varchar(60)
        error = validar_sin_caracteres_especiales(direccion, 1, 60, "Dirección", permitir_espacios=True)
        if error:
            return error
        self.direccion = direccion

        error = self._validar_estado()
        if error:
            return error

        return None

    def _validar_datos_actualizacion(self) -> Optional[str]:
        """Valida los datos para actualizar una entrega."""
        entrega_id = str(self.entrega_id).strip() if self.entrega_id is not None else ""
        if not entrega_id:
            return "ID de entrega no especificado."
        # Entrega.ID_entrega varchar(10)
        error = validar_texto_numero(entrega_id, 1, 10, "ID de entrega")
        if error:
            return error
        self.entrega_id = entrega_id

        direccion = str(self.direccion).strip() if self.direccion is not None else ""
        if not direccion:
            return "La dirección es obligatoria."
        # Entrega.Direccion_entrega varchar(60)
        error = validar_sin_caracteres_especiales(direccion, 1, 60, "Dirección", permitir_espacios=True)
        if error:
            return error
        self.direccion = direccion

        error = self._validar_estado()
        if error:
            return error

        return None

    # ==================== CONSULTAS ====================

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

        error = validar_texto_numero(str(entrega).strip(), 1, 10, "ID de entrega")
        if error:
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

    # ==================== MUTACIONES ====================

    def registrar_entrega(self) -> str:
        """Registra una nueva entrega"""
        error = self._validar_datos_registro()
        if error:
            raise ValueError(error)

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
        error = self._validar_datos_actualizacion()
        if error:
            return error

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
        entrega_id = str(self.entrega_id).strip() if self.entrega_id is not None else ""
        if not entrega_id:
            return "ID de entrega no especificado."
        # Entrega.ID_entrega varchar(10)
        error = validar_texto_numero(entrega_id, 1, 10, "ID de entrega")
        if error:
            return error
        self.entrega_id = entrega_id

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