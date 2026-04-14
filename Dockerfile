FROM python:3.12-slim

WORKDIR /app

# Instalamos Flask
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el proyecto al contenedor
COPY . .

# Exponemos el puerto
EXPOSE 5000

# Ejecutamos el archivo de entrada
CMD ["python", "run.py"]