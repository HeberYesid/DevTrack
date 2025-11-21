# 🚀 Guía de Migración a Render.com (GRATIS)

## ¿Por qué Render?

- ✅ **100% Gratis** para apps pequeñas (750 horas/mes)
- ✅ Base de datos PostgreSQL incluida GRATIS
- ✅ Deploy automático desde GitHub
- ✅ HTTPS incluido
- ✅ Similar a Railway pero sin costos
- ⚠️ Se "duerme" después de 15 min sin uso (primer request tarda ~30 seg)

---

## 📦 PASO 1: Preparar el Código

### 1.1 Actualizar `requirements.txt`

Tu archivo ya tiene lo necesario, solo asegúrate que incluya:

```txt
Django==5.0.6
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==3.0.1
PyMySQL==1.1.0
psycopg2-binary==2.9.9  # ← AGREGAR ESTA LÍNEA (para PostgreSQL)
python-dotenv==1.0.1
django-cors-headers==4.3.1
django-ratelimit==4.1.0
drf-spectacular==0.27.2
```

### 1.2 Agregar archivo `build.sh` en la raíz de `backend/`

Render ejecutará este script en cada deploy:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput

# NOTE: Las migraciones se ejecutan DESPUÉS del build, 
# cuando la BD ya está disponible
```

**⚠️ IMPORTANTE**: Las migraciones NO se ejecutan durante el build porque la base de datos no está disponible en ese momento. Se ejecutan en el "Pre-Deploy Command" que verás más adelante.

### 1.3 Actualizar `settings.py` para soportar PostgreSQL

Render usa PostgreSQL (no MySQL). Tu configuración actual ya soporta `DATABASE_URL`, solo necesitamos un pequeño ajuste:

En `backend/config/settings.py`, la sección de base de datos debería verse así:

```python
# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Render/Railway provee DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True if 'postgresql' in DATABASE_URL else False
        )
    }
else:
    # Local development (MySQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'devtrack'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            }
        }
    }
```

---

## 🔑 PASO 2: Commit y Push a GitHub

```powershell
# Agregar archivos modificados
git add backend/requirements.txt
git add backend/build.sh
git add backend/config/settings.py
git add render.yaml

# Commit
git commit -m "feat: Configuración para Render.com"

# Push
git push origin main
```

---

## 🌐 PASO 3: Desplegar Backend en Render

### 3.1 Crear cuenta
1. Ve a https://render.com
2. **Sign up with GitHub**
3. Autoriza a Render

### 3.2 Crear Web Service

1. Dashboard → **New +** → **Web Service**
2. **Connect your GitHub repo**: Selecciona `DevTrack`
3. Configura:
   - **Name**: `devtrack-backend`
   - **Region**: Oregon (más cerca)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Pre-Deploy Command**: `python manage.py migrate` ⭐ **IMPORTANTE**
   - **Start Command**: `gunicorn config.wsgi:application`
   - **Instance Type**: **Free**

**⚠️ CRÍTICO**: El **Pre-Deploy Command** es donde van las migraciones. Esto se ejecuta DESPUÉS del build cuando la BD ya está disponible.

### 3.3 Crear Base de Datos PostgreSQL

1. Dashboard → **New +** → **PostgreSQL**
2. Configura:
   - **Name**: `devtrack-db`
   - **Database**: `devtrack`
   - **User**: (auto-generado)
   - **Region**: Oregon (misma que el backend)
   - **Instance Type**: **Free**
3. Click **Create Database**

### 3.4 Vincular DB al Backend

1. Ve a tu Web Service (`devtrack-backend`)
2. Tab **Environment**
3. Click **Add Environment Variable**
4. Busca y conecta: **DATABASE_URL** → Selecciona `devtrack-db`
5. Render automáticamente conectará la BD

### 3.5 Configurar Variables de Entorno

En **Environment**, agrega estas variables:

```bash
# Django Core
DJANGO_SECRET_KEY=generate-a-random-secret-key-here
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings
PYTHON_VERSION=3.11.0

