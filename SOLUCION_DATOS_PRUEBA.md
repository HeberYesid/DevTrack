# 🔧 GUÍA DE SOLUCIÓN: Ejercicios de Prueba No Se Guardan

## ❌ Problema
Al instalar DevTrack en una nueva máquina, los ejercicios de prueba no aparecen en el sistema.

## ✅ Solución Completa

### Paso 1: Verificar Instalación de Dependencias
```bash
# Verificar que Django esté instalado
python -c "import django; print(django.VERSION)"

# Verificar que el proyecto funcione
python manage.py check
```

### Paso 2: Configurar Variables de Entorno
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### Paso 3: Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 4: CREAR DATOS DE PRUEBA (PASO CRÍTICO)
```bash
python manage.py create_sample_data
```

### Paso 5: Verificar que los Datos se Crearon
```bash
python manage.py shell -c "from exercises.models import Exercise; print(f'Ejercicios creados: {Exercise.objects.count()}')"
```

## 🚀 Instalación Automática (Recomendada)

### Windows
```bash
install_windows.bat
```

### Linux/Mac
```bash
chmod +x install_linux_mac.sh
./install_linux_mac.sh
```

## 🔍 Verificación Manual

### Comando de Verificación Rápida
```bash
# Ejecutar este script para verificar todo
test_sample_data.bat  # Windows
```

### Verificar Base de Datos Manualmente
```bash
python manage.py shell
```

```python
from exercises.models import Exercise, ExerciseSubmission, User

# Verificar ejercicios
print(f"Ejercicios: {Exercise.objects.count()}")
if Exercise.objects.count() > 0:
    print("✅ Ejercicios encontrados:")
    for ex in Exercise.objects.all()[:3]:
        print(f"  - {ex.title}")
else:
    print("❌ No hay ejercicios - ejecuta: python manage.py create_sample_data")

# Verificar usuarios
users = User.objects.filter(username__startswith='estudiante')
print(f"\nUsuarios de prueba: {users.count()}")
if users.count() > 0:
    print("✅ Usuarios encontrados:")
    for user in users:
        print(f"  - {user.username}")
else:
    print("❌ No hay usuarios de prueba")

# Verificar envíos
submissions = ExerciseSubmission.objects.count()
print(f"\nEnvíos de ejercicios: {submissions}")
```

## 🐛 Problemas Comunes y Soluciones

### Error: "No module named 'exercises'"
**Causa:** Las migraciones no se han ejecutado correctamente.
**Solución:**
```bash
python manage.py makemigrations exercises
python manage.py migrate
```

### Error: "FOREIGN KEY constraint failed"
**Causa:** Problema en el orden de creación de objetos.
**Solución:**
```bash
# Eliminar base de datos y recrear
rm db.sqlite3  # Solo para SQLite
python manage.py migrate
python manage.py create_sample_data
```

### Error: "mysqlclient not installed"
**Causa:** Problema con la instalación de mysqlclient.
**Solución:**
```bash
# Cambiar a SQLite temporalmente en .env
DB_ENGINE=django.db.backends.sqlite3

# O instalar mysqlclient correctamente (ver README.md)
```

### Los ejercicios se crean pero no aparecen en la web
**Causa:** Problema de permisos o configuración de templates.
**Solución:**
```bash
# Verificar que el servidor esté corriendo
python manage.py runserver

# Verificar en Django Admin
python manage.py createsuperuser
# Ir a http://127.0.0.1:8000/admin/
```

### Error: "Secret key not configured"
**Causa:** Archivo .env mal configurado.
**Solución:**
```bash
# Verificar que .env existe y tiene SECRET_KEY
echo "SECRET_KEY=django-insecure-ejemplo-key-123" >> .env
```

## 📞 Si Nada Funciona

### Reinstalación Completa
```bash
# 1. Eliminar entorno virtual
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows

# 2. Eliminar base de datos
rm db.sqlite3  # Solo si usas SQLite

# 3. Ejecutar instalación automática
install_windows.bat  # Windows
./install_linux_mac.sh  # Linux/Mac
```

### Verificación Final
Después de cualquier solución, siempre ejecuta:
```bash
python manage.py create_sample_data
python manage.py runserver
```

Y verifica en http://127.0.0.1:8000/exercises/ que aparezcan los ejercicios.

## 👥 Usuarios de Prueba Creados

Una vez que el comando funcione, tendrás estos usuarios:
- **estudiante1** - Contraseña: `password123`
- **estudiante2** - Contraseña: `password123`
- **estudiante3** - Contraseña: `password123`
- **estudiante4** - Contraseña: `password123`
- **estudiante5** - Contraseña: `password123`

## 📊 Datos Creados

El comando `create_sample_data` crea:
- **10 ejercicios** de diferentes dificultades
- **5 usuarios estudiantes** con contraseñas
- **Envíos aleatorios** con estados Verde/Amarillo/Rojo
- **Calificaciones automáticas** basadas en los envíos
- **Perfiles de usuario** completos

---

**💡 Tip:** Siempre ejecuta `python manage.py create_sample_data` después de una instalación nueva.
