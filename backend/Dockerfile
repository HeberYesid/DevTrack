# Multi-stage build para optimización

# ======================================
# Stage 1: Builder
# ======================================
FROM python:3.11-slim as builder

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar solo requirements primero (para cache de layers)
COPY requirements.txt .

# Instalar dependencias de Python en un directorio local del usuario
RUN pip install --user --no-warn-script-location -r requirements.txt

# ======================================
# Stage 2: Runtime
# ======================================
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    TZ=America/Bogota

# Instalar dependencias runtime (solo las necesarias para ejecutar)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Configurar timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias de Python del builder stage
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY . .

# Copiar y dar permisos a scripts de inicialización
COPY entrypoint.sh wait-for-it.sh ./
RUN chmod +x entrypoint.sh wait-for-it.sh

# Crear directorios para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/mediafiles

# Exponer puerto
EXPOSE 8000

# Health check para verificar que el servicio está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8000/api/ || exit 1

# Usar entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

# Comando por defecto (Gunicorn para producción)
CMD ["gunicorn", "config.wsgi:application", "--config", "gunicorn.conf.py"]