# Database (ya conectada automáticamente)
DATABASE_URL=[Conectada desde la BD]

# CORS (actualizar después con URL de frontend)
CORS_ALLOWED_ORIGINS=https://devtrack-frontend.onrender.com

# URLs
FRONTEND_URL=https://devtrack-frontend.onrender.com

# Email (tus credenciales)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=heberyesiddazatoloza@gmail.com
EMAIL_HOST_PASSWORD=bbyb vcsg qwpn exrl
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=DevTrack <heberyesiddazatoloza@gmail.com>

# Turnstile
TURNSTILE_SECRET_KEY=0x4AAAAAAB195dF8QdRbAuGMD3aVvy8Q_V4

# Rate Limiting
RATELIMIT_ENABLE=True

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3.6 Deploy

1. Click **Create Web Service**
2. Render automáticamente iniciará el build (tarda 3-5 min)
3. Una vez completado, tendrás una URL como: `https://devtrack-backend.onrender.com`
4. **ANOTA ESTA URL**

---

## 🎨 PASO 4: Desplegar Frontend en Render

### 4.1 Crear Static Site

1. Dashboard → **New +** → **Static Site**
2. Conecta tu repo `DevTrack`
3. Configura:
   - **Name**: `devtrack-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### 4.2 Variables de Entorno

En **Environment**, agrega:

```bash
VITE_API_BASE_URL=https://devtrack-backend.onrender.com
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

### 4.3 Deploy

1. Click **Create Static Site**
2. Render construirá tu frontend (2-3 min)
3. URL final: `https://devtrack-frontend.onrender.com`

---

## 🔗 PASO 5: Conectar Frontend ↔ Backend

### 5.1 Actualizar CORS en Backend

1. Ve a `devtrack-backend` → **Environment**
2. Edita `CORS_ALLOWED_ORIGINS`:
   ```
   https://devtrack-frontend.onrender.com
   ```
3. Edita `FRONTEND_URL`:
   ```
   https://devtrack-frontend.onrender.com
   ```

### 5.2 Actualizar ALLOWED_HOSTS

En tu `settings.py`, ya tienes `ALLOWED_HOSTS = ['*']`, pero es mejor restringirlo:

```python
ALLOWED_HOSTS = [
    'devtrack-backend.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1'
]
```

### 5.3 Redeploy

Render auto-redesplegará al detectar cambios en las variables.

---

## 👤 PASO 6: Crear Superusuario

### Opción 1: Usando Shell de Render

1. Ve a `devtrack-backend` → Tab **Shell**
2. Ejecuta:
   ```bash
   python manage.py createsuperuser
   ```

### Opción 2: Usando script remoto

Puedes usar el script `create_superuser_remote.py` que tienes en la raíz del proyecto.

---

## ✅ PASO 7: Verificar Todo

### Backend:
- ✅ Admin: `https://devtrack-backend.onrender.com/admin`
- ✅ API Docs: `https://devtrack-backend.onrender.com/api/docs/`

### Frontend:
- ✅ App: `https://devtrack-frontend.onrender.com`

### Pruebas:
1. Registrar usuario
2. Login
3. Verificación de email
4. Crear materia (admin)
5. Inscribir estudiantes

---

## ⚠️ Limitaciones del Plan GRATUITO

1. **Backend se "duerme"** después de 15 min sin uso
   - Primer request tarda ~30 segundos en "despertar"
   - Requests siguientes son instantáneos
   
2. **Base de datos PostgreSQL gratis**:
   - 1 GB de almacenamiento
   - Expira después de 90 días (pero puedes crear una nueva)
   
3. **750 horas/mes** = ~31 días completos (suficiente para 1 proyecto)

4. **Build time**: 3-5 minutos por deploy

---

## 🔄 Migrar Datos desde Railway

Si ya tienes datos en Railway MySQL y quieres migrarlos a Render PostgreSQL:

### Paso 1: Exportar desde Railway
```bash
# Conectarte a Railway MySQL y exportar
railway run python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json
```

