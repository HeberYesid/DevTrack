# DevTrack - Product Requirements Document (PRD)

## 1. Visión del Producto

DevTrack es un sistema integral de seguimiento académico diseñado para facilitar la gestión y evaluación continua del progreso de estudiantes en instituciones educativas. Utilizando un sistema de semáforo intuitivo (🟢 Verde / 🟡 Amarillo / 🔴 Rojo), permite a profesores y administradores monitorear el desempeño estudiantil en tiempo real y calcular calificaciones de forma automática.

### Problema que Resuelve
- **Seguimiento manual ineficiente**: Elimina hojas de cálculo y registros físicos
- **Falta de visibilidad en tiempo real**: Proporciona información actualizada del progreso estudiantil
- **Cálculo manual de notas**: Automatiza la generación de calificaciones basadas en desempeño
- **Comunicación fragmentada**: Centraliza notificaciones entre estudiantes y profesores

### Propuesta de Valor
- Sistema de evaluación visual e intuitivo mediante códigos de color
- Cálculo automático de calificaciones basado en desempeño acumulado
- Gestión masiva de estudiantes mediante carga CSV
- Notificaciones automáticas de cambios relevantes
- Acceso multiplataforma (web responsive)

---

## 2. Objetivos del Producto

### Objetivos Primarios
1. **Facilitar el seguimiento académico**: Reducir en 70% el tiempo dedicado a registro manual de evaluaciones
2. **Mejorar la comunicación**: Garantizar notificaciones instantáneas de cambios en el estado académico
3. **Automatizar cálculos**: Eliminar errores humanos en el cálculo de calificaciones finales
4. **Escalar eficientemente**: Soportar instituciones desde 50 hasta 5,000+ estudiantes

### Objetivos Secundarios
- Proporcionar analytics básicos sobre rendimiento por materia
- Implementar sistema de sesiones seguro con timeout configurable
- Ofrecer temas claro/oscuro para mejor experiencia de usuario
- Mantener >90% de cobertura de pruebas automatizadas

### Métricas de Éxito
- Tiempo promedio de registro de evaluaciones: <2 minutos por clase
- Tasa de adopción docente: >80% en primer mes
- Satisfacción de usuarios: >4.2/5.0
- Uptime del sistema: >99.5%

---

## 3. Usuarios y Roles

### 3.1 Estudiantes (STUDENT)
**Características:**
- Usuario final más numeroso (ratio típico: 30:1 estudiante:profesor)
- Acceso de solo lectura a su información académica
- Requiere verificación de email para activar cuenta

**Capacidades:**
- Ver materias en las que está inscrito
- Consultar ejercicios y su estado de resultados (Verde/Amarillo/Rojo)
- Visualizar calificación calculada en tiempo real
- Recibir notificaciones de cambios en sus resultados
- Actualizar perfil y foto
- Configurar timeout de sesión (5-120 minutos)

**Restricciones:**
- No puede modificar resultados de ejercicios
- No puede inscribirse automáticamente en materias (requiere invitación de profesor)
- No puede ver información de otros estudiantes

### 3.2 Profesores (TEACHER)
**Características:**
- Gestionan una o más materias
- Crean y evalúan ejercicios de sus estudiantes
- Rol intermedio con permisos de lectura/escritura limitados

**Capacidades:**
- Crear y gestionar materias (solo las propias)
- Registrar ejercicios y sus resultados para estudiantes
- Inscribir estudiantes mediante emails individuales o CSV masivo
- Subir resultados de ejercicios mediante CSV
- Ver estadísticas agregadas de sus materias
- Enviar notificaciones a estudiantes de sus materias
- Gestionar códigos de invitación para materias

**Restricciones:**
- No puede editar materias de otros profesores
- No puede eliminar estudiantes del sistema (solo desinscribir de su materia)
- No puede modificar roles de usuarios

### 3.3 Administradores (ADMIN)
**Características:**
- Acceso total al sistema
- Responsables de configuración general y gestión de usuarios
- Típicamente 1-3 por institución

**Capacidades:**
- Todas las capacidades de TEACHER
- Crear, editar y eliminar cualquier materia
- Gestionar usuarios (crear, editar, eliminar, cambiar roles)
- Generar códigos de invitación para profesores
- Acceder a estadísticas globales del sistema
- Configurar parámetros del sistema

