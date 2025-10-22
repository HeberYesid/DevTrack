# 🔧 Troubleshooting: Problemas al Trabajar en Diferentes Máquinas

**Fecha:** 21 de Octubre, 2025  
**Situación:** El proyecto funcionaba en una PC pero no en otra

---

## 🚨 Problema

El proyecto DevTrack funcionaba correctamente en una máquina pero no en otra, lo que llevó a hacer cambios desde la segunda máquina (commit `4010c43`).

---

## 🔍 Posibles Causas Comunes

### 1. **Problemas con PowerShell ExecutionPolicy (Windows)**

**Síntoma:**
```powershell
PS> .\.venv\Scripts\Activate.ps1
.\.venv\Scripts\Activate.ps1 : No se puede cargar el archivo porque la 
ejecución de scripts está deshabilitada en este sistema.
```

**Solución:** (Ahora documentada en README.md)
```powershell
# Opción 1: Temporal (solo para esta sesión)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Opción 2: Permanente para el usuario
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

### 2. **Variables de Entorno No Configuradas**

**Síntoma:**
- Error al iniciar el servidor Django
- Problemas de conexión a base de datos
- Error: `SECRET_KEY` no configurado

**Solución:**
```bash
# Backend
cd backend
copy .env.example .env  # Crear archivo .env

# Generar SECRET_KEY de Django
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Configurar en `backend/.env`:
```env
DJANGO_SECRET_KEY=tu_clave_generada_aqui
DB_NAME=devtrack
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
FRONTEND_URL=http://localhost:5173
```

---

### 3. **Python/Node.js con Diferentes Versiones**

**Problema:** Incompatibilidades entre versiones

**Verificar versiones:**
```bash
# Python
python --version  # Debe ser 3.11+

# Node.js
node --version    # Debe ser 18+

# npm
npm --version
```

**Solución:**
- Asegurarse de usar las mismas versiones en ambas máquinas
- Considerar usar `pyenv` (Python) y `nvm` (Node.js) para gestionar versiones

---

### 4. **Base de Datos MySQL No Configurada**

**Síntoma:**
```
django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")
```

**Verificar:**
```bash
# ¿MySQL está corriendo?
# Windows:
services.msc  # Buscar MySQL

# Verificar conexión
mysql -u root -p
```

**Solución:**
```sql
-- Crear base de datos y usuario
CREATE DATABASE devtrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'devtrack'@'%' IDENTIFIED BY 'devtrack_password';
GRANT ALL PRIVILEGES ON devtrack.* TO 'devtrack'@'%';
FLUSH PRIVILEGES;
```

---

### 5. **Dependencias No Instaladas o Desactualizadas**

**Backend:**
```bash
cd backend
pip install -r requirements.txt

# Si hay problemas con mysqlclient en Windows:
pip install mysqlclient
# O alternativamente:
pip install pymysql
# Y en settings.py agregar:
# import pymysql
# pymysql.install_as_MySQLdb()
```

**Frontend:**
```bash
cd frontend
npm install

# Si package-lock.json tiene conflictos:
rm package-lock.json
rm -rf node_modules
npm install
```

---

### 6. **Migraciones de Base de Datos No Aplicadas**

**Síntoma:**
```
django.db.utils.ProgrammingError: (1146, "Table 'devtrack.accounts_user' doesn't exist")
```

**Solución:**
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

---

### 7. **Puertos Ocupados**

**Síntoma:**
```
Error: That port is already in use.
```

**Verificar puertos:**
```powershell
# Backend (puerto 8000)
netstat -ano | findstr :8000

# Frontend (puerto 5173)
netstat -ano | findstr :5173
```

**Solución:**
```powershell
# Matar proceso por PID
taskkill /PID <numero_pid> /F

# O usar puertos diferentes:
python manage.py runserver 8001
npm run dev -- --port 5174
```

---

### 8. **Problema con el Campo `used` vs `is_used`**

**Este fue el bug que se corrigió en el commit `4010c43`**

**Síntoma:**
- Error al verificar código de 6 dígitos
- `FieldError: Cannot resolve keyword 'used' into field`

**Causa:**
El modelo `EmailVerificationCode` usa el campo `is_used`, pero en el serializer se buscaba `used=False`

**Solución aplicada:**
```python
# backend/accounts/serializers.py
verification_code = EmailVerificationCode.objects.filter(
    user=user,
    code=code,
    is_used=False  # ✅ Corregido (antes era: used=False)
).first()
```

