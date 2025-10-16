# 🔐 Recuperación de Contraseña

Sistema para recuperar la contraseña usando código de verificación por email.

## Flujo

1. Usuario va a `/forgot-password`
2. Ingresa su email
3. Recibe código de 6 dígitos por email (válido 15 min)
4. Va a `/reset-password`
5. Ingresa: email, código y nueva contraseña
6. Contraseña restablecida ✅

## Endpoints Backend

- `POST /api/auth/forgot-password/` - Solicitar código
  - Body: `{ "email": "user@example.com" }`
  - Envía código por email
  
- `POST /api/auth/reset-password/` - Restablecer contraseña
  - Body: `{ "email": "...", "code": "123456", "new_password": "..." }`
  - Valida código y cambia contraseña

## Frontend

- `/forgot-password` - Solicitar código
- `/reset-password` - Ingresar código y nueva contraseña
- Link en `/login` - "¿Olvidaste tu contraseña?"

## Testing

```bash
# 1. Iniciar backend
cd backend
python manage.py runserver

# 2. Iniciar frontend
cd frontend
npm run dev

# 3. Probar:
# - Ir a http://localhost:5173/login
# - Click en "¿Olvidaste tu contraseña?"
# - Ingresar email de un usuario existente
# - Revisar consola del backend para ver el código
# - Ingresar código en /reset-password
# - Cambiar contraseña
```

## Seguridad

- Rate limiting: 3 intentos cada 5 minutos
- Código válido por 15 minutos
- Código de un solo uso
- Notificación creada al restablecer
- No revela si el email existe

## Fixes Aplicados

✅ Añadidos imports `random` y `timedelta`
✅ Creación manual del código con `expires_at`
✅ Permisos `AllowAny` configurados
✅ Rutas añadidas al frontend
