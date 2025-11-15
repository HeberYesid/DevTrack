# Sistema de Tour Interactivo de DevTrack

## Descripción General

DevTrack ahora incluye un **tour interactivo de bienvenida** para nuevos usuarios, diseñado con `react-joyride`. El tour se adapta automáticamente según el rol del usuario (STUDENT, TEACHER, ADMIN) y guía a través de las funcionalidades principales de la plataforma.

## Características Principales

### 🎯 Tours Específicos por Rol

#### **Estudiante (STUDENT)**
1. Bienvenida inicial
2. Toggle de tema claro/oscuro
3. Campana de notificaciones
4. Panel principal del dashboard
5. Estadísticas de progreso (resultados, verdes/amarillos/rojos, tasa de éxito)
6. Grid de materias inscritas
7. Resumen final con funcionalidades disponibles

#### **Profesor (TEACHER)**
1. Bienvenida para profesores
2. Toggle de tema
3. Notificaciones (inscripciones, ejercicios completados)
4. Panel de control de materias
5. Estadísticas (materias creadas, estudiantes inscritos)
6. Tabla de materias con opciones de gestión
7. Enlace a Gestión de Materias
8. Resumen con funcionalidades clave (CRUD materias, ejercicios, inscripciones CSV, resultados CSV)

#### **Administrador (ADMIN)**
1. Bienvenida para administradores
2. Toggle de tema
3. Notificaciones del sistema
4. Panel de administración
5. Estadísticas globales
6. Acceso completo a todas las materias
7. Resumen de privilegios admin

### 🎨 Integración con Temas

El tour respeta automáticamente el sistema de temas (dark/light) de DevTrack:
- Colores dinámicos usando variables CSS (`var(--bg-card)`, `var(--text-primary)`, `var(--primary)`)
- Overlay oscuro semitransparente para destacar elementos
- Botones estilizados según el tema activo

### 💾 Control de Estado

- **LocalStorage**: Guarda el estado del tour por rol (`devtrack-tour-completed-{ROLE}`)
- **Activación automática**: Se muestra solo la primera vez que el usuario accede al dashboard
- **Reinicio manual**: Disponible desde el perfil del usuario

### 📍 Funcionamiento Técnico

#### Componente `AppTour.jsx`

```javascript
// Ubicación: frontend/src/components/AppTour.jsx

// Detecta automáticamente:
- Usuario autenticado
- Ruta actual (solo en '/')
- Estado del tour en localStorage

// Proporciona:
- Tour personalizado por rol
- Botones: Atrás, Siguiente, Saltar tour, Finalizar
- Indicador de progreso
- Traducciones en español
```

#### Integración en `App.jsx`

```jsx
import AppTour from './components/AppTour'

export default function App() {
  return (
    <div className="app">
      <NavBar />
      <AppTour />  {/* Tour activo globalmente */}
      <main className="container">
        {/* Rutas... */}
      </main>
    </div>
  )
}
```

#### Botón de Reinicio en `UserProfile.jsx`

Los usuarios pueden reiniciar el tour desde su perfil:

```jsx
import { resetTour } from '../components/AppTour'

// En el perfil:
<button onClick={() => {
  resetTour(user.role)
  navigate('/')
}}>
  🔄 Reiniciar Tour de Bienvenida
</button>
```

## Instalación y Configuración

### Dependencias

```json
{
  "dependencies": {
    "react-joyride": "^2.9.2"
  }
}
```

### Instalación

```bash
cd frontend
npm install
```

## Uso

### Activación Automática

1. Usuario registra cuenta o inicia sesión por primera vez
2. Al llegar al dashboard (`/`), el tour inicia automáticamente después de 1 segundo
3. El usuario puede:
   - **Siguiente**: Avanzar al siguiente paso
   - **Atrás**: Retroceder al paso anterior
   - **Saltar tour**: Cerrar y marcar como completado
   - **ESC**: Cerrar el tour

### Reinicio Manual

