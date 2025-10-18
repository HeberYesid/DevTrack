# 📚 Guía Completa de la API de DevTrack

## 🚀 Introducción

DevTrack es una API REST construida con Django REST Framework que permite gestionar un sistema de seguimiento académico. La API utiliza autenticación JWT (JSON Web Tokens) y sigue las mejores prácticas de REST.

**URL Base:** `http://localhost:8000/api/`

---

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Autenticación](#autenticación)
3. [Endpoints de Usuarios](#endpoints-de-usuarios)
4. [Endpoints de Cursos](#endpoints-de-cursos)
5. [Endpoints de Ejercicios y Resultados](#endpoints-de-ejercicios-y-resultados)
6. [Endpoints de Notificaciones](#endpoints-de-notificaciones)
7. [Códigos de Estado HTTP](#códigos-de-estado)
8. [Ejemplos con diferentes herramientas](#ejemplos-con-herramientas)

---

## ⚙️ Configuración Inicial

### 1. Iniciar el Servidor

```bash
# Navegar a la carpeta backend
cd backend

# Iniciar el servidor de desarrollo
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

### 2. Verificar que la API está funcionando

```bash
curl http://localhost:8000/
```

Respuesta esperada:
```json
{
  "message": "🎓 Bienvenido a DevTrack API",
  "version": "1.0.0",
  "status": "active",
  "endpoints": {
    "authentication": "/api/auth/",
    "courses": "/api/courses/",
    "notifications": "/api/notifs/",
    "admin_panel": "/admin/",
    "api_documentation": "/api/docs/",
    "api_schema": "/api/schema/"
  }
}
```

### 3. Documentación Interactiva

La API incluye documentación interactiva Swagger:

**URL:** `http://localhost:8000/api/docs/`

Aquí puedes:
- Ver todos los endpoints disponibles
- Probar las peticiones directamente desde el navegador
- Ver los esquemas de datos

---

## 🔐 Autenticación

DevTrack usa **JWT (JSON Web Tokens)** para autenticación. Hay 3 roles de usuario:
- **STUDENT** (Estudiante)
- **TEACHER** (Profesor)
- **ADMIN** (Administrador)

### 📝 Registro de Estudiante

**Endpoint:** `POST /api/auth/register/`

**Body (JSON):**
```json
{
  "email": "estudiante@ejemplo.com",
  "password": "MiPassword123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "turnstile_token": "token_del_captcha"
}
```

**Respuesta (201 Created):**
```json
{
  "message": "Registro exitoso. Hemos enviado un código de verificación de 6 dígitos a tu correo."
}
```

### 👨‍🏫 Registro de Profesor

**Endpoint:** `POST /api/auth/register-teacher/`

**Body (JSON):**
```json
{
  "email": "profesor@ejemplo.com",
  "password": "MiPassword123",
  "first_name": "María",
  "last_name": "García",
  "invitation_code": "ABC123",
  "turnstile_token": "token_del_captcha"
}
```

### ✅ Verificar Email con Código

**Endpoint:** `POST /api/auth/verify-code/`

**Body (JSON):**
```json
{
  "email": "estudiante@ejemplo.com",
  "code": "123456"
}
```

**Respuesta (200 OK):**
```json
{
  "message": "Email verificado exitosamente. Ya puedes iniciar sesión."
}
```

### 🔑 Iniciar Sesión

**Endpoint:** `POST /api/auth/login/`

**Body (JSON):**
```json
{
  "email": "estudiante@ejemplo.com",
  "password": "MiPassword123",
  "turnstile_token": "token_del_captcha"
}
```

**Respuesta (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "estudiante@ejemplo.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "role": "STUDENT",
    "is_verified": true
  }
}
```

**⚠️ IMPORTANTE:** Guarda el `access` token. Lo necesitarás para todas las peticiones autenticadas.

### 🔄 Refrescar Token

Los tokens de acceso expiran después de cierto tiempo. Para obtener uno nuevo:

**Endpoint:** `POST /api/auth/token/refresh/`

**Body (JSON):**
```json
{
  "refresh": "tu_refresh_token_aqui"
}
```

**Respuesta (200 OK):**
```json
{
  "access": "nuevo_access_token_aqui"
}
```

### 👤 Obtener Información del Usuario Actual

**Endpoint:** `GET /api/auth/me/`

**Headers:**
```
Authorization: Bearer {tu_access_token}
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "email": "estudiante@ejemplo.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "role": "STUDENT",
  "is_verified": true,
  "is_active": true
}
```

### 🔒 Cambiar Contraseña

**Endpoint:** `POST /api/auth/change-password/`

**Headers:**
```
Authorization: Bearer {tu_access_token}
```

**Body (JSON):**
```json
{
  "old_password": "MiPasswordViejo123",
  "new_password": "MiPasswordNuevo456"
}
```

### 🔓 Recuperar Contraseña (Olvidé mi contraseña)

**Paso 1: Solicitar código de recuperación**

**Endpoint:** `POST /api/auth/forgot-password/`

**Body (JSON):**
```json
{
  "email": "estudiante@ejemplo.com",
  "turnstile_token": "token_del_captcha"
}
```

**Paso 2: Restablecer con código**

**Endpoint:** `POST /api/auth/reset-password/`

**Body (JSON):**
```json
{
  "email": "estudiante@ejemplo.com",
  "code": "123456",
  "new_password": "MiNuevaPassword789",
  "turnstile_token": "token_del_captcha"
}
```

### ✉️ Verificar si un Usuario Existe

**Endpoint:** `GET /api/auth/check-user-exists/?email={email}`

**Headers:**
```
Authorization: Bearer {tu_access_token}
```

**Ejemplo:**
```
GET /api/auth/check-user-exists/?email=juan@ejemplo.com
```

**Respuesta si existe (200 OK):**
```json
{
  "exists": true,
  "email": "juan@ejemplo.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "role": "STUDENT",
  "is_active": true,
  "is_verified": true
}
```

**Respuesta si NO existe (404 Not Found):**
```json
{
  "exists": false,
  "detail": "Usuario no encontrado"
}
```

---

## 📚 Endpoints de Cursos

Todas estas peticiones requieren autenticación con token JWT.

### 📋 Listar Materias

**Endpoint:** `GET /api/courses/subjects/`

**Headers:**
```
Authorization: Bearer {tu_access_token}
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Programación Web",
    "code": "PW001",
    "teacher": {
      "id": 2,
      "email": "profesor@ejemplo.com",
      "first_name": "María",
      "last_name": "García"
    },
    "created_at": "2025-10-01T10:00:00Z"
  },
  {
    "id": 2,
    "name": "Base de Datos",
    "code": "BD001",
    "teacher": {...}
  }
]
```

**Filtros disponibles:**
- Los **estudiantes** solo ven materias donde están inscritos
- Los **profesores** solo ven sus propias materias
- Los **admins** ven todas las materias

### 📖 Obtener Detalle de una Materia

**Endpoint:** `GET /api/courses/subjects/{id}/`

**Ejemplo:**
```
GET /api/courses/subjects/1/
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "name": "Programación Web",
  "code": "PW001",
  "teacher": {
    "id": 2,
    "email": "profesor@ejemplo.com",
    "first_name": "María",
    "last_name": "García"
  },
  "created_at": "2025-10-01T10:00:00Z",
  "enrollments_count": 25
}
```

### ➕ Crear una Materia (Solo Profesores/Admins)

**Endpoint:** `POST /api/courses/subjects/`

**Headers:**
```
Authorization: Bearer {tu_access_token}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "name": "Inteligencia Artificial",
  "code": "IA001"
}
```

**Respuesta (201 Created):**
```json
{
  "id": 3,
  "name": "Inteligencia Artificial",
  "code": "IA001",
  "teacher": {
    "id": 2,
    "email": "profesor@ejemplo.com",
    "first_name": "María",
    "last_name": "García"
  },
  "created_at": "2025-10-18T15:30:00Z"
}
```

### ✏️ Actualizar una Materia

**Endpoint:** `PUT /api/courses/subjects/{id}/`

**Body (JSON):**
```json
{
  "name": "Inteligencia Artificial Avanzada",
  "code": "IA001"
}
```

### 🗑️ Eliminar una Materia

**Endpoint:** `DELETE /api/courses/subjects/{id}/`

**Respuesta (204 No Content)**

### 👥 Obtener Estudiantes Inscritos

**Endpoint:** `GET /api/courses/subjects/{id}/enrollments/`

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "student": {
      "id": 1,
      "email": "estudiante@ejemplo.com",
      "first_name": "Juan",
      "last_name": "Pérez"
    },
    "created_at": "2025-10-02T09:00:00Z"
  }
]
```

### ➕ Inscribir un Estudiante

**Endpoint:** `POST /api/courses/subjects/{id}/enrollments/`

**Body (JSON):**
```json
{
  "student_email": "nuevo@ejemplo.com"
}
```

**Respuesta (201 Created):**
```json
{
  "id": 2,
  "student": {
    "id": 5,
    "email": "nuevo@ejemplo.com",
    "first_name": "Carlos",
    "last_name": "López"
  },
  "created_at": "2025-10-18T16:00:00Z"
}
```

**Nota:** Si el estudiante no existe, se crea automáticamente y se le envía un email de verificación.

### 📤 Carga Masiva de Estudiantes (CSV)

**Endpoint:** `POST /api/courses/subjects/{id}/enrollments/upload-csv/`

**Headers:**
```
Authorization: Bearer {tu_access_token}
Content-Type: multipart/form-data
```

**Body (Form Data):**
```
file: archivo.csv
```

**Formato del CSV:**
```csv
email,first_name,last_name
juan@ejemplo.com,Juan,Pérez
maria@ejemplo.com,María,García
```

**Respuesta (200 OK):**
```json
{
  "created": 2,
  "existed": 0,
  "errors": []
}
```

### 📊 Dashboard de una Materia

**Endpoint:** `GET /api/courses/subjects/{id}/dashboard/`

**Respuesta (200 OK):**
```json
{
  "total_exercises": 10,
  "aggregates": {
    "avg_grade": 4.2,
    "pct_green": 65.0,
    "pct_yellow": 25.0,
    "pct_red": 10.0
  },
  "enrollments": [
    {
      "enrollment_id": 1,
      "student_email": "juan@ejemplo.com",
      "total": 10,
      "green": 7,
      "yellow": 2,
      "red": 1,
      "grade": 4.5,
      "semaphore": "GREEN"
    }
  ]
}
```

### 📥 Exportar Resultados a CSV

**Endpoint:** `GET /api/courses/subjects/{id}/export-csv/`

**Respuesta:** Descarga un archivo CSV con todos los resultados de la materia.

---

## 📝 Endpoints de Ejercicios y Resultados

### 📋 Listar Ejercicios

**Endpoint:** `GET /api/courses/exercises/`

**Query Parameters:**
- `subject={id}` - Filtrar por materia

**Ejemplo:**
```
GET /api/courses/exercises/?subject=1
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Ejercicio 1 - Variables",
    "subject": 1,
    "order": 1,
    "deadline": "2025-10-25T23:59:59Z",
    "description": "Práctica de declaración de variables"
  }
]
```

### ➕ Crear un Ejercicio (Solo Profesores/Admins)

**Endpoint:** `POST /api/courses/exercises/`

**Body (JSON):**
```json
{
  "subject": 1,
  "name": "Ejercicio 2 - Funciones",
  "description": "Práctica de funciones en JavaScript",
  "deadline": "2025-10-30T23:59:59Z",
  "order": 2
}
```

### ✏️ Actualizar un Ejercicio

**Endpoint:** `PUT /api/courses/exercises/{id}/`

### 🗑️ Eliminar un Ejercicio

**Endpoint:** `DELETE /api/courses/exercises/{id}/`

### 📊 Listar Resultados

**Endpoint:** `GET /api/courses/results/`

**Query Parameters:**
- `subject={id}` - Filtrar por materia
- `enrollment={id}` - Filtrar por inscripción

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "enrollment": 1,
    "exercise": 1,
    "status": "GREEN",
    "comment": "¡Excelente trabajo!",
    "created_at": "2025-10-15T10:00:00Z",
    "updated_at": "2025-10-15T10:00:00Z"
  }
]
```

**Estados posibles:**
- `GREEN` - Verde (Completado exitosamente)
- `YELLOW` - Amarillo (Con observaciones)
- `RED` - Rojo (No completado)

### ➕ Crear/Asignar un Resultado (Solo Profesores/Admins)

**Endpoint:** `POST /api/courses/results/`

**Body (JSON):**
```json
{
  "enrollment_id": 1,
  "exercise_id": 1,
  "status": "GREEN",
  "comment": "¡Excelente trabajo! Sigue así."
}
```

### ✏️ Actualizar un Resultado

**Endpoint:** `PUT /api/courses/results/{id}/`

**Body (JSON):**
```json
{
  "status": "YELLOW",
  "comment": "Buen intento, pero revisa la lógica del bucle."
}
```

### 📤 Carga Masiva de Resultados (CSV)

**Endpoint:** `POST /api/courses/subjects/{id}/results/upload-csv/`

**Body (Form Data):**
```
file: resultados.csv
```

**Formato del CSV:**
```csv
student_email,exercise_name,status,comment
juan@ejemplo.com,Ejercicio 1,GREEN,Excelente
maria@ejemplo.com,Ejercicio 1,YELLOW,Revisa la sintaxis
```

---

## 📱 Endpoints de Estudiantes

### 📚 Mis Inscripciones

**Endpoint:** `GET /api/courses/my-enrollments/`

**Headers:**
```
Authorization: Bearer {tu_access_token}
```

**Respuesta (200 OK):**
```json
{
  "enrollments": [
    {
      "enrollment_id": 1,
      "subject_id": 1,
      "subject_code": "PW001",
      "subject_name": "Programación Web",
      "stats": {
        "total_exercises": 10,
        "green_count": 7,
        "yellow_count": 2,
        "red_count": 1,
        "grade": 4.5,
        "semaphore": "GREEN"
      }
    }
  ]
}
```

### 📊 Dashboard del Estudiante

**Endpoint:** `GET /api/courses/student-dashboard/`

**Respuesta (200 OK):**
```json
{
  "summary": {
    "total_results": 45,
    "green_count": 30,
    "yellow_count": 10,
    "red_count": 5,
    "success_rate": 66.7,
    "total_pending": 5
  },
  "subjects_progress": [
    {
      "subject_id": 1,
      "subject_name": "Programación Web",
      "subject_code": "PW001",
      "total_exercises": 10,
      "completed_exercises": 8,
      "green_count": 6,
      "yellow_count": 2,
      "red_count": 0,
      "completion_rate": 80,
      "success_rate": 75.0
    }
  ],
  "pending_exercises": [
    {
      "id": 5,
      "name": "Ejercicio 5 - Arrays",
      "subject_id": 1,
      "subject_name": "Programación Web",
      "subject_code": "PW001",
      "deadline": "2025-10-25T23:59:59Z"
    }
  ],
  "recent_results": [
    {
      "id": 1,
      "exercise_name": "Ejercicio 1",
      "subject_name": "Programación Web",
      "status": "GREEN",
      "comment": "Excelente trabajo",
      "created_at": "2025-10-18T10:00:00Z"
    }
  ]
}
```

### 📝 Ver Resultados de una Inscripción

**Endpoint:** `GET /api/courses/enrollments/{enrollment_id}/results/`

**Respuesta (200 OK):**
```json
{
  "enrollment_id": 1,
  "student_email": "juan@ejemplo.com",
  "results": [
    {
      "exercise_id": 1,
      "exercise_name": "Ejercicio 1",
      "status": "GREEN",
      "updated_at": "2025-10-15T10:00:00Z"
    }
  ],
  "stats": {
    "total_exercises": 10,
    "green_count": 7,
    "yellow_count": 2,
    "red_count": 1,
    "grade": 4.5,
    "semaphore": "GREEN"
  }
}
```

---

## 🔔 Endpoints de Notificaciones

### 📋 Listar Notificaciones

**Endpoint:** `GET /api/courses/notifications/`

**Headers:**
```
Authorization: Bearer {tu_access_token}
```

**Respuesta (200 OK):**
```json
[
  {
    "id": 1,
    "notification_type": "RESULT_CREATED",
    "title": "Nuevo resultado registrado",
    "message": "Se registró un resultado VERDE en Ejercicio 1 de Programación Web",
    "is_read": false,
    "created_at": "2025-10-18T14:30:00Z"
  }
]
```

**Tipos de notificación:**
- `ENROLLMENT` - Inscripción a materia
- `RESULT_CREATED` - Resultado creado
- `RESULT_UPDATED` - Resultado actualizado
- `EXERCISE_CREATED` - Ejercicio creado
- `GENERAL` - Notificación general

### 📬 Contar Notificaciones No Leídas

**Endpoint:** `GET /api/courses/notifications/unread-count/`

**Respuesta (200 OK):**
```json
{
  "unread_count": 5
}
```

### ✅ Marcar Notificación como Leída

**Endpoint:** `POST /api/courses/notifications/{id}/mark-read/`

**Respuesta (200 OK):**
```json
{
  "message": "Notificación marcada como leída",
  "notification": {
    "id": 1,
    "is_read": true,
    ...
  }
}
```

### ✅ Marcar Todas como Leídas

**Endpoint:** `POST /api/courses/notifications/mark-all-read/`

**Respuesta (200 OK):**
```json
{
  "message": "5 notificaciones marcadas como leídas",
  "updated_count": 5
}
```

---

## 📊 Códigos de Estado HTTP

La API usa los códigos de estado HTTP estándar:

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Petición exitosa |
| 201 | Created | Recurso creado exitosamente |
| 204 | No Content | Recurso eliminado exitosamente |
| 400 | Bad Request | Datos inválidos en la petición |
| 401 | Unauthorized | Token faltante o inválido |
| 403 | Forbidden | Sin permisos para la acción |
| 404 | Not Found | Recurso no encontrado |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Error del servidor |

---

## 🛠️ Ejemplos con Diferentes Herramientas

### 🖥️ cURL

**Registro de usuario:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com",
    "password": "Test12345",
    "first_name": "Test",
    "last_name": "User",
    "turnstile_token": "token_aqui"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com",
    "password": "Test12345",
    "turnstile_token": "token_aqui"
  }'
```

