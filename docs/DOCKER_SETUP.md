# 🐳 Guía de Setup de Docker para DevTrack

**Última actualización:** 22 de Octubre, 2025

---

## 📋 Tabla de Contenidos

1. [Pre-requisitos](#pre-requisitos)
2. [Instalación de Docker](#instalación-de-docker)
3. [Configuración Inicial](#configuración-inicial)
4. [Primer Uso](#primer-uso)
5. [Comandos Comunes](#comandos-comunes)
6. [Desarrollo](#desarrollo)
7. [Producción](#producción)
8. [Solución de Problemas](#solución-de-problemas)

---

## ✅ Pre-requisitos

### Sistema Operativo
- **Windows 10/11** Pro, Enterprise o Education (64-bit)
- WSL 2 habilitado (recomendado)
- Al menos **8GB de RAM** (4GB mínimo)
- **20GB** de espacio en disco libre

### Software Necesario
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (incluye Docker Compose)
- PowerShell 5.1 o superior
- Git (para clonar el repositorio)

---

## 🔧 Instalación de Docker

### Paso 1: Descargar Docker Desktop

1. Ve a https://www.docker.com/products/docker-desktop
2. Descarga la versión para Windows
3. Ejecuta el instalador

### Paso 2: Configurar Docker Desktop

1. Durante la instalación, marca:
   - ✅ Use WSL 2 instead of Hyper-V (recomendado)
   - ✅ Add shortcut to desktop

2. Reinicia tu computadora cuando se solicite

### Paso 3: Verificar Instalación

Abre PowerShell y ejecuta:

```powershell
docker --version
docker-compose --version
```

Deberías ver algo como:
```
Docker version 24.0.x
Docker Compose version v2.x.x
```

### Paso 4: Iniciar Docker Desktop

1. Abre Docker Desktop desde el menú de inicio
2. Espera a que el ícono de Docker en la bandeja del sistema muestre "Docker Desktop is running"
3. Verifica con: `docker info`

---

## ⚙️ Configuración Inicial

### 1. Clonar el Repositorio (si aún no lo has hecho)

```powershell
git clone https://github.com/HeberYesid/DevTrack.git
cd DevTrack
```

### 2. Configurar Variables de Entorno

El archivo `.env.docker.example` ya contiene valores por defecto para desarrollo.

```powershell
# Copiar archivo de ejemplo
Copy-Item .env.docker.example .env.docker
```

**Para desarrollo:** Los valores por defecto funcionan bien.

**Para producción:** Edita `.env.docker` y cambia:

```env
# Generar SECRET_KEY seguro
DJANGO_SECRET_KEY=tu-clave-secreta-aqui

# Deshabilitar debug
DJANGO_DEBUG=False

# Configurar contraseñas fuertes
DB_PASSWORD=contraseña-segura-aqui
DB_ROOT_PASSWORD=otra-contraseña-segura

# Configurar hosts permitidos
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# URLs de producción
API_BASE_URL=https://api.tudominio.com
FRONTEND_URL=https://tudominio.com
```

### 3. Generar DJANGO_SECRET_KEY

```powershell
# Desde el directorio del proyecto
docker run --rm python:3.11-slim python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y pégalo en `.env.docker` como `DJANGO_SECRET_KEY`.

---

## 🚀 Primer Uso

### Opción 1: Usando Scripts (Recomendado)

```powershell
# Iniciar en modo desarrollo
.\scripts\docker-dev.ps1
```

El script automáticamente:
- ✅ Verifica que Docker esté corriendo
- ✅ Crea `.env.docker` si no existe
- ✅ Construye las imágenes
- ✅ Inicia todos los servicios

### Opción 2: Manual

```powershell
# Build de imágenes
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

# Iniciar servicios
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Primera Ejecución

La primera vez tomará varios minutos porque:
1. Descarga imágenes base (Python, Node, MySQL)
2. Instala dependencias de Python
3. Instala dependencias de Node.js
4. Crea la base de datos
5. Aplica migraciones

**Progreso normal:**
```
✅ Building backend...
✅ Building frontend...
✅ Creating devtrack-mysql...
✅ Creating devtrack-backend...
✅ Creating devtrack-frontend...
🔄 Waiting for MySQL...
🔄 Applying migrations...
🔄 Collecting static files...
✅ Initialization completed!
🚀 Starting Django server...
```

### Verificar que Todo Funciona

Una vez iniciado, abre tu navegador:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api/
- **API Docs (Swagger):** http://localhost:8000/api/docs/
- **Admin Panel:** http://localhost:8000/admin/

---

## 🔍 Comandos Comunes

### Ver Estado de Contenedores

```powershell
docker-compose ps
```

Salida esperada:
```
NAME                 STATUS          PORTS
devtrack-mysql       Up 2 minutes    0.0.0.0:3306->3306/tcp
devtrack-backend     Up 2 minutes    0.0.0.0:8000->8000/tcp
devtrack-frontend    Up 2 minutes    0.0.0.0:5173->5173/tcp
```

### Ver Logs

```powershell
# Todos los servicios
.\scripts\docker-logs.ps1

# Seguir logs en tiempo real
.\scripts\docker-logs.ps1 -Follow

# Un servicio específico
.\scripts\docker-logs.ps1 -Service backend
docker-compose logs backend

# Últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Ejecutar Comandos en Contenedores

```powershell
# Abrir shell en backend
.\scripts\docker-shell.ps1 backend
# o manualmente:
docker-compose exec backend bash

# Ejecutar comando Django
docker-compose exec backend python manage.py createsuperuser

# Abrir shell en frontend
.\scripts\docker-shell.ps1 frontend

# Conectar a MySQL
.\scripts\docker-shell.ps1 db
# Luego dentro:
mysql -u devtrack -p devtrack
```

### Ejecutar Tests

```powershell
.\scripts\docker-test.ps1

# O manualmente:
docker-compose exec backend python manage.py test
docker-compose exec frontend npm test
```

### Detener Servicios

```powershell
# Ctrl+C en la terminal donde corre docker-compose

# O desde otra terminal:
docker-compose down

# Detener y eliminar volúmenes (⚠️ elimina la DB):
docker-compose down -v
```

### Reiniciar un Servicio

```powershell
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild sin Cache

```powershell
docker-compose build --no-cache backend
docker-compose build --no-cache frontend
```

---

## 💻 Desarrollo

### Hot Reload

En modo desarrollo, los cambios en el código se reflejan automáticamente:

- **Backend (Django):** Detecta cambios en archivos `.py` y recarga
- **Frontend (Vite):** Hot Module Replacement (HMR) instantáneo

No necesitas reiniciar los contenedores.

### Agregar Dependencias

**Backend (Python):**

```powershell
# 1. Edita requirements.txt
# 2. Rebuild la imagen
docker-compose build backend
# 3. Reinicia
docker-compose restart backend
```

**Frontend (npm):**

```powershell
# 1. Edita package.json
# 2. Rebuild la imagen
docker-compose build frontend
# 3. Reinicia
docker-compose restart frontend
```

### Crear Migraciones

```powershell
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Crear Superusuario

```powershell
docker-compose exec backend python manage.py createsuperuser
```

### Acceder a la Base de Datos

**Desde un cliente MySQL externo:**

```
Host: localhost
Port: 3306
User: devtrack
Password: devtrack_password
Database: devtrack
```

**Desde la línea de comandos:**

```powershell
docker-compose exec db mysql -u devtrack -p devtrack
```

### Debugging

**Backend con ipdb/pdb:**

```python
# En tu código
import ipdb; ipdb.set_trace()
```

Luego ejecuta:
```powershell
docker-compose up
```

El debugger se detendrá en el breakpoint.

---

## 🚀 Producción

### Configuración

1. **Edita `.env.docker` con valores de producción:**
   - `DJANGO_DEBUG=False`
   - SECRET_KEY seguro
   - Contraseñas fuertes
   - ALLOWED_HOSTS correcto

2. **Configura HTTPS** (recomendado):
   - Usa un reverse proxy (Nginx, Traefik, Caddy)
   - O configura certificados SSL en nginx/

### Iniciar en Producción

```powershell
.\scripts\docker-prod.ps1
```

Esto:
- ✅ Construye imágenes optimizadas
- ✅ Usa Gunicorn en lugar de runserver
- ✅ Sirve frontend con Nginx optimizado
- ✅ Inicia en modo detached (background)

### Verificar Estado

```powershell
docker-compose ps
docker-compose logs -f
```

### Actualizar Producción

```powershell
# 1. Pull últimos cambios
git pull origin main

# 2. Rebuild y reiniciar
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 3. Aplicar migraciones
docker-compose exec backend python manage.py migrate

# 4. Recolectar estáticos
docker-compose exec backend python manage.py collectstatic --noinput
```

### Backup de Base de Datos

```powershell
# Crear backup
docker-compose exec db mysqldump -u root -p devtrack > backup.sql

# Restaurar backup
docker-compose exec -T db mysql -u root -p devtrack < backup.sql
```

---

## 🆘 Solución de Problemas

### Docker Desktop no está corriendo

**Error:**
```
error during connect: ... cannot find the file specified
```

**Solución:**
1. Abre Docker Desktop
2. Espera a que el ícono muestre "Docker Desktop is running"
3. Verifica con: `docker info`

### Puerto ya en uso

**Error:**
```
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solución:**
```powershell
# Ver qué está usando el puerto
netstat -ano | findstr :8000

# Matar el proceso (reemplaza PID)
taskkill /PID <PID> /F

# O cambiar el puerto en .env.docker
BACKEND_PORT=8001
```

### Contenedor sale inmediatamente

**Ver logs para diagnóstico:**
```powershell
docker-compose logs backend
```

**Problemas comunes:**
- Error de sintaxis en Python/JavaScript
- Variable de entorno faltante
- MySQL no está listo (aumentar timeout en wait-for-it.sh)

### MySQL no se puede conectar

**Error:**
```
Can't connect to MySQL server
```

**Soluciones:**
1. Espera más tiempo (MySQL tarda en iniciar la primera vez)
2. Verifica logs: `docker-compose logs db`
3. Verifica credenciales en `.env.docker`
4. Reinicia el contenedor: `docker-compose restart db`

### Hot reload no funciona

**Backend:**
- Verifica que el volumen esté montado: `docker-compose config`
- Reinicia: `docker-compose restart backend`

**Frontend:**
- Verifica que Vite esté usando `--host 0.0.0.0`
- Limpia cache: `docker-compose build --no-cache frontend`

### Cambios no se aplican

```powershell
# Rebuild sin cache
docker-compose build --no-cache

# Reiniciar todo
docker-compose down
docker-compose up --build
```

### Limpiar Todo y Empezar de Nuevo

```powershell
.\scripts\docker-clean.ps1

# O manualmente:
docker-compose down -v  # ⚠️ Elimina la base de datos
docker system prune -a  # Limpia todo Docker
```

### Problemas de Permisos

**Windows:**
- Asegúrate de que Docker Desktop tiene permisos para acceder al directorio
- Settings > Resources > File Sharing

### Out of Memory

Si Docker se queda sin memoria:

1. Docker Desktop > Settings > Resources
2. Aumenta Memory a al menos 4GB
3. Aumenta CPU cores si es posible

---

## 📚 Recursos Adicionales

- [Plan completo de Docker](./DOCKER_PLAN.md)
- [Troubleshooting específico](./DOCKER_TROUBLESHOOTING.md)
- [Documentación oficial de Docker](https://docs.docker.com/)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)

---

## 🎓 Tips y Mejores Prácticas

1. **Usa `.dockerignore`** - Ya está configurado, no modifiques
2. **No subas `.env.docker` a Git** - Contiene secretos
3. **Usa scripts** - Facilitan operaciones comunes
4. **Monitorea recursos** - Docker Desktop > Dashboard
5. **Backup regular** - Especialmente en producción
6. **Actualiza imágenes** - `docker-compose pull` regularmente

---

**¿Preguntas?** Revisa [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) o abre un issue en GitHub.
