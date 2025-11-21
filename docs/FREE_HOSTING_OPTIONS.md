# 🆓 Alternativas Gratuitas para Desplegar DevTrack

## 📊 Comparación de Servicios Gratuitos (2025)

| Plataforma | Backend | Base de Datos | Limitaciones | Costo Mensual | Recomendación |
|------------|---------|---------------|--------------|---------------|---------------|
| **🏆 Render.com** | ✅ 750h/mes | ✅ PostgreSQL 1GB | Se duerme 15min | $0 | ⭐⭐⭐⭐⭐ |
| **Railway.app** | ⚠️ $5 crédito | ✅ MySQL/PostgreSQL | Crédito se agota | ~$5-10/mes | ⭐⭐⭐⭐ |
| **Fly.io** | ✅ 3 VMs | ✅ PostgreSQL 3GB | Solo PostgreSQL | $0 | ⭐⭐⭐⭐ |
| **Vercel + Supabase** | ⚠️ Serverless | ✅ PostgreSQL 500MB | Requiere adaptar | $0 | ⭐⭐⭐ |
| **PythonAnywhere** | ✅ 1 app | ✅ MySQL 512MB | Sin SSL, lento | $0 | ⭐⭐ |

---

## 🥇 Opción 1: Render.com (RECOMENDADA)

### ✅ Ventajas
- **100% GRATIS permanente** (750 horas/mes = suficiente para 1 app)
- Base de datos PostgreSQL incluida (1 GB)
- Deploy automático desde GitHub
- HTTPS incluido
- Muy similar a Railway
- Fácil configuración

### ⚠️ Desventajas
- Backend se "duerme" después de 15 min sin uso
- Primer request tarda ~30 segundos en despertar
- BD expira a los 90 días (pero puedes crear otra nueva)

### 📚 Documentación
Ver: [`docs/RENDER_DEPLOY.md`](./RENDER_DEPLOY.md)

### 🚀 Resumen de pasos
```powershell
# 1. Agregar soporte PostgreSQL
# Ya está configurado en el código

# 2. Commit y push
git add .
git commit -m "feat: Soporte para Render.com"
git push origin main

# 3. En Render.com
- Crear cuenta con GitHub
- New Web Service → Conectar repo
- New PostgreSQL → Base de datos
- Vincular DATABASE_URL
- Deploy automático
```

**Tiempo estimado**: 15 minutos

---

## 🥈 Opción 2: Fly.io

### ✅ Ventajas
- **3 VMs pequeñas gratis**
- No se duerme (siempre activo)
- PostgreSQL 3GB incluida
- Buen rendimiento
- Múltiples regiones

### ⚠️ Desventajas
- Configuración más compleja (requiere CLI)
- Solo soporta PostgreSQL (no MySQL)
- Requiere tarjeta de crédito (pero no cobra)

### 🚀 Pasos rápidos

1. **Instalar Fly CLI**:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

2. **Login**:
```powershell
fly auth login
```

3. **Configurar app**:
```powershell
cd backend
fly launch --name devtrack-backend
```

4. **Crear base de datos**:
```powershell
fly postgres create --name devtrack-db
fly postgres attach devtrack-db
```

5. **Configurar secrets**:
```powershell
fly secrets set DJANGO_SECRET_KEY=your-secret-key
fly secrets set EMAIL_HOST_PASSWORD=your-password
```

6. **Deploy**:
```powershell
fly deploy
```

**Tiempo estimado**: 30 minutos

---

## 🥉 Opción 3: Vercel + Supabase

### ✅ Ventajas
- Totalmente gratis
- Excelente rendimiento
- Base de datos PostgreSQL (500MB)
- Supabase incluye autenticación

### ⚠️ Desventajas
- Requiere adaptar Django a serverless
- Más complejo de configurar
- Limitaciones de tiempo de ejecución (10 seg max)

### 🚀 Configuración

