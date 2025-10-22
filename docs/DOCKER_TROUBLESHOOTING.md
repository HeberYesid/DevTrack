# 🐳 Docker Troubleshooting - DevTrack

**Guía de solución de problemas para Docker**  
**Última actualización:** 22 de Octubre, 2025

---

## 📋 Índice de Problemas

1. [Docker Desktop](#docker-desktop)
2. [Build Errors](#build-errors)
3. [Container Startup](#container-startup)
4. [Base de Datos](#base-de-datos)
5. [Networking](#networking)
6. [Volúmenes y Persistencia](#volúmenes-y-persistencia)
7. [Performance](#performance)
8. [Development Issues](#development-issues)

---

## 🐋 Docker Desktop

### Problema: Docker Desktop no inicia

**Síntomas:**
- Ícono de Docker permanece en gris
- "Docker Desktop starting..." indefinidamente

**Soluciones:**

1. **Reiniciar completamente:**
   ```powershell
   # Cerrar Docker Desktop completamente
   taskkill /F /IM "Docker Desktop.exe"
   
   # Limpiar procesos huérfanos
   wsl --shutdown
   
   # Reiniciar Docker Desktop
   Start-Process "Docker Desktop"
   ```

2. **Verificar WSL 2:**
   ```powershell
   wsl --list --verbose
   ```
   Debe mostrar versión 2. Si no:
   ```powershell
   wsl --set-default-version 2
   ```

3. **Reinstalar Docker Desktop:**
   - Desinstalar completamente
   - Eliminar `C:\ProgramData\Docker`
   - Reiniciar PC
   - Instalar de nuevo

---

### Problema: "Cannot connect to Docker daemon"

**Error:**
```
error during connect: ... cannot find the file specified
```

**Soluciones:**

1. Verificar que Docker Desktop está corriendo
2. Ejecutar como administrador
3. Verificar permisos:
   - Docker Desktop > Settings > General
   - ✅ "Use the WSL 2 based engine"

---

## 🔨 Build Errors

### Problema: Build falla en backend

**Error común:**
```
ERROR: failed to solve: process "/bin/sh -c pip install..." didn't complete successfully
```

**Soluciones:**

1. **Limpiar caché de Docker:**
   ```powershell
   docker-compose build --no-cache backend
   ```

2. **Verificar requirements.txt:**
   ```powershell
   # Ver el archivo
   cat backend\requirements.txt
   
   # Buscar caracteres raros o dependencias rotas
   ```

3. **Problemas con mysqlclient:**
   ```dockerfile
   # El Dockerfile ya incluye las dependencias necesarias:
   # gcc, default-libmysqlclient-dev, pkg-config
   ```

4. **Timeout en pip:**
   Agregar en `backend/Dockerfile`:
   ```dockerfile
   ENV PIP_DEFAULT_TIMEOUT=100
   ```

---

### Problema: Build falla en frontend

**Error común:**
```
npm ERR! code ELIFECYCLE
```

**Soluciones:**

1. **Eliminar node_modules y package-lock.json:**
   ```powershell
   Remove-Item frontend\node_modules -Recurse -Force
   Remove-Item frontend\package-lock.json -Force
   docker-compose build --no-cache frontend
   ```

2. **Verificar package.json:**
   - No debe tener dependencias con versiones incompatibles
   - Usa `npm install` localmente primero para verificar

3. **Problemas de memoria:**
   ```powershell
   # Aumentar memoria de Node en Dockerfile:
   ENV NODE_OPTIONS="--max-old-space-size=4096"
   ```

---

## 🚀 Container Startup

### Problema: Backend container sale inmediatamente

**Verificar logs:**
```powershell
docker-compose logs backend
```

**Causas comunes:**

1. **Error de sintaxis en Python:**
   ```
   SyntaxError: invalid syntax
   ```
   - Revisar el archivo indicado en el error
   - Corregir sintaxis
   - Rebuild: `docker-compose build backend`

2. **Variable de entorno faltante:**
   ```
   KeyError: 'DJANGO_SECRET_KEY'
   ```
   - Verificar `.env.docker` existe
   - Verificar que tiene todas las variables de `.env.docker.example`

3. **Falta wait-for-it.sh:**
   ```
   ./wait-for-it.sh: not found
   ```
   - Re-descargar el script:
   ```powershell
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh" -OutFile "backend\wait-for-it.sh"
   ```

---

### Problema: Frontend container sale inmediatamente

**Verificar logs:**
```powershell
docker-compose logs frontend
```

**Causas comunes:**

1. **Error en código JavaScript:**
   ```
   SyntaxError: Unexpected token
   ```
   - ESLint/compilación falló
   - Corregir error
   - Rebuild

2. **Vite no puede iniciar:**
   ```
   Port 5173 is already in use
   ```
   - Cambiar puerto en `.env.docker`:
   ```env
   FRONTEND_PORT=5174
   ```

---

## 🗄️ Base de Datos

### Problema: MySQL no se conecta

**Error:**
```
Can't connect to MySQL server on 'db'
```

**Soluciones:**

1. **Esperar a que MySQL inicie:**
   ```powershell
   # Ver logs de MySQL
   docker-compose logs db
   
   # Esperar hasta ver:
   # "mysqld: ready for connections"
   ```

2. **Verificar health check:**
   ```powershell
   docker-compose ps
   # Estado debe ser "healthy"
   ```

3. **Aumentar timeout en wait-for-it.sh:**
   En `backend/entrypoint.sh`:
   ```bash
   ./wait-for-it.sh ${DB_HOST}:${DB_PORT} --timeout=120  # Aumentar a 120s
   ```

4. **Verificar credenciales:**
   ```powershell
   # En .env.docker:
   DB_USER=devtrack
   DB_PASSWORD=devtrack_password
   DB_NAME=devtrack
   ```

---

### Problema: "Table doesn't exist"

**Error:**
```
django.db.utils.ProgrammingError: (1146, "Table 'devtrack.accounts_user' doesn't exist")
```

**Solución:**

```powershell
# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Si no funciona, recrear DB:
docker-compose down -v
docker-compose up -d
```

---

### Problema: Perder datos al reiniciar

**Causa:** Volúmenes no configurados correctamente

**Verificar:**
```powershell
docker volume ls | Select-String "devtrack"
```

Debe mostrar:
```
devtrack-mysql-data
devtrack-static-files
devtrack-media-files
```

**Si no existen:**
```powershell
# Recrear con volúmenes
docker-compose down
docker-compose up -d
```

---

## 🌐 Networking

### Problema: Frontend no puede conectar con Backend

**Error en consola del navegador:**
```
Failed to fetch
net::ERR_CONNECTION_REFUSED
```

**Soluciones:**

1. **Verificar VITE_API_BASE_URL:**
   ```powershell
   # En .env.docker:
   VITE_API_BASE_URL=http://localhost:8000
   ```

2. **CORS no configurado:**
   En `backend/config/settings.py`:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:5173",
       "http://127.0.0.1:5173",
   ]
   ```

3. **Backend no está escuchando en todas las interfaces:**
   Verificar comando en Dockerfile:
   ```bash
   CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
   ```

---

### Problema: No se puede acceder desde navegador

**URL no carga:** http://localhost:5173

**Soluciones:**

1. **Verificar que el contenedor está corriendo:**
   ```powershell
   docker-compose ps
   ```

2. **Verificar mapeo de puertos:**
   ```powershell
   docker-compose port frontend 5173
   # Debe mostrar: 0.0.0.0:5173
   ```

3. **Firewall bloqueando:**
   - Permitir Docker en Firewall de Windows
   - Verificar antivirus no está bloqueando

4. **Usar IP directa:**
   ```powershell
   # Obtener IP del contenedor
   docker inspect devtrack-frontend | Select-String "IPAddress"
   ```

---

## 💾 Volúmenes y Persistencia

### Problema: Cambios en código no se reflejan

**En desarrollo (con hot reload):**

1. **Verificar montaje de volumen:**
   ```powershell
   docker-compose config | Select-String "volumes" -Context 5,5
   ```

2. **Restart container:**
   ```powershell
   docker-compose restart backend
   docker-compose restart frontend
   ```

3. **Build sin caché:**
   ```powershell
   docker-compose build --no-cache backend
   docker-compose up -d backend
   ```

---

### Problema: Archivos estáticos no se sirven

**En producción:**

```powershell
# Recolectar estáticos manualmente
docker-compose exec backend python manage.py collectstatic --noinput

# Verificar volumen
docker volume inspect devtrack-static-files
```

---

## 🐌 Performance

### Problema: Build muy lento

**Optimizaciones:**

1. **Usar .dockerignore:**
   Ya configurado, asegurarse de que excluye:
   - `node_modules/`
   - `__pycache__/`
   - `.git/`

2. **Configurar BuildKit:**
   ```powershell
   $env:DOCKER_BUILDKIT=1
   docker-compose build
   ```

3. **Aumentar recursos en Docker Desktop:**
   - Settings > Resources
   - Memory: 4GB+
   - CPUs: 2+

---

### Problema: Contenedores lentos

**Soluciones:**

1. **Verificar uso de recursos:**
   ```powershell
   docker stats
   ```

2. **Limpiar imágenes sin usar:**
   ```powershell
   docker system prune -a
   ```

3. **Configurar MySQL para desarrollo:**
   En docker-compose.yml agregar:
   ```yaml
   db:
     command: --innodb-flush-log-at-trx-commit=0
   ```

---

## 💻 Development Issues

### Problema: Hot reload no funciona (Backend)

**Django no detecta cambios:**

1. **Verificar volumen montado:**
   ```powershell
   docker-compose exec backend ls -la /app
   # Debe mostrar archivos del proyecto
   ```

2. **Usar polling (más lento pero más confiable):**
   En `docker-compose.dev.yml`:
   ```yaml
   backend:
     environment:
       PYTHONUNBUFFERED: "1"
       WATCHDOG_POLL: "true"
   ```

---

### Problema: Hot reload no funciona (Frontend)

**Vite no detecta cambios:**

1. **Verificar que usa --host 0.0.0.0:**
   ```yaml
   frontend:
     command: npm run dev -- --host 0.0.0.0
   ```

2. **Agregar watchOptions en vite.config.js:**
   ```javascript
   export default {
     server: {
       watch: {
         usePolling: true
       }
     }
   }
   ```

---

### Problema: Cannot install packages

**Backend (pip):**

```powershell
# Instalar en el contenedor directamente
docker-compose exec backend pip install nombre-paquete

# Luego agregar a requirements.txt
echo "nombre-paquete==version" >> backend\requirements.txt

# Rebuild para persistir
docker-compose build backend
```

**Frontend (npm):**

```powershell
# Instalar en el contenedor
docker-compose exec frontend npm install paquete

# Actualizar package.json (ya se hace automáticamente)

# Rebuild
docker-compose build frontend
```

---

## 🧪 Testing Issues

### Problema: Tests fallan en Docker pero funcionan localmente

**Causas comunes:**

1. **Base de datos de test:**
   ```powershell
   # Django crea automáticamente test_devtrack
   # Asegurarse de que el usuario tiene permisos
   docker-compose exec backend python manage.py test --keepdb
   ```

2. **Variables de entorno diferentes:**
   - Verificar `.env.docker`
   - Comparar con tu `.env` local

3. **Timezone diferente:**
   En Dockerfile ya configurado:
   ```dockerfile
   ENV TZ=America/Bogota
   ```

---

## 🆘 Comandos de Diagnóstico

### Información General

```powershell
# Ver estado de Docker
docker info

# Ver todos los contenedores
docker ps -a

# Ver imágenes
docker images

# Ver volúmenes
docker volume ls

# Ver redes
docker network ls
```

### Logs Detallados

```powershell
# Logs de todos los servicios
docker-compose logs

# Seguir logs en tiempo real
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100

# Solo errores
docker-compose logs 2>&1 | Select-String "error"
```

### Inspeccionar Contenedores

```powershell
# Info completa
docker inspect devtrack-backend

# Solo IP
docker inspect devtrack-backend | Select-String "IPAddress"

# Variables de entorno
docker inspect devtrack-backend | Select-String "Env" -Context 0,20
```

### Uso de Recursos

```powershell
# Uso en tiempo real
docker stats

# Espacio en disco
docker system df
```

---

## 🔧 Reset Completo

Si todo falla, reset completo:

```powershell
# 1. Detener todo
docker-compose down -v

# 2. Eliminar imágenes de DevTrack
docker rmi devtrack-backend devtrack-frontend

# 3. Limpiar sistema Docker
docker system prune -a --volumes

# 4. Rebuild desde cero
docker-compose build --no-cache

# 5. Iniciar
docker-compose up
```

---

## 📞 Obtener Ayuda

Si el problema persiste:

1. **Recopilar información:**
   ```powershell
   docker-compose ps > docker-status.txt
   docker-compose logs > docker-logs.txt
   docker info > docker-info.txt
   ```

2. **Verificar versiones:**
   ```powershell
   docker --version
   docker-compose --version
   ```

3. **Documentar:**
   - Qué estabas intentando hacer
   - Mensaje de error exacto
   - Pasos para reproducir

4. **Buscar en:**
   - [Docker Documentation](https://docs.docker.com/)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/docker)
   - Issues del repositorio DevTrack

---

## 📚 Recursos Adicionales

- [Guía de Setup](./DOCKER_SETUP.md)
- [Plan de Docker](./DOCKER_PLAN.md)
- [Troubleshooting General](./TROUBLESHOOTING.md)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Última actualización:** 22 de Octubre, 2025