---

## 4. Características Principales

### 4.1 Sistema de Autenticación y Seguridad

#### 4.1.1 Registro y Verificación
- **Registro de Estudiantes**: Por invitación mediante email o código
- **Registro de Profesores**: Mediante código de invitación generado por ADMIN
- **Verificación de Email**: Código de 6 dígitos (válido 15 minutos)
- **Reenvío de Código**: Disponible después de 1 minuto

#### 4.1.2 Autenticación
- **JWT Tokens**: Access token (15 min) + Refresh token (7 días)
- **Auto-refresh**: Transparente en cliente cuando access token expira
- **Protección CSRF**: Para endpoints sensibles
- **Rate Limiting**: 
  - Login/Registro: 5 intentos/minuto por IP
  - Verificación email: 3 intentos/minuto
  - Endpoints generales: 100 req/minuto

#### 4.1.3 Gestión de Sesiones
- **Timeout Configurable**: 5-120 minutos por usuario (default: 30)
- **Auto-logout**: Por inactividad (mouse/teclado)
- **Logout Manual**: Disponible en cualquier momento
- **Sesiones Simultáneas**: Permitidas con tokens independientes

### 4.2 Gestión de Materias (Subjects)

#### 4.2.1 Creación y Configuración
- **Campos Obligatorios**: name, teacher_id
- **Campos Opcionales**: description
- **Validaciones**: 
  - Nombre único por profesor
  - Máximo 200 caracteres en nombre
  - Descripción hasta 1000 caracteres

#### 4.2.2 Inscripción de Estudiantes
- **Individual**: Por email (auto-crea usuario si no existe)
- **Masiva CSV**: Formato `email, first_name, last_name`
  - Auto-creación de usuarios faltantes
  - Validación de duplicados
  - Reporte detallado: {created, existed, errors}
- **Desinscripción**: Soft-delete de Enrollment (mantiene histórico)

#### 4.2.3 Códigos de Invitación
- **Generación**: Por profesor o admin
- **Validez**: Configurable (default: sin límite de tiempo)
- **Uso Único**: Se invalida después del primer uso
- **Tracking**: Registro de quién usó cada código

### 4.3 Ejercicios y Evaluaciones

#### 4.3.1 Creación de Ejercicios
- **Campos**: name, description, order, subject_id
- **Orden Automático**: Si no se especifica, asigna siguiente número
- **Validaciones**: 
  - Nombre único por materia
  - Order debe ser único por materia

#### 4.3.2 Registro de Resultados
- **Estados Posibles**: 
  - 🟢 **GREEN**: Ejercicio completado satisfactoriamente
  - 🟡 **YELLOW**: Completado con observaciones/ayuda
  - 🔴 **RED**: No completado o con errores graves
  
- **Registro Individual**: 
  - Un resultado por estudiante por ejercicio
  - Permite actualización (mantiene histórico)
  - Campo opcional de observaciones (notes)

- **Registro Masivo CSV**: 
  - Formato: `student_email, exercise_name, status`
  - Validación de emails y nombres de ejercicios
  - Creación automática de ejercicios si no existen
  - Actualización de resultados existentes
  - Reporte detallado de operaciones

#### 4.3.3 Cálculo de Calificaciones
**Algoritmo Automático** (escala 0.0 - 5.0):
```
total_exercises = count(all exercises)
green_count = count(GREEN results)
yellow_count = count(YELLOW results)
red_count = count(RED results)

IF green_count == total_exercises:
    grade = 5.0
ELIF yellow_count / total_exercises >= 0.6:
    grade = 3.0
ELSE:
    grade = 5.0 * (green_count / total_exercises)
```

**Ejemplo:**
- 10 ejercicios: 7 GREEN, 2 YELLOW, 1 RED → grade = 3.5
- 10 ejercicios: 10 GREEN → grade = 5.0
- 10 ejercicios: 6 YELLOW, 4 RED → grade = 3.0

### 4.4 Sistema de Notificaciones

#### 4.4.1 Generación Automática (Signals)
**Eventos que Generan Notificaciones:**
- Inscripción a materia (→ estudiante + profesor)
- Nuevo ejercicio creado (→ todos los estudiantes de la materia)
- Resultado registrado/actualizado (→ estudiante afectado)
- Cambio de calificación significativo (>0.5 puntos)

