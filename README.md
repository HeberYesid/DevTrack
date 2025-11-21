# DevTrack

**Sistema de seguimiento académico full-stack** para monitoreo del rendimiento estudiantil con clasificación automática y notificaciones en tiempo real.

---

## 🎯 Características Principales

- **Gestión de Cursos**: Creación y administración de materias, ejercicios y resultados
- **Sistema de Semáforo**: Clasificación automática verde/amarillo/rojo según rendimiento
- **Cálculo Automático de Notas**: Lógica inteligente basada en estado de ejercicios
- **Notificaciones en Tiempo Real**: Alertas automáticas generadas por eventos del sistema
- **Carga Masiva de Datos**: Importación CSV de estudiantes y resultados
- **Control de Acceso Granular**: Tres roles con permisos específicos (Student/Teacher/Admin)
- **Autenticación Segura**: JWT con refresh tokens y verificación de email por código de 6 dígitos
- **Protección Anti-Abuso**: Rate limiting configurable en endpoints sensibles
- **Sistema de Temas**: Modo claro/oscuro con CSS variables

---

## 🛠️ Stack Tecnológico

**Backend**
- Django 5.0 + Django REST Framework
- MySQL 8+ para persistencia de datos
- JWT para autenticación
- Pytest para testing con cobertura >90%

**Frontend**
- React 18 + Vite
- Context API para estado global
- Axios con interceptores automáticos
- Vitest para testing de componentes

---

## 🚀 Inicio Rápido

### Requisitos
- Python 3.11+
- MySQL 8+
- Node 18+

### 1. Clonar el repositorio
```powershell
git clone https://github.com/HeberYesid/DevTrack.git
cd DevTrack
```

### 2. Configurar Backend

**Crear entorno virtual**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Variables de entorno**
```powershell
copy .env.example .env
```

Edita `backend/.env`:
```env
DJANGO_SECRET_KEY=<genera-con-comando-abajo>
DB_NAME=devtrack
DB_USER=devtrack
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:5173
FRONTEND_URL=http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Generar secret key:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Base de datos MySQL**
```sql
CREATE DATABASE devtrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'devtrack'@'%' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON devtrack.* TO 'devtrack'@'%';
FLUSH PRIVILEGES;
```

**Ejecutar migraciones**
```powershell
python manage.py migrate
python manage.py createsuperuser
```

**Iniciar servidor**
```powershell
python manage.py runserver
```

### 3. Configurar Frontend

**Variables de entorno**
```powershell
cd frontend
copy .env.example .env
```

Edita `frontend/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

**Instalar dependencias y ejecutar**
```powershell
npm install
npm run dev
```

### Accesos
- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **Documentación API**: http://127.0.0.1:8000/api/docs/
- **Admin Django**: http://127.0.0.1:8000/admin/

---

## 📚 Documentación

Toda la documentación técnica está en **[`docs/`](./docs/)**:

- **[API Guide](./docs/API_GUIDE.md)** - Referencia completa de endpoints REST
- **[Testing Guide](./docs/TESTING.md)** - Configuración de pytest y vitest
- **[Theme System](./docs/THEME_SYSTEM_DOCS.md)** - Sistema de temas CSS
- **[Role-Based Views](./docs/ROLE_BASED_VIEWS.md)** - Permisos y vistas por rol
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Solución de problemas comunes

Ver [índice completo](./docs/README.md) para más guías.

---

## 🌐 Despliegue en Producción

### ☁️ Opciones Gratuitas Recomendadas

DevTrack está listo para desplegarse en servicios gratuitos en la nube:

#### 🏆 **Render.com** (Recomendada)
- ✅ **100% gratis** (750 horas/mes)
- ✅ Backend + Base de datos PostgreSQL incluida
- ✅ Deploy automático desde GitHub
- ⚠️ Backend se duerme después de 15 min sin uso

**Guía completa**: [docs/RENDER_DEPLOY.md](./docs/RENDER_DEPLOY.md)

#### 🥈 **Fly.io**
- ✅ 3 VMs gratis (siempre activas)
- ✅ PostgreSQL incluida (3GB)
- ⚠️ Requiere CLI y tarjeta de crédito

#### 🥉 **Railway.app**
- ⚠️ Ya no es totalmente gratis (~$5-10/mes)
- ✅ Soporta MySQL y PostgreSQL
- ✅ Configuración muy fácil

**Comparación detallada**: [docs/FREE_HOSTING_OPTIONS.md](./docs/FREE_HOSTING_OPTIONS.md)

### 📦 Frontend en Vercel (Gratis)
```powershell
# El frontend ya tiene vercel.json configurado
# Solo conecta tu repo en vercel.com
```

---

## 📊 Lógica de Calificación

El sistema calcula notas automáticamente según el estado de los ejercicios:

```python
if ejercicios_verdes == total_ejercicios:
    nota = 5.0
elif ejercicios_amarillos / total >= 0.6:
    nota = 3.0
else:
    nota = 5.0 * (ejercicios_verdes / total)
```

**Estados de ejercicios:**
- 🟢 **Verde**: Ejercicio completado correctamente
- 🟡 **Amarillo**: Ejercicio con observaciones
- 🔴 **Rojo**: Ejercicio incompleto o con errores

---

## 🔐 Sistema de Autenticación

