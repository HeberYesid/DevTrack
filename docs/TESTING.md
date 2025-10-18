# 🧪 Guía de Pruebas - DevTrack

## 📋 Resumen

DevTrack ahora incluye un sistema completo de pruebas para backend (Django + pytest) y frontend (React + Vitest).

## 🔙 Backend - Django Tests

### Instalación de Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### Ejecutar Todas las Pruebas

```bash
pytest
```

### Ejecutar con Cobertura

```bash
pytest --cov
```

### Ejecutar Pruebas Específicas

```bash
# Solo pruebas de accounts
pytest accounts/tests/

# Solo pruebas de modelos
pytest accounts/tests/test_models.py

# Solo pruebas de API
pytest accounts/tests/test_api.py

# Ejecutar una prueba específica
pytest accounts/tests/test_models.py::TestUserModel::test_create_user
```

### Ver Reporte de Cobertura HTML

```bash
pytest --cov --cov-report=html
# Abre htmlcov/index.html en tu navegador
```

### Pruebas Implementadas (Backend)

#### Accounts App
- ✅ **Modelos**:
  - User (creación, roles, superuser)
  - EmailVerificationCode (creación, validación, expiración)
  - TeacherInvitationCode (generación, validación, uso)

- ✅ **API Endpoints**:
  - Registro de estudiantes
  - Registro de profesores con código de invitación
  - Login con validación de captcha
  - Verificación de email por código
  - Reenvío de código de verificación
  - Usuario actual (me)

#### Courses App
- ✅ **Modelos**:
  - Subject (materias)
  - Enrollment (inscripciones)
  - Assignment (tareas)
  - Submission (entregas)

- ✅ **API Endpoints**:
  - CRUD de materias
  - Inscripción de estudiantes
  - Gestión de tareas
  - Envío y calificación de trabajos

#### Notifications App
- ✅ **Modelos**:
  - Notification (notificaciones)

- ✅ **API Endpoints**:
  - Listado de notificaciones
  - Contador de no leídas
  - Marcar como leída
  - Marcar todas como leídas

## 🎨 Frontend - React Tests

### Instalación de Dependencias

```bash
cd frontend
npm install
```

### Ejecutar Todas las Pruebas

```bash
npm test
```

### Ejecutar en Modo Watch (Desarrollo)

```bash
npm test -- --watch
```

### Ejecutar con UI Interactiva

```bash
npm run test:ui
```

### Ejecutar con Cobertura

```bash
npm run test:coverage
```

### Pruebas Implementadas (Frontend)

#### Componentes de Páginas
- ✅ **Login.jsx**:
  - Renderizado del formulario
  - Validación de campos
  - Manejo de errores
  - Enlaces de navegación

- ✅ **Register.jsx**:
  - Formulario completo
  - Selección de rol
  - Validaciones
  - Enlaces relacionados

- ✅ **Dashboard.jsx**:
  - Renderizado con usuario autenticado
  - Mensaje de bienvenida
  - Estado de carga

#### Componentes Core
- ✅ **NavBar.jsx**:
  - Logo y navegación
  - Menú de usuario
  - Estado autenticado/no autenticado
  - Función de logout

- ✅ **ProtectedRoute.jsx**:
  - Protección de rutas
  - Redirección a login
  - Estado de carga

## 📊 Cobertura de Código

### Objetivos de Cobertura

- **Backend**: > 80%
- **Frontend**: > 70%

### Ver Reportes

**Backend:**
```bash
cd backend
pytest --cov --cov-report=html
# Abre htmlcov/index.html
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
# Abre coverage/index.html
```

## 🔧 Configuración

### Backend (pytest.ini)

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
addopts = --strict-markers --tb=short --cov=. --reuse-db
```

### Frontend (vitest.config.js)

```javascript
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js'
  }
})
```

## 🎯 Mejores Prácticas

### Backend

1. **Usar fixtures** para datos de prueba reutilizables
2. **Mockear llamadas externas** (emails, APIs externas)
3. **Probar casos de error** además de casos exitosos
4. **Usar `@pytest.mark.django_db`** para pruebas con base de datos

### Frontend

1. **Usar `renderWithProviders`** para incluir contextos
2. **Simular interacciones de usuario** con `userEvent`
3. **Probar accesibilidad** con queries semánticas
4. **Mockear módulos externos** cuando sea necesario

## 🚀 CI/CD

Para integración continua, agrega estos comandos:

```yaml
# GitHub Actions example
- name: Run Backend Tests
  run: |
    cd backend
    pytest --cov --cov-report=xml

- name: Run Frontend Tests
  run: |
    cd frontend
    npm test -- --coverage
```

## 📝 Agregar Nuevas Pruebas

### Backend

```python
# accounts/tests/test_my_feature.py
import pytest
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class TestMyFeature:
    def test_something(self, student_user):
        # Tu prueba aquí
        assert True
```

### Frontend

```javascript
// src/components/__tests__/MyComponent.test.jsx
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import MyComponent from '../MyComponent'
import { renderWithProviders } from '../../test/utils'

describe('MyComponent', () => {
  it('renders correctly', () => {
    renderWithProviders(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

## 🐛 Debugging

### Backend

```bash
# Ejecutar con output detallado
pytest -v

# Ejecutar con print statements
pytest -s

# Detener en primera falla
pytest -x
```

### Frontend

```bash
# Modo debug
npm test -- --inspect

# Ver en navegador
npm run test:ui
```

## ✅ Checklist de Pruebas

Antes de hacer push:

- [ ] Todas las pruebas pasan
- [ ] Cobertura > 80% (backend)
- [ ] Cobertura > 70% (frontend)
- [ ] No hay warnings
- [ ] Nuevas funcionalidades tienen pruebas
- [ ] Casos de error están probados

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)

## 🎉 ¡Listo!

Tu proyecto ahora tiene un sistema completo de pruebas. Ejecuta:

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

¡Happy Testing! 🚀