#### 4.4.2 Gestión de Notificaciones
- **Marcado de Lectura**: Individual o masivo
- **Eliminación**: Soft-delete (mantiene registro)
- **Filtrado**: Por tipo, materia, leídas/no leídas
- **Ordenamiento**: Por fecha descendente

#### 4.4.3 Tipos de Notificación
```
ENROLLMENT = Inscripción en materia
EXERCISE = Nuevo ejercicio disponible
RESULT = Resultado registrado/actualizado
GRADE = Cambio de calificación
GENERAL = Mensajes administrativos
```

### 4.5 Gestión de Perfil de Usuario

#### 4.5.1 Información Editable
- Nombre (first_name, last_name)
- Email (requiere re-verificación)
- Contraseña (requiere actual)
- Foto de perfil (upload + validación de formato/tamaño)
- Session timeout (5-120 minutos)

#### 4.5.2 Visualización
- Dashboard personalizado por rol:
  - **STUDENT**: Materias inscritas, resultados recientes, calificaciones
  - **TEACHER**: Materias que imparte, estadísticas de estudiantes
  - **ADMIN**: Estadísticas globales, usuarios activos

---

## 5. Requisitos Funcionales Detallados

### RF-01: Autenticación de Usuarios
- **Prioridad**: Alta
- **Descripción**: El sistema debe permitir registro, login y verificación de email
- **Criterios de Aceptación**:
  - Usuario puede registrarse con email único
  - Sistema envía código de 6 dígitos para verificación
  - Login exitoso devuelve access + refresh tokens
  - Tokens inválidos retornan 401 con mensaje claro

### RF-02: Gestión de Materias
- **Prioridad**: Alta
- **Descripción**: TEACHER/ADMIN pueden crear y gestionar materias
- **Criterios de Aceptación**:
  - Profesor solo ve/edita sus propias materias
  - Admin puede gestionar cualquier materia
  - Nombre de materia es único por profesor

### RF-03: Inscripción de Estudiantes
- **Prioridad**: Alta
- **Descripción**: Profesor puede inscribir estudiantes individual o masivamente
- **Criterios de Aceptación**:
  - CSV con emails crea usuarios faltantes automáticamente
  - Sistema reporta created/existed/errors
  - Duplicados se manejan correctamente
  - Inscripciones generan notificaciones

### RF-04: Registro de Resultados
- **Prioridad**: Alta
- **Descripción**: Profesor registra resultados GREEN/YELLOW/RED para ejercicios
- **Criterios de Aceptación**:
  - CSV masivo permite actualizar múltiples resultados
  - Sistema valida existencia de estudiante y ejercicio
  - Actualización de resultado existente mantiene histórico
  - Cambios generan notificaciones automáticas

### RF-05: Cálculo de Calificaciones
- **Prioridad**: Alta
- **Descripción**: Sistema calcula calificación automática según algoritmo definido
- **Criterios de Aceptación**:
  - Calificación se actualiza en tiempo real con cada resultado
  - Todos GREEN resulta en 5.0
  - 60%+ YELLOW resulta en 3.0
  - Otros casos usan fórmula proporcional

### RF-06: Sistema de Notificaciones
- **Prioridad**: Media
- **Descripción**: Usuarios reciben notificaciones de eventos relevantes
- **Criterios de Aceptación**:
  - Notificaciones se generan automáticamente (signals)
  - Usuario puede marcar como leídas
  - Contador de no leídas visible en navbar
  - Filtrado por tipo y estado funcional

### RF-07: Gestión de Perfil
- **Prioridad**: Media
- **Descripción**: Usuarios pueden actualizar información personal
- **Criterios de Aceptación**:
  - Cambio de email requiere re-verificación
  - Cambio de contraseña requiere actual
  - Foto de perfil valida formato (JPG, PNG) y tamaño (<5MB)
  - Session timeout es configurable por usuario

### RF-08: Códigos de Invitación
- **Prioridad**: Media
- **Descripción**: Admin genera códigos para registro de profesores
- **Criterios de Aceptación**:
  - Código es único y auto-generado
  - Se invalida después del primer uso
  - Sistema rastrea quién usó cada código

### RF-09: Rate Limiting
- **Prioridad**: Alta (Seguridad)
- **Descripción**: Sistema limita requests para prevenir abuso
- **Criterios de Aceptación**:
  - Login: 5 intentos/min por IP
  - Verificación email: 3 intentos/min
  - API general: 100 req/min por usuario

