from __future__ import annotations
from app.models.database import conectar


class Orden_servicio():
    def __init__(self, ID_orden_e: int, Estado_orden_servicio: str, Descripcion_reparacion: str, Costo_reparacion: float, Nota_orden_servicio: str, Fecha_entrada, Fecha_salida,ID_foto_orden_servicio: str, Foto_orden_servicio: str):
        self.ID_orden_e = ID_orden_e
        self.Estado_orden_servicio = Estado_orden_servicio
        self.Descripcion_reparacion = Descripcion_reparacion
        self.Costo_reparacion = Costo_reparacion
        self.Nota_orden_servicio = Nota_orden_servicio
        self.Fecha_ingreso = Fecha_entrada
        self.Fecha_salida = Fecha_salida
        self.ID_foto_orden_servicio = ID_foto_orden_servicio
        self.Foto_orden_servicio = Foto_orden_servicio

        self._conexion = conectar()

    def listar_ordenes_servicio(self):
        db = self._conexion.conexion1()
        if not db:
            mensaje = "Error al conectar con la base de datos."
            return mensaje
        
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    os.ID_orden_servicio AS id_orden,
                    os.Estado_orden_servicio AS estado,
                    os.Descripcion_reparacion AS descripcion,
                    os.Costo_reparacion AS costo,
                    os.Nota_orden_servicio AS nota,
                    os.Fecha_entrada AS fecha_e,
                    os.Fecha_salida AS fecha_s
                FROM Orden_servicio os
                JOIN Equipo e ON os.ID_equipo = e.ID_equipo
                JOIN Fotos_orden_servicio fot ON os.ID_orden_servicio = fot.ID_orden_servicio
                ORDER BY os.ID_orden_servicio DESC
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar órdenes de servicio: {e}")
            return []
        finally:
            cursor.close()
            db.close()
    
    def verificar_foto_existe_por_ruta(self) -> bool:
        ruta_foto = self.Foto_orden_servicio.strip()
     
        """Verifica si una foto existe por su ruta o nombre de archivo"""
        db = self.__conexion_bd.conexion1()
        if not db:
         return False

        cursor = db.cursor()
        try:
            cursor.execute(
            "SELECT 1 FROM Fotos_orden_servicio WHERE Ruta_foto = %s LIMIT 1",
            (ruta_foto.strip(),),
        )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            db.close()



    def agregar_foto_orden_servicio(self) -> str:
        id_foto = self.ID_foto_orden_servicio.strip()
        ruta_foto = self.Foto_orden_servicio.strip()

        if len(id_foto) > 10:
            return "El ID de la foto no puede tener más de 10 caracteres."
        
        if len(ruta_foto) > 255:
            return "La ruta de la foto no puede tener más de 255 caracteres."
        
        if self.verificar_foto_existe_por_ruta():
            mensaje = f"La foto '{ruta_foto}' ya existe."
            return mensaje

        db = self._conexion.conexion()
        if not db:
            mesaje = "Error al conectar con la base de datos."
            return mesaje
        
        cursor = db.cursor()
        try:
            sql = 'CALL Agregar_foto(%s, %s)' 
            cursor.execute(sql, (ruta_foto))
            while cursor.nextset():
                pass
            db.commit()
            mensaje = f"Foto agregada exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al agregar la foto: {e}")
            db.rollback()
            mensaje = "Error al agregar la foto."
            return mensaje

        finally:
            cursor.close()
            db.close()    
           
    def eliminar_foto_orden_servicio(self) -> str:
        id_foto = self.ID_foto_orden_servicio.strip()

        if not id_foto:
            mensaje = "El ID de la foto es obligatorio."
            return mensaje
        
        if not self.verificar_foto_existe_por_id():
            mensaje = f"No se encontró una foto con ID {id_foto} para eliminar."
            return mensaje
        
        db = self._conexion.conexion()
        if not db:
            mensaje = "Error al conectar con la base de datos."
            return mensaje
        
        cursor = db.cursor()
        try:
            sql = "DELETE FROM Fotos_orden_servicio WHERE ID_foto_orden_servicio = %s"
            cursor.execute(sql, (id_foto,))
            db.commit()
            mensaje = f"La foto con ID {id_foto} se eliminó exitosamente."
            return mensaje
        except Exception as e:
            print(f"Error al eliminar la foto: {e}")
            db.rollback()
            mensaje = "Error al eliminar la foto."
            return mensaje
        finally:
            cursor.close()
            db.close()
