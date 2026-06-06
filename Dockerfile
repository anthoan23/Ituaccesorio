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

# Ejecutamos el archivo de entrada
CMD ["python", "run.py"]

# Esto solo lo vamos a poner cuando nos toque subir a produccion, para que en desarrollo podamos usar el modo debug de Flask y no tener que reiniciar el contenedor cada vez que hagamos un cambio
# y funcionen las notificaciones en tiempo real sin tener que configurar un bus de mensajes externo como Redis o RabbitMQ
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--worker-class", "gthread", "run:app"]
