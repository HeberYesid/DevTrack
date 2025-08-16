from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Exercise, ExerciseSubmission, StudentGrade, UserProfile


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'is_active', 'created_at']
    list_filter = ['difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'


@admin.register(ExerciseSubmission)
class ExerciseSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'status', 'submission_date']
    list_filter = ['status', 'submission_date', 'exercise__difficulty']
    search_fields = ['user__username', 'exercise__title']
    list_editable = ['status']
    date_hierarchy = 'submission_date'
    raw_id_fields = ['user', 'exercise']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Recalcular la nota del estudiante cuando se modifica un envío
        grade, created = StudentGrade.objects.get_or_create(user=obj.user)
        grade.calculate_grade()


@admin.register(StudentGrade)
class StudentGradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'calculated_grade', 'total_exercises', 'green_exercises', 'yellow_exercises', 'red_exercises', 'last_calculation']
    list_filter = ['calculated_grade', 'last_calculation']
    search_fields = ['user__username']
    readonly_fields = ['last_calculation']
    
    actions = ['recalculate_grades']
    
    def recalculate_grades(self, request, queryset):
        for grade in queryset:
            grade.calculate_grade()
        self.message_user(request, f"Se recalcularon {queryset.count()} calificaciones.")
    recalculate_grades.short_description = "Recalcular calificaciones seleccionadas"


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'created_at']
    search_fields = ['user__username', 'student_id']
    date_hierarchy = 'created_at'
