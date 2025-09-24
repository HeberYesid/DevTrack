import os
import requests
from django.core.mail import send_mail
from django.conf import settings
from .models import User


def send_verification_email(user: User) -> str:
    """
    Creates a verification token and sends an email with the verification link.
    Returns the token for logging/testing purposes.
    """
    token = user.create_email_verification_token()
    # API verification endpoint (reverted)
    verify_url = f"{getattr(settings, 'API_BASE_URL', 'http://127.0.0.1:8000')}/api/auth/verify/?token={token}"

    subject = 'Verifica tu correo - DevTrack'
    message = (
        f"Hola {user.first_name or user.email},\n\n"
        f"Para activar tu cuenta, por favor verifica tu correo haciendo clic en el siguiente enlace:\n"
        f"{verify_url}\n\n"
        f"Si no registraste una cuenta en DevTrack, ignora este mensaje.\n"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost'),
        recipient_list=[user.email],
        fail_silently=False,
    )
    return token


def send_verification_code_email(user: User) -> str:
    """
    Crea un código de verificación de 6 dígitos y lo envía por email.
    También muestra el código en la consola del servidor.
    Retorna el código para propósitos de logging/testing.
    """
    code = user.create_email_verification_code()
    
    # Mostrar el código en la consola del servidor
    print(f"\n{'='*50}")
    print(f"🔐 CÓDIGO DE VERIFICACIÓN GENERADO")
    print(f"{'='*50}")
    print(f"Usuario: {user.email}")
    print(f"Código: {code}")
    print(f"Válido por: 15 minutos")
    print(f"{'='*50}\n")

    subject = 'Código de verificación - DevTrack'
    message = (
        f"Hola {user.first_name or user.email},\n\n"
        f"Tu código de verificación es: {code}\n\n"
        f"Este código es válido por 15 minutos.\n\n"
        f"Si no solicitaste este código, ignora este mensaje.\n\n"
        f"Equipo DevTrack"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost'),
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(f"✅ Email enviado exitosamente a {user.email}")
    except Exception as e:
        print(f"❌ Error enviando email a {user.email}: {str(e)}")
    
    return code


def verify_turnstile_token(token: str, remote_ip: str = None) -> bool:
    """
    Verifies a Cloudflare Turnstile token.
    Returns True if the token is valid, False otherwise.
    """
    if not token:
        return False
    
    secret_key = os.getenv('TURNSTILE_SECRET_KEY')
    if not secret_key:
        # For development, you might want to skip verification
        # In production, this should always be required
        return getattr(settings, 'DEBUG', False)
    
    url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    data = {
        'secret': secret_key,
        'response': token,
    }
    
    if remote_ip:
        data['remoteip'] = remote_ip
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get('success', False)
    except (requests.RequestException, ValueError, KeyError):
        # In case of network errors or invalid responses, 
        # you might want to allow or deny based on your security policy
        return False