**Listar materias (con autenticación):**
```bash
curl -X GET http://localhost:8000/api/courses/subjects/ \
  -H "Authorization: Bearer tu_token_aqui"
```

### 🐍 Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
login_data = {
    "email": "test@ejemplo.com",
    "password": "Test12345",
    "turnstile_token": "token_aqui"
}

response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
token = response.json()["access"]

# Listar materias
headers = {
    "Authorization": f"Bearer {token}"
}

subjects = requests.get(f"{BASE_URL}/courses/subjects/", headers=headers)
print(subjects.json())

# Crear una materia
new_subject = {
    "name": "Machine Learning",
    "code": "ML001"
}

response = requests.post(
    f"{BASE_URL}/courses/subjects/",
    headers=headers,
    json=new_subject
)
print(response.json())
```

### 🟢 Node.js (axios)

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api';

// Login
async function login() {
  try {
    const response = await axios.post(`${BASE_URL}/auth/login/`, {
      email: 'test@ejemplo.com',
      password: 'Test12345',
      turnstile_token: 'token_aqui'
    });
    
    return response.data.access;
  } catch (error) {
    console.error('Error en login:', error.response.data);
  }
}

// Listar materias
async function getSubjects(token) {
  try {
    const response = await axios.get(`${BASE_URL}/courses/subjects/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error al obtener materias:', error.response.data);
  }
}

