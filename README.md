# DevTrack

Aplicación web completa (backend Django + frontend React) para gestión académica: materias, inscripciones, ejercicios y resultados, dashboard, exportes y notificaciones in‑app.

## � Inicio Rápido

### Con Docker (Recomendado) 🐳

```powershell
# 1. Clonar repositorio
git clone https://github.com/HeberYesid/DevTrack.git
cd DevTrack

# 2. Iniciar con Docker
.\scripts\docker-dev.ps1
```

¡Listo! Abre http://localhost:5173

**Ventajas de Docker:**
- ✅ Setup en un solo comando
- ✅ Funciona en cualquier máquina
- ✅ No más problemas de versiones o configuración

Ver: **[Guía de Docker](./DOCKER_README.md)** | **[Setup completo](./docs/DOCKER_SETUP.md)**

### Sin Docker (Manual)

Ver instrucciones detalladas más abajo ↓

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

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" #Generar secret key django
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

## Flujo de profesor (pruebas)

1. Crear usuario profesor en Django Admin

- Entrar a `http://127.0.0.1:8000/admin/` con el superusuario.
- Crear un `User` con `email` y `username` iguales (ej. `prof@demo.com`).
- Establecer `role=TEACHER` y marcar `is_email_verified=True` (para poder iniciar sesión sin verificar por correo).

2. Ingresar al frontend como profesor

- Ir a `http://localhost:5173/login` e iniciar sesión con el correo del profesor.
- Navegar a `Materias` y crear una nueva materia.
- Entrar al detalle de la materia y:
  - Inscribir estudiantes por correo o con CSV (`samples/enrollments.csv`).
  - Cargar resultados con CSV (`student_email,exercise_name,status`).
  - Revisar el dashboard de la materia y exportar CSV.
- Ir a `Notificaciones` para ver las notificaciones generadas por inscripciones y resultados.

3. Flujo de estudiante

- Registrarse en `/register` (rol forzado a `STUDENT`).
- Verificar correo con código de 6 dígitos:
  - El código se muestra en la consola del servidor
  - También se envía por email (si está configurado)
  - Ingresar el código en `/verify-code`
- Iniciar sesión una vez verificado el correo.
- Revisar `Mis resultados` y el dashboard personal.

### Ejemplos de CSV

Inscripciones (en `samples/enrollments.csv`):

```
email,first_name,last_name
ana@example.com,Ana,Pérez
bob@example.com,Bob,López
```

Resultados:

```
student_email,exercise_name,status
ana@example.com,Ejercicio 1,verde
ana@example.com,Ejercicio 2,amarillo
bob@example.com,Ejercicio 1,rojo
```

Valores admitidos en `status`: `verde/green/g/1/true`, `amarillo/yellow/y`, `rojo/red/r/0/false`.

---

## Estructura principal

```
backend/
  accounts/ courses/ notifications/ config/
  requirements.txt  .env.example
frontend/
  src/  package.json  .env.example  vite.config.js  index.html
samples/
  enrollments.csv
```

---

## Publicar en GitHub

1. Asegúrate de no subir secretos: `.env` está en `.gitignore`.
2. Inicializa el repo y primer commit:

```bash
git init
git add .
git commit -m "DevTrack: backend Django + frontend React, CSV, notifs, dashboards"
```

3. Crea el repositorio en GitHub y añade el remoto:

```bash
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```

> Tip: considera añadir una licencia (MIT), `CONTRIBUTING.md` y CI en el futuro.

---

## Notas

- El registro público asigna `STUDENT` por defecto. Para `TEACHER`/`ADMIN`, configúralo via Admin.
- Las notificaciones son in‑app. En el futuro se pueden enviar también por email.
- El sistema de verificación por código de 6 dígitos es obligatorio para nuevos registros.
- Los códigos se muestran en la consola del servidor para facilitar el desarrollo.
- Para producción, asegúrate de configurar un proveedor de email real (Gmail, SendGrid, etc.).
