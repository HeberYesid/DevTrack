# Auditoría de Dependencias - DevTrack

## Backend (Python)

### ✅ Dependencias Esenciales (54 → 45)

#### Django Core
- ✅ **Django==5.0.6** - Framework principal
- ✅ **djangorestframework==3.15.2** - API REST
- ✅ **djangorestframework-simplejwt==5.3.1** - Autenticación JWT
- ✅ **django-cors-headers==4.3.1** - CORS
- ✅ **django-ratelimit==4.1.0** - Rate limiting
- ✅ **drf-spectacular==0.27.2** - Documentación OpenAPI

#### Base de Datos
- ✅ **PyMySQL==1.1.0** - MySQL connector
- ✅ **psycopg2-binary==2.9.10** - PostgreSQL (producción)
- ⚠️ **psycopg==3.2.3** - DUPLICADO - eliminar (psycopg2 es suficiente)
- ✅ **dj-database-url==3.0.1** - Configuración DB por URL

#### Servidor & Deployment
- ✅ **gunicorn==21.2.0** - WSGI server
- ✅ **whitenoise==6.6.0** - Static files
- ✅ **python-dotenv==1.0.1** - Variables de entorno

#### Seguridad
- ✅ **cryptography==43.0.1** - Encriptación (JWT)
- ✅ **PyJWT==2.8.0** - JWT tokens

#### Utilidades
- ✅ **requests==2.31.0** - HTTP client (rate limit tests)
- ✅ **python-dateutil==2.9.0** - Date parsing
- ✅ **pytz==2024.1** - Timezones
- ⚠️ **sendgrid==6.11.0** - Email service (OPCIONAL - solo si se usa en prod)

#### Testing (Desarrollo)
- ✅ **pytest==8.0.0**
- ✅ **pytest-django==4.8.0**
- ✅ **pytest-cov==4.1.0**
- ✅ **coverage==7.10.7**
- ❌ **factory-boy==3.3.0** - NO USADO - eliminar
- ❌ **Faker==22.6.0** - NO USADO - eliminar

#### Otras
- ⚠️ **certifi==2024.12.14** - Auto-instalada, mantener
- ⚠️ **charset-normalizer==3.4.1** - Auto-instalada, mantener
- ⚠️ **idna==3.10** - Auto-instalada, mantener
- ⚠️ **urllib3==2.3.0** - Auto-instalada, mantener

### ❌ Dependencias NO USADAS (9 paquetes a eliminar)

1. **httpie==3.2.4** - CLI HTTP client, no usado en código
2. **git-filter-repo==2.47.0** - Herramienta git, no necesaria
3. **factory-boy==3.3.0** - No hay uso en tests
4. **Faker==22.6.0** - No hay uso en tests
5. **psycopg==3.2.3** - Duplicado de psycopg2-binary

**Dependencias adicionales de httpie (pueden eliminarse):**
6. httpie-auth-*.* (varios plugins)
7. multidict==6.1.0
8. pygments==2.19.1
9. markdown-it-py==3.0.0

---

## Frontend (React)

### ✅ Dependencias Runtime (8 → 8)

#### Core React
- ✅ **react==18.2.0** - Framework
- ✅ **react-dom==18.2.0** - DOM rendering
- ✅ **react-router-dom==6.22.3** - Routing

#### HTTP & Auth
- ✅ **axios==1.6.7** - HTTP client
- ✅ **jwt-decode==4.0.0** - JWT parsing

#### UI/UX
- ❌ **framer-motion==12.23.22** - NO USADO - eliminar
- ❌ **lucide-react==0.544.0** - NO USADO (solo 1 icono SVG manual)
- ✅ **react-joyride==2.9.3** - Tours (AppTour.jsx)
- ❌ **recharts==2.12.7** - NO USADO - eliminar

### ✅ Dependencias Dev (8 → 8)

#### Build Tools
- ✅ **vite==5.1.6** - Build tool
- ✅ **@vitejs/plugin-react==4.2.1** - React plugin

#### Testing
- ✅ **vitest==1.2.2** - Test runner
- ✅ **@testing-library/react==14.2.1** - React testing
- ✅ **@testing-library/jest-dom==6.4.2** - Jest matchers
- ✅ **@testing-library/user-event==14.5.2** - User interactions
- ✅ **jsdom==24.0.0** - DOM simulation
- ✅ **@vitest/coverage-v8==1.2.2** - Coverage

---

## Resumen de Cambios Recomendados

### Backend: Eliminar 9 paquetes

```bash
# Paquetes a ELIMINAR de requirements.txt
httpie==3.2.4
git-filter-repo==2.47.0
factory-boy==3.3.0
Faker==22.6.0
psycopg==3.2.3
multidict==6.1.0
pygments==2.19.1
markdown-it-py==3.0.0
certifi==2024.12.14  # Auto-instalada
charset-normalizer==3.4.1  # Auto-instalada
idna==3.10  # Auto-instalada
urllib3==2.3.0  # Auto-instalada
```

**Decisión sobre SendGrid:**
- Si se usa en PRODUCCIÓN → MANTENER
- Si solo es para desarrollo (console email) → ELIMINAR

### Frontend: Eliminar 3 paquetes

```bash
# Paquetes a ELIMINAR de package.json
npm uninstall framer-motion lucide-react recharts
```

---

## Impacto Estimado

### Backend
- **Reducción:** ~15-20 MB en tamaño de instalación
- **Paquetes:** 54 → 40-42 (dependiendo de SendGrid)
- **Riesgo:** BAJO - ningún código usa las dependencias eliminadas

### Frontend
- **Reducción:** ~500 KB en bundle size
- **Paquetes:** 16 → 13
- **Riesgo:** BAJO - no se usan en código actual

---

## Próximos Pasos

1. ✅ Crear branch `chore/dependency-cleanup`
2. ⚠️ Eliminar paquetes backend
3. ⚠️ Eliminar paquetes frontend
4. ⚠️ Ejecutar tests backend: `pytest`
5. ⚠️ Ejecutar tests frontend: `npm test`
6. ⚠️ Probar aplicación localmente
7. ⚠️ Commit y merge si todo funciona

---

## Notas Adicionales

### Backend
- `conftest.py` usa fixtures manuales en lugar de factory-boy (bien hecho)
- `sendgrid` solo se usa en `accounts/utils.py` con fallback a Django email
- Sin dependencias de producción críticas en riesgo

### Frontend
- `AppTour.jsx` usa `react-joyride` correctamente (mantener)
- NotificationBell usa SVG manual en lugar de lucide-react (ya corregido)
- No hay animaciones de framer-motion en código actual
- No hay gráficos de recharts en dashboards actuales

---

**Generado:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Revisor:** GitHub Copilot
