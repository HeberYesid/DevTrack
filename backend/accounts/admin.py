from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .models import User, EmailVerificationToken, EmailVerificationCode, TeacherInvitationCode
from .utils import send_teacher_invitation_email


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


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'code_type', 'created_at', 'expires_at', 'is_used', 'is_valid')
    list_filter = ('is_used', 'code_type', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Válido'


@admin.register(TeacherInvitationCode)
class TeacherInvitationCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'expires_at', 'used', 'is_valid', 'used_by')
    list_filter = ('used', 'created_at')
    search_fields = ('email', 'code')
    readonly_fields = ('created_at', 'used_at', 'used_by', 'code')
    actions = ['send_invitation_emails']
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Válido'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Solo cuando se crea
            obj.created_by = request.user
            if not obj.code:
                obj.code = TeacherInvitationCode.generate_code()
            if not obj.expires_at:
                obj.expires_at = timezone.now() + timedelta(days=7)
        super().save_model(request, obj, form, change)
        
        # Enviar email con el código si es nuevo
        if not change:
            try:
                send_teacher_invitation_email(obj)
            except Exception as e:
                self.message_user(request, f"Código creado pero no se pudo enviar email: {str(e)}", level='warning')
    
    def send_invitation_emails(self, request, queryset):
        """Acción para reenviar emails de invitación"""
        sent = 0
        for invitation in queryset.filter(used=False):
            try:
                send_teacher_invitation_email(invitation)
                sent += 1
            except Exception:
                pass
        self.message_user(request, f"{sent} emails enviados exitosamente.")
    send_invitation_emails.short_description = "Enviar/Reenviar emails de invitación"
