# 📚 Documentación de DevTrack

Bienvenido a la documentación del proyecto DevTrack. Esta carpeta contiene toda la documentación técnica, guías de implementación y referencias del sistema.

## 📖 Índice de Documentación

### 🚀 Guías de Inicio Rápido

- **[API_GUIDE.md](./API_GUIDE.md)** - Guía completa para usar el backend como API REST
  - Autenticación JWT
  - Endpoints disponibles
  - Ejemplos con cURL, Python, Node.js, Postman
  - Flujos completos de uso

### 🔧 Configuración y Setup

- **[TURNSTILE_SETUP.md](./TURNSTILE_SETUP.md)** - Configuración de Cloudflare Turnstile (CAPTCHA)
- **[TESTING.md](./TESTING.md)** - Guía de testing y pruebas del sistema

### 🎨 Sistema de Temas

- **[THEME_SYSTEM_DOCS.md](./THEME_SYSTEM_DOCS.md)** - Documentación del sistema de temas (light/dark mode)
  - Implementación
  - Personalización de colores
  - Componentes con soporte de temas

### 🔐 Autenticación y Seguridad

- **[PASSWORD_RECOVERY.md](./PASSWORD_RECOVERY.md)** - Sistema de recuperación de contraseñas
  - Flujo de recuperación
  - Códigos de verificación
  - Expiración de tokens

- **[PASSWORD_CHANGE_NOTIFICATION.md](./PASSWORD_CHANGE_NOTIFICATION.md)** - Notificaciones de cambio de contraseña

### 🎯 Funcionalidades Implementadas

- **[ROLE_BASED_VIEWS.md](./ROLE_BASED_VIEWS.md)** - Vistas basadas en roles (STUDENT, TEACHER, ADMIN)
  - Renderizado condicional
  - Permisos por rol
  - Restricciones de UI

- **[USER_EXISTS_CHECK.md](./USER_EXISTS_CHECK.md)** - Verificación de existencia de usuarios
  - Endpoint de verificación
  - Integración en frontend
  - Indicadores visuales

- **[EMAIL_DUPLICATE_NOTIFICATION.md](./EMAIL_DUPLICATE_NOTIFICATION.md)** - Notificaciones de email duplicado
  - Detección de errores específicos
  - Mensajes de error mejorados
  - Enlaces de acción

- **[STUDENT_DASHBOARD_LAYOUT.md](./STUDENT_DASHBOARD_LAYOUT.md)** - Layout del dashboard de estudiantes
  - Diseño responsivo
  - Grids optimizados
  - Uso de espacio horizontal

### 🐛 Fixes y Correcciones

- **[RESULTS_COUNTER_FIX.md](./RESULTS_COUNTER_FIX.md)** - Corrección de contadores de resultados
  - Problema de compatibilidad de keys
  - Solución implementada
  - Stats con formato dual

- **[NOTIFICATION_FIX.md](./NOTIFICATION_FIX.md)** - Correcciones en el sistema de notificaciones

### 👨‍🏫 Documentación Específica

- **[TEACHER_DOCS.txt](./TEACHER_DOCS.txt)** - Documentación específica para profesores

---

## 🏗️ Estructura del Proyecto

```
DevTrack/
├── docs/                    # 📚 Documentación (estás aquí)
├── backend/                 # 🐍 Django REST Framework API
│   ├── accounts/           # Autenticación y usuarios
│   ├── courses/            # Materias, ejercicios, resultados
│   ├── notifications/      # Sistema de notificaciones
│   └── config/             # Configuración del proyecto
├── frontend/               # ⚛️ React + Vite
│   └── src/
│       ├── components/     # Componentes reutilizables
│       ├── pages/          # Páginas de la aplicación
│       ├── contexts/       # Context API (Auth, Theme)
│       └── utils/          # Utilidades y helpers
└── samples/                # 📊 Archivos CSV de ejemplo

```

## 🚀 Quick Start

1. **Ver la API disponible:**
   - Lee [API_GUIDE.md](./API_GUIDE.md) para entender todos los endpoints
   - Accede a Swagger UI en `http://localhost:8000/api/docs/`

2. **Configurar el proyecto:**
   - Backend: Instala dependencias con `pip install -r requirements.txt`
   - Frontend: Instala dependencias con `npm install`

3. **Iniciar el desarrollo:**
   ```bash
   # Backend
   cd backend
   python manage.py runserver

   # Frontend (en otra terminal)
   cd frontend
   npm run dev
   ```

## 📝 Contribuir a la Documentación

Si añades una nueva funcionalidad o fix importante:

1. Crea un archivo `.md` con un nombre descriptivo
2. Documenta el problema, solución e implementación
3. Añádelo a este índice en la sección correspondiente
4. Incluye ejemplos de código si es relevante

## 🔗 Enlaces Útiles

- **API Docs (Swagger):** http://localhost:8000/api/docs/
- **Panel Admin:** http://localhost:8000/admin/
- **Frontend Dev:** http://localhost:5173/

---

**Última actualización:** 18 de Octubre, 2025
