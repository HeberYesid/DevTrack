from __future__ import annotations
import csv
import io
from typing import List, Dict

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, status, decorators, parsers, views
from rest_framework.response import Response

from .models import Subject, Enrollment, Exercise, StudentExerciseResult
from .serializers import (
    SubjectSerializer,
    EnrollmentSerializer,
    ExerciseSerializer,
    StudentExerciseResultSerializer,
    CSVUploadSerializer,
)
from .permissions import (
    IsOwnerTeacherOrAdmin,
)

User = get_user_model()


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'ADMIN':
            return Subject.objects.all()
        if getattr(user, 'role', None) == 'TEACHER':
            return Subject.objects.filter(teacher=user)
        # Students: subjects where enrolled
        return Subject.objects.filter(enrollments__student=user).distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'upload_enrollments_csv', 'upload_results_csv']:
            return [permissions.IsAuthenticated(), IsOwnerTeacherOrAdmin()]
        return super().get_permissions()

    @decorators.action(detail=True, methods=['get', 'post'], url_path='enrollments')
    def enrollments(self, request, pk=None):
        subject = self.get_object()
        if request.method == 'GET':
            enrollments = subject.enrollments.select_related('student')
            data = [
                {
                    'id': e.id,
                    'student': {
                        'id': e.student.id,
                        'email': e.student.email,
                        'first_name': e.student.first_name,
                        'last_name': e.student.last_name,
                    },
                    'created_at': e.created_at,
                } for e in enrollments
            ]
            return Response(data)
        else:
            serializer = EnrollmentSerializer(data=request.data, context={'request': request, 'subject': subject})
            serializer.is_valid(raise_exception=True)
            enrollment = serializer.save()
            return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=['post'], url_path='enrollments/upload-csv', parser_classes=[parsers.MultiPartParser])
    def upload_enrollments_csv(self, request, pk=None):
        subject = self.get_object()
        file_serializer = CSVUploadSerializer(data=request.data)
        file_serializer.is_valid(raise_exception=True)
        f = file_serializer.validated_data['file']
        decoded = f.read().decode('utf-8', errors='ignore')
        reader = csv.DictReader(io.StringIO(decoded))
        required_cols = {'email'}
        if not required_cols.issubset(set([c.strip().lower() for c in reader.fieldnames or []])):
            return Response({'detail': 'CSV inválido. Debe tener columnas: email, (opcional) first_name, last_name.'}, status=400)

        created, existed, errors = 0, 0, []
        for i, row in enumerate(reader, start=2):
            email = (row.get('email') or '').strip().lower()
            if not email:
                errors.append({'row': i, 'error': 'Email vacío'})
                continue
            first_name = (row.get('first_name') or '').strip()
            last_name = (row.get('last_name') or '').strip()
            student, _ = User.objects.get_or_create(
                email=email,
                defaults={'username': email, 'first_name': first_name, 'last_name': last_name, 'role': 'STUDENT', 'is_active': True}
            )
            # update names if provided
            update_fields = []
            if first_name and student.first_name != first_name:
                student.first_name = first_name
                update_fields.append('first_name')
            if last_name and student.last_name != last_name:
                student.last_name = last_name
                update_fields.append('last_name')
            if update_fields:
                student.save(update_fields=update_fields)

            enrollment, was_created = Enrollment.objects.get_or_create(subject=subject, student=student)
            if was_created:
                created += 1
            else:
                existed += 1

        return Response({'created': created, 'existed': existed, 'errors': errors})

    @decorators.action(detail=True, methods=['get'], url_path='dashboard')
    def dashboard(self, request, pk=None):
        subject = self.get_object()
        exercises_count = subject.exercises.count()
        enrollments = subject.enrollments.select_related('student').all()

        items = []
        grades = []
        greens = yellows = reds = totals = 0
        for e in enrollments:
            s = e.stats()
            items.append({
                'enrollment_id': e.id,
                'student_email': e.student.email,
                'total': s['total'],
                'green': s['green'],
                'yellow': s['yellow'],
                'red': s['red'],
                'grade': s['grade'],
                'semaphore': s['semaphore'],
            })
            grades.append(s['grade'])
            greens += s['green']
            yellows += s['yellow']
            reds += s['red']
            totals += s['total']

        aggregates = {
            'avg_grade': round(sum(grades) / len(grades), 2) if grades else 0.0,
            'pct_green': round(100.0 * greens / totals, 2) if totals else 0.0,
            'pct_yellow': round(100.0 * yellows / totals, 2) if totals else 0.0,
            'pct_red': round(100.0 * reds / totals, 2) if totals else 0.0,
        }
        return Response({
            'subject_id': subject.id,
            'subject_code': subject.code,
            'subject_name': subject.name,
            'total_exercises': exercises_count,
            'enrollments': items,
            'aggregates': aggregates,
        })

    @decorators.action(detail=True, methods=['get'], url_path='export-csv')
    def export_csv(self, request, pk=None):
        subject = self.get_object()
        # Prepare CSV with header: student_email, total, green, yellow, red, grade
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{subject.code}_consolidado.csv"'

        writer = csv.writer(response)
        writer.writerow(['student_email', 'total', 'green', 'yellow', 'red', 'grade'])
        for e in subject.enrollments.select_related('student').all():
            s = e.stats()
            writer.writerow([e.student.email, s['total'], s['green'], s['yellow'], s['red'], s['grade']])
        return response

    @decorators.action(detail=True, methods=['post'], url_path='results/upload-csv', parser_classes=[parsers.MultiPartParser])
    def upload_results_csv(self, request, pk=None):
        subject = self.get_object()
        file_serializer = CSVUploadSerializer(data=request.data)
        file_serializer.is_valid(raise_exception=True)
        f = file_serializer.validated_data['file']
        decoded = f.read().decode('utf-8', errors='ignore')
        reader = csv.DictReader(io.StringIO(decoded))
        required = {'student_email', 'exercise_name', 'status'}
        if not required.issubset(set([c.strip().lower() for c in (reader.fieldnames or [])])):
            return Response({'detail': 'CSV inválido. Debe tener columnas: student_email, exercise_name, status.'}, status=400)

        def normalize_status(val: str) -> str | None:
            v = (val or '').strip().lower()
            if v in {'green', 'verde', 'g', '1', 'true'}:
                return StudentExerciseResult.Status.GREEN
            if v in {'yellow', 'amarillo', 'y'}:
                return StudentExerciseResult.Status.YELLOW
            if v in {'red', 'rojo', 'r', '0', 'false'}:
                return StudentExerciseResult.Status.RED
            return None

        created, updated, skipped, errors = 0, 0, 0, []
        # Optionally precreate exercises
        exercise_cache: Dict[str, Exercise] = {ex.name.lower(): ex for ex in subject.exercises.all()}

        for i, row in enumerate(reader, start=2):
            email = (row.get('student_email') or '').strip().lower()
            ex_name = (row.get('exercise_name') or '').strip()
            status_val = normalize_status(row.get('status'))
            if not email or not ex_name or status_val is None:
                errors.append({'row': i, 'error': 'Datos inválidos en columnas requeridas'})
                continue

            try:
                student = User.objects.get(email=email)
            except User.DoesNotExist:
                errors.append({'row': i, 'error': f'Estudiante no encontrado: {email}'})
                continue

            try:
                enrollment = Enrollment.objects.get(subject=subject, student=student)
            except Enrollment.DoesNotExist:
                errors.append({'row': i, 'error': f'Estudiante no inscrito en la materia: {email}'})
                continue

            exercise = exercise_cache.get(ex_name.lower())
            if not exercise:
                exercise = Exercise.objects.create(subject=subject, name=ex_name, order=subject.exercises.count())
                exercise_cache[ex_name.lower()] = exercise

            obj, was_created = StudentExerciseResult.objects.update_or_create(
                enrollment=enrollment,
                exercise=exercise,
                defaults={'status': status_val}
            )
            if was_created:
                created += 1
            else:
                updated += 1

        # Create notifications to students and teacher (bulk) via signals or here (optional)
        return Response({'created': created, 'updated': updated, 'skipped': skipped, 'errors': errors})