### RF-10: Soft Delete
- **Prioridad**: Media
- **Descripción**: Eliminaciones mantienen datos para auditoría
- **Criterios de Aceptación**:
  - Objetos eliminados tienen deleted_at timestamp
  - Queries por default excluyen eliminados
  - Admin puede ver/restaurar eliminados

---

## 6. Requisitos No Funcionales

### RNF-01: Rendimiento
- **Tiempo de respuesta**: <500ms para 95% de requests
- **Carga masiva CSV**: <30 segundos para 500 estudiantes
- **Consultas con paginación**: 20 items por página default

### RNF-02: Escalabilidad
- **Carga concurrente**: Soportar 100 usuarios simultáneos
- **Volumen de datos**: 
  - 5,000 estudiantes
  - 500 materias
  - 10,000 ejercicios

### RNF-03: Disponibilidad
- **Uptime**: 99.5% mensual
- **Mantenimientos**: Ventanas programadas fuera de horario escolar
- **Backups**: Diarios automáticos con retención de 30 días

### RNF-04: Seguridad
- **Autenticación**: JWT con refresh tokens
- **Encriptación**: Contraseñas con bcrypt
- **HTTPS**: Obligatorio en producción
- **CORS**: Lista blanca de orígenes permitidos
- **Rate Limiting**: Implementado en endpoints críticos

### RNF-05: Usabilidad
- **Responsive**: Funcional en desktop, tablet y móvil
- **Accesibilidad**: Cumplir WCAG 2.1 nivel AA
- **Internacionalización**: Preparado para i18n (español prioridad)
- **Temas**: Claro/oscuro con persistencia de preferencia

### RNF-06: Mantenibilidad
- **Cobertura de tests**: >90% en backend y frontend
- **Documentación**: API docs con Swagger/OpenAPI
- **Logs**: Centralizados con niveles (DEBUG, INFO, WARNING, ERROR)
- **Monitoreo**: Alertas automáticas en errores críticos

### RNF-07: Compatibilidad
- **Navegadores**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Bases de datos**: MySQL 8.0+ (dev) y PostgreSQL 13+ (prod)
- **Python**: 3.10+
- **Node.js**: 18+

---

## 7. Stack Tecnológico

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Base de datos**: 
  - MySQL 8.0 (desarrollo local)
  - PostgreSQL 14 (producción en Render/Railway)
- **Autenticación**: djangorestframework-simplejwt
- **Testing**: pytest + pytest-django + pytest-cov
- **Rate Limiting**: django-ratelimit
- **CORS**: django-cors-headers

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 4
- **State Management**: Context API
- **HTTP Client**: Axios con interceptores
- **Routing**: React Router v6
- **Testing**: Vitest + React Testing Library
- **Estilos**: CSS variables con temas

### DevOps y Deployment
- **Desarrollo Local**:
  - Backend: `python manage.py runserver`
  - Frontend: `npm run dev`
  
- **Producción**:
  - Backend: Render/Railway (con PostgreSQL managed)
  - Frontend: Vercel/Netlify
  - Storage: Cloudinary para imágenes

- **CI/CD**: GitHub Actions
  - Tests automáticos en PRs
  - Deploy automático en merge a main

---

## 8. Casos de Uso Principales

### CU-01: Registro de Estudiante
**Actor**: Estudiante nuevo
**Precondición**: Tiene email de invitación o código
**Flujo Principal**:
1. Estudiante accede a página de registro
2. Ingresa email, contraseña, nombre
3. Opcionalmente ingresa código de materia
4. Sistema envía código de verificación a email
5. Estudiante ingresa código de 6 dígitos
6. Sistema activa cuenta y lo redirige a dashboard
**Postcondición**: Estudiante tiene cuenta verificada e inscrito en materia (si usó código)

### CU-02: Profesor Crea Materia e Inscribe Estudiantes
**Actor**: Profesor
**Precondición**: Profesor autenticado
**Flujo Principal**:
1. Profesor navega a "Mis Materias"
2. Click en "Nueva Materia"
3. Ingresa nombre y descripción
4. Sistema crea materia
5. Profesor sube CSV con emails de estudiantes
6. Sistema procesa CSV y reporta resultados
7. Sistema envía notificaciones a estudiantes inscritos
**Postcondición**: Materia creada con N estudiantes inscritos