// Uso
(async () => {
  const token = await login();
  const subjects = await getSubjects(token);
  console.log(subjects);
})();
```

### 📮 Postman

1. **Crear una colección** llamada "DevTrack API"

2. **Configurar variables de entorno:**
   - `base_url`: `http://localhost:8000/api`
   - `token`: (se llenará después del login)

3. **Crear petición de Login:**
   - Método: `POST`
   - URL: `{{base_url}}/auth/login/`
   - Body (JSON):
     ```json
     {
       "email": "test@ejemplo.com",
       "password": "Test12345",
       "turnstile_token": "token_aqui"
     }
     ```
   - Tests (para guardar el token automáticamente):
     ```javascript
     if (pm.response.code === 200) {
       pm.environment.set("token", pm.response.json().access);
     }
     ```

4. **Crear petición autenticada:**
   - Método: `GET`
   - URL: `{{base_url}}/courses/subjects/`
   - Authorization:
     - Type: `Bearer Token`
     - Token: `{{token}}`

### 🦊 HTTPie

```bash
# Login
http POST http://localhost:8000/api/auth/login/ \
  email=test@ejemplo.com \
  password=Test12345 \
  turnstile_token=token_aqui

# Listar materias
http GET http://localhost:8000/api/courses/subjects/ \
  "Authorization:Bearer tu_token_aqui"

# Crear materia
http POST http://localhost:8000/api/courses/subjects/ \
  "Authorization:Bearer tu_token_aqui" \
  name="Redes de Computadoras" \
  code="RC001"
```

