FROM python:3.12-slim

WORKDIR /app

# Instalamos Flask
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el proyecto al contenedor
COPY . .

# El bus de notificaciones vive en memoria, asi que en produccion conviene
# un solo worker de Gunicorn y varios hilos. Ejemplo:
# gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 8 --worker-class gthread run:app
# Con mas de un worker, cada proceso tendria su propia memoria y el SSE no
# veria las notificaciones que se generaron en otro worker.

# Exponemos el puerto
EXPOSE 5000

# Ejecutamos el archivo de entrada con Gunicorn: 1 solo worker porque el bus de
# notificaciones vive en memoria (con mas workers el SSE se rompe) y varios hilos.
# Timeout alto porque los endpoints de IA (Gemini) pueden tardar mas de 30s.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--worker-class", "gthread", "--timeout", "120", "run:app"]
