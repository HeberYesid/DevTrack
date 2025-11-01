# 🚀 Guía de Despliegue - DevTrack

## 📋 Archivos Preparados para Despliegue

✅ **Backend:**
- `requirements.txt` - Actualizado con gunicorn y whitenoise
- `Procfile` - Para Railway/Render
- `railway.json` - Configuración específica de Railway
- `runtime.txt` - Versión de Python
- `settings.py` - Configurado con WhiteNoise para archivos estáticos

✅ **Frontend:**
- `vercel.json` - Configuración para Vercel

---

## 🎯 Opción Recomendada: Railway + Vercel

### Ventajas:
- ✅ **Totalmente GRATIS** para empezar ($5 USD gratis/mes en Railway)
- ✅ Backend y Base de Datos en un solo lugar
- ✅ Configuración automática
- ✅ HTTPS incluido
- ✅ Deploy automático desde GitHub

---

## 📦 PASO 1: Preparar el Repositorio Git

### 1.1 Verificar que tienes Git configurado

```powershell
# Verificar si ya tienes un repositorio
git status

# Si no está inicializado, inicializar
git init

# Agregar origin (si aún no lo tienes)
git remote add origin https://github.com/HeberYesid/DevTrack.git
```

### 1.2 Commit de los cambios de configuración

```powershell
# Agregar archivos modificados
git add backend/requirements.txt
git add backend/Procfile
git add backend/railway.json
git add backend/runtime.txt
git add backend/config/settings.py
git add frontend/vercel.json

# Commit
git commit -m "feat: Configuración para despliegue en Railway y Vercel"

# Push al repositorio
git push origin main
```

---

## 🚂 PASO 2: Desplegar Backend en Railway

### 2.1 Crear cuenta en Railway
1. Ve a https://railway.app
2. **Sign up with GitHub** (usa tu cuenta de GitHub)
3. Autoriza a Railway

### 2.2 Crear nuevo proyecto

1. Click en **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Selecciona tu repositorio **DevTrack**
4. Railway detectará automáticamente que es Django

### 2.3 Configurar Base de Datos MySQL

1. En tu proyecto de Railway, click en **"+ New"**
2. Selecciona **"Database" → "Add MySQL"**
3. Railway creará automáticamente una base de datos MySQL
4. Anota las credenciales (o déjalas, Railway las conectará automáticamente)

### 2.4 Configurar Variables de Entorno del Backend

En Railway, ve a tu servicio Django → **Variables** y agrega:

```bash
# Django
DJANGO_SECRET_KEY=your-super-secret-key-change-this-in-production
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings
ALLOWED_HOSTS=.railway.app,your-domain.com

# Database (Railway las configura automáticamente, pero verifica)
DB_NAME=${{MySQL.MYSQL_DATABASE}}
DB_USER=${{MySQL.MYSQL_USER}}
DB_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
DB_HOST=${{MySQL.MYSQL_HOST}}
DB_PORT=${{MySQL.MYSQL_PORT}}

# CORS (agregará la URL de Vercel después)
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Email (usar tus credenciales reales)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=heberyesiddazatoloza@gmail.com
EMAIL_HOST_PASSWORD=bbyb vcsg qwpn exrl
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=DevTrack <heberyesiddazatoloza@gmail.com>

# Turnstile
TURNSTILE_SECRET_KEY=0x4AAAAAAB195dF8QdRbAuGMD3aVvy8Q_V4

# URLs (actualizar después con dominios reales)
FRONTEND_URL=https://your-frontend.vercel.app
API_BASE_URL=https://your-backend.railway.app

# Rate Limiting
RATELIMIT_ENABLE=True

# Security (para producción)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2.5 Configurar el Root Directory

1. En Railway → Settings
2. **Root Directory**: `backend`
3. **Start Command**: `gunicorn config.wsgi:application --log-file -`

### 2.6 Deploy

1. Click en **"Deploy"**
2. Espera a que termine el build (puede tardar 2-5 minutos)
3. Una vez desplegado, Railway te dará una URL como: `https://devtrack-production.up.railway.app`
4. **ANOTA ESTA URL**, la necesitarás para el frontend

### 2.7 Crear Superusuario

En Railway, ve a tu servicio → **Terminal** y ejecuta:

```bash
python manage.py createsuperuser
```

---

## 🌐 PASO 3: Desplegar Frontend en Vercel

### 3.1 Crear cuenta en Vercel
1. Ve a https://vercel.com
2. **Sign up with GitHub**
3. Autoriza a Vercel

### 3.2 Importar proyecto

1. Click en **"Add New..." → "Project"**
2. Selecciona tu repositorio **DevTrack**
3. Vercel detectará automáticamente que es Vite

### 3.3 Configurar el proyecto

**Framework Preset**: Vite
**Root Directory**: `frontend`
**Build Command**: `npm run build`
**Output Directory**: `dist`

### 3.4 Configurar Variables de Entorno