### Registro y Verificación
1. Usuario se registra → Recibe código de 6 dígitos por email
2. Ingresa código → Email verificado
3. Login → Obtiene tokens JWT (access + refresh)

### Endpoints principales
```
POST /api/auth/register/         # Registro (rol STUDENT por defecto)
POST /api/auth/login/            # Login (requiere email verificado)
POST /api/auth/verify-code/      # Verificar código de 6 dígitos
POST /api/auth/resend-code/      # Reenviar código
GET  /api/auth/me/               # Perfil del usuario autenticado
POST /api/auth/logout/           # Cerrar sesión
POST /api/auth/token/refresh/    # Renovar access token
```

### Protecciones
- Rate limiting en endpoints de autenticación (5 intentos/minuto)
- Integración con Cloudflare Turnstile anti-bot
- Códigos de verificación expiran en 15 minutos
- Tokens JWT con refresh automático

---

## 👥 Sistema de Roles

### Student (Estudiante)
- Ver materias en las que está inscrito
- Consultar ejercicios y sus resultados
- Ver notificaciones personales
- Dashboard con progreso por materia

### Teacher (Profesor)
- Crear y gestionar materias propias
- Agregar ejercicios a sus materias
- Inscribir estudiantes (manual o CSV)
- Cargar resultados masivamente (CSV)
- Ver estadísticas de sus materias

### Admin (Administrador)
- Acceso total al sistema
- Gestionar usuarios y roles
- Ver todas las materias y resultados
- Acceso al panel de Django Admin

---

## ⚙️ Setup Manual

### Requisitos
- Python 3.11+
- MySQL 8+
- Node 18+

### Backend (Django)

1. **Crear entorno virtual e instalar dependencias**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

2. **Configurar variables de entorno**
```powershell
copy .env.example .env
```

Edita `backend/.env`:
```env
DJANGO_SECRET_KEY=<genera-con-comando-abajo>
DB_NAME=devtrack
DB_USER=devtrack
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:5173
FRONTEND_URL=http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Generar secret key:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. **Crear base de datos MySQL**
```sql
CREATE DATABASE devtrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'devtrack'@'%' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON devtrack.* TO 'devtrack'@'%';
FLUSH PRIVILEGES;
```

4. **Ejecutar migraciones**
```powershell
python manage.py migrate
python manage.py createsuperuser
```

5. **Iniciar servidor**
```powershell
python manage.py runserver
```

API disponible en: http://127.0.0.1:8000

### Frontend (React + Vite)

1. **Configurar variables de entorno**
```powershell
cd frontend
copy .env.example .env
```

Edita `frontend/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

2. **Instalar dependencias y ejecutar**
```powershell
npm install
npm run dev
```

Aplicación disponible en: http://localhost:5173

---

## 🧪 Testing

### Backend (Pytest)
```powershell
cd backend
pytest --cov                           # Con cobertura
pytest --cov --cov-report=html        # Reporte HTML en htmlcov/
pytest -v                             # Modo verbose
pytest courses/tests/                 # Solo app específica
```

### Frontend (Vitest)
```powershell
cd frontend
npm test                              # Tests en modo watch
npm run test:coverage                 # Con cobertura
```

---

## 📦 Carga Masiva de Datos

El sistema permite importar estudiantes y resultados mediante archivos CSV.

### Inscribir Estudiantes
**Endpoint**: `POST /api/courses/subjects/{id}/enrollments_upload_csv/`

CSV de ejemplo (`samples/enrollments.csv`):
```csv
email
student1@example.com
student2@example.com
```

### Cargar Resultados
**Endpoint**: `POST /api/courses/subjects/{id}/results_upload_csv/`

CSV de ejemplo (`samples/student_results.csv`):
```csv
student_email,exercise_name,status,grade,comments
student1@example.com,Exercise 1,GREEN,5.0,Excelente trabajo
student2@example.com,Exercise 1,YELLOW,3.5,Mejorar documentación
```

**Estados válidos**: `GREEN`, `YELLOW`, `RED`

---

## 🔔 Sistema de Notificaciones

Las notificaciones se generan automáticamente mediante signals de Django:

- **Inscripción a materia**: Notifica a estudiante y profesor
- **Nueva calificación**: Notifica al estudiante
- **Cambio de rol**: Notifica al usuario afectado
- **Cambio de contraseña**: Notifica al usuario

Endpoints:
```
GET  /api/notifications/              # Listar notificaciones
POST /api/notifications/{id}/read/    # Marcar como leída
POST /api/notifications/read_all/     # Marcar todas como leídas
```

---

## 🚨 Problemas Comunes

### Estudiantes no ven materias
Las materias se filtran automáticamente por inscripción. Verifica que el estudiante esté inscrito en `Enrollment`.

### Notificaciones duplicadas
Las notificaciones se generan por signals. Verifica que `courses/apps.py` importe `signals` correctamente.

### Rate limit en desarrollo
Desactiva en `backend/.env`:
```env
RATELIMIT_ENABLE=False
```

Ver más en [Troubleshooting](./docs/TROUBLESHOOTING.md).

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📧 Contacto

**Autor**: Heber Yesid  
**Repositorio**: [github.com/HeberYesid/DevTrack](https://github.com/HeberYesid/DevTrack)

Para reportar bugs o solicitar features, por favor abre un issue en GitHub.