---

## 🔒 Seguridad

### Rate Limiting

La API implementa rate limiting para prevenir abuso:

- **Endpoints de autenticación:** 5 intentos por 5 minutos
- **Otros endpoints:** 100 peticiones por minuto

Si excedes el límite, recibirás un error `429 Too Many Requests`.

### CORS

El backend está configurado para permitir peticiones desde `http://localhost:5173` (frontend de desarrollo).

Para producción, ajusta `CORS_ALLOWED_ORIGINS` en `config/settings.py`.

### Turnstile Captcha

Los endpoints de registro y login requieren un token de Cloudflare Turnstile para prevenir bots. En desarrollo, puedes omitirlo o usar un token de prueba.

---

## 📝 Notas Importantes

1. **Tokens JWT:** Los tokens de acceso expiran después de 60 minutos. Usa el refresh token para obtener uno nuevo.

2. **Permisos:**
   - Estudiantes: Solo pueden ver sus propias materias e inscripciones
   - Profesores: Pueden gestionar sus materias y estudiantes
   - Admins: Acceso completo a toda la plataforma

3. **Creación automática de usuarios:** Al inscribir un estudiante que no existe, se crea automáticamente con contraseña temporal y se envía email de verificación.

4. **Notificaciones:** Se generan automáticamente para eventos como:
   - Inscripción a materia
   - Creación/actualización de resultados
   - Creación de ejercicios