### Paso 2: Importar en Render
```bash
# En Render Shell
python manage.py loaddata data.json
```

**Alternativa**: Empezar desde cero (solo para desarrollo).

---

## 🆚 Comparación con Otras Opciones

| Plataforma | Backend | Base de Datos | Limitaciones | Recomendación |
|------------|---------|---------------|--------------|---------------|
| **Render.com** | ✅ Gratis | ✅ PostgreSQL 1GB | Se duerme 15 min | ⭐ MEJOR para apps pequeñas |
| **Railway** | ⚠️ $5/mes* | ✅ MySQL/PostgreSQL | Crédito limitado | Bueno pero ya no es gratis |
| **Vercel** | ⚠️ Serverless | ❌ Solo frontend | Requiere adaptar Django | Solo para SPA/SSG |
| **Fly.io** | ✅ 3 VMs | ✅ PostgreSQL | Solo PostgreSQL | Alternativa sólida |
| **PythonAnywhere** | ✅ Gratis | ✅ MySQL 512MB | Sin SSL gratis | No recomendado |

\* Railway ya no tiene plan gratis permanente, solo $5 USD de crédito inicial.

---

## 💡 Consejos Pro

### 1. **Mantener Backend "despierto"**
Usa un servicio como **UptimeRobot** (gratis) para hacer ping cada 5 minutos:
- https://uptimerobot.com
- Configura: `https://devtrack-backend.onrender.com/admin/login/`
- Frecuencia: cada 5 minutos

### 2. **Monitoreo de Logs**
Render Dashboard → tu servicio → **Logs** (en tiempo real)

### 3. **Deploy Automático**
Cada `git push` a `main` → Redeploy automático (backend + frontend)

### 4. **Revertir Deploy**
Render → **Manual Deploy** → Selecciona commit anterior

---

## 📝 Checklist Final

- [ ] `psycopg2-binary` agregado a `requirements.txt`
- [ ] `build.sh` creado en `backend/`
- [ ] `settings.py` actualizado para PostgreSQL
- [ ] Código pusheado a GitHub
- [ ] Backend desplegado en Render
- [ ] Base de datos PostgreSQL creada
- [ ] Variables de entorno configuradas
- [ ] Frontend desplegado en Render
- [ ] CORS actualizado con URL de frontend
- [ ] Superusuario creado
- [ ] Pruebas funcionales completadas

---

## 🎉 ¡Listo!

Tu app DevTrack ahora está 100% GRATIS en Render.com

**URLs finales:**
- Frontend: `https://devtrack-frontend.onrender.com`
- Backend API: `https://devtrack-backend.onrender.com/api/docs/`
- Admin: `https://devtrack-backend.onrender.com/admin`

---

## 🆘 Troubleshooting

### Error: "Can't connect to MySQL server on '127.0.0.1'"
**Causa**: Django intenta conectarse a MySQL durante el build, pero:
1. Render usa PostgreSQL (no MySQL)
2. La BD no está disponible durante build time

**Solución**: 
1. **NO ejecutar migraciones en `build.sh`**
2. Usar **Pre-Deploy Command** en Render:
   - Ve a tu Web Service → Settings
   - En **Pre-Deploy Command**: `python manage.py migrate`
3. El `build.sh` debe tener solo:
   ```bash
   pip install -r requirements.txt
   python manage.py collectstatic --noinput
   ```

### Error: "Application failed to respond"
**Causa**: Backend dormido o error en el código
**Solución**: 
1. Revisa logs en Render
2. Espera 30 segundos (si estaba dormido)

### Error: "Database connection failed"
**Solución**: 
1. Verifica que `DATABASE_URL` esté conectada
2. En Shell: `python manage.py migrate`

### Error: CORS
**Solución**: Verifica `CORS_ALLOWED_ORIGINS` incluya la URL exacta de Render

### Frontend no conecta
**Solución**: 
1. Verifica `VITE_API_BASE_URL` en variables de entorno
2. Redeploy frontend

---

¿Necesitas ayuda con algún paso? ¡Solo pregunta! 🚀