### CU-03: Registro de Resultados de Ejercicios
**Actor**: Profesor
**Precondición**: Materia tiene estudiantes y ejercicios
**Flujo Principal**:
1. Profesor navega a materia específica
2. Click en "Subir Resultados"
3. Sube CSV con formato: student_email, exercise_name, status
4. Sistema valida datos
5. Sistema actualiza/crea resultados
6. Sistema recalcula calificaciones afectadas
7. Sistema envía notificaciones a estudiantes
8. Muestra reporte: {created, updated, errors}
**Postcondición**: Resultados actualizados, calificaciones recalculadas

### CU-04: Estudiante Consulta Progreso
**Actor**: Estudiante
**Precondición**: Estudiante autenticado e inscrito en materias
**Flujo Principal**:
1. Estudiante accede a dashboard
2. Ve lista de materias inscritas con calificación actual
3. Click en materia específica
4. Ve lista de ejercicios con estado (Verde/Amarillo/Rojo)
5. Ve calificación calculada en tiempo real
6. Puede ver detalles/observaciones de cada resultado
**Postcondición**: Estudiante conoce su progreso actualizado

### CU-05: Admin Gestiona Usuarios
**Actor**: Administrador
**Precondición**: Admin autenticado
**Flujo Principal**:
1. Admin navega a "Gestión de Usuarios"
2. Ve lista de todos los usuarios
3. Puede filtrar por rol, estado de verificación
4. Click en usuario para editar
5. Puede cambiar rol, activar/desactivar cuenta
6. Puede generar código de invitación para profesores
**Postcondición**: Usuario actualizado según cambios

---

## 9. Flujos de Datos Críticos

### Flujo de Autenticación
```
1. POST /api/accounts/login/ {email, password}
   ↓
2. Backend valida credenciales
   ↓
3. Genera access_token (15 min) + refresh_token (7 días)
   ↓
4. Frontend almacena tokens en localStorage
   ↓
5. Requests subsiguientes incluyen: Authorization: Bearer {access_token}
   ↓
6. Si 401 por token expirado:
   → POST /api/accounts/token/refresh/ {refresh_token}
   → Obtiene nuevo access_token
   → Re-intenta request original
```

### Flujo de Notificaciones Automáticas
```
1. Profesor registra resultado de ejercicio
   ↓
2. Signal post_save(StudentExerciseResult) se dispara
   ↓
3. Signal crea Notification para estudiante afectado
   ↓
4. Frontend hace polling periódico a /api/courses/notifications/
   ↓
5. Muestra badge con contador de no leídas
   ↓
6. Usuario marca como leída: PATCH /api/courses/notifications/{id}/mark-read/
```

### Flujo de Cálculo de Calificaciones
```
1. Resultado de ejercicio se registra/actualiza
   ↓
2. Modelo StudentExerciseResult llama a enrollment.calculate_grade()
   ↓
3. Método Enrollment.stats() ejecuta:
   - Cuenta GREEN, YELLOW, RED
   - Aplica algoritmo de calificación
   - Actualiza campo calculated_grade
   ↓
4. Si cambio > 0.5 puntos: genera notificación
   ↓
5. Calificación visible instantáneamente en API
```

---

## 10. Roadmap y Fases de Desarrollo

### Fase 1: MVP (Completado ✅)
**Duración**: 6-8 semanas
**Funcionalidades**:
- ✅ Sistema de autenticación completo (JWT + verificación email)
- ✅ CRUD de usuarios con roles (STUDENT/TEACHER/ADMIN)
- ✅ Gestión de materias y ejercicios
- ✅ Registro de resultados individual y masivo (CSV)
- ✅ Cálculo automático de calificaciones
- ✅ Sistema de notificaciones básico
- ✅ Dashboard por rol
- ✅ Temas claro/oscuro

### Fase 2: Mejoras de Usabilidad (En Progreso 🚧)
**Duración**: 4 semanas
**Funcionalidades**:
- 🚧 Filtros avanzados en listados
- 🚧 Exportación de datos (PDF/Excel)
- 🚧 Gráficos de progreso estudiantil
- 🚧 Búsqueda global con autocompletado
- 🚧 Modo offline para consultas