5. **Carga masiva CSV:** Los archivos CSV deben tener codificación UTF-8 y las columnas deben coincidir exactamente con los nombres especificados.

---

## 🐛 Solución de Problemas

### Error 401 Unauthorized

**Causa:** Token inválido o expirado

**Solución:** Usa el refresh token para obtener un nuevo access token o vuelve a hacer login.

### Error 403 Forbidden

**Causa:** No tienes permisos para realizar la acción

**Solución:** Verifica que tu rol de usuario tiene los permisos necesarios.

### Error 404 Not Found

**Causa:** El recurso no existe o no tienes acceso a él

**Solución:** Verifica el ID del recurso y tus permisos.

### Error 429 Too Many Requests

**Causa:** Excediste el rate limit

**Solución:** Espera unos minutos antes de hacer más peticiones.

---

## 📚 Recursos Adicionales

- **Documentación interactiva:** `http://localhost:8000/api/docs/`
- **Schema OpenAPI:** `http://localhost:8000/api/schema/`
- **Panel de administración:** `http://localhost:8000/admin/`

---

## 💡 Ejemplos de Flujos Completos

### Flujo de Profesor: Crear materia e inscribir estudiantes

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Login como profesor
login_response = requests.post(f"{BASE_URL}/auth/login/", json={
    "email": "profesor@ejemplo.com",
    "password": "ProfePassword123",
    "turnstile_token": "token"
})
token = login_response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Crear una materia
subject_response = requests.post(
    f"{BASE_URL}/courses/subjects/",
    headers=headers,
    json={"name": "Cálculo I", "code": "CALC001"}
)
subject_id = subject_response.json()["id"]
print(f"Materia creada con ID: {subject_id}")