1. Usuario navega a **Perfil** (`/profile`)
2. Hace clic en **"🔄 Reiniciar Tour de Bienvenida"**
3. Es redirigido al dashboard donde el tour inicia nuevamente

## Personalización

### Agregar Nuevos Steps

Para agregar pasos al tour de un rol específico:

```javascript
// frontend/src/components/AppTour.jsx

const STUDENT_STEPS = [
  // ... steps existentes
  {
    target: '.mi-nuevo-elemento',  // Selector CSS
    content: 'Descripción del elemento',
    placement: 'bottom',  // top, bottom, left, right, center
    disableBeacon: true,
  },
]
```

### Cambiar Estilos

Modifica el objeto `styles` en el componente `Joyride`:

```javascript
<Joyride
  styles={{
    options: {
      primaryColor: 'var(--primary)',  // Color principal
      textColor: 'var(--text-primary)',
      // ... más opciones
    },
  }}
/>
```

### Modificar Traducciones

```javascript
<Joyride
  locale={{
    back: 'Atrás',
    next: 'Siguiente',
    skip: 'Saltar tour',
    last: 'Finalizar',
  }}
/>
```

## Selectores CSS Utilizados

| Selector | Elemento | Rol |
|----------|----------|-----|
| `.theme-toggle` | Botón de cambio de tema | Todos |
| `.notification-bell` | Campana de notificaciones | Todos |
| `.dashboard-title` | Título del dashboard | Todos |
| `.stats-grid-responsive` | Grid de estadísticas | Estudiante |
| `.subjects-grid-responsive` | Grid de materias | Estudiante |
| `.stats-grid` | Estadísticas profesor | Profesor/Admin |
| `.data-table` | Tabla de materias | Profesor/Admin |
| `a[href="/subjects"]` | Enlace gestión materias | Profesor/Admin |

## Buenas Prácticas

### ✅ Hacer

- Mantener los steps cortos y concisos (1-2 oraciones)
- Usar emojis para hacer el tour más amigable
- Probar el tour en ambos temas (dark/light)
- Verificar que los selectores CSS existan antes de agregar steps
- Agregar un delay (`setTimeout`) si el DOM necesita cargar

### ❌ Evitar

- Steps demasiado largos o técnicos
- Referenciar elementos que pueden no existir (ej: materia específica)
- Forzar el tour en cada visita al dashboard
- Selectores CSS muy específicos que puedan cambiar

## Troubleshooting

### El tour no aparece

1. **Verificar autenticación**: Usuario debe estar autenticado
2. **Verificar ruta**: Debe estar en `/` (dashboard)
3. **Limpiar localStorage**:
   ```javascript
   localStorage.removeItem('devtrack-tour-completed-STUDENT')
   localStorage.removeItem('devtrack-tour-completed-TEACHER')
   localStorage.removeItem('devtrack-tour-completed-ADMIN')
   ```
4. **Verificar consola**: Puede haber errores de selectores

### El tour apunta al elemento incorrecto

1. Verificar que el selector CSS sea correcto
2. Inspeccionar el DOM para confirmar la clase/id
3. Agregar `disableBeacon: true` si el beacon no aparece correctamente

### El tour no se cierra

1. Verificar que el callback `handleJoyrideCallback` esté manejando `STATUS.FINISHED` y `STATUS.SKIPPED`
2. Confirmar que `localStorage.setItem` se está ejecutando

## Futuras Mejoras

- [ ] Tour adicional para la página de detalle de materia
- [ ] Tour para la gestión de ejercicios
- [ ] Animaciones personalizadas entre steps
- [ ] Tooltips contextuales fuera del tour principal
- [ ] Analytics de completitud del tour
- [ ] Tour multi-idioma (inglés/español)

## Referencias

- [react-joyride Documentation](https://docs.react-joyride.com/)
- [DevTrack Theme System](./THEME_SYSTEM_DOCS.md)
- [DevTrack Role-Based Permissions](./ROLE_BASED_VIEWS.md)

---

**Implementado**: Noviembre 2025  
**Versión**: 1.0  
**Mantenedor**: DevTrack Team
