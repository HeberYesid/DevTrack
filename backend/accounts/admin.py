from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .models import User, EmailVerificationToken, EmailVerificationCode, TeacherInvitationCode, ContactMessage
from .utils import send_teacher_invitation_email

# Ocultar el modelo Group del admin ya que no se usa en este proyecto
admin.site.unregister(Group)

# Personalizar títulos del admin
admin.site.site_header = "DevTrack - Panel de Administración"
admin.site.site_title = "DevTrack Admin"
admin.site.index_title = "Gestión del Sistema"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Gestión de usuarios del sistema (Estudiantes, Profesores, Administradores)"""
    # Show extra fields in change form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información Personal'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permisos y Acceso'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Fechas Importantes'), {'fields': ('last_login', 'date_joined')}),
        (_('DevTrack - Configuración'), {'fields': ('role', 'is_email_verified')}),
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
    """Tokens de verificación de email (Sistema interno - Solo para debugging)"""
    list_display = ('user', 'token_preview', 'created_at', 'expires_at', 'used')
    search_fields = ('user__email',)
    readonly_fields = ('token', 'created_at', 'expires_at', 'user')
    list_filter = ('used', 'created_at')
    
    def token_preview(self, obj):
        return obj.token[:20] + '...' if len(obj.token) > 20 else obj.token
    token_preview.short_description = 'Token'
    
    def has_add_permission(self, request):
        # No permitir crear manualmente
        return False


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    """Códigos de verificación de 6 dígitos enviados por email"""
    list_display = ('user', 'code', 'code_type_display', 'created_at', 'expires_at', 'is_used', 'is_valid')
    list_filter = ('is_used', 'code_type', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at', 'user', 'code', 'expires_at')
    
    def code_type_display(self, obj):
        return obj.get_code_type_display()
    code_type_display.short_description = 'Tipo'
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Válido'
    
    def has_add_permission(self, request):
        # No permitir crear manualmente
        return False
    is_valid.short_description = 'Válido'


@admin.register(TeacherInvitationCode)
class TeacherInvitationCodeAdmin(admin.ModelAdmin):
    """Códigos de invitación para registro de profesores"""
    list_display = ('email', 'code', 'created_at', 'expires_at', 'used', 'is_valid', 'used_by')
    list_filter = ('used', 'created_at')
    search_fields = ('email', 'code')
    readonly_fields = ('created_at', 'used_at', 'used_by', 'code')
    exclude = ('created_by',)
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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Mensajes del formulario de contacto público"""
    list_display = ('id', 'name', 'email', 'subject_display', 'message_preview', 'created_at', 'is_read')
    list_filter = ('is_read', 'subject', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'message_formatted')
    actions = ['mark_as_read', 'mark_as_unread']
    list_per_page = 20
    
    fieldsets = (
        ('Información del Remitente', {
            'fields': ('name', 'email')
        }),
        ('Mensaje', {
            'fields': ('subject', 'message_formatted')
        }),
        ('Estado', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    def subject_display(self, obj):
        """Mostrar el asunto en español"""
        return obj.get_subject_display()
    subject_display.short_description = 'Asunto'
    
    def message_preview(self, obj):
        """Mostrar vista previa del mensaje en la lista"""
        if len(obj.message) > 100:
            return obj.message[:100] + '...'
        return obj.message
    message_preview.short_description = 'Vista previa del mensaje'
    
    def message_formatted(self, obj):
        """Mostrar el mensaje completo con mejor formato en el detalle"""
        from django.utils.html import format_html
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px; '
            'border-left: 4px solid #007bff; white-space: pre-wrap; font-family: '
            'Arial, sans-serif; line-height: 1.6;">{}</div>',
            obj.message
        )
    message_formatted.short_description = 'Mensaje completo'
    
    def mark_as_read(self, request, queryset):
        """Marcar mensajes como leídos"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} mensaje(s) marcado(s) como leído(s).")
    mark_as_read.short_description = "Marcar como leído"
    
    def mark_as_unread(self, request, queryset):
        """Marcar mensajes como no leídos"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} mensaje(s) marcado(s) como no leído(s).")
    mark_as_unread.short_description = "Marcar como no leído"
