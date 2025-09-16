from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, EmailVerificationToken


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Show extra fields in change form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('DevTrack'), {'fields': ('role', 'is_email_verified')}),
    )

    # Show extra fields in add form and use password1/password2 flow
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_email_verified'),
        }),
    )

    list_display = ('id', 'username', 'email', 'role', 'is_email_verified', 'is_staff', 'is_active')
    list_filter = ('role', 'is_email_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('id',)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'used')
    search_fields = ('user__email', 'token')
