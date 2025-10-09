# 📁 Archivos de Muestra - DevTrack

Estos archivos CSV sirven como ejemplos para importar datos masivamente al sistema.

## 📄 Archivos Disponibles

### 1. enrollments.csv
**Propósito:** Inscribir estudiantes a materias

**Campos:**
- `email` - Email del estudiante (debe existir en el sistema)
- `first_name` - Nombres del estudiante
- `last_name` - Apellidos del estudiante

**Ejemplo:**
```csv
email,first_name,last_name
erickmatoja@gmail.com,Erick,Toloza
jairssv@gmail.com,Jair,Sanjuan
```

**Uso:**
1. Los estudiantes deben estar registrados previamente
2. Se pueden inscribir a múltiples materias
3. No se permiten inscripciones duplicadas

---

### 2. student_results.csv
**Propósito:** Cargar resultados de ejercicios de estudiantes

**Campos:**
- `student_email` - Email del estudiante inscrito
- `exercise_name` - Nombre del ejercicio
- `status` - Resultado del ejercicio: `GREEN`, `YELLOW`, o `RED`

**Ejemplo:**
```csv
student_email,exercise_name,status
erickmatoja@gmail.com,Ejercicio 1 - Ecuaciones,GREEN
erickmatoja@gmail.com,Ejercicio 2 - Derivadas,YELLOW
jairssv@gmail.com,Ejercicio 1 - Ecuaciones,GREEN
```

**⚠️ Nota Importante:**
- Los ejercicios se crean **automáticamente** si no existen al subir el CSV
- También puedes crear ejercicios manualmente desde la página de la materia antes de subir resultados

**Estados Disponibles:**
- 🟢 **GREEN** - Ejercicio completado exitosamente
- 🟡 **YELLOW** - Ejercicio completado con observaciones
- 🔴 **RED** - Ejercicio no completado o con errores

**Validaciones:**
1. El estudiante debe estar inscrito en la materia
2. El ejercicio debe existir en la materia
3. El status debe ser GREEN, YELLOW o RED
4. No se permiten resultados duplicados para el mismo ejercicio

---

## 🚀 Cómo Usar los Archivos

### Opción 1: Importación Manual via Admin

1. Accede al panel de administración: `http://localhost:8000/admin/`
2. Ve a la sección correspondiente (Enrollments o Results)
3. Usa la opción de importación masiva
4. Selecciona el archivo CSV
5. Confirma la importación

### Opción 2: Script de Importación

```python
# Ejemplo para importar resultados
import csv
from courses.models import Subject, Exercise, Enrollment, StudentExerciseResult
from accounts.models import User

with open('student_results.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        try:
            user = User.objects.get(email=row['email'])
            subject = Subject.objects.get(code=row['subject_code'])
            enrollment = Enrollment.objects.get(student=user, subject=subject)
            exercise = Exercise.objects.get(
                subject=subject, 
                name=row['exercise_name']
            )
            
            StudentExerciseResult.objects.update_or_create(
                enrollment=enrollment,
                exercise=exercise,
                defaults={'status': row['status']}
            )
            print(f"✅ Resultado creado: {user.email} - {exercise.name}")
        except Exception as e:
            print(f"❌ Error en {row['email']}: {e}")
```

### Opción 3: Comando de Management

```bash
# Importar inscripciones
python manage.py import_enrollments samples/enrollments.csv

# Importar resultados
python manage.py import_results samples/student_results.csv
```

---

## 📊 Cálculo de Calificaciones

El sistema calcula automáticamente:

- **Total de ejercicios** completados
- **Distribución de estados** (verde/amarillo/rojo)
- **Nota numérica** basada en el desempeño
- **Semáforo general** del estudiante en la materia

### Fórmula de Calificación:

- **100% verde** → Nota: 5.0 🟢
- **≥60% amarillo** → Nota: 3.0 🟡
- **Mixto** → Nota: 5.0 × (verdes/total) 📊
- **Mayoría rojo** → Nota proporcional 🔴

---

## ⚠️ Notas Importantes

1. **Formato CSV**: Asegúrate de usar UTF-8 con BOM para caracteres especiales
2. **Headers obligatorios**: La primera fila debe contener los nombres de las columnas
3. **Datos limpios**: Evita espacios en blanco al inicio o final de los valores
4. **Validación**: El sistema validará cada fila antes de importar
5. **Backup**: Siempre haz un backup antes de importaciones masivas

---

## 🔧 Crear tus Propios Archivos

### Template para Resultados:

```csv
email,subject_code,exercise_name,status
estudiante@ejemplo.com,CODIGO_MATERIA,Nombre del Ejercicio,GREEN
```

### Template para Inscripciones:

```csv
email,first_name,last_name
estudiante@ejemplo.com,Nombre,Apellido
```

---

## 📞 Soporte

Si tienes problemas con la importación:

1. Verifica que los emails existan en el sistema
2. Confirma que los códigos de materia sean correctos
3. Asegúrate de que los ejercicios estén creados
4. Revisa los logs del servidor para errores específicos

---

## 📈 Estadísticas Post-Importación

Después de importar resultados, puedes ver:

- **Dashboard del estudiante**: Resumen de su desempeño
- **Vista de materia**: Progreso de todos los estudiantes
- **Reportes**: Estadísticas agregadas por ejercicio

---

**Última actualización:** Octubre 2025
**Versión:** 1.0
