# 🛡️ Sistema de Rate Limiting - Vista General

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENTE (Frontend/API)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Request
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DJANGO SERVER                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    MIDDLEWARE STACK                        │  │
│  │  - CORS                                                    │  │
│  │  - Security                                                │  │
│  │  - CSRF Protection                                         │  │
│  │  - Authentication (JWT)                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              RATE LIMITING DECORATOR                       │  │
│  │  @method_decorator(ratelimit_auth, name='post')           │  │
│  │                                                            │  │
│  │  1. Extrae IP del cliente                                 │  │
│  │  2. Consulta cache (intentos previos)                     │  │
│  │  3. Verifica límite (ej: 5/minuto)                        │  │
│  │  4. Incrementa contador                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                    │                    │                        │
│         ┌──────────┴──────────┐         │                        │
│         ▼                     ▼         ▼                        │
│  ┌──────────┐          ┌──────────┐ ┌────────────────┐         │
│  │  CACHE   │          │ ALLOWED  │ │   RATE LIMITED │         │
│  │ (LocMem/ │◄─────────│ REQUEST  │ │   (429 Error)  │         │
│  │  Redis)  │          │          │ └────────────────┘         │
│  └──────────┘          └──────────┘                             │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    VIEW FUNCTION                           │  │
│  │  - RegisterView                                            │  │
│  │  - LoginView                                               │  │
│  │  - VerifyCodeView                                          │  │
│  │  - etc.                                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    DATABASE (MySQL)                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Response
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          RESPUESTA                               │
│                                                                  │
│  SUCCESS (200/201):                                             │
│  { "message": "Login exitoso", "access_token": "..." }         │
│                                                                  │
│  RATE LIMITED (429):                                            │
│  { "detail": "Demasiados intentos...",                         │
│    "error": "rate_limit_exceeded" }                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Decoradores Implementados

```python
┌─────────────────────────────────────────────────────────────────┐
│                  DECORADORES DE RATE LIMITING                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  @ratelimit_auth                                                │
│  ├─ Límite: 5 intentos / 1 minuto                              │
│  ├─ Aplicado a: Login, Registro                                │
│  └─ Protección: Ataques de fuerza bruta básicos                │
│                                                                  │
│  @ratelimit_strict_auth                                         │
│  ├─ Límite: 3 intentos / 1 minuto                              │
│  ├─ Aplicado a: Verificación código, Cambio contraseña         │
│  └─ Protección: Operaciones sensibles                          │
│                                                                  │
│  @ratelimit_email                                               │
│  ├─ Límite: 3 intentos / 5 minutos                             │
│  ├─ Aplicado a: Reenvío de códigos                             │
│  └─ Protección: Abuso del sistema de emails                    │
│                                                                  │
│  @ratelimit_api_read                                            │
│  ├─ Límite: 100 intentos / 1 minuto                            │
│  ├─ Aplicado a: Operaciones de lectura (GET)                   │
│  └─ Protección: Scraping y sobrecarga                          │
│                                                                  │
│  @ratelimit_api_write                                           │
│  ├─ Límite: 30 intentos / 1 minuto                             │
│  ├─ Aplicado a: Operaciones de escritura (POST/PUT/DELETE)     │
│  └─ Protección: Modificaciones masivas                         │
│                                                                  │
│  @ratelimit_upload                                              │
│  ├─ Límite: 5 intentos / 1 minuto                              │
│  ├─ Aplicado a: Subida de archivos CSV                         │
│  └─ Protección: Abuso de uploads                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Flujo de Decisión

```
┌───────────────────┐
│ Request arrives   │
└────────┬──────────┘
         │
         ▼
┌────────────────────┐
│ Extract client IP  │
│ or user ID         │
└────────┬───────────┘
         │
         ▼
┌────────────────────────┐
│ Query cache for:       │
│ - IP/User + Endpoint   │
│ - Request count        │
│ - Time window          │
└────────┬───────────────┘
         │
         ▼
    ┌────────┐
    │ Count  │
    │ exists?│
    └───┬────┘
        │
    ┌───┴────┐
    │        │
   YES      NO
    │        │
    ▼        ▼
┌─────────┐ ┌─────────────┐
│ Count >= │ │ Create new  │
│ Limit?   │ │ count = 1   │
└───┬─────┘ └──────┬──────┘
    │              │
┌───┴────┐         │
│        │         │
YES     NO         │
│        │         │
▼        └────┬────┘
┌──────────┐  │
│ BLOCK    │  ▼
│ Return   │ ┌──────────────┐
│ 429      │ │ ALLOW        │
└──────────┘ │ Increment    │
             │ Process view │
             └──────────────┘
