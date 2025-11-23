# 🚀 Migración Rápida a Servicios Gratuitos

## ✅ Tu Aplicación Está Lista

He preparado todo lo necesario para migrar tu app de Railway a servicios **100% gratuitos**:

### 📦 Archivos Modificados/Creados

1. ✅ **`backend/requirements.txt`** - Agregado `psycopg2-binary` para PostgreSQL
2. ✅ **`backend/build.sh`** - Script de build para Render
3. ✅ **`backend/config/settings.py`** - Soporte dual MySQL/PostgreSQL
4. ✅ **`render.yaml`** - Configuración de blueprint para Render
5. ✅ **`docs/RENDER_DEPLOY.md`** - Guía paso a paso completa
6. ✅ **`docs/FREE_HOSTING_OPTIONS.md`** - Comparación de opciones
7. ✅ **`README.md`** - Actualizado con sección de despliegue
8. ✅ **`scripts/prepare-render.ps1`** - Script para commit automático

---

## 🎯 Opción Recomendada: Render.com

### ¿Por qué Render?
- ✅ **100% gratis** (750 horas/mes = suficiente)
- ✅ Base de datos PostgreSQL incluida (1GB)
- ✅ Deploy automático desde GitHub
- ✅ HTTPS incluido
- ✅ Similar a Railway, fácil de configurar
- ⚠️ Se duerme después de 15 min (solo molesto en primera carga)

### ⏱️ Tiempo Estimado
**15 minutos** desde cero hasta app en producción

---

## 🚀 Pasos Rápidos

### 1️⃣ Commit y Push (2 minutos)

**Opción A: Automático (Recomendado)**
```powershell
.\scripts\prepare-render.ps1
```

**Opción B: Manual**
```powershell
git add .
git commit -m "feat: Preparado para Render.com"
git push origin main
```

### 2️⃣ Crear cuenta en Render (1 minuto)
1. Ve a https://render.com
2. Click **"Sign up with GitHub"**
3. Autoriza a Render

### 3️⃣ Desplegar Backend (5 minutos)

1. **Crear Web Service**:
   - Dashboard → **New +** → **Web Service**
   - Conecta tu repo `DevTrack`
   - Configuración:
     - Name: `devtrack-backend`
     - Root Directory: `backend`
     - Build Command: `./build.sh`
     - Start Command: `gunicorn config.wsgi:application`
     - Instance Type: **Free**

2. **Crear Base de Datos**:
   - Dashboard → **New +** → **PostgreSQL**
   - Name: `devtrack-db`
   - Instance Type: **Free**

3. **Vincular BD al Backend**:
   - En el Web Service → **Environment**
   - Add Environment Variable → Conecta `DATABASE_URL` a `devtrack-db`

4. **Variables de Entorno**:
   ```bash
   DJANGO_SECRET_KEY=<genera-uno-aleatorio>
   DJANGO_DEBUG=False
   CORS_ALLOWED_ORIGINS=https://tu-frontend.onrender.com
   EMAIL_HOST_USER=heberyesiddazatoloza@gmail.com
   EMAIL_HOST_PASSWORD=bbyb vcsg qwpn exrl
   TURNSTILE_SECRET_KEY=0x4AAAAAAB195dF8QdRbAuGMD3aVvy8Q_V4
   ```

5. **Deploy**: Render lo hace automáticamente ✨

### 4️⃣ Desplegar Frontend (5 minutos)

1. **Crear Static Site**:
   - Dashboard → **New +** → **Static Site**
   - Conecta repo `DevTrack`
   - Configuración:
     - Name: `devtrack-frontend`
     - Root Directory: `frontend`
     - Build Command: `npm install && npm run build`
     - Publish Directory: `dist`

2. **Variables de Entorno**:
   ```bash
   VITE_API_BASE_URL=https://devtrack-backend.onrender.com
   VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
   ```

3. **Deploy**: Automático ✨

### 5️⃣ Conectar Frontend ↔ Backend (2 minutos)

1. Actualiza `CORS_ALLOWED_ORIGINS` en backend con la URL real del frontend
2. Render redesplegará automáticamente

### 6️⃣ Crear Superusuario

En Render → Backend → **Shell**:
```bash
python manage.py createsuperuser
```

---

## 🎉 ¡Listo!

Tu app estará disponible en:
- 🌐 Frontend: `https://devtrack-frontend.onrender.com`
- 🔌 Backend API: `https://devtrack-backend.onrender.com/api/docs/`
- 👤 Admin: `https://devtrack-backend.onrender.com/admin`

---

## 📚 Documentación Completa

Si necesitas más detalles:

- **Guía paso a paso**: [`docs/RENDER_DEPLOY.md`](../docs/RENDER_DEPLOY.md)
- **Comparación de opciones**: [`docs/FREE_HOSTING_OPTIONS.md`](../docs/FREE_HOSTING_OPTIONS.md)

---

## 🆚 Otras Opciones

### 🥈 Fly.io (Si necesitas que esté siempre activo)
- ✅ No se duerme
- ✅ 3 VMs gratis
- ⚠️ Más complejo de configurar

### 🥉 Railway (Ya no es gratis)
- ⚠️ ~$5-10/mes después del crédito inicial
- ✅ Muy fácil de usar

Ver comparación completa en [`docs/FREE_HOSTING_OPTIONS.md`](../docs/FREE_HOSTING_OPTIONS.md)

---

## 💡 Tips Pro

### Mantener Backend Activo
Usa **UptimeRobot** (gratis) para hacer ping cada 5 minutos:
1. Crea cuenta en https://uptimerobot.com
2. Agrega monitor: `https://devtrack-backend.onrender.com/admin/login/`
3. Intervalo: 5 minutos

Esto evita que el backend se duerma.

---

## ⚠️ Importante: Limitaciones Gratuitas

| Concepto | Límite | ¿Es Problema? |
|----------|--------|---------------|
| Horas/mes | 750 | ❌ Suficiente para 1 app |
| Base de datos | 1 GB | ❌ Más que suficiente |
| Se duerme | 15 min | ⚠️ Solo primera carga |
| BD expira | 90 días | ⚠️ Puedes crear nueva |
| Build time | 3-5 min | ❌ Solo en deploy |

**Para una app académica pequeña, Render es perfecto.**

---

## 🆘 Problemas Comunes

### Backend no responde
**Solución**: Espera ~30 segundos (estaba dormido)

### CORS error
**Solución**: Verifica que `CORS_ALLOWED_ORIGINS` tenga la URL correcta

### Database error
**Solución**: Verifica que `DATABASE_URL` esté conectada

Ver más en [`docs/RENDER_DEPLOY.md`](../docs/RENDER_DEPLOY.md)

---

## 📞 Siguiente Paso

```powershell
# 1. Commit y push
.\scripts\prepare-render.ps1

# 2. Ir a Render.com y seguir los pasos
# 3. ¡Listo en 15 minutos!
```

---

## 💬 ¿Necesitas Ayuda?

- **Guía detallada**: [`docs/RENDER_DEPLOY.md`](../docs/RENDER_DEPLOY.md)
- **Opciones alternativas**: [`docs/FREE_HOSTING_OPTIONS.md`](../docs/FREE_HOSTING_OPTIONS.md)
- **Documentación Render**: https://render.com/docs
- **GitHub Issues**: https://github.com/HeberYesid/DevTrack/issues

---

**¡Todo está listo para migrar! 🚀**
