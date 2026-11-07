from __future__ import annotations
from app.models.database import conectar
from app.models.bitacora import Bitacora
from app.utils.validators import (
    validar_celular,
    validar_direccion_proveedor,
    validar_email,
    validar_limite_credito,
    validar_rif,
    validar_solo_letras_numeros,
)
import mysql.connector


class Proveedores:
    """Modelo para la tabla Proveedor"""
    
    def __init__(self, id_proveedor: int = 0, rif: str = "", nombre: str = "", 
                 tipo: str = "", celular: str = "", correo: str = "", 
                 direccion: str = "", limite_credito: int = 0, usuario_id: str = None):
        self.id_proveedor = id_proveedor
        self.rif = rif
        self.nombre = nombre
        self.tipo = tipo
        self.celular = celular
        self.correo = correo
        self.direccion = direccion
        self.limite_credito = limite_credito
        self.usuario_id = usuario_id
        self.__conexion_bd = conectar()

    def _conexion(self):
        return self.__conexion_bd.conexion1()

    def _siguiente_id(self) -> int:
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("SELECT COALESCE(MAX(ID_proveedor), 0) + 1 FROM Proveedor")
            row = cursor.fetchone()
            return int(row[0])
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def listar_proveedores(self, q: str | None = None) -> list:
        """Lista todos los proveedores, opcionalmente filtrados por búsqueda"""
        db = self._conexion()
        if not db:
            return []

        cursor = db.cursor(dictionary=True)
        try:
            where_sql = ""
            params = []
            if q:
                where_sql = "WHERE (Nombre_proveedor LIKE %s OR Rif_proveedor LIKE %s OR CAST(ID_proveedor AS CHAR) LIKE %s)"
                params = [f"%{q}%", f"%{q}%", f"%{q}%"]
            
            cursor.execute(f"""
                SELECT
                    ID_proveedor AS id,
                    Rif_proveedor AS rif,
                    Nombre_proveedor AS nombre,
                    Tipo_proveedor AS tipo,
                    Celular_proveedor AS celular,
                    Correo_proveedor AS correo,
                    Direccion_proveedor AS direccion,
                    Limite_credito AS limite_credito
                FROM Proveedor
                {where_sql}
                ORDER BY Nombre_proveedor ASC
            """, tuple(params))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def verificar_existencia(self) -> bool:
        """Verifica si un proveedor existe (usa el atributo id_proveedor)"""
        if self.id_proveedor == 0:
            return False
        db = self._conexion()
        if not db:
            return False
        cursor = db.cursor()
        try:
            cursor.execute("SELECT 1 FROM Proveedor WHERE ID_proveedor = %s LIMIT 1", (self.id_proveedor,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()

    def obtener_proveedor(self) -> dict | None:
        """Obtiene un proveedor por su ID (usa el atributo id_proveedor)"""
        if self.id_proveedor == 0:
            return None
            
        db = self._conexion()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    ID_proveedor AS id,
                    Rif_proveedor AS rif,
                    Nombre_proveedor AS nombre,
                    Tipo_proveedor AS tipo,
                    Celular_proveedor AS celular,
                    Correo_proveedor AS correo,
                    Direccion_proveedor AS direccion,
                    Limite_credito AS limite_credito
                FROM Proveedor
                WHERE ID_proveedor = %s
                LIMIT 1
            """, (self.id_proveedor,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    # ==================== MÉTODO CON STORED PROCEDURE ====================
    
    def obtener_proveedor_con_productos_procedure(self) -> dict:
        """
        Usa el stored procedure sp_obtener_proveedor_completo
        para obtener el proveedor y sus productos en una sola llamada
        """
        if self.id_proveedor == 0:
            return {"proveedor": None, "productos": [], "success": False, "error": "ID de proveedor no especificado"}
        
        db = self._conexion()
        if not db:
            return {"proveedor": None, "productos": [], "success": False, "error": "No se pudo conectar a la BD"}
        
        cursor = None
        try:
            cursor = db.cursor(dictionary=True)
            
            # Ejecutar el procedure
            cursor.callproc('sp_obtener_proveedor_completo', (self.id_proveedor,))
            
            proveedor = None
            productos = []
            result_count = 0
            
            # Iterar sobre los resultados
            for result in cursor.stored_results():
                rows = result.fetchall()
                result_count += 1
                
                if rows:
                    # Primer resultado: datos del proveedor
                    if result_count == 1:
                        proveedor = rows[0] if len(rows) == 1 else rows
                    # Segundo resultado: productos
                    elif result_count == 2:
                        productos = rows
            
            return {
                "proveedor": proveedor,
                "productos": productos,
                "success": True
            }
            
        except mysql.connector.Error as e:
            print(f"Error en procedure: {e}")
            return {
                "proveedor": None,
                "productos": [],
                "error": str(e),
                "success": False
            }
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    # ==================== FIN MÉTODO CON STORED PROCEDURE ====================

    def _validar_datos_basicos(self):
        self.rif = str(self.rif or "").strip() or None
        self.nombre = str(self.nombre or "").strip()
        self.tipo = str(self.tipo or "").strip() or None
        self.celular = str(self.celular or "").strip() or None
        self.correo = str(self.correo or "").strip() or None
        self.direccion = str(self.direccion or "").strip() or None

        if self.limite_credito in (None, ""):
            self.limite_credito = None
        else:
            try:
                self.limite_credito = int(self.limite_credito)
            except (TypeError, ValueError):
                raise ValueError("El límite de crédito debe ser numérico.")
            if self.limite_credito < 0:
                raise ValueError("El límite de crédito no puede ser negativo.")

        error_nombre = validar_solo_letras_numeros(self.nombre, 2, 60, "Nombre del proveedor")
        if error_nombre:
            raise ValueError(error_nombre)

        error_rif = validar_rif(self.rif, 8, 15, "RIF")
        if error_rif:
            raise ValueError(error_rif)

        error_celular = validar_celular(self.celular, 11, 11, "Teléfono")
        if error_celular:
            raise ValueError(error_celular)

        error_correo = validar_email(self.correo) if self.correo else None
        if error_correo:
            raise ValueError(error_correo)

        error_direccion = validar_direccion_proveedor(self.direccion, 100, "Dirección")
        if error_direccion:
            raise ValueError(error_direccion)

        error_limite = validar_limite_credito(self.limite_credito, "Límite de crédito")
        if error_limite:
            raise ValueError(error_limite)

    def _validar_productos_para_proveedor(self, productos):
        if productos in (None, ""):
            return []
        if not isinstance(productos, list):
            raise ValueError("Productos debe ser una lista.")

        productos_norm: list[dict] = []
        for item in productos:
            if not isinstance(item, dict):
                raise ValueError("Cada producto debe ser un objeto.")
            if "id_modelo" not in item:
                raise ValueError("id_modelo es obligatorio en productos.")

            id_modelo_val = str(item.get("id_modelo") or "").strip()
            if not id_modelo_val:
                raise ValueError("id_modelo es obligatorio en productos.")

            costo = item.get("costo")
            costo_val = None
            if costo not in (None, ""):
                try:
                    costo_val = int(costo)
                except (TypeError, ValueError):
                    raise ValueError("El costo debe ser numérico.")
                if costo_val < 0:
                    raise ValueError(f"El costo del producto '{id_modelo_val}' no puede ser negativo.")

            if self.limite_credito is not None and costo_val is not None and costo_val > self.limite_credito:
                raise ValueError(
                    f"El costo del producto ID '{id_modelo_val}' ({costo_val} Bs) no puede superar el límite de crédito del proveedor ({self.limite_credito} Bs)."
                )

            productos_norm.append({"id_modelo": id_modelo_val, "costo": costo_val})

        return productos_norm

    def crear_proveedor(self) -> int:
        """Crea un nuevo proveedor usando el stored procedure sp_registrar_proveedor."""
        self._validar_datos_basicos()

        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = None
        try:
            cursor = db.cursor(dictionary=True)

            # Validación extra del modelo: evitar duplicados por nombre y rif
            cursor.execute("""
                SELECT 1 FROM Proveedor
                WHERE LOWER(TRIM(Nombre_proveedor)) = LOWER(TRIM(%s))
                LIMIT 1
            """, (self.nombre,))
            if cursor.fetchone():
                raise ValueError(f"Ya existe un proveedor con el nombre '{self.nombre}'.")

            if self.rif:
                cursor.execute("""
                    SELECT 1 FROM Proveedor
                    WHERE LOWER(TRIM(Rif_proveedor)) = LOWER(TRIM(%s))
                    LIMIT 1
                """, (self.rif,))
                if cursor.fetchone():
                    raise ValueError(f"Ya existe un proveedor con el RIF '{self.rif}'.")

            cursor.callproc(
                'sp_registrar_proveedor',
                (
                    self.rif or '',
                    self.nombre,
                    self.tipo or '',
                    self.celular or '',
                    self.correo or '',
                    self.direccion or '',
                    self.limite_credito if self.limite_credito is not None else 0,
                    0,
                    '',
                    ''
                )
            )

            cursor.execute(
                "SELECT @_sp_registrar_proveedor_7 AS id_proveedor, @_sp_registrar_proveedor_8 AS estado, @_sp_registrar_proveedor_9 AS mensaje"
            )
            resultado = cursor.fetchone()

            if not resultado:
                raise RuntimeError("El procedimiento de registro no devolvió información.")

            self.id_proveedor = int(resultado['id_proveedor'])
            estado = resultado['estado']
            mensaje = resultado['mensaje']

            if not self.id_proveedor or estado != 'OK':
                raise ValueError(mensaje or "No se pudo registrar el proveedor.")

            db.commit()

            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear proveedor",
                    descripcion=f"Se creó el proveedor: {self.nombre} - RIF: {self.rif or 'N/A'} - Límite crédito: {self.limite_credito or 0}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Proveedores"
                )
                bitacora.registrar()

            return self.id_proveedor
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def actualizar_proveedor(self) -> bool:
        """Actualiza un proveedor existente usando los atributos de la instancia"""
        if self.id_proveedor == 0:
            raise ValueError("ID del proveedor es requerido para actualizar.")
        self._validar_datos_basicos()

        if self.limite_credito is not None:
            productos = self.listar_productos_por_proveedor() or []
            if productos:
                costo_maximo = max((p.get("costo") or 0) for p in productos)
                if self.limite_credito < costo_maximo:
                    raise ValueError(
                        f"El nuevo límite de crédito ({self.limite_credito} Bs) no puede ser menor que el costo del producto más caro que ya tiene asignado ({costo_maximo} Bs). Reduzca los costos primero o elimine productos."
                    )

        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE Proveedor
                SET
                    Rif_proveedor = %s,
                    Nombre_proveedor = %s,
                    Tipo_proveedor = %s,
                    Celular_proveedor = %s,
                    Correo_proveedor = %s,
                    Direccion_proveedor = %s,
                    Limite_credito = %s
                WHERE ID_proveedor = %s
            """, (self.rif or None, self.nombre, self.tipo or None, self.celular or None,
                  self.correo or None, self.direccion or None,
                  self.limite_credito or None, self.id_proveedor))
            db.commit()
            updated = cursor.rowcount > 0

            # Registrar en bitácora
            if updated and self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar proveedor",
                    descripcion=f"Se actualizó el proveedor ID: {self.id_proveedor} - Nuevo nombre: {self.nombre} - RIF: {self.rif or 'N/A'}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Proveedores"
                )
                bitacora.registrar()

            return updated
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def eliminar_proveedor(self) -> bool:
        """Elimina un proveedor usando el atributo id_proveedor"""
        if self.id_proveedor == 0:
            raise ValueError("ID del proveedor es requerido para eliminar.")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Proveedor WHERE ID_proveedor = %s", (self.id_proveedor,))
            db.commit()
            deleted = cursor.rowcount > 0
            
            # Registrar en bitácora
            if deleted and self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar proveedor",
                    descripcion=f"Se eliminó el proveedor ID: {self.id_proveedor} - Nombre: {self.nombre}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Proveedores"
                )
                bitacora.registrar()
            
            return deleted
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def tiene_relaciones_activas(self) -> tuple[bool, str]:
        """Verifica si el proveedor tiene relaciones activas en otros módulos"""
        if self.id_proveedor == 0:
            return True, "ID de proveedor no especificado"
        
        db = self._conexion()
        if not db:
            return True, "No se pudo conectar a la base de datos"
        
        cursor = db.cursor(dictionary=True)
        try:
            # Verificar órdenes de compra pendientes o completadas
            cursor.execute("""
                SELECT COUNT(*) as total FROM Orden_compra 
                WHERE ID_proveedor = %s 
                AND Estado_orden_compra IN ('Pendiente', 'Completada')
            """, (self.id_proveedor,))
            ordenes = cursor.fetchone()
            if ordenes and ordenes['total'] > 0:
                return True, f"No se puede eliminar el proveedor porque tiene {ordenes['total']} órdenes de compra asociadas."
            
            # Verificar productos suministrados
            cursor.execute("""
                SELECT COUNT(*) as total FROM Suministra 
                WHERE ID_proveedor = %s
            """, (self.id_proveedor,))
            suministros = cursor.fetchone()
            if suministros and suministros['total'] > 0:
                return True, f"No se puede eliminar el proveedor porque tiene {suministros['total']} productos asociados."
            
            return False, ""
        except Exception as e:
            print(f"Error verificando relaciones: {e}")
            return True, "Error al verificar relaciones del proveedor"
        finally:
            cursor.close()
            db.close()

    def obtener_detalle_relaciones(self) -> dict:
        """Obtiene el detalle de las relaciones activas del proveedor"""
        if self.id_proveedor == 0:
            return {}
        
        db = self._conexion()
        if not db:
            return {}
        
        cursor = db.cursor(dictionary=True)
        try:
            # Obtener órdenes de compra
            cursor.execute("""
                SELECT ID_orden_compra as id, Estado_orden_compra as estado, DATE(Fecha_orden_compra) as fecha
                FROM Orden_compra 
                WHERE ID_proveedor = %s 
                AND Estado_orden_compra IN ('Pendiente', 'Completada')
            """, (self.id_proveedor,))
            ordenes = cursor.fetchall()
            
            # Obtener productos suministrados
            cursor.execute("""
                SELECT 
                    s.ID_producto as id_modelo,
                    p.Nombre_producto as nombre,
                    s.Costo_producto as costo
                FROM Suministra s
                JOIN Producto p ON s.ID_producto = p.ID_producto
                WHERE s.ID_proveedor = %s
            """, (self.id_proveedor,))
            productos = cursor.fetchall()
            
            return {
                "ordenes": ordenes or [],
                "productos": productos or []
            }
        except Exception as e:
            print(f"Error obteniendo detalle de relaciones: {e}")
            return {}
        finally:
            cursor.close()
            db.close()

    def listar_productos_por_proveedor(self) -> list:
        """Lista los productos que suministra este proveedor"""
        if self.id_proveedor == 0:
            return []
        
        db = self._conexion()
        if not db:
            return []
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    s.ID_producto AS id_modelo,
                    p.Nombre_producto AS modelo_nombre,
                    ma.Nombre_marca AS marca_nombre,
                    cl.Nombre_Clase AS clase_nombre,
                    s.Costo_producto AS costo
                FROM Suministra s
                JOIN Producto p ON s.ID_producto = p.ID_producto
                JOIN Marca_producto ma ON p.ID_marca = ma.ID_marca
                JOIN Clase_producto cl ON p.ID_Clase = cl.ID_Clase
                WHERE s.ID_proveedor = %s
                ORDER BY CAST(cl.ID_Clase AS UNSIGNED) ASC, 
                         CAST(ma.ID_marca AS UNSIGNED) ASC, 
                         p.Nombre_producto ASC
            """, (self.id_proveedor,))
            return cursor.fetchall() or []
        finally:
            cursor.close()
            db.close()

    def upsert_producto_proveedor(self, id_modelo: str = None, costo: int | None = None) -> bool:
        """Inserta o actualiza un producto para este proveedor"""
        if self.id_proveedor == 0:
            raise ValueError("ID del proveedor es requerido")

        id_modelo = str(id_modelo or "").strip()
        if not id_modelo:
            raise ValueError("El modelo es obligatorio.")

        if costo not in (None, ""):
            try:
                costo = int(costo)
            except (TypeError, ValueError):
                raise ValueError("El costo debe ser numérico.")
            if costo < 0:
                raise ValueError("El costo no puede ser negativo.")

        proveedor = self.obtener_proveedor()
        limite_credito = proveedor.get("limite_credito") if proveedor else None
        if limite_credito is not None and costo is not None and costo > limite_credito:
            raise ValueError(
                f"El costo del producto ({costo} Bs) no puede superar el límite de crédito del proveedor ({limite_credito} Bs)."
            )

        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE Costo_producto = VALUES(Costo_producto)
            """, (self.id_proveedor, id_modelo, costo))
            db.commit()
            updated = cursor.rowcount > 0

            # Registrar en bitácora
            if updated and self.usuario_id:
                bitacora = Bitacora(
                    accion="Actualizar producto de proveedor",
                    descripcion=f"Se actualizó producto para proveedor ID: {self.id_proveedor} - Modelo ID: {id_modelo} - Costo: {costo}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Proveedores"
                )
                bitacora.registrar()

            return updated
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def eliminar_producto_proveedor(self, id_modelo: str = None) -> bool:
        """Elimina un producto de este proveedor"""
        if self.id_proveedor == 0:
            raise ValueError("ID del proveedor es requerido")
        if not id_modelo:
            raise ValueError("ID del modelo es requerido")
        
        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")
        
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute(
                "DELETE FROM Suministra WHERE ID_proveedor = %s AND ID_producto = %s",
                (self.id_proveedor, id_modelo)
            )
            db.commit()
            deleted = cursor.rowcount > 0
            
            # Registrar en bitácora
            if deleted and self.usuario_id:
                bitacora = Bitacora(
                    accion="Eliminar producto de proveedor",
                    descripcion=f"Se eliminó producto del proveedor ID: {self.id_proveedor} - Modelo ID: {id_modelo}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Proveedores"
                )
                bitacora.registrar()
            
            return deleted
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def crear_proveedor_con_productos(self, productos: list[dict]) -> int:
        """Crea un proveedor con sus productos iniciales en una transacción"""
        self._validar_datos_basicos()
        productos_validos = self._validar_productos_para_proveedor(productos)

        db = self._conexion()
        if not db:
            raise RuntimeError("No se pudo conectar a la base de datos.")

        cursor = None
        try:
            cursor = db.cursor()

            # Si no tiene ID o es 0, obtener el siguiente
            if self.id_proveedor == 0:
                self.id_proveedor = self._siguiente_id()

            # Insertar proveedor
            cursor.execute("""
                INSERT INTO Proveedor
                    (ID_proveedor, Rif_proveedor, Nombre_proveedor, Tipo_proveedor, Celular_proveedor,
                     Correo_proveedor, Direccion_proveedor, Limite_credito)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.id_proveedor, self.rif or None, self.nombre, self.tipo or None,
                  self.celular or None, self.correo or None,
                  self.direccion or None, self.limite_credito or None))

            # Insertar productos
            rows = []
            for item in productos_validos:
                id_modelo = item["id_modelo"]
                costo = item["costo"]
                rows.append((self.id_proveedor, str(id_modelo), costo))

            if rows:
                cursor.executemany("""
                    INSERT INTO Suministra (ID_proveedor, ID_producto, Costo_producto)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE Costo_producto = VALUES(Costo_producto)
                """, rows)

            db.commit()

            # Registrar en bitácora
            if self.usuario_id:
                bitacora = Bitacora(
                    accion="Crear proveedor",
                    descripcion=f"Se creó el proveedor: {self.nombre} - RIF: {self.rif or 'N/A'} - Límite crédito: {self.limite_credito or 0} - Productos: {len(productos_validos)}",
                    usuario_id=self.usuario_id,
                    modulo_nombre="Proveedores"
                )
                bitacora.registrar()

            return self.id_proveedor
        except Exception as e:
            if db:
                db.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()