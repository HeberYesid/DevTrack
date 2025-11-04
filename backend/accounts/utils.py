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


def send_verification_code_email(user: User, is_password_reset: bool = False) -> str:
    """
    Crea y envía un código de verificación por email.
    Puede ser para verificación de cuenta o recuperación de contraseña.
    También muestra el código en la consola del servidor.
    Retorna el código generado.
    """
    # Crear el código de verificación
    code = user.create_email_verification_code()
    email = user.email
    
    # Mostrar el código en la consola del servidor
    code_type = "RECUPERACIÓN DE CONTRASEÑA" if is_password_reset else "VERIFICACIÓN DE CUENTA"
    print(f"\n{'='*50}")
    print(f"🔐 CÓDIGO DE {code_type}")
    print(f"{'='*50}")
    print(f"Email: {email}")
    print(f"Código: {code}")
    print(f"Válido por: 15 minutos")
    print(f"{'='*50}\n")

    if is_password_reset:
        subject = 'Recuperación de contraseña - DevTrack'
        message = (
            f"Hola,\n\n"
            f"Has solicitado recuperar tu contraseña en DevTrack.\n\n"
            f"Tu código de verificación es: {code}\n\n"
            f"Este código es válido por 15 minutos.\n\n"
            f"Si no solicitaste recuperar tu contraseña, ignora este mensaje.\n\n"
            f"Equipo DevTrack"
        )
    else:
        subject = 'Código de verificación - DevTrack'
        message = (
            f"Hola,\n\n"
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
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"✅ Email enviado exitosamente a {email}")
    except Exception as e:
        print(f"❌ Error enviando email a {email}: {str(e)}")
    
    return code


def send_teacher_invitation_email(invitation) -> None:
    """
    Envía un email con el código de invitación para registro de profesor.
    También muestra el código en la consola del servidor.
    """
    # Mostrar el código en la consola del servidor
    print(f"\n{'='*60}")
    print(f"📧 CÓDIGO DE INVITACIÓN PARA PROFESOR")
    print(f"{'='*60}")
    print(f"Email: {invitation.email}")
    print(f"Código: {invitation.code}")
    print(f"Válido hasta: {invitation.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    register_url = f"{frontend_url}/register-teacher"

    subject = '🎓 Invitación para registrarse como Profesor - DevTrack'
    message = (
        f"¡Hola!\n\n"
        f"Has sido invitado a unirte a DevTrack como profesor.\n\n"
        f"Tu código de invitación es: {invitation.code}\n\n"
        f"Para completar tu registro, visita el siguiente enlace:\n"
        f"{register_url}\n\n"
        f"Este código es válido hasta: {invitation.expires_at.strftime('%d/%m/%Y %H:%M')}\n\n"
        f"Si no solicitaste esta invitación, puedes ignorar este mensaje.\n\n"
        f"Equipo DevTrack"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost'),
            recipient_list=[invitation.email],
            fail_silently=False,
        )
        print(f"✅ Email de invitación enviado exitosamente a {invitation.email}")
    except Exception as e:
        print(f"❌ Error enviando email de invitación a {invitation.email}: {str(e)}")
        raise


def verify_turnstile_token(token: str, remote_ip: str = None) -> bool:
    """
    Verifies a Cloudflare Turnstile token.
    Returns True if the token is valid, False otherwise.
    """
    if not token:
        print("❌ Turnstile: Token vacío")
        return False
    
    secret_key = os.getenv('TURNSTILE_SECRET_KEY')
    if not secret_key:
        print("⚠️  Turnstile: SECRET_KEY no configurado")
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
        success = result.get('success', False)
        
        if not success:
            print(f"❌ Turnstile falló: {result.get('error-codes', [])}")
        else:
            print(f"✅ Turnstile validado correctamente")
            
        return success
    except (requests.RequestException, ValueError, KeyError) as e:
        # In case of network errors or invalid responses, 
        # you might want to allow or deny based on your security policy
        print(f"❌ Turnstile error: {str(e)}")
        return False
