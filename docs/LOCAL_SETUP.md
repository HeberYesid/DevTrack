# 🚀 Guía de Setup Local - DevTrack

## 📋 Requisitos Previos

- Python 3.11+
- Node.js 18+
- MySQL 8+
- Git

---

## 🔧 Configuración Inicial (Solo Primera Vez)

### 1️⃣ Clonar y Configurar Repositorio

```powershell
# Clonar el repo
git clone https://github.com/HeberYesid/DevTrack.git
cd DevTrack

# Cambiar a rama develop
git checkout develop
git pull origin develop
```

### 2️⃣ Backend Setup

```powershell
cd backend

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Instalar dependencias
pip install -r requirements.txt
```

### 3️⃣ Configurar Base de Datos MySQL

```sql
-- Abrir MySQL (mysql -u root -p)
CREATE DATABASE devtrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'devtrack'@'localhost' IDENTIFIED BY 'devtrack123';
GRANT ALL PRIVILEGES ON devtrack.* TO 'devtrack'@'localhost';
FLUSH PRIVILEGES;
```

### 4️⃣ Variables de Entorno

El archivo `.env` ya está creado con valores por defecto.

**Verifica** en `backend/.env`:
- `DB_PASSWORD=devtrack123` (debe coincidir con MySQL)
- `TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA` (key de prueba)

### 5️⃣ Migraciones y Superuser

```powershell
# Ejecutar migraciones
python manage.py migrate

# Crear superusuario local
python manage.py createsuperuser
# Email: admin@local.com
# Password: admin123
```

### 6️⃣ Frontend Setup

```powershell
cd ..\frontend

# Instalar dependencias
npm install
```

El archivo `.env` ya está creado con:
- `VITE_API_BASE_URL=http://127.0.0.1:8000`
- `VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA` (key de prueba)

---

## 🚀 Ejecutar en Desarrollo

### Cada vez que trabajes:

**Terminal 1 - Backend:**
```powershell
cd backend
.venv\Scripts\Activate.ps1
python manage.py runserver
```
Backend disponible en: http://127.0.0.1:8000

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```
Frontend disponible en: http://localhost:5173

---

## 🌿 Workflow con Ramas

### Crear Nueva Feature

```powershell
# 1. Actualizar develop
git checkout develop
git pull origin develop

# 2. Crear rama de feature
git checkout -b feature/nombre-descriptivo
# Ejemplos:
# - feature/dashboard-mejorado
# - feature/exportar-csv
# - fix/corregir-login

# 3. Trabajar normalmente...
# ... editar código ...

# 4. Commits frecuentes
git add .
git commit -m "feat: descripción del cambio"

# 5. Push a GitHub
git push -u origin feature/nombre-descriptivo

# 6. Crear Pull Request en GitHub
# Base: develop ← Compare: feature/nombre-descriptivo
```

### Volver a Develop

```powershell
# Guardar cambios si no están commiteados
git add .
git commit -m "wip: trabajo en progreso"

# Cambiar a develop
git checkout develop
git pull origin develop
```

---

## 📝 Comandos Útiles

### Git

```powershell
# Ver rama actual
git branch --show-current

# Ver todas las ramas
git branch -a

# Ver estado
git status

# Ver log
git log --oneline --graph --all -10
```

### Backend

```powershell
# Activar entorno
.venv\Scripts\Activate.ps1

# Ejecutar servidor
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Tests
pytest --cov

# Shell de Django
python manage.py shell
```

### Frontend

```powershell
# Ejecutar dev server
npm run dev

# Tests
npm test

# Build para producción
npm run build

# Preview del build
npm run preview
```

---

## 🗂️ Estructura de Carpetas

```
DevTrack/
├── backend/
│   ├── .env                    # Variables locales (NO commitear)
│   ├── .venv/                  # Entorno virtual (NO commitear)
│   ├── manage.py
│   ├── requirements.txt
│   ├── accounts/               # App de usuarios
│   ├── courses/                # App de cursos
│   ├── notifications/          # App de notificaciones
│   └── config/                 # Configuración Django
│
├── frontend/
│   ├── .env                    # Variables locales (NO commitear)
│   ├── node_modules/           # Dependencias (NO commitear)
│   ├── src/
│   │   ├── api/               # Configuración de axios
│   │   ├── components/        # Componentes React
│   │   ├── pages/             # Páginas/Vistas
│   │   └── state/             # Context API
│   └── package.json
│
└── docs/                       # Documentación
```

---

## 🐛 Troubleshooting

### Backend no inicia

```powershell
# Verificar entorno virtual activado
.venv\Scripts\Activate.ps1

# Verificar que MySQL está corriendo
# Verificar credenciales en .env
```

### Frontend no conecta con Backend

```powershell
# Verificar VITE_API_BASE_URL en frontend/.env
# Debe ser: http://127.0.0.1:8000

# Verificar CORS en backend/.env
# Debe incluir: http://localhost:5173
```

### Error de Migraciones

```powershell
# Resetear migraciones (CUIDADO: borra datos)
python manage.py migrate --fake
python manage.py migrate

# O eliminar DB y recrear
DROP DATABASE devtrack;
CREATE DATABASE devtrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
python manage.py migrate
```

### Conflictos de Git

```powershell
# Ver estado
git status

# Descartar cambios locales
git restore <archivo>

# Actualizar desde develop
git checkout develop
git pull origin develop
git checkout feature/mi-feature
git merge develop
# Resolver conflictos y commit
```

---

## ✅ Verificar Todo Funciona

1. **Backend**: http://127.0.0.1:8000/admin
2. **Frontend**: http://localhost:5173
3. **API Docs**: http://127.0.0.1:8000/api/docs/

---

## 🎯 Siguiente Paso

Ahora puedes:
1. Crear tu primera feature branch
2. Hacer cambios
3. Probar localmente
4. Crear PR a develop

**Ejemplo:**
```powershell
git checkout -b feature/mi-primera-feature
# ... trabajar ...
git add .
git commit -m "feat: mi cambio"
git push -u origin feature/mi-primera-feature
```

---

¿Dudas? Consulta `CONTRIBUTING.md` o abre un Issue en GitHub.
