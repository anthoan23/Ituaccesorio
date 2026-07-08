import os
import json
import google.generativeai as genai  # Cambio aquí
from google.generativeai import types  # Cambio aquí
from dotenv import load_dotenv

load_dotenv()

class IAService:
    def __init__(self):
        # Obtener la API key desde variables de entorno
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en variables de entorno. Por favor, configura tu API key en el archivo .env")
        
        # Configurar la API key
        genai.configure(api_key=api_key)  # Cambio aquí
        
        # Inicializa el cliente de Gemini
        self.client = genai.GenerativeModel("gemini-2.5-flash")  # Cambio aquí
        self.model_name = "gemini-2.5-flash"

    def determinar_tecnico_ideal(self, datos_orden, datos_tecnicos):
        """
        Analiza el problema del equipo y los técnicos disponibles usando Gemini
        para retornar el más apto y desocupado en formato JSON.
        """
        # Validar que los datos de entrada sean válidos
        if not datos_orden or not datos_tecnicos:
            return {
                "error": True,
                "message": "Datos de orden o técnicos incompletos"
            }

        # Filtrado de datos de la orden para ahorrar tokens
        orden_info = datos_orden.get('orden', {})
        detalles_reparacion = {
            "id_orden": orden_info.get("id_orden"),
            "descripcion_problema": orden_info.get("descripcion_reparacion", "No especificada"),
            "producto": orden_info.get("nombre_producto", "No especificado"),
            "clase": orden_info.get("clase_producto", "No especificada"),
            "marca": orden_info.get("marca_producto", "No especificada")
        }

        # Validar que tengamos técnicos para analizar
        tecnicos = datos_tecnicos.get('tecnicos', [])
        if not tecnicos:
            return {
                "error": True,
                "message": "No hay técnicos disponibles para analizar"
            }

        # Construcción del prompt
        prompt = f"""
        Actúa como un asignador inteligente de un taller de servicio técnico. 
        Tu objetivo es analizar los detalles de un ticket de reparación y la lista de técnicos disponibles para decidir quién es el más adecuado basándote en dos factores principales:
        1. Especialidad y nivel de capacitación acorde al tipo de producto/problema (Aptitud).
        2. Carga de trabajo actual ('total_ordenes_asignadas'), priorizando al más desocupado en caso de empate técnico.

        DATOS DE LA ORDEN DE REPARACIÓN:
        {json.dumps(detalles_reparacion, indent=2, ensure_ascii=False)}

        LISTA DE TÉCNICOS DISPONIBLES Y CARGA DE TRABAJO:
        {json.dumps(tecnicos, indent=2, ensure_ascii=False)}

        INSTRUCCIONES DE RESPUESTA:
        Devuelve una respuesta estructurada en formato JSON válido que contenga EXACTAMENTE las siguientes llaves:
        - "id_tecnico_elegido": El ID del empleado seleccionado (entero o string).
        - "nombre_cargo": El cargo del técnico.
        - "razon_seleccion": Una explicación concisa de por qué es el más apto y desocupado para este caso en particular.
        - "nivel_urgencia_estimado": Tu análisis de qué tan compleja es la reparación (Bajo, Medio, Alto).

        IMPORTANTE: 
        - Solo debes devolver el JSON válido, sin texto adicional.
        - Si no encuentras un técnico adecuado, selecciona el que tenga menor carga de trabajo.
        - La respuesta debe ser en español.
        """

        try:
            # Llamada a la API de Gemini
            respuesta = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=1024,
                    response_mime_type="application/json"
                )
            )
            
            # Verificar que la respuesta no esté vacía
            if not respuesta.text:
                return {
                    "error": True,
                    "message": "La respuesta de Gemini está vacía"
                }
            
            # Convertimos el texto JSON devuelto por Gemini en un diccionario de Python
            decision_json = json.loads(respuesta.text)
            
            # Validar que la respuesta tenga los campos esperados
            campos_requeridos = ['id_tecnico_elegido', 'nombre_cargo', 'razon_seleccion', 'nivel_urgencia_estimado']
            for campo in campos_requeridos:
                if campo not in decision_json:
                    return {
                        "error": True,
                        "message": f"La respuesta de Gemini no contiene el campo requerido: {campo}"
                    }
            
            return decision_json

        except json.JSONDecodeError as e:
            # Error al parsear el JSON
            return {
                "error": True,
                "message": f"Error al parsear la respuesta de Gemini: {str(e)}",
                "respuesta_raw": respuesta.text if 'respuesta' in locals() else None
            }
        except Exception as e:
            # Fallback en caso de que ocurra un error de cuota (Rate Limit) o de red
            return {
                "error": True,
                "message": f"No se pudo procesar la decisión por Gemini: {str(e)}"
            }

    def determinar_tecnico_ideal_fallback(self, datos_tecnicos):
        """
        Método de fallback que selecciona el técnico con menor carga de trabajo
        en caso de que la IA falle.
        """
        tecnicos = datos_tecnicos.get('tecnicos', [])
        if not tecnicos:
            return {
                "error": True,
                "message": "No hay técnicos disponibles"
            }
        
        # Ordenar por carga de trabajo (menor primero)
        tecnicos_ordenados = sorted(tecnicos, key=lambda x: x.get('total_ordenes_asignadas', 0))
        tecnico_elegido = tecnicos_ordenados[0] if tecnicos_ordenados else None
        
        if not tecnico_elegido:
            return {
                "error": True,
                "message": "No se pudo seleccionar ningún técnico"
            }
        
        return {
            "id_tecnico_elegido": tecnico_elegido.get('id_empleado'),
            "nombre_cargo": tecnico_elegido.get('cargo', 'Técnico'),
            "razon_seleccion": f"Seleccionado por tener la menor carga de trabajo ({tecnico_elegido.get('total_ordenes_asignadas', 0)} órdenes asignadas)",
            "nivel_urgencia_estimado": "Medio",
            "fallback": True
        }