from app.models.database import conectar


class TradeIn(conectar):
    def obtener_tradeins(self):
        db = self.conexion1()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM tradein ORDER BY ID_Tradein DESC")
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()
