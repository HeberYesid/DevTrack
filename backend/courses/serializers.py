from typing import Any
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Subject, Enrollment, Exercise, StudentExerciseResult

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
    student_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'subject', 'student', 'student_email', 'created_at']
        read_only_fields = ['student', 'created_at']

    def validate(self, attrs):
        # ensure teacher owns subject
        request = self.context['request']
        subject = attrs.get('subject') or self.context.get('subject')
        if subject is None:
            raise serializers.ValidationError('Materia (subject) requerida.')
        # inject subject for create
        attrs['subject'] = subject
        if request.user.role not in ['ADMIN', 'TEACHER']:
            raise serializers.ValidationError('No tienes permisos para inscribir estudiantes.')
        if request.user.role == 'TEACHER' and subject.teacher_id != request.user.id:
            raise serializers.ValidationError('Solo el profesor dueño de la materia puede inscribir estudiantes.')
        return attrs

    def create(self, validated_data):
        email = validated_data.pop('student_email').lower().strip()
        subject: Subject = validated_data['subject']
        # get or create student user
        student, _created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'role': 'STUDENT',
                'is_active': True,
            }
        )
        # if student has no usable password, set one random
        if not student.has_usable_password():
            student.set_unusable_password()
            student.save(update_fields=['password'])
        enrollment, _ = Enrollment.objects.get_or_create(subject=subject, student=student)
        return enrollment


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'subject', 'name', 'order']


class StudentExerciseResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExerciseResult
        fields = ['id', 'enrollment', 'exercise', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


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
