# OnlineGDB Stats - Sistema de Estadísticas de Ejercicios

Una aplicación web Django para hacer seguimiento y estadísticas de ejercicios de programación realizados en OnlineGDB.

## 🚀 Características

- **Sistema de Semáforos**: Clasifica ejercicios con indicadores Verde/Amarillo/Rojo
- **Cálculo Automático de Notas**: 
  - 100% Verde = 5.0
  - 60% Amarillo = 3.0
  - Resto = (Ejercicios Verdes / Total) × 5.0
- **Dashboard Interactivo**: Gráficas y estadísticas en tiempo real
- **Gestión de Usuarios**: Sistema completo de autenticación
- **Panel Administrativo**: Gestión completa desde Django Admin
- **Responsive Design**: Compatible con dispositivos móviles

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.11+ + Django 5.2
- **Base de Datos**: SQLite (desarrollo) / MySQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Gráficas**: Chart.js
- **Iconos**: Font Awesome 6

## 📋 Requisitos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Virtualenv (recomendado)

### Para producción con MySQL:
- MySQL 5.7+ o MariaDB 10.2+
- mysqlclient

## 🚀 Instalación y Configuración

### Instalación Automática (Recomendada)

Para una instalación rápida y sin errores, usa los scripts automáticos:

**Windows:**
```bash
install_windows.bat
```

**Linux/Mac:**
```bash
chmod +x install_linux_mac.sh
./install_linux_mac.sh
```

Los scripts automáticos ejecutan todos los pasos necesarios:
- Crean el entorno virtual
- Instalan dependencias
- Configuran variables de entorno
- Ejecutan migraciones
- **Crean datos de prueba automáticamente**

### Instalación Manual

Si prefieres instalar paso a paso:

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd proyecto1.0
```

### 2. Crear y activar entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install django mysqlclient django-cors-headers pillow python-decouple whitenoise
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de configuración de ejemplo
copy .env.example .env

# En Linux/Mac usar:
# cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones. Para desarrollo básico, puedes usar la configuración por defecto (SQLite).

### 5. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario
```bash
python manage.py createsuperuser
```

### 7. Cargar datos de prueba (IMPORTANTE)
```bash
# Crear ejercicios y usuarios de ejemplo para probar el sistema
python manage.py create_sample_data
```

Este comando creará:
- 10 ejercicios de ejemplo con diferentes dificultades
- 5 usuarios estudiantes (estudiante1 a estudiante5, contraseña: password123)
- Envíos de ejercicios con estados Verde/Amarillo/Rojo aleatorios
- Calificaciones calculadas automáticamente

### 8. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

La aplicación estará disponible en: http://127.0.0.1:8000

## 📊 Uso del Sistema

### Para Estudiantes:
1. **Registro**: Crear cuenta en el sistema
2. **Ejercicios**: Explorar lista de ejercicios disponibles
3. **Envío**: Registrar estado de ejercicios (Verde/Amarillo/Rojo)
4. **Dashboard**: Ver progreso y estadísticas personales
5. **Perfil**: Gestionar información personal

### Para Administradores:
1. **Admin Panel**: Acceso a `/admin/`
2. **Gestión de Ejercicios**: Crear, editar y eliminar ejercicios
3. **Revisión de Envíos**: Validar y modificar estados de ejercicios
4. **Gestión de Usuarios**: Administrar cuentas de estudiantes

## 🗂️ Estructura del Proyecto

```
proyecto1.0/
├── onlinegdb_stats/          # Configuración principal
├── exercises/                # App de ejercicios
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Lógica de vistas
│   ├── forms.py             # Formularios
│   └── admin.py             # Configuración admin
├── dashboard/               # App del dashboard
├── templates/               # Templates HTML
│   ├── base.html           # Template base
│   ├── exercises/          # Templates de ejercicios
│   ├── dashboard/          # Templates del dashboard
│   └── registration/       # Templates de autenticación
├── static/                  # Archivos estáticos
│   ├── css/
│   └── js/
├── media/                   # Archivos subidos
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## 🎨 Sistema de Calificación

El sistema implementa la lógica de calificación especificada:

1. **100% Ejercicios Verdes**: Nota = 5.0
2. **60% o más Ejercicios Amarillos**: Nota = 3.0
3. **Otros casos**: Nota = (Ejercicios Verdes ÷ Total de Ejercicios) × 5.0

## 🚀 Despliegue en Producción

### Opciones Gratuitas Recomendadas:

1. **Railway** (recomendado)
2. **Heroku** (plan gratuito limitado)
3. **PythonAnywhere**
4. **Google Cloud Platform** (créditos gratuitos)

### Configuración para Producción:

1. **Variables de entorno**:
```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
SECRET_KEY=clave-secreta-produccion
DB_ENGINE=django.db.backends.mysql
# ... configuración MySQL
```

2. **Archivos estáticos**:
```bash
python manage.py collectstatic
```

3. **Configurar WhiteNoise** (ya incluido) para servir archivos estáticos

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

### Problemas Comunes

#### Los ejercicios de prueba no aparecen
Si después de la instalación no ves ejercicios en el sistema:

1. **Verificar que se ejecutó el comando de datos de prueba:**
```bash
python manage.py create_sample_data
```

2. **Verificar la base de datos:**
```bash
python manage.py shell
```
```python
from exercises.models import Exercise
print(f"Ejercicios en DB: {Exercise.objects.count()}")
```

3. **Verificar configuración de .env:**
   - Asegúrate de que el archivo `.env` existe
   - Verifica la configuración de `DB_ENGINE`

4. **Recrear la base de datos (si es necesario):**
```bash
# CUIDADO: Esto borra todos los datos
rm db.sqlite3  # o elimina la base de datos MySQL
python manage.py migrate
python manage.py create_sample_data
```

#### Error al instalar mysqlclient
Si tienes problemas con mysqlclient:

**Windows:**
- Descarga el wheel desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
- Instala con: `pip install mysqlclient-x.x.x-cp3xx-cp3xx-win_amdxx.whl`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install default-libmysqlclient-dev build-essential

# CentOS/RHEL
sudo yum install mysql-devel gcc gcc-c++

# macOS
brew install mysql
```

#### No se pueden crear usuarios
Asegúrate de que las migraciones se ejecutaron correctamente:
```bash
python manage.py makemigrations exercises
python manage.py migrate
```

### Obtener Ayuda

#### Los ejercicios de prueba no aparecen
**📖 GUÍA COMPLETA:** Ver [`SOLUCION_DATOS_PRUEBA.md`](./SOLUCION_DATOS_PRUEBA.md) para una guía paso a paso detallada.

Si tienes problemas o preguntas:

1. Revisa la documentación
2. Busca en issues existentes
3. Crea un nuevo issue con detalles del problema

## 🔗 Referencias

- [Ejemplo GitLab](https://gitlab.com/estructuras-de-datos-ufps/flujo_revision_notas)
- [Demo Web](https://estructuras-de-datos-ufps.gitlab.io/flujo_revision_notas/visor/visor_fundamentos.html)
- [Documentación Django](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)

---

**OnlineGDB Stats** - Sistema de seguimiento académico para ejercicios de programación 📊
