# 1. Imagen base (por ejemplo, Python oficial)
FROM python:3.11-slim

# 2. Establece un directorio dentro del contenedor
WORKDIR /app

# 3. Instala dependencias del sistema necesarias para ffmpeg y otras herramientas
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Copia los archivos de requisitos primero (para aprovechar la caché de Docker)
COPY requirements.txt /app/

# 5. Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia el resto de los archivos de la aplicación
COPY . /app

# 7. Crea las carpetas necesarias para la aplicación
RUN mkdir -p RAG/Base_de_Conocimientos

# 8. Expone el puerto que usa Streamlit (8501 por defecto)
EXPOSE 8501

# 9. Comando para ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]