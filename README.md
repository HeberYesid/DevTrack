# DevTrack

Aplicación web completa (backend Django + frontend React) para gestión académica: materias, inscripciones, ejercicios y resultados, dashboard, exportes y notificaciones in‑app.

---

## �📚 Documentación

Toda la documentación técnica, guías de implementación y referencias del sistema están organizadas en la carpeta **[`docs/`](./docs/)**:

- **[API Guide](./docs/API_GUIDE.md)** - Guía completa para usar el backend como API REST
- **[Docker Setup](./docs/DOCKER_SETUP.md)** - 🐳 Guía completa de Docker
- **[Theme System](./docs/THEME_SYSTEM_DOCS.md)** - Sistema de temas (light/dark mode)
- **[Role-Based Views](./docs/ROLE_BASED_VIEWS.md)** - Vistas basadas en roles
- **[Testing Guide](./docs/TESTING.md)** - Guía de testing
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Solución de problemas
- Y mucho más...

Visita el [índice completo de documentación](./docs/README.md) para más detalles.

---

## ⚙️ Setup Manual (Sin Docker)

### Requisitos

- Python 3.11+
- MySQL 8+
- Node 18+

---

## Backend (Django)

1. Crear entorno virtual e instalar dependencias

```bash
cd backend
python -m venv .venv 
#Escoger una de las dos
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass # saltar el bloqueo de scripts una sola vez
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned # deshabilitar permanente para el usuario
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Variables de entorno

```bash
copy .env.example .env  # Windows
```

Edita `backend/.env` y define:

- `DJANGO_SECRET_KEY`
```bash

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" #GENERAR SECRET KEY
```
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`
- `FRONTEND_URL=http://localhost:5173`

3. Base de datos MySQL (ejemplo)

```sql
CREATE DATABASE devtrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'devtrack'@'%' IDENTIFIED BY 'devtrack_password';
GRANT ALL PRIVILEGES ON devtrack.* TO 'devtrack'@'%';
FLUSH PRIVILEGES;
```

4. Migraciones y superusuario

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Ejecutar servidor

```bash
python manage.py runserver
```

Documentación de API: http://127.0.0.1:8000/api/docs/

### Autenticación y verificación por email

DevTrack incluye un sistema completo de verificación por código de 6 dígitos:

**Endpoints de autenticación:**
- Registro: `POST /api/auth/register/` (rol forzado a `STUDENT` por seguridad)
- Login: `POST /api/auth/login/` (requiere email verificado)
- Verificación por código: `POST /api/auth/verify-code/` (código de 6 dígitos)
- Reenviar código: `POST /api/auth/resend-code/`
- Verificación por token: `GET /api/auth/verify/?token=...` (sistema legacy)
- Perfil: `GET /api/auth/me/`

**Sistema de códigos de verificación:**
- Se generan códigos aleatorios de 6 dígitos
- Validez: 15 minutos
- Se invalidan automáticamente al generar uno nuevo
- Se muestran en la consola del servidor para desarrollo
- Se envían por email al usuario

**Configuración de email:**
Para envío real de emails, configura en `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=DevTrack <tu-email@gmail.com>
```

Para Gmail, necesitas generar una contraseña de aplicación en tu cuenta Google.

**Seguridad:**

- Integración con Cloudflare Turnstile para prevenir bots
- Validación de IP en verificaciones de seguridad
- Tokens JWT para autenticación de sesiones
- Códigos de verificación con expiración automática

---

## Frontend (React + Vite)

1. Variables de entorno

```bash
cd frontend
copy .env.example .env
```

En `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

Para producción, necesitarás configurar tus propias claves de Turnstile en [Cloudflare](https://developers.cloudflare.com/turnstile/).

2. Instalar y ejecutar

```bash
npm install
npm run dev
```

Abrir http://localhost:5173

---