En **Environment Variables**, agrega:

```bash
VITE_API_BASE_URL=https://your-backend.railway.app
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

**IMPORTANTE**: Reemplaza `your-backend.railway.app` con la URL real de Railway del paso anterior.

### 3.5 Deploy

1. Click en **"Deploy"**
2. Espera a que termine el build (1-2 minutos)
3. Vercel te dará una URL como: `https://devtrack.vercel.app`

---

## 🔗 PASO 4: Conectar Frontend con Backend

### 4.1 Actualizar CORS en Railway

Regresa a Railway → Variables de entorno del backend y actualiza:

```bash
CORS_ALLOWED_ORIGINS=https://devtrack.vercel.app
FRONTEND_URL=https://devtrack.vercel.app
```

### 4.2 Actualizar ALLOWED_HOSTS

```bash
ALLOWED_HOSTS=.railway.app,.vercel.app,devtrack-production.up.railway.app
```

### 4.3 Redeploy Backend

Railway automáticamente redeployará con los nuevos cambios.

---

## ✅ PASO 5: Verificar el Despliegue

### 5.1 Probar Backend

Abre en tu navegador:
- `https://your-backend.railway.app/admin` - Panel admin
- `https://your-backend.railway.app/api/docs/` - API Docs

### 5.2 Probar Frontend

Abre en tu navegador:
- `https://devtrack.vercel.app` - Tu aplicación

### 5.3 Pruebas funcionales

1. **Registro de usuario** - Debe funcionar
2. **Login** - Debe funcionar
3. **Email de verificación** - Verifica que llegue
4. **Creación de materias** (como admin)
5. **Inscripción de estudiantes**

---

## 🔧 Troubleshooting

### Error: "DisallowedHost"
**Solución**: Agrega tu dominio a `ALLOWED_HOSTS` en Railway

### Error: CORS
**Solución**: Verifica que `CORS_ALLOWED_ORIGINS` en Railway incluya tu URL de Vercel

### Error: "Static files not found"
**Solución**: En Railway terminal:
```bash
python manage.py collectstatic --noinput
```

### Error: "Database connection"
**Solución**: Verifica las variables `DB_*` en Railway. Railway debe configurarlas automáticamente.

### Frontend no conecta con Backend
**Solución**: 
1. Verifica `VITE_API_BASE_URL` en Vercel
2. Redeploy el frontend desde Vercel

---

## 🎨 PASO 6: Configurar Dominio Personalizado (Opcional)

### Para el Backend (Railway):
1. Railway → Settings → Domains
2. Agrega tu dominio: `api.tudominio.com`
3. Configura el DNS CNAME apuntando a Railway

### Para el Frontend (Vercel):
1. Vercel → Settings → Domains
2. Agrega tu dominio: `tudominio.com`
3. Configura el DNS según las instrucciones de Vercel

---

## 📊 Monitoreo y Logs

### Railway (Backend):
- **Logs**: Click en tu servicio → Deployments → View logs
- **Métricas**: Railway muestra uso de CPU/RAM/Red

### Vercel (Frontend):
- **Analytics**: Vercel → Analytics
- **Logs**: Vercel → Deployments → Function Logs

---

## 🔄 Deploys Automáticos

Ambas plataformas ya están configuradas para **deploy automático**:

- Cada `git push` a `main` → Redeploy automático
- Railway reconstruirá el backend
- Vercel reconstruirá el frontend

---

## 💰 Costos

### Railway (Backend + Database):
- **Gratis**: $5 USD de crédito/mes (suficiente para desarrollo)
- **Hobby Plan**: $5 USD/mes (cuando se acabe el crédito)

### Vercel (Frontend):
- **Gratis**: Ilimitado para proyectos personales
- Deploy automático incluido

---

## 📝 Checklist Final

- [ ] Repositorio Git actualizado y pusheado
- [ ] Backend desplegado en Railway
- [ ] Base de datos MySQL creada en Railway
- [ ] Variables de entorno configuradas en Railway
- [ ] Superusuario creado
- [ ] Frontend desplegado en Vercel
- [ ] Variables de entorno configuradas en Vercel
- [ ] CORS actualizado con URL de Vercel
- [ ] Pruebas funcionales completadas
- [ ] (Opcional) Dominio personalizado configurado

---

## 🎉 ¡Listo!

Tu aplicación DevTrack ahora está en producción y accesible desde cualquier parte del mundo.

**URLs finales:**
- Frontend: `https://devtrack.vercel.app`
- Backend API: `https://devtrack-production.up.railway.app/api/docs/`
- Admin Panel: `https://devtrack-production.up.railway.app/admin`

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs** en Railway/Vercel
2. **Verifica las variables de entorno**
3. **Consulta la documentación**:
   - Railway: https://docs.railway.app
   - Vercel: https://vercel.com/docs

¿Necesitas ayuda? Déjame saber y te guío paso a paso.
