from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates or updates a superuser'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email for the superuser')
        parser.add_argument('--password', type=str, required=True, help='Password for the superuser')
        parser.add_argument('--first-name', type=str, default='Admin', help='First name')
        parser.add_argument('--last-name', type=str, default='User', help='Last name')
        parser.add_argument('--update', action='store_true', help='Update password if user exists')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        update = options.get('update', False)

        try:
            user = User.objects.get(email=email)
            if update:
                # Update existing user
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.is_staff = True
                user.is_superuser = True
                user.role = 'ADMIN'
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Superuser {email} updated successfully!'))
            else:
                self.stdout.write(self.style.WARNING(f'ℹ️  User {email} already exists (use --update to change password)'))
        except User.DoesNotExist:
            # Create new superuser
            User.objects.create_superuser(
                username=email,  # Django's AbstractUser requires username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='ADMIN'
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Superuser {email} created successfully!'))
