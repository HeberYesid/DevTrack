# 🛡️ Rate Limiting - Guía de Inicio Rápido

## ✅ ¿Qué se ha implementado?

El sistema de **Rate Limiting** protege tu aplicación contra:
- ⚔️ Ataques de fuerza bruta en login/registro
- 🤖 Bots y automatización maliciosa
- 📧 Abuso del sistema de correos
- 💥 Sobrecarga del servidor

## 🚀 Instalación Rápida

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

Esto instalará `django-ratelimit==4.1.0` automáticamente.

### 2. Verificar Configuración

El archivo `.env` ya debe tener (si no, agrégalo):

```env
RATELIMIT_ENABLE=True
```

### 3. Iniciar el Servidor

```bash
python manage.py runserver
```

¡Listo! El rate limiting está activo. 🎉

## 🧪 Verificar que Funciona

### Opción 1: Script Automático (Recomendado)

```bash
# Ejecuta el script de prueba
python test_rate_limit_simple.py
```

Este script:
- ✓ Verifica que el servidor esté corriendo
- ✓ Hace 7 intentos de login
- ✓ Confirma que el 6to intento es bloqueado (HTTP 429)
- ✓ Muestra un resumen de resultados

### Opción 2: Prueba Manual con cURL

**Windows (PowerShell):**
```powershell
# Hacer 6 intentos de login
1..6 | ForEach-Object {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"email":"test@test.com","password":"test","turnstile_token":"test"}' `
        -ErrorAction SilentlyContinue
    Write-Host "Intento $_: $($response)"
}
```

**Linux/Mac (bash):**
```bash
# Hacer 6 intentos de login
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test","turnstile_token":"test"}'
  echo "Intento $i"
done
```

**Resultado esperado:**
- Intentos 1-5: Error 400/401 (credenciales incorrectas - normal)
- Intento 6: **Error 429** ✅ (rate limit - bloqueado)

### Opción 3: Pruebas Automatizadas Completas

```bash
# Ejecutar todas las pruebas de rate limiting
pytest backend/accounts/tests/test_ratelimit.py -v

# Ver cobertura de código
pytest backend/accounts/tests/test_ratelimit.py --cov=accounts.ratelimit --cov-report=html
```

## 📊 Límites Configurados

| Endpoint | Límite | Período |
|----------|--------|---------|
| Login | 5 intentos | 1 minuto |
| Registro | 5 intentos | 1 minuto |
| Verificar código | 3 intentos | 1 minuto |
| Reenviar código | 3 intentos | 5 minutos |
| Cambiar contraseña | 3 intentos | 1 minuto |

## 🔧 Personalizar Límites

Edita `backend/accounts/ratelimit.py`:

```python
def ratelimit_auth(view_func):
    """Cambiar de 5/m a 10/m"""
    return apply_ratelimit(key='ip', rate='10/m', method='POST', block=True)(view_func)
```

## 📚 Documentación Completa

- **Resumen ejecutivo**: `RATE_LIMITING_SUMMARY.md`
- **Documentación detallada**: `RATE_LIMITING_DOCS.md`
- **Diagrama visual**: `RATE_LIMITING_VISUAL.md`

## 🐛 Solución de Problemas

### "Rate limiting no funciona"

1. Verifica instalación:
   ```bash
   pip show django-ratelimit
   ```

2. Confirma que esté habilitado en `.env`:
   ```env
   RATELIMIT_ENABLE=True
   ```

3. Reinicia el servidor:
   ```bash
   # Ctrl+C para detener
   python manage.py runserver
   ```

### "Siempre me bloquea"

- Espera 1 minuto entre pruebas
- O limpia el cache:
  ```bash
  python manage.py shell
  >>> from django.core.cache import cache
  >>> cache.clear()
  >>> exit()
  ```

## 🚀 Para Producción

### 1. Instalar Redis (Recomendado)

```bash
pip install redis django-redis
```

### 2. Actualizar `settings.py`

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Iniciar Redis

```bash
# Docker (más fácil)
docker run -d -p 6379:6379 redis:alpine

# O instalar Redis nativo
# Windows: https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt install redis-server
# Mac: brew install redis
```

## ✨ Características

✅ **Instalación simple**: Solo `pip install`  
✅ **Configuración automática**: Funciona out-of-the-box  
✅ **Sin cambios en código existente**: Solo decoradores agregados  
✅ **Respuestas JSON claras**: Mensajes en español  
✅ **Tests incluidos**: Suite completa de pruebas  
✅ **Documentación completa**: Múltiples guías y ejemplos  

## 🎯 Próximos Pasos

1. ✅ **Probado localmente** - Ejecuta `test_rate_limit_simple.py`
2. 🔧 **Ajusta límites** - Modifica según tu tráfico
3. 🧪 **Tests completos** - Ejecuta pytest
4. 🚀 **Producción** - Configura Redis
5. 📊 **Monitoreo** - Implementa logging (opcional)

## 🆘 Soporte

- **Documentación completa**: `RATE_LIMITING_DOCS.md`
- **Ejemplos visuales**: `RATE_LIMITING_VISUAL.md`
- **Tests de referencia**: `accounts/tests/test_ratelimit.py`
- **Código fuente**: `accounts/ratelimit.py`

---

**¡Tu aplicación ahora está protegida contra ataques de fuerza bruta!** 🛡️✨