**Backend (Vercel Serverless)**:
Requiere crear `vercel.json` especial y adaptar Django:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "config/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "config/wsgi.py"
    }
  ]
}
```

**Base de datos (Supabase)**:
1. Crear cuenta en https://supabase.com
2. Crear proyecto
3. Obtener DATABASE_URL
4. Configurar en Vercel

**⚠️ No recomendado** para principiantes debido a la complejidad.

---

## 🚫 NO Recomendadas

### ❌ PythonAnywhere
- Sin SSL en plan gratuito
- Muy lento
- Interfaz anticuada
- Solo para pruebas

### ❌ Heroku
- Ya no tiene plan gratuito (desde 2022)
- Mínimo $5/mes por dyno

### ❌ Google Cloud / AWS
- No tienen planes gratis permanentes
- Muy caros después del trial
- Demasiado complejos para apps pequeñas

---

## 🎯 Recomendación Final

Para **DevTrack** (app pequeña, académica):

### 🏆 **Usa Render.com**

**Razones**:
1. ✅ 100% gratis permanente
2. ✅ Configuración casi idéntica a Railway
3. ✅ Base de datos incluida
4. ✅ Deploy automático
5. ✅ No requiere tarjeta de crédito
6. ✅ Fácil de configurar (15 minutos)

**Acepta**:
- Backend se duerme (solo molesto en primera carga)
- BD expira a los 90 días (fácil crear nueva)

### 🥈 **Si necesitas que esté siempre activo**: Fly.io

### 🥉 **Si ya tienes experiencia con serverless**: Vercel + Supabase

---

## 💡 Tips para Mantener Backend Activo (Render)

### Opción 1: UptimeRobot (Gratis)
1. Crear cuenta en https://uptimerobot.com
2. Agregar monitor:
   - URL: `https://devtrack-backend.onrender.com/admin/login/`
   - Intervalo: cada 5 minutos
   - Tipo: HTTP(s)

### Opción 2: Cron-job.org (Gratis)
1. Crear cuenta en https://cron-job.org
2. Crear job:
   - URL: tu backend
   - Cada 5 minutos

### Opción 3: Script local (GitHub Actions)
```yaml
# .github/workflows/keepalive.yml
name: Keep Backend Alive
on:
  schedule:
    - cron: '*/5 * * * *'  # Cada 5 minutos
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - run: curl https://devtrack-backend.onrender.com/admin/login/
```

---

## 📦 Archivos Preparados

Ya tienes todo listo para Render:

- ✅ `backend/requirements.txt` - Con `psycopg2-binary`
- ✅ `backend/build.sh` - Script de build para Render
- ✅ `backend/config/settings.py` - Soporta PostgreSQL y MySQL
- ✅ `render.yaml` - Blueprint de configuración
- ✅ `docs/RENDER_DEPLOY.md` - Guía detallada paso a paso

---

## 🚀 Siguiente Paso

**Sigue la guía completa**: [`docs/RENDER_DEPLOY.md`](./RENDER_DEPLOY.md)

O ejecuta estos comandos para empezar:

```powershell
# Verificar que todos los archivos estén listos
git status

# Commit y push
git add .
git commit -m "feat: Preparado para Render.com"
git push origin main

# Ir a Render.com y seguir los pasos
```

---

## ❓ Preguntas Frecuentes

### ¿Cuánto cuesta realmente?
**Render**: $0/mes permanente (con limitaciones aceptables)
**Fly.io**: $0/mes (requiere tarjeta, no cobra)
**Railway**: ~$5-10/mes después del crédito inicial

### ¿Cuál es más rápida?
**Fly.io** > **Railway** > **Render** (en actividad)
**Render** es lenta solo en el primer request después de dormir.

### ¿Puedo usar MySQL en lugar de PostgreSQL?
**Render**: No, solo PostgreSQL gratis
**Railway**: Sí, soporta MySQL
**Fly.io**: No, solo PostgreSQL

### ¿Mis datos están seguros?
Todas las plataformas tienen:
- ✅ HTTPS obligatorio
- ✅ Backups automáticos (en planes pagos)
- ✅ Encriptación
Para apps pequeñas académicas, son seguros.

### ¿Qué pasa si supero el límite gratuito?
**Render**: App se detiene hasta el próximo mes
**Fly.io**: Te notifican pero no cobran
**Railway**: Empieza a cobrar automáticamente

---

## 📞 Soporte

- **Render**: https://render.com/docs
- **Fly.io**: https://fly.io/docs
- **DevTrack Issues**: https://github.com/HeberYesid/DevTrack/issues

¿Dudas? Abre un issue o consulta las guías en `docs/`.
