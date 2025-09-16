from django.contrib import admin
from .models import Subject, Enrollment, Exercise, StudentExerciseResult


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "teacher", "created_at")
    search_fields = ("code", "name", "teacher__email")
    list_filter = ("teacher",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "student", "created_at")
    search_fields = ("subject__code", "student__email")
    list_filter = ("subject",)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "name", "order")
    search_fields = ("subject__code", "name")
    list_filter = ("subject",)


@admin.register(StudentExerciseResult)
class StudentExerciseResultAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "exercise", "status", "created_at", "updated_at")
    search_fields = ("enrollment__student__email", "exercise__name")
    list_filter = ("status", "exercise__subject")
