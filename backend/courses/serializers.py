from typing import Any
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subject, Enrollment, Exercise, StudentExerciseResult, Notification

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']


class SubjectSerializer(serializers.ModelSerializer):
    teacher = SimpleUserSerializer(read_only=True)
    enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'teacher', 'created_at', 'enrollments_count']
        read_only_fields = ['teacher', 'created_at', 'enrollments_count']

    def get_enrollments_count(self, obj):
        """Return the number of students enrolled in this subject"""
        return obj.enrollments.count()

    def create(self, validated_data):
        request = self.context['request']
        validated_data['teacher'] = request.user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    student = SimpleUserSerializer(read_only=True)
    student_email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'subject', 'student', 'student_email', 'created_at']
        read_only_fields = ['student', 'created_at', 'subject']

    def validate_student_email(self, value):
        """Validate and clean email"""
        if not value:
            raise serializers.ValidationError('El email es requerido.')
        return value.lower().strip()

    def validate(self, attrs):
        # Get subject from context (set by the view)
        subject = self.context.get('subject')
        if subject is None:
            raise serializers.ValidationError({'detail': 'Materia (subject) no encontrada en el contexto.'})
        
        # Check permissions
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError({'detail': 'Usuario no autenticado.'})
        
        user_role = getattr(request.user, 'role', None)
        if user_role not in ['ADMIN', 'TEACHER']:
            raise serializers.ValidationError({'detail': 'No tienes permisos para inscribir estudiantes. Solo profesores y administradores pueden hacerlo.'})
        
        if user_role == 'TEACHER' and subject.teacher_id != request.user.id:
            raise serializers.ValidationError({'detail': 'Solo el profesor dueño de la materia puede inscribir estudiantes.'})
        
        # Store subject in attrs for create method
        attrs['subject'] = subject
        return attrs

    def create(self, validated_data):
        email = validated_data.pop('student_email')
        subject = validated_data['subject']
        
        # Get or create student user
        student, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'role': 'STUDENT',
                'is_active': True,
            }
        )
        
        # If student has no usable password, set one
        if not student.has_usable_password():
            student.set_unusable_password()
            student.save(update_fields=['password'])
        
        # Create enrollment (or get if already exists)
        enrollment, was_created = Enrollment.objects.get_or_create(
            subject=subject, 
            student=student
        )
        
        if not was_created:
            raise serializers.ValidationError({'detail': f'El estudiante {email} ya está inscrito en esta materia.'})
        
        return enrollment


class ExerciseSerializer(serializers.ModelSerializer):
    deadline_status = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = ['id', 'subject', 'name', 'order', 'deadline', 'description', 
                  'deadline_status', 'days_until_deadline', 'is_overdue']
    
    def get_deadline_status(self, obj):
        return obj.deadline_status()
    
    def get_days_until_deadline(self, obj):
        return obj.days_until_deadline()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()


class StudentExerciseResultSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source='enrollment.student.email', read_only=True)
    student_name = serializers.SerializerMethodField()
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    subject_id = serializers.IntegerField(source='enrollment.subject.id', read_only=True)
    
    class Meta:
        model = StudentExerciseResult
        fields = [
            'id', 
            'enrollment', 
            'exercise', 
            'status',
            'submission_file',
            'comment',
            'student_email',
            'student_name',
            'exercise_name',
            'subject_id',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'enrollment', 'exercise']
    
    def get_student_name(self, obj):
        return f"{obj.enrollment.student.first_name} {obj.enrollment.student.last_name}".strip()


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class EnrollmentStatsSerializer(serializers.Serializer):
    enrollment_id = serializers.IntegerField()
    student_email = serializers.EmailField()
    total = serializers.IntegerField()
    green = serializers.IntegerField()
    yellow = serializers.IntegerField()
    red = serializers.IntegerField()
    grade = serializers.FloatField()
    semaphore = serializers.CharField()


class SubjectDashboardSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField()
    subject_code = serializers.CharField()
    subject_name = serializers.CharField()
    total_exercises = serializers.IntegerField()
    enrollments = EnrollmentStatsSerializer(many=True)
    aggregates = serializers.DictField(child=serializers.FloatField(), allow_empty=True)


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'is_read',
            'link',
            'created_at',
            'time_ago'
        ]
        read_only_fields = ['created_at']
    
    def get_time_ago(self, obj):
        """Return human-readable time difference"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return 'Hace un momento'
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f'Hace {minutes} minuto{"s" if minutes > 1 else ""}'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f'Hace {hours} hora{"s" if hours > 1 else ""}'
        elif diff < timedelta(days=7):
            days = diff.days
            return f'Hace {days} día{"s" if days > 1 else ""}'
        else:
            return obj.created_at.strftime('%d/%m/%Y %H:%M')