```

---

## 🎯 Endpoints Protegidos

```
POST /api/auth/register/
├─ Rate Limit: 5/min
├─ Key: IP Address
└─ Response 429: "Demasiados intentos..."

POST /api/auth/login/
├─ Rate Limit: 5/min
├─ Key: IP Address
└─ Response 429: "Demasiados intentos..."

POST /api/auth/verify-code/
├─ Rate Limit: 3/min
├─ Key: IP Address
└─ Response 429: "Demasiados intentos..."

POST /api/auth/resend-code/
├─ Rate Limit: 3/5min
├─ Key: IP Address
└─ Response 429: "Demasiados intentos..."

POST /api/auth/register-teacher/
├─ Rate Limit: 5/min
├─ Key: IP Address
└─ Response 429: "Demasiados intentos..."

POST /api/auth/change-password/
├─ Rate Limit: 3/min
├─ Key: IP Address
└─ Response 429: "Demasiados intentos..."
```

---

## 🧪 Ejemplo de Prueba

```
┌────────────────────────────────────────────────────────────┐
│           SIMULACIÓN DE ATAQUE DE FUERZA BRUTA             │
└────────────────────────────────────────────────────────────┘

Atacante intenta login con diferentes contraseñas:

Intento 1 → POST /api/auth/login/ → 401 Unauthorized ✓
Intento 2 → POST /api/auth/login/ → 401 Unauthorized ✓
Intento 3 → POST /api/auth/login/ → 401 Unauthorized ✓
Intento 4 → POST /api/auth/login/ → 401 Unauthorized ✓
Intento 5 → POST /api/auth/login/ → 401 Unauthorized ✓
Intento 6 → POST /api/auth/login/ → 429 Too Many Requests ❌ BLOQUEADO

┌────────────────────────────────────────────────────────────┐
│ 🛡️ RATE LIMITING ACTIVADO - ATAQUE DETENIDO              │
└────────────────────────────────────────────────────────────┘

Cache State:
{
  "rl:func:login:ip:192.168.1.1": {
    "count": 6,
    "expires_at": "2025-10-14T10:35:00"
  }
}

Atacante debe esperar 60 segundos para reintentar.
```

---

## 🔧 Configuración del Cache

```
DEVELOPMENT (LocMemCache)
├─ Backend: django.core.cache.backends.locmem.LocMemCache
├─ Storage: En memoria del proceso Python
├─ Persistencia: Se pierde al reiniciar servidor
└─ Uso: Solo para desarrollo/testing

PRODUCTION (Redis - Recomendado)
├─ Backend: django.core.cache.backends.redis.RedisCache
├─ Storage: Servidor Redis independiente
├─ Persistencia: Sobrevive reinicios de Django
├─ Escalabilidad: Soporta múltiples workers/servidores
└─ Performance: Muy rápido y confiable
```

---

## 📈 Métricas de Seguridad

```
SIN RATE LIMITING:
├─ Intentos de login por minuto: ∞
├─ Posibles combinaciones probadas: Ilimitadas
├─ Tiempo para probar 1000 contraseñas: ~1 segundo
└─ ⚠️ Sistema VULNERABLE

CON RATE LIMITING (5/min):
├─ Intentos de login por minuto: 5
├─ Posibles combinaciones probadas: 5
├─ Tiempo para probar 1000 contraseñas: ~200 minutos (3.3 horas)
└─ ✅ Sistema PROTEGIDO

CON RATE LIMITING + TURNSTILE:
├─ Intentos de login por minuto: 5 (humanos verificados)
├─ Bots bloqueados: 99%
├─ Tiempo para probar 1000 contraseñas: Inviable
└─ ✅✅ Sistema MUY PROTEGIDO
```

---

## 🎨 Stack de Seguridad Completo

```
┌─────────────────────────────────────────────────────────┐
│                  CAPAS DE SEGURIDAD                      │
├─────────────────────────────────────────────────────────┤
│ 7. Cloudflare Turnstile (Bot Protection)         ✅    │
│ 6. Rate Limiting (Brute Force Protection)        ✅    │
│ 5. JWT Authentication (Session Management)       ✅    │
│ 4. Role-Based Permissions (Authorization)        ✅    │
│ 3. CSRF Protection (Cross-Site Request)          ✅    │
│ 2. Django ORM (SQL Injection Prevention)         ✅    │
│ 1. Input Validation (Serializers)                ✅    │
└─────────────────────────────────────────────────────────┘
```

---

*DevTrack ahora tiene protección multicapa contra amenazas web comunes* 🛡️✨
