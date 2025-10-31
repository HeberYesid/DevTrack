# 🚀 DevTrack - Guía de Ejecución Local

## ✅ Estado Actual
- ✅ **Backend Django**: Corriendo en http://localhost:8000
- ✅ **Frontend React**: Corriendo en http://localhost:5173
- ✅ **Base de Datos MySQL**: Configurada en XAMPP

---

## 📋 Configuración Completada

### Backend
1. ✅ Entorno virtual creado en `backend/venv`
2. ✅ Dependencias instaladas (Django, DRF, PyMySQL, etc.)
3. ✅ Archivo `.env` configurado con MySQL local
4. ✅ Base de datos `devtrack` creada
5. ✅ Migraciones ejecutadas
6. ✅ Servidor Django corriendo

### Frontend
1. ✅ Dependencias de npm instaladas
2. ✅ Archivo `.env` configurado
3. ✅ Servidor Vite corriendo

---

## 🎯 Acceso a la Aplicación

### URLs Principales
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs/

### Crear Usuario Administrador
Para acceder al panel admin, necesitas crear un superusuario:

```powershell
# Abrir terminal en backend
cd backend
.\venv\Scripts\Activate.ps1
python manage.py createsuperuser

# Seguir las instrucciones:
# Email: tu@email.com
# First name: Tu Nombre
# Last name: Tu Apellido
# Password: (tu contraseña segura)
# Role: ADMIN
```

---

## 🔄 Comandos para Futuras Sesiones

### Iniciar Backend
```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### Iniciar Frontend
```powershell
# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Verificar MySQL (XAMPP)
- Asegúrate de que el servicio MySQL esté corriendo en XAMPP
- Panel de Control XAMPP → Start MySQL

---

## 🛠️ Comandos Útiles

### Backend (Django)
```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell interactivo
python manage.py shell

# Ejecutar tests
pytest

# Acceso directo a MySQL
python manage.py dbshell
```

### Frontend (React + Vite)
```powershell
cd frontend

# Instalar nuevas dependencias
npm install

# Ejecutar tests
npm test

# Build para producción
npm run build

# Preview del build
npm run preview
```

### Base de Datos (MySQL)
```powershell
# Acceso directo con XAMPP
C:\xampp\mysql\bin\mysql.exe -u root devtrack

# Ver tablas
SHOW TABLES;

# Consultas
SELECT * FROM accounts_user;
```

---

## 📁 Estructura de Archivos Importantes

```
DevTrack/
├── backend/
│   ├── venv/              # Entorno virtual (NO subir a git)
│   ├── .env               # Variables de entorno (NO subir a git)
│   ├── manage.py          # Comando principal Django
│   ├── requirements.txt   # Dependencias producción
│   └── requirements.dev.txt  # Dependencias desarrollo
├── frontend/
│   ├── node_modules/      # Dependencias npm (NO subir a git)
│   ├── .env               # Variables de entorno (NO subir a git)
│   ├── package.json       # Configuración npm
│   └── src/               # Código fuente React
└── docs/                  # Documentación del proyecto
```

---

## ⚠️ Troubleshooting

### Error: "Cannot connect to database"
- Verifica que MySQL esté corriendo en XAMPP
- Revisa las credenciales en `backend/.env`
- Verifica que la base de datos `devtrack` exista

### Error: "Port already in use"
**Backend (8000):**
```powershell
# Buscar proceso usando el puerto
netstat -ano | findstr :8000
# Matar proceso (reemplaza PID)
taskkill /PID <número> /F
```

**Frontend (5173):**
```powershell
netstat -ano | findstr :5173
taskkill /PID <número> /F
```

### Frontend no conecta con Backend
- Verifica que `frontend/.env` tenga: `VITE_API_BASE_URL=http://localhost:8000`
- Reinicia el servidor Vite: `Ctrl+C` y luego `npm run dev`

### Cambios en modelos no se reflejan
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py makemigrations
python manage.py migrate
```

---

## 🎨 Próximos Pasos

1. **Crear superusuario** para acceder al admin
2. **Explorar API Docs** en http://localhost:8000/api/docs/
3. **Registrar usuarios** desde el frontend
4. **Crear materias y ejercicios** desde el panel admin
5. **Probar flujo completo** de estudiantes y profesores

---

## 📚 Documentación Adicional

- **API Guide**: `docs/API_GUIDE.md`
- **Testing**: `docs/TESTING.md`
- **Theme System**: `docs/THEME_SYSTEM_DOCS.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

---

## 🔐 Credenciales de Prueba

### Email de Prueba (Cloudflare Turnstile)
- **Site Key**: `0x4AAAAAAB195XyO5y089iC-` (configurado en `.env`)
- **Secret Key**: `0x4AAAAAAB195dF8QdRbAuGMD3aVvy8Q_V4` (configurado en backend)

### Base de Datos
- **Host**: 127.0.0.1
- **Puerto**: 3306
- **Usuario**: root
- **Contraseña**: (vacío)
- **Base de datos**: devtrack

---

¡Todo listo! 🎉 El proyecto está corriendo localmente sin Docker.
