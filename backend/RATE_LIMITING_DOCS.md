# 🛡️ Documentación de Rate Limiting

## Descripción General

El sistema de **Rate Limiting** (limitación de tasa) ha sido implementado para proteger la aplicación DevTrack contra:

- ⚔️ Ataques de fuerza bruta en login y registro
- 🤖 Bots y scrapers automatizados
- 📧 Abuso de endpoints de envío de correos
- 💥 Sobrecarga del servidor por uso excesivo

## Configuración Implementada

### Endpoints Protegidos

| Endpoint | Límite | Período | Descripción |
|----------|--------|---------|-------------|
| `/api/auth/register/` | 5 intentos | 1 minuto | Registro de nuevos usuarios |
| `/api/auth/login/` | 5 intentos | 1 minuto | Inicio de sesión |
| `/api/auth/verify-code/` | 3 intentos | 1 minuto | Verificación de código email |
| `/api/auth/resend-code/` | 3 intentos | 5 minutos | Reenvío de código de verificación |
| `/api/auth/register-teacher/` | 5 intentos | 1 minuto | Registro de profesores |
| `/api/auth/change-password/` | 3 intentos | 1 minuto | Cambio de contraseña |

### Tipos de Limitación

#### 1. **Rate Limit Estándar de Autenticación**
```python
@ratelimit_auth  # 5 intentos por minuto
```
- Aplicado a: Login, Registro
- Protege contra ataques de fuerza bruta básicos

#### 2. **Rate Limit Estricto**
```python
@ratelimit_strict_auth  # 3 intentos por minuto
```
- Aplicado a: Verificación de códigos, Cambio de contraseña
- Mayor protección para operaciones sensibles

#### 3. **Rate Limit de Email**
```python
@ratelimit_email  # 3 intentos cada 5 minutos
```
- Aplicado a: Reenvío de códigos de verificación
- Previene abuso del sistema de correo

## Instalación

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

La dependencia `django-ratelimit==4.1.0` se instalará automáticamente.

### 2. Configuración en `.env`

```env
# Habilitar/deshabilitar rate limiting (útil para desarrollo)
RATELIMIT_ENABLE=True
```

### 3. Configuración de Cache

El proyecto usa **LocMemCache** para desarrollo. Para producción, se recomienda:

**Opción A: Redis (Recomendado)**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

**Opción B: Memcached**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

## Respuestas HTTP

### Cuando se Excede el Límite

**HTTP 429 Too Many Requests**
```json
{
  "detail": "Demasiados intentos. Por favor, espera un momento antes de intentar nuevamente.",
  "error": "rate_limit_exceeded"
}
```

### Headers de Respuesta

El servidor incluye headers informativos (opcional, puede configurarse):
- `X-RateLimit-Limit`: Límite total permitido
- `X-RateLimit-Remaining`: Intentos restantes
- `X-RateLimit-Reset`: Timestamp cuando se resetea el límite

## Pruebas Manuales

### Prueba 1: Límite de Login

```bash
# Intenta hacer login 6 veces seguidas
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "wrongpassword",
      "turnstile_token": "dummy"
    }'
  echo "\nIntento $i"
done
```

**Resultado esperado**: Los primeros 5 intentos responderán normalmente, el 6to devolverá HTTP 429.

### Prueba 2: Límite de Reenvío de Código

```bash
# Intenta reenviar código 4 veces en 5 minutos
for i in {1..4}; do
  curl -X POST http://localhost:8000/api/auth/resend-code/ \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com"
    }'
  echo "\nIntento $i"
done
```

**Resultado esperado**: Los primeros 3 intentos responderán normalmente, el 4to devolverá HTTP 429.

## Pruebas Automatizadas

```python
# tests/test_ratelimit.py
import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_login_rate_limit(api_client):
    """Test que el rate limit funciona en login"""
    url = reverse('login')
    data = {
        'email': 'test@example.com',
        'password': 'wrong',
        'turnstile_token': 'test'
    }
    
    # Primeros 5 intentos deben funcionar (aunque fallen)
    for i in range(5):
        response = api_client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, 
                                        status.HTTP_401_UNAUTHORIZED]
    
    # El 6to intento debe ser bloqueado
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert 'Demasiados intentos' in response.json()['detail']
```

## Personalización

### Crear Nuevos Decoradores

En `accounts/ratelimit.py`:

```python
def ratelimit_custom(view_func):
    """
    Rate limit personalizado: 10 intentos por hora
    """
    return apply_ratelimit(
        key='ip', 
        rate='10/h', 
        method='POST', 
        block=True
    )(view_func)
```

### Aplicar a Nuevas Vistas

```python
from accounts.ratelimit import ratelimit_custom

@method_decorator(ratelimit_custom, name='post')
class MyCustomView(APIView):
    def post(self, request):
        # Tu lógica aquí
        pass
```

## Monitoreo y Logs

### Agregar Logging (Recomendado)

```python
import logging
logger = logging.getLogger(__name__)

def ratelimit_handler(request, exception):
    logger.warning(
        f"Rate limit exceeded for IP {request.META.get('REMOTE_ADDR')} "
        f"on {request.path}"
    )
    return JsonResponse({
        'detail': 'Demasiados intentos...',
        'error': 'rate_limit_exceeded'
    }, status=429)
```

## Deshabilitación Temporal

Para desarrollo o debugging:

```env
# En .env
RATELIMIT_ENABLE=False
```

O temporalmente en el código:
```python
# En settings.py
RATELIMIT_ENABLE = False  # Solo para desarrollo
```

## Best Practices

1. ✅ **Siempre usa rate limiting en producción**
2. ✅ **Configura Redis/Memcached para producción** (no LocMemCache)
3. ✅ **Monitorea logs de rate limit** para detectar ataques
4. ✅ **Ajusta límites según tu tráfico** real
5. ✅ **Combina con Cloudflare** para protección adicional
6. ⚠️ **No deshabilites en producción** salvo emergencia
7. ⚠️ **Considera whitelist de IPs** para servicios internos

## Solución de Problemas

### Problema: "Rate limit no funciona"

**Solución:**
1. Verifica que `django-ratelimit` esté instalado
2. Comprueba que `CACHES` esté configurado
3. Asegúrate de que `RATELIMIT_ENABLE=True`

### Problema: "Límite se alcanza muy rápido"

**Solución:**
1. Aumenta el límite en los decoradores
2. Verifica que no haya múltiples IPs detrás de un proxy
3. Considera usar `key='user'` en lugar de `key='ip'` para usuarios autenticados

### Problema: "Límite no se resetea"

**Solución:**
1. Reinicia el cache: `python manage.py cache.clear` (si disponible)
2. Verifica la configuración del cache backend
3. En desarrollo con LocMemCache, reinicia el servidor Django

## Configuración para Producción

```python
# settings.py - Configuración recomendada para producción

# 1. Usar Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 2. Habilitar rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# 3. Configurar logging
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/ratelimit.log',
        },
    },
    'loggers': {
        'django_ratelimit': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
    },
}
```

## Recursos Adicionales

- 📚 [django-ratelimit Documentation](https://django-ratelimit.readthedocs.io/)
- 🔐 [OWASP Rate Limiting Best Practices](https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks)
- ⚡ [Redis Configuration Guide](https://redis.io/docs/getting-started/)

## Soporte

Para problemas o preguntas sobre rate limiting:
1. Revisa los logs del servidor
2. Verifica la configuración de cache
3. Consulta la documentación de django-ratelimit
4. Revisa las pruebas en `tests/test_ratelimit.py`