# 3. Inscribir estudiantes individualmente
students = ["est1@ejemplo.com", "est2@ejemplo.com", "est3@ejemplo.com"]

for email in students:
    enrollment_response = requests.post(
        f"{BASE_URL}/courses/subjects/{subject_id}/enrollments/",
        headers=headers,
        json={"student_email": email}
    )
    print(f"Estudiante {email} inscrito")

# 4. Crear ejercicios
exercises = [
    {"name": "Ejercicio 1 - Límites", "description": "Calcular límites", "order": 1},
    {"name": "Ejercicio 2 - Derivadas", "description": "Derivar funciones", "order": 2}
]

for exercise in exercises:
    exercise_data = {**exercise, "subject": subject_id}
    ex_response = requests.post(
        f"{BASE_URL}/courses/exercises/",
        headers=headers,
        json=exercise_data
    )
    print(f"Ejercicio '{exercise['name']}' creado")

# 5. Ver dashboard
dashboard_response = requests.get(
    f"{BASE_URL}/courses/subjects/{subject_id}/dashboard/",
    headers=headers
)
print("Dashboard:", dashboard_response.json())
```

### Flujo de Estudiante: Ver mis materias y resultados

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Login como estudiante
login_response = requests.post(f"{BASE_URL}/auth/login/", json={
    "email": "estudiante@ejemplo.com",
    "password": "EstPassword123",
    "turnstile_token": "token"
})
token = login_response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Ver mis inscripciones
enrollments_response = requests.get(
    f"{BASE_URL}/courses/my-enrollments/",
    headers=headers
)
my_enrollments = enrollments_response.json()["enrollments"]
print(f"Estoy inscrito en {len(my_enrollments)} materias")

# 3. Ver mi dashboard general
dashboard_response = requests.get(
    f"{BASE_URL}/courses/student-dashboard/",
    headers=headers
)
dashboard = dashboard_response.json()
print(f"Tasa de éxito: {dashboard['summary']['success_rate']}%")

# 4. Ver resultados detallados de cada materia
for enrollment in my_enrollments:
    enrollment_id = enrollment["enrollment_id"]
    subject_name = enrollment["subject_name"]
    
    results_response = requests.get(
        f"{BASE_URL}/courses/enrollments/{enrollment_id}/results/",
        headers=headers
    )
    results = results_response.json()
    
    print(f"\n=== {subject_name} ===")
    print(f"Nota: {results['stats']['grade']}")
    print(f"Verdes: {results['stats']['green_count']}")
    print(f"Amarillos: {results['stats']['yellow_count']}")
    print(f"Rojos: {results['stats']['red_count']}")
    
    for result in results["results"]:
        status_emoji = "🟢" if result["status"] == "GREEN" else "🟡" if result["status"] == "YELLOW" else "🔴"
        print(f"  {status_emoji} {result['exercise_name']}")

# 5. Ver notificaciones
notifications_response = requests.get(
    f"{BASE_URL}/courses/notifications/",
    headers=headers
)
notifications = notifications_response.json()
unread = [n for n in notifications if not n["is_read"]]
print(f"\nTienes {len(unread)} notificaciones sin leer")
```

---

¡Y eso es todo! Ahora tienes una guía completa para usar la API de DevTrack. 🚀

**¿Preguntas?** Consulta la documentación interactiva en `http://localhost:8000/api/docs/`
