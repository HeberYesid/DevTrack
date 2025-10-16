# 🔐 Notificación de Cambio de Contraseña

Cuando un usuario cambia su contraseña, el sistema:
- Muestra un toast visual (8s)
- Crea notificación en BD
- Aparece en bell icon y página de notificaciones

## Backend

**`backend/accounts/views.py`** - En `ChangePasswordView`:

```python
from courses.models import Notification
from django.utils import timezone

# Después de user.set_password(new_password) y user.save()
Notification.objects.create(
    user=user,
    notification_type='GENERAL',
    title='🔐 Contraseña actualizada',
    message=f'Tu contraseña fue cambiada el {timezone.now().strftime("%d/%m/%Y a las %H:%M")}...',
    is_read=False
)
```

## Frontend

**`frontend/src/utils/toast.js`** - Sistema de toasts (nuevo):

```javascript
// Uso simple
import { showPasswordChangeToast } from '../utils/toast'
showPasswordChangeToast()

// O personalizado
import { toast } from '../utils/toast'
toast.success('Guardado')
toast.error('Error')
toast.warning('Advertencia')
toast.info('Información')
toast.security('Acción de seguridad')
```

**`frontend/src/pages/UserProfile.jsx`**:

```javascript
import { showPasswordChangeToast } from '../utils/toast'

async function handleChangePassword(e) {
  await api.post('/api/auth/change-password/', {...})
  showPasswordChangeToast() // Toast visual por 8 segundos
  // Limpiar formulario...
}
```

## Testing

1. Iniciar servers: `python manage.py runserver` y `npm run dev`
2. Login → Perfil → Cambiar Contraseña
3. Verificar toast púrpura (8s), bell icon y /notifications