### Fase 3: Analytics y Reportes (Planificado 📋)
**Duración**: 4-6 semanas
**Funcionalidades**:
- 📋 Dashboard de estadísticas avanzadas
- 📋 Comparativas entre materias/períodos
- 📋 Alertas tempranas de estudiantes en riesgo
- 📋 Reportes personalizables por profesor
- 📋 Exportación masiva de calificaciones

### Fase 4: Integraciones (Futuro 🔮)
**Duración**: 6-8 semanas
**Funcionalidades**:
- 🔮 API pública para integraciones
- 🔮 LMS integration (Moodle, Canvas)
- 🔮 SSO con proveedores institucionales
- 🔮 App móvil nativa (iOS/Android)
- 🔮 Notificaciones push en móvil

---

## 11. Riesgos y Mitigaciones

### Riesgo 1: Sobrecarga del Servidor en Períodos de Evaluación
**Probabilidad**: Media | **Impacto**: Alto
**Mitigación**:
- Implementar caché Redis para queries frecuentes
- Usar CDN para assets estáticos
- Escalado horizontal con load balancer
- Rate limiting agresivo en picos

### Riesgo 2: Pérdida de Datos por Fallos
**Probabilidad**: Baja | **Impacto**: Crítico
**Mitigación**:
- Backups automáticos diarios
- Replicación de base de datos
- Soft-delete en todas las entidades críticas
- Auditoría completa de cambios

### Riesgo 3: Acceso No Autorizado
**Probabilidad**: Media | **Impacto**: Alto
**Mitigación**:
- Rate limiting en autenticación
- Logs detallados de accesos
- 2FA opcional para roles sensibles (roadmap)
- Revisiones de seguridad trimestrales

### Riesgo 4: Adopción Baja por Complejidad
**Probabilidad**: Media | **Impacto**: Medio
**Mitigación**:
- Tutoriales interactivos en primer login
- Documentación clara para usuarios finales
- Soporte activo en período de onboarding
- Iteración basada en feedback temprano

---

## 12. Criterios de Éxito

### Métricas Técnicas
- ✅ Cobertura de tests >90%
- ✅ Tiempo de respuesta <500ms (p95)
- ✅ Uptime >99.5%
- ⏳ 0 vulnerabilidades críticas (auditoría de seguridad)

### Métricas de Usuario
- ⏳ Tasa de adopción docente >80% en primer mes
- ⏳ Satisfacción de usuarios >4.2/5
- ⏳ Tiempo promedio de registro de evaluaciones <2 min
- ⏳ Reducción de 70% en tiempo de gestión académica vs. métodos manuales

### Métricas de Negocio
- ⏳ 5 instituciones piloto en primeros 3 meses
- ⏳ Retención de clientes >85% después de 6 meses
- ⏳ NPS (Net Promoter Score) >50

---

## 13. Documentación Relacionada

- `docs/API_GUIDE.md` - Referencia completa de endpoints REST
- `docs/TESTING.md` - Estrategia y guías de pruebas
- `docs/THEME_SYSTEM_DOCS.md` - Sistema de temas CSS
- `docs/TROUBLESHOOTING.md` - Resolución de problemas comunes
- `docs/RENDER_DEPLOY.md` - Guía de deployment en producción
- `samples/` - Archivos CSV de ejemplo para carga masiva

---

## 14. Glosario

- **Ejercicio**: Actividad evaluable dentro de una materia
- **Materia/Subject**: Curso o asignatura gestionado por un profesor
- **Enrollment**: Inscripción de un estudiante en una materia
- **Status**: Estado de un resultado (GREEN/YELLOW/RED)
- **Calculated Grade**: Calificación automática calculada por el sistema (0.0-5.0)
- **Signal**: Mecanismo de Django para ejecutar código automático en eventos del modelo
- **Rate Limiting**: Limitación de requests por IP/usuario en ventana de tiempo
- **Soft Delete**: Marcado de eliminación sin borrado físico de base de datos

---

## 15. Contacto y Mantenimiento del Documento

**Versión**: 1.0  
**Última Actualización**: Diciembre 16, 2025  
**Autor**: Equipo DevTrack  
**Revisores**: Product Owner, Tech Lead

**Ciclo de Revisión**: Trimestral o ante cambios mayores en roadmap

---

**Fin del Documento**
