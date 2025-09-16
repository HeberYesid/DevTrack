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