---

## 📋 Checklist de Configuración para Nueva Máquina

Cuando configures el proyecto en una nueva máquina, verifica:

### Backend:
- [ ] Python 3.11+ instalado
- [ ] MySQL 8+ instalado y corriendo
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos creada
- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Superusuario creado (opcional: `python manage.py createsuperuser`)
- [ ] Servidor inicia correctamente (`python manage.py runserver`)

### Frontend:
- [ ] Node.js 18+ instalado
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Dependencias instaladas (`npm install`)
- [ ] Servidor inicia correctamente (`npm run dev`)

### Permisos (Windows):
- [ ] PowerShell ExecutionPolicy configurado
- [ ] Permisos de lectura/escritura en la carpeta del proyecto

---

## 🔄 Sincronización entre Máquinas

### Mejores Prácticas:

1. **Git - Control de Versiones:**
   ```bash
   # En la máquina donde hiciste cambios
   git add .
   git commit -m "feat: descripción de los cambios"
   git push origin main
   
   # En tu PC principal
   git pull origin main
   ```

2. **NO subir a Git:**
   - ✅ `.env` debe estar en `.gitignore`
   - ✅ `node_modules/` debe estar en `.gitignore`
   - ✅ `.venv/` debe estar en `.gitignore`
   - ✅ `__pycache__/` debe estar en `.gitignore`

3. **Documentar configuraciones específicas:**
   - Crear `docs/SETUP_WINDOWS.md` si hay pasos específicos para Windows
   - Crear `docs/SETUP_MAC.md` si hay pasos específicos para Mac/Linux

4. **Usar Docker (opcional pero recomendado):**
   - Garantiza el mismo entorno en todas las máquinas
   - Evita problemas de "funciona en mi máquina"

---

## 🐳 Solución Definitiva: Docker (Recomendado)

Para evitar estos problemas en el futuro, considera usar Docker:

### Ventajas:
- ✅ Mismo entorno en todas las máquinas
- ✅ No importa el sistema operativo
- ✅ No hay problemas con versiones de dependencias
- ✅ Setup en minutos

### Ejemplo básico de `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: mysql:8
    environment:
      MYSQL_DATABASE: devtrack
      MYSQL_USER: devtrack
      MYSQL_PASSWORD: devtrack_password
      MYSQL_ROOT_PASSWORD: root_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DB_HOST=db
      - DB_NAME=devtrack
      - DB_USER=devtrack
      - DB_PASSWORD=devtrack_password

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  mysql_data:
```

Con Docker, solo necesitas:
```bash
docker-compose up
```

---

## 📝 Recomendaciones

1. **Mantener documentación actualizada:**
   - Si encuentras un problema nuevo, documentalo en `docs/TROUBLESHOOTING.md`

2. **Usar mensajes de commit descriptivos:**
   - Facilita entender qué cambió y por qué
   - Ejemplo: `fix: correct field name from 'used' to 'is_used' in email verification`

3. **Crear scripts de setup:**
   - `scripts/setup_windows.ps1`
   - `scripts/setup_unix.sh`

4. **Probar en ambas máquinas antes de hacer commit:**
   - Asegurarse de que los cambios funcionan en todos los entornos

5. **Considerar CI/CD:**
   - GitHub Actions puede probar automáticamente que todo funciona
   - Detecta problemas antes de que lleguen a producción

---

## 🆘 ¿Sigues Teniendo Problemas?

Si el proyecto aún no funciona en alguna máquina:

1. **Revisar logs:**
   ```bash
   # Backend
   python manage.py runserver  # Ver errores en consola
   
   # Frontend
   npm run dev  # Ver errores en consola
   ```

2. **Verificar configuración:**
   ```bash
   # Backend
   python manage.py check
   python manage.py showmigrations
   
   # Frontend
   npm run build  # Verificar si hay errores de build
   ```

3. **Comparar entornos:**
   ```bash
   # Python
   pip freeze > requirements_actual.txt
   diff requirements.txt requirements_actual.txt
   
   # Node.js
   npm list --depth=0
   ```

4. **Pedir ayuda:**
   - Documentar el error exacto
   - Incluir logs completos
   - Especificar sistema operativo y versiones

---

**Última actualización:** 21 de Octubre, 2025  
**Documento creado por:** GitHub Copilot  
**Estado:** 📝 Guía de troubleshooting activa
