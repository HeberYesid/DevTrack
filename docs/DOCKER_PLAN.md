# 🐳 Plan de Contenerización de DevTrack

**Fecha:** 21 de Octubre, 2025  
**Objetivo:** Contenerizar la aplicación DevTrack para facilitar despliegue y desarrollo

---

## 📋 Tabla de Contenidos

1. [Objetivos](#objetivos)
2. [Arquitectura de Contenedores](#arquitectura-de-contenedores)
3. [Estructura de Archivos](#estructura-de-archivos)
4. [Plan de Implementación](#plan-de-implementación)
5. [Archivos a Crear](#archivos-a-crear)
6. [Configuración de Entornos](#configuración-de-entornos)
7. [Scripts de Automatización](#scripts-de-automatización)
8. [Testing y Validación](#testing-y-validación)
9. [Despliegue en Producción](#despliegue-en-producción)
10. [Checklist de Implementación](#checklist-de-implementación)

---

## 🎯 Objetivos

### Objetivos Principales:

1. ✅ **Portabilidad:** Mismo entorno en todas las máquinas (desarrollo, staging, producción)
2. ✅ **Simplicidad:** Setup en minutos con un solo comando
3. ✅ **Aislamiento:** Cada servicio en su propio contenedor
4. ✅ **Escalabilidad:** Fácil escalar servicios independientemente
5. ✅ **Reproducibilidad:** Eliminar "funciona en mi máquina"

### Beneficios Específicos:

- 🔧 **Para Desarrollo:**
  - No más problemas con versiones de Python/Node.js
  - No más problemas con PowerShell ExecutionPolicy
  - Setup instantáneo para nuevos desarrolladores
  
- 🚀 **Para Producción:**
  - Despliegue consistente y confiable
  - Fácil rollback a versiones anteriores
  - Monitoreo y logs centralizados

---

## 🏗️ Arquitectura de Contenedores

### Servicios Propuestos:

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │  Frontend   │    │  Backend    │    │   MySQL     │    │
│  │   (React)   │◄───┤  (Django)   │◄───┤  Database   │    │
│  │  Port: 5173 │    │  Port: 8000 │    │  Port: 3306 │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│        │                    │                   │           │
│        │                    │                   │           │
│  ┌─────┴────────────────────┴───────────────────┴─────┐    │
│  │              Docker Network (devtrack-net)          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Volumes (Persistent Storage)              │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │  • mysql-data (Base de datos)                       │    │
│  │  • static-files (Archivos estáticos Django)         │    │
│  │  • media-files (Uploads de usuarios)                │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Características por Servicio:

#### 1. **Frontend (React + Vite)**
- **Base Image:** `node:18-alpine`
- **Puerto:** 5173
- **Build:** Multi-stage (desarrollo y producción)
- **Volúmenes:** 
  - Código fuente (desarrollo)
  - node_modules (optimización)

#### 2. **Backend (Django)**
- **Base Image:** `python:3.11-slim`
- **Puerto:** 8000
- **Servidor:** Gunicorn (producción) / runserver (desarrollo)
- **Volúmenes:**
  - Código fuente (desarrollo)
  - Archivos estáticos
  - Media uploads

#### 3. **Database (MySQL)**
- **Base Image:** `mysql:8.0`
- **Puerto:** 3306
- **Volúmenes:**
  - mysql-data (persistencia)
- **Inicialización:** Scripts SQL automáticos

#### 4. **Nginx (Opcional - Producción)**
- **Base Image:** `nginx:alpine`
- **Puerto:** 80, 443
- **Función:** Reverse proxy + servir estáticos

---

## 📁 Estructura de Archivos

```
DevTrack/
├── docker-compose.yml              # Orquestación principal
├── docker-compose.dev.yml          # Overrides para desarrollo
├── docker-compose.prod.yml         # Overrides para producción
├── .dockerignore                   # Archivos a ignorar
├── .env.docker.example             # Variables de entorno ejemplo
│
├── backend/
│   ├── Dockerfile                  # Imagen del backend
│   ├── Dockerfile.dev              # Imagen para desarrollo
│   ├── requirements.txt
│   ├── requirements.dev.txt        # Dependencias de desarrollo
│   ├── entrypoint.sh              # Script de inicialización
│   ├── wait-for-it.sh             # Esperar por MySQL
│   └── gunicorn.conf.py           # Configuración de Gunicorn
│
├── frontend/
│   ├── Dockerfile                  # Imagen del frontend
│   ├── Dockerfile.dev              # Imagen para desarrollo
│   ├── nginx.conf                  # Configuración de Nginx
│   └── package.json
│
├── nginx/
│   ├── Dockerfile                  # Nginx para producción
│   ├── nginx.conf                  # Configuración principal
│   └── default.conf                # Virtual host config
│
├── scripts/
│   ├── docker-dev.sh              # Levantar desarrollo
│   ├── docker-prod.sh             # Levantar producción
│   ├── docker-test.sh             # Ejecutar tests
│   └── docker-clean.sh            # Limpiar contenedores
│
└── docs/
    ├── DOCKER_PLAN.md             # Este documento
    ├── DOCKER_SETUP.md            # Guía de uso
    └── DOCKER_TROUBLESHOOTING.md  # Solución de problemas
```

---

## 📝 Plan de Implementación

### Fase 1: Preparación (1-2 horas)

**Tareas:**
1. ✅ Crear `.dockerignore` en raíz, backend y frontend
2. ✅ Crear plantillas de archivos `.env`
3. ✅ Documentar dependencias del sistema
4. ✅ Revisar y actualizar `requirements.txt`

**Entregables:**
- `.dockerignore` configurado
- `.env.docker.example` creado
- Documentación de dependencias

---

### Fase 2: Backend - Dockerfile (2-3 horas)

**Tareas:**
1. ✅ Crear `backend/Dockerfile` (multi-stage build)
2. ✅ Crear `backend/Dockerfile.dev`
3. ✅ Crear `backend/entrypoint.sh`
4. ✅ Crear `backend/wait-for-it.sh`
5. ✅ Configurar Gunicorn
6. ✅ Ajustar `settings.py` para Docker

**Consideraciones:**
- Usar Python 3.11-slim para menor tamaño
- Separar dependencias de desarrollo y producción
- Configurar timezone America/Bogota
- Instalar mysqlclient correctamente
- Health checks para el contenedor

**Entregables:**
- Dockerfile funcional para backend
- Scripts de inicialización
- Configuración de Gunicorn

---

### Fase 3: Frontend - Dockerfile (2-3 horas)

**Tareas:**
1. ✅ Crear `frontend/Dockerfile` (multi-stage build)
2. ✅ Crear `frontend/Dockerfile.dev`
3. ✅ Configurar Nginx para servir React SPA
4. ✅ Optimizar build de producción
5. ✅ Configurar variables de entorno en build time

**Consideraciones:**
- Node 18-alpine para desarrollo
- Nginx-alpine para producción
- Build optimizado con Vite
- Configurar VITE_API_BASE_URL dinámicamente
- Habilitar Hot Module Replacement (HMR)

**Entregables:**
- Dockerfile funcional para frontend
- Configuración de Nginx
- Build optimizado

---

### Fase 4: Docker Compose (2-3 horas)

**Tareas:**
1. ✅ Crear `docker-compose.yml` (base)
2. ✅ Crear `docker-compose.dev.yml` (overrides desarrollo)
3. ✅ Crear `docker-compose.prod.yml` (overrides producción)
4. ✅ Configurar redes
5. ✅ Configurar volúmenes
6. ✅ Configurar health checks
7. ✅ Configurar dependencias entre servicios

**Servicios a configurar:**
- MySQL con inicialización automática
- Backend con wait-for-mysql
- Frontend con proxy a backend
- Nginx (solo producción)

**Entregables:**
- docker-compose.yml completo
- Overrides para cada entorno
- Red y volúmenes configurados

---

### Fase 5: Scripts de Automatización (1-2 horas)

**Tareas:**
1. ✅ Crear scripts para desarrollo
2. ✅ Crear scripts para producción
3. ✅ Crear scripts para testing
4. ✅ Crear scripts de limpieza
5. ✅ Documentar uso de scripts

**Scripts necesarios:**
- `docker-dev.sh` - Levantar entorno de desarrollo
- `docker-prod.sh` - Levantar producción
- `docker-test.sh` - Ejecutar tests
- `docker-clean.sh` - Limpiar todo
- `docker-logs.sh` - Ver logs
- `docker-shell.sh` - Abrir shell en contenedor

**Entregables:**
- Scripts ejecutables
- Documentación de cada script
- Permisos correctos

---

### Fase 6: Testing y Validación (2-3 horas)

**Tareas:**
1. ✅ Probar build de todas las imágenes
2. ✅ Probar entorno de desarrollo
3. ✅ Probar entorno de producción
4. ✅ Verificar persistencia de datos
5. ✅ Probar conectividad entre servicios
6. ✅ Ejecutar tests de integración
7. ✅ Verificar logs y monitoreo

**Tests específicos:**
- Backend puede conectarse a MySQL
- Frontend puede hacer requests al backend
- Migraciones se aplican correctamente
- Archivos estáticos se sirven bien
- Hot reload funciona en desarrollo
- Build de producción es optimizado

**Entregables:**
- Todos los servicios funcionando
- Tests pasando
- Documentación de problemas encontrados

---

### Fase 7: Documentación (1-2 horas)

**Tareas:**
1. ✅ Crear `DOCKER_SETUP.md` (guía de uso)
2. ✅ Crear `DOCKER_TROUBLESHOOTING.md`
3. ✅ Actualizar README principal
4. ✅ Crear ejemplos de uso
5. ✅ Documentar variables de entorno

**Contenido a documentar:**
- Requisitos previos (Docker, Docker Compose)
- Comandos básicos
- Desarrollo vs Producción
- Solución de problemas comunes
- Mejores prácticas
- Tips de optimización

**Entregables:**
- Documentación completa
- Ejemplos funcionales
- Troubleshooting guide

---

## 📄 Archivos a Crear

### 1. `.dockerignore` (Raíz)
```
# Git
.git
.gitignore

# Documentation
docs/
*.md
!README.md

# Environment files
.env
.env.*
!.env.docker.example

# Python
backend/**/__pycache__
backend/**/*.pyc
backend/**/*.pyo
backend/**/*.pyd
backend/.venv
backend/venv
backend/**/.pytest_cache

# Node
frontend/node_modules
frontend/dist
frontend/.vite

# Databases
*.sqlite3
*.db

# IDE
.vscode
.idea
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Coverage
coverage/
htmlcov/
.coverage

# Temporary
tmp/
temp/
```

### 2. `backend/Dockerfile`
```dockerfile
# Multi-stage build para optimización

# Stage 1: Builder
FROM python:3.11-slim as builder

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema para compilar
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear y usar directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python en un directorio temporal
RUN pip install --user --no-warn-script-location -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    TZ=America/Bogota

# Instalar dependencias runtime de MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Configurar timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias de Python del builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY . .

# Copiar y dar permisos a scripts
COPY entrypoint.sh wait-for-it.sh ./
RUN chmod +x entrypoint.sh wait-for-it.sh

# Crear directorios para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/mediafiles

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/', timeout=5)"

# Usar entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Comando por defecto (puede ser sobrescrito)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### 3. `backend/Dockerfile.dev`
```dockerfile
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=America/Bogota

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Configurar timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt requirements.dev.txt ./

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.dev.txt

# Copiar scripts
COPY entrypoint.sh wait-for-it.sh ./
RUN chmod +x entrypoint.sh wait-for-it.sh

# Exponer puerto
EXPOSE 8000

# Health check más simple para desarrollo
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:8000/api/ || exit 1

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Comando por defecto para desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 4. `backend/entrypoint.sh`
```bash
#!/bin/bash
set -e

echo "🔄 Esperando a que MySQL esté listo..."
./wait-for-it.sh ${DB_HOST:-db}:${DB_PORT:-3306} --timeout=60 --strict -- echo "✅ MySQL está listo!"

echo "🔄 Aplicando migraciones..."
python manage.py migrate --noinput

echo "🔄 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "✅ Inicialización completada!"
echo "🚀 Iniciando servidor..."

# Ejecutar el comando que se pase (CMD en Dockerfile)
exec "$@"
```

### 5. `backend/wait-for-it.sh`
```bash
#!/bin/bash
# Script wait-for-it.sh de vishnubob
# https://github.com/vishnubob/wait-for-it

# [Contenido completo del script wait-for-it.sh]
# Por brevedad, usar el script oficial de GitHub
```

### 6. `backend/gunicorn.conf.py`
```python
"""Configuración de Gunicorn para producción"""
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "devtrack-backend"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (si se necesita)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
```

### 7. `backend/requirements.dev.txt`
```
# Dependencias adicionales para desarrollo
ipython==8.20.0
django-debug-toolbar==4.3.0
django-extensions==3.2.3
```

### 8. `frontend/Dockerfile`
```dockerfile
# Multi-stage build para producción

# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Build de producción
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Stage 2: Producción con Nginx
FROM nginx:alpine

# Copiar configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos build desde el stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Nginx se ejecuta por defecto
CMD ["nginx", "-g", "daemon off;"]
```

### 9. `frontend/Dockerfile.dev`
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar todas las dependencias (incluyendo dev)
RUN npm install

# Exponer puerto de Vite
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5173/ || exit 1

# Comando para desarrollo con hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### 10. `frontend/nginx.conf`
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Cache control para assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing - todas las rutas van a index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (opcional, si no usas URL absoluta)
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 11. `docker-compose.yml` (Base)
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: devtrack-mysql
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: ${DB_NAME:-devtrack}
      MYSQL_USER: ${DB_USER:-devtrack}
      MYSQL_PASSWORD: ${DB_PASSWORD:-devtrack_password}
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD:-root_password}
      TZ: America/Bogota
    ports:
      - "${DB_PORT:-3306}:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - devtrack-net
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${DB_ROOT_PASSWORD:-root_password}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: devtrack-backend
    restart: unless-stopped
    env_file:
      - .env.docker
    environment:
      DB_HOST: db
      DB_PORT: 3306
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    volumes:
      - ./backend:/app
      - static-files:/app/staticfiles
      - media-files:/app/mediafiles
    depends_on:
      db:
        condition: service_healthy
    networks:
      - devtrack-net
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_BASE_URL: ${VITE_API_BASE_URL:-http://localhost:8000}
    container_name: devtrack-frontend
    restart: unless-stopped
    ports:
      - "${FRONTEND_PORT:-80}:80"
    depends_on:
      - backend
    networks:
      - devtrack-net

networks:
  devtrack-net:
    driver: bridge

volumes:
  mysql-data:
    driver: local
  static-files:
    driver: local
  media-files:
    driver: local
```

### 12. `docker-compose.dev.yml` (Overrides Desarrollo)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
      - /app/__pycache__
    environment:
      DJANGO_DEBUG: "True"
      DJANGO_SETTINGS_MODULE: config.settings
    command: python manage.py runserver 0.0.0.0:8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    command: npm run dev -- --host 0.0.0.0
```

### 13. `docker-compose.prod.yml` (Overrides Producción)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DJANGO_DEBUG: "False"
    volumes:
      - static-files:/app/staticfiles
      - media-files:/app/mediafiles
    # No montar código fuente en producción

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    # No montar código fuente en producción

  nginx:
    image: nginx:alpine
    container_name: devtrack-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - static-files:/usr/share/nginx/html/static:ro
      - media-files:/usr/share/nginx/html/media:ro
      # - ./nginx/ssl:/etc/nginx/ssl:ro  # Para HTTPS
    depends_on:
      - backend
      - frontend
    networks:
      - devtrack-net
```

### 14. `.env.docker.example`
```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-generate-with-django
DJANGO_DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (MySQL)
DB_NAME=devtrack
DB_USER=devtrack
DB_PASSWORD=devtrack_password
DB_ROOT_PASSWORD=root_password
DB_HOST=db
DB_PORT=3306

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:80

# URLs
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=DevTrack <no-reply@localhost>

# Cloudflare Turnstile
TURNSTILE_SECRET_KEY=0x4AAAAAAB195WFOAznQQxpTPx6rTPWgz6E
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-

# Ports (para docker-compose)
BACKEND_PORT=8000
FRONTEND_PORT=5173
DB_PORT=3306
```

---

## 🔧 Configuración de Entornos

### Desarrollo:
```bash
# Copiar archivo de entorno
cp .env.docker.example .env.docker

# Levantar servicios
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# O usando el script
./scripts/docker-dev.sh
```

### Producción:
```bash
# Configurar variables de entorno para producción
cp .env.docker.example .env.docker
# Editar .env.docker con valores de producción

# Levantar servicios
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# O usando el script
./scripts/docker-prod.sh
```

---

## 🚀 Scripts de Automatización

### `scripts/docker-dev.sh`
```bash
#!/bin/bash
echo "🚀 Iniciando DevTrack en modo DESARROLLO..."

# Copiar env si no existe
if [ ! -f .env.docker ]; then
    echo "📝 Creando .env.docker desde ejemplo..."
    cp .env.docker.example .env.docker
fi

# Build y start
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo "✅ DevTrack desarrollo detenido"
```

### `scripts/docker-prod.sh`
```bash
#!/bin/bash
echo "🚀 Iniciando DevTrack en modo PRODUCCIÓN..."

# Verificar .env.docker
if [ ! -f .env.docker ]; then
    echo "❌ Error: .env.docker no encontrado"
    echo "📝 Copia .env.docker.example y configura los valores"
    exit 1
fi

# Build y start en background
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo "✅ DevTrack producción iniciado"
echo "📊 Ver logs: docker-compose logs -f"
```

### `scripts/docker-test.sh`
```bash
#!/bin/bash
echo "🧪 Ejecutando tests en contenedor..."

# Backend tests
echo "🐍 Tests de Backend..."
docker-compose exec backend python manage.py test

# Frontend tests
echo "⚛️ Tests de Frontend..."
docker-compose exec frontend npm test

echo "✅ Tests completados"
```

### `scripts/docker-clean.sh`
```bash
#!/bin/bash
echo "🧹 Limpiando contenedores y volúmenes de DevTrack..."

# Detener servicios
docker-compose down

# Opcional: Eliminar volúmenes (CUIDADO: elimina la base de datos)
read -p "¿Eliminar volúmenes (base de datos)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down -v
    echo "🗑️ Volúmenes eliminados"
fi

# Limpiar imágenes sin usar
docker image prune -f

echo "✅ Limpieza completada"
```

---

## ✅ Testing y Validación

### Checklist de Pruebas:

#### Build:
- [ ] Backend build exitoso
- [ ] Frontend build exitoso
- [ ] MySQL inicializa correctamente
- [ ] Tamaños de imágenes razonables

#### Conectividad:
- [ ] Backend conecta a MySQL
- [ ] Frontend conecta a Backend
- [ ] Health checks pasan
- [ ] Logs sin errores críticos

#### Funcionalidad:
- [ ] Migraciones se aplican
- [ ] Registro de usuario funciona
- [ ] Login funciona
- [ ] API endpoints responden
- [ ] Frontend renderiza correctamente

#### Persistencia:
- [ ] Datos persisten al reiniciar
- [ ] Archivos estáticos se sirven
- [ ] Uploads funcionan

#### Performance:
- [ ] Tiempo de inicio < 2 minutos
- [ ] Hot reload funciona (dev)
- [ ] Build optimizado (prod)

---

## 🌐 Despliegue en Producción

### Plataformas Recomendadas:

1. **DigitalOcean App Platform**
   - Docker-compose nativo
   - Fácil configuración
   - Escalado automático

2. **AWS ECS/Fargate**
   - Alta escalabilidad
   - Integración con servicios AWS
   - Más complejo

3. **Google Cloud Run**
   - Serverless containers
   - Pago por uso
   - Auto-scaling

4. **Railway / Render**
   - Muy fácil setup
   - Git push deploy
   - Planes gratuitos disponibles

### Pre-requisitos Producción:

- [ ] Dominio configurado
- [ ] Certificado SSL (Let's Encrypt)
- [ ] Variables de entorno seguras
- [ ] Base de datos gestionada (opcional)
- [ ] Backups configurados
- [ ] Monitoreo y alertas
- [ ] CI/CD pipeline

---

## ✅ Checklist de Implementación

### Fase Preparación:
- [ ] Instalar Docker Desktop
- [ ] Instalar Docker Compose
- [ ] Crear estructura de directorios
- [ ] Crear archivos `.dockerignore`
- [ ] Crear `.env.docker.example`

### Fase Backend:
- [ ] Crear `Dockerfile`
- [ ] Crear `Dockerfile.dev`
- [ ] Crear `entrypoint.sh`
- [ ] Descargar `wait-for-it.sh`
- [ ] Crear `gunicorn.conf.py`
- [ ] Crear `requirements.dev.txt`
- [ ] Ajustar `settings.py`

### Fase Frontend:
- [ ] Crear `Dockerfile`
- [ ] Crear `Dockerfile.dev`
- [ ] Crear `nginx.conf`
- [ ] Configurar variables de entorno

### Fase Orquestación:
- [ ] Crear `docker-compose.yml`
- [ ] Crear `docker-compose.dev.yml`
- [ ] Crear `docker-compose.prod.yml`
- [ ] Configurar redes
- [ ] Configurar volúmenes
- [ ] Configurar health checks

### Fase Scripts:
- [ ] Crear `docker-dev.sh`
- [ ] Crear `docker-prod.sh`
- [ ] Crear `docker-test.sh`
- [ ] Crear `docker-clean.sh`
- [ ] Dar permisos de ejecución

### Fase Testing:
- [ ] Probar build de imágenes
- [ ] Probar desarrollo
- [ ] Probar producción
- [ ] Ejecutar tests
- [ ] Verificar persistencia

### Fase Documentación:
- [ ] Crear `DOCKER_SETUP.md`
- [ ] Crear `DOCKER_TROUBLESHOOTING.md`
- [ ] Actualizar README
- [ ] Documentar comandos comunes

---

## 📊 Estimación de Tiempo

| Fase | Tiempo Estimado | Prioridad |
|------|-----------------|-----------|
| Preparación | 1-2 horas | Alta |
| Backend | 2-3 horas | Alta |
| Frontend | 2-3 horas | Alta |
| Docker Compose | 2-3 horas | Alta |
| Scripts | 1-2 horas | Media |
| Testing | 2-3 horas | Alta |
| Documentación | 1-2 horas | Media |
| **TOTAL** | **11-18 horas** | - |

**Tiempo real probable:** 2-3 días de trabajo

---

## 📝 Notas Importantes

1. **Seguridad:**
   - NUNCA commitear archivos `.env` con secretos reales
   - Usar secrets management en producción
   - Cambiar contraseñas por defecto

2. **Performance:**
   - Multi-stage builds reducen tamaño de imágenes
   - Usar `.dockerignore` para builds más rápidos
   - Cachear dependencias correctamente

3. **Desarrollo:**
   - Hot reload debe funcionar con volúmenes
   - No usar `--build` en cada reinicio en dev
   - Logs accesibles con `docker-compose logs`

4. **Producción:**
   - Usar images pre-built
   - No montar código fuente
   - Configurar reverse proxy (Nginx)
   - Habilitar HTTPS

---

## 🔗 Recursos Útiles

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/dev-best-practices/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

---

**Plan creado:** 21 de Octubre, 2025  
**Autor:** GitHub Copilot  
**Estado:** 📋 Plan completo - Listo para implementación
