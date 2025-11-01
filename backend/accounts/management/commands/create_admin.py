from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates a superuser if it does not exist'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email for the superuser')
        parser.add_argument('--password', type=str, required=True, help='Password for the superuser')
        parser.add_argument('--first-name', type=str, default='Admin', help='First name')
        parser.add_argument('--last-name', type=str, default='User', help='Last name')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User {email} already exists'))
            return

        # AbstractUser requires username, we use email as username
        User.objects.create_superuser(
            username=email,  # Django's AbstractUser requires username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='ADMIN'
        )
        self.stdout.write(self.style.SUCCESS(f'✅ Superuser {email} created successfully!'))