class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Exercise.objects.select_related('subject', 'subject__teacher')
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if getattr(user, 'role', None) == 'ADMIN':
            return qs
        if getattr(user, 'role', None) == 'TEACHER':
            return qs.filter(subject__teacher=user)
        # students can view exercises of their subjects
        return qs.filter(subject__enrollments__student=user).distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerTeacherOrAdmin()]
        return super().get_permissions()


class EnrollmentResultsView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=True, methods=['get'], url_path='results')
    def list_results(self, request, pk=None):
        enrollment = get_object_or_404(Enrollment, pk=pk)
        user = request.user
        # permissions: student owner, subject teacher, or admin
        allowed = (
            getattr(user, 'role', None) == 'ADMIN' or
            (getattr(user, 'role', None) == 'TEACHER' and enrollment.subject.teacher_id == user.id) or
            enrollment.student_id == user.id
        )
        if not allowed:
            return Response({'detail': 'No autorizado.'}, status=403)

        results = StudentExerciseResult.objects.filter(enrollment=enrollment).select_related('exercise')
        data = [
            {
                'exercise_id': r.exercise_id,
                'exercise_name': r.exercise.name,
                'status': r.status,
                'updated_at': r.updated_at,
            } for r in results
        ]
        return Response({'enrollment_id': enrollment.id, 'student_email': enrollment.student.email, 'results': data, 'stats': enrollment.stats()})


class MyEnrollmentsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, 'role', None) != 'STUDENT':
            return Response({'detail': 'No autorizado.'}, status=403)
        enrollments = Enrollment.objects.filter(student=user).select_related('subject')
        items = []
        for e in enrollments:
            items.append({
                'enrollment_id': e.id,
                'subject_id': e.subject.id,
                'subject_code': e.subject.code,
                'subject_name': e.subject.name,
                'stats': e.stats(),
            })
        return Response({'enrollments': items})
