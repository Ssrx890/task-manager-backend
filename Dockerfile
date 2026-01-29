# 1. Usamos una imagen de Python ligera (slim)
FROM python:3.11-slim

# 2. Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /code

# 4. Instalamos dependencias del sistema necesarias para algunas librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiamos e instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copiamos todo el código de nuestra carpeta 'app'
COPY ./app ./app

# 7. Exponemos el puerto donde corre FastAPI
EXPOSE 8000

# 8. Comando para arrancar la app en producción (usando 4 trabajadores para velocidad)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]