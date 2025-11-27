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

from .models import Subject, Enrollment, Exercise, StudentExerciseResult, Notification
from .serializers import (
    SubjectSerializer,
    EnrollmentSerializer,
    ExerciseSerializer,
    StudentExerciseResultSerializer,
    CSVUploadSerializer,
    NotificationSerializer,
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
        # Annotate to avoid N+1 queries when getting enrollments_count
        qs = Subject.objects.select_related('teacher').prefetch_related('enrollments')
        
        if getattr(user, 'role', None) == 'ADMIN':
            return qs
        if getattr(user, 'role', None) == 'TEACHER':
            return qs.filter(teacher=user)
        # Students: subjects where enrolled
        return qs.filter(enrollments__student=user).distinct()

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

    @decorators.action(detail=True, methods=['post'], url_path='submit', parser_classes=[parsers.MultiPartParser])
    def submit_solution(self, request, pk=None):
        exercise = self.get_object()
        user = request.user
        
        # Verify user is a student enrolled in the subject
        try:
            enrollment = Enrollment.objects.get(subject=exercise.subject, student=user)
        except Enrollment.DoesNotExist:
            return Response({'detail': 'No estás inscrito en esta materia.'}, status=status.HTTP_403_FORBIDDEN)
            
        # Get or create result
        result, created = StudentExerciseResult.objects.get_or_create(
            enrollment=enrollment,
            exercise=exercise,
            defaults={'status': 'SUBMITTED'}
        )
        
        # Check if file is provided
        if 'submission_file' not in request.FILES:
             return Response({'detail': 'No se proporcionó ningún archivo.'}, status=status.HTTP_400_BAD_REQUEST)
             
        file_obj = request.FILES['submission_file']
        
        # Validate file size (1MB = 1024 * 1024 bytes)
        if file_obj.size > 1024 * 1024:
            return Response({'detail': 'El archivo excede el tamaño máximo de 1MB.'}, status=status.HTTP_400_BAD_REQUEST)
            
        result.submission_file = file_obj
        result.status = 'SUBMITTED'
        result.save()
        
        return Response(StudentExerciseResultSerializer(result).data)


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


class StudentExerciseResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual student exercise results.
    Allows teachers and admins to create and update result status.
    """
    serializer_class = StudentExerciseResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = StudentExerciseResult.objects.select_related(
            'enrollment__student',
            'enrollment__subject',
            'enrollment__subject__teacher',
            'exercise'
        )
        
        # Filter by subject if provided
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            qs = qs.filter(enrollment__subject_id=subject_id)
        
        # Permission filtering
        if getattr(user, 'role', None) == 'ADMIN':
            return qs
        if getattr(user, 'role', None) == 'TEACHER':
            return qs.filter(enrollment__subject__teacher=user)
        # Students can only see their own results
        return qs.filter(enrollment__student=user)
    
    def create(self, request, *args, **kwargs):
        """Create a new result for a student-exercise pair"""
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # Only teachers and admins can create results
        if user_role not in ['ADMIN', 'TEACHER']:
            return Response({'detail': 'Solo profesores y administradores pueden crear resultados.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get enrollment and exercise from request
        enrollment_id = request.data.get('enrollment')
        exercise_id = request.data.get('exercise')
        result_status = request.data.get('status')
        comment = request.data.get('comment', '')
        
        if not enrollment_id or not exercise_id or not result_status:
            return Response({'detail': 'enrollment, exercise y status son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            enrollment = Enrollment.objects.select_related('subject').get(id=enrollment_id)
            exercise = Exercise.objects.get(id=exercise_id)
        except Enrollment.DoesNotExist:
            return Response({'detail': 'Inscripción no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        except Exercise.DoesNotExist:
            return Response({'detail': 'Ejercicio no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify the exercise belongs to the same subject as enrollment
        if exercise.subject_id != enrollment.subject_id:
            return Response({'detail': 'El ejercicio no pertenece a la materia del estudiante.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Teachers can only create results for their own subjects
        if user_role == 'TEACHER':
            if enrollment.subject.teacher_id != user.id:
                return Response({'detail': 'No tienes permiso para crear resultados en esta materia.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if result already exists
        existing = StudentExerciseResult.objects.filter(enrollment=enrollment, exercise=exercise).first()
        if existing:
            return Response({
                'detail': f'Ya existe un resultado para este estudiante y ejercicio. Usa PATCH para actualizarlo.',
                'existing_result_id': existing.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the result
        result = StudentExerciseResult.objects.create(
            enrollment=enrollment,
            exercise=exercise,
            status=result_status,
            comment=comment
        )
        
        serializer = self.get_serializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update a result status"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Verify user can modify this result
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # Only teachers and admins can edit
        if user_role not in ['ADMIN', 'TEACHER']:
            return Response({'detail': 'Solo profesores y administradores pueden editar resultados.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Teachers can only edit results from their own subjects
        if user_role == 'TEACHER':
            if instance.enrollment.subject.teacher_id != user.id:
                return Response({'detail': 'No tienes permiso para modificar resultados de esta materia.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


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


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications.
    Users can only see their own notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return notifications for the current user"""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def get_permissions(self):
        # Users can only list and update their own notifications
        return super().get_permissions()

    @decorators.action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Mark all notifications as read for current user"""
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({
            'message': f'{updated} notificaciones marcadas como le\u00eddas',
            'updated_count': updated
        })

    @decorators.action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark a single notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({
            'message': 'Notificación marcada como leída',
            'notification': NotificationSerializer(notification).data
        })

    @decorators.action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})
    
    @decorators.action(detail=False, methods=['post'], url_path='delete-all')
    def delete_all(self, request):
        """Delete all notifications for current user"""
        count = Notification.objects.filter(user=request.user).count()
        Notification.objects.filter(user=request.user).delete()
        return Response({
            'message': f'{count} notificaciones eliminadas',
            'deleted': count
        })


class StudentDashboardView(views.APIView):
    """Dashboard personalizado para estudiantes"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Obtener dashboard del estudiante con:
        - Resumen de resultados (verde, amarillo, rojo)
        - Progreso por materia
        - Ejercicios pendientes
        - Estadísticas generales
        """
        user = request.user
        
        # Verificar que sea estudiante
        if user.role != 'STUDENT':
            return Response(
                {'error': 'Este endpoint es solo para estudiantes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener todas las inscripciones del estudiante
        enrollments = Enrollment.objects.filter(student=user).select_related('subject')
        
        # Resumen general
        all_results = StudentExerciseResult.objects.filter(enrollment__student=user)
        total_results = all_results.count()
        green_count = all_results.filter(status='GREEN').count()
        yellow_count = all_results.filter(status='YELLOW').count()
        red_count = all_results.filter(status='RED').count()
        
        # Calcular porcentaje de éxito
        success_rate = round((green_count / total_results * 100), 1) if total_results > 0 else 0
        
        # Progreso por materia
        subjects_progress = []
        for enrollment in enrollments:
            subject = enrollment.subject
            
            # Obtener todos los ejercicios de la materia
            all_exercises = Exercise.objects.filter(subject=subject)
            total_exercises = all_exercises.count()
            
            # Obtener resultados del estudiante en esta materia
            results = StudentExerciseResult.objects.filter(enrollment=enrollment)
            completed_exercises = results.count()
            
            # Contar por estado
            green = results.filter(status='GREEN').count()
            yellow = results.filter(status='YELLOW').count()
            red = results.filter(status='RED').count()
            
            # Calcular porcentaje de completado
            completion_rate = round((completed_exercises / total_exercises * 100), 1) if total_exercises > 0 else 0
            
            # Ejercicios pendientes de esta materia
            completed_exercise_ids = results.values_list('exercise_id', flat=True)
            pending_exercises = all_exercises.exclude(id__in=completed_exercise_ids)
            
            subjects_progress.append({
                'subject_id': subject.id,
                'subject_name': subject.name,
                'subject_code': subject.code,
                'total_exercises': total_exercises,
                'completed_exercises': completed_exercises,
                'pending_exercises': pending_exercises.count(),
                'completion_rate': completion_rate,
                'green_count': green,
                'yellow_count': yellow,
                'red_count': red,
                'success_rate': round((green / completed_exercises * 100), 1) if completed_exercises > 0 else 0
            })
        
        # Ejercicios pendientes (todos)
        all_enrolled_subjects = enrollments.values_list('subject_id', flat=True)
        all_subject_exercises = Exercise.objects.filter(subject_id__in=all_enrolled_subjects).select_related('subject')
        completed_exercise_ids = all_results.values_list('exercise_id', flat=True)
        pending_exercises_queryset = all_subject_exercises.exclude(id__in=completed_exercise_ids).order_by('-id')[:10]
        
        pending_exercises = []
        for exercise in pending_exercises_queryset:
            pending_exercises.append({
                'id': exercise.id,
                'name': exercise.name,
                'subject_name': exercise.subject.name,
                'subject_code': exercise.subject.code,
                'subject_id': exercise.subject.id,
                'deadline': exercise.deadline.strftime('%d/%m/%Y %H:%M') if exercise.deadline else None
            })
        
        # Últimos resultados
        recent_results = all_results.select_related('exercise__subject', 'enrollment').order_by('-created_at')[:5]
        recent_results_data = []
        for result in recent_results:
            recent_results_data.append({
                'id': result.id,
                'exercise_name': result.exercise.name,
                'subject_name': result.enrollment.subject.name,
                'status': result.status,
                'comment': result.comment or '',
                'created_at': result.created_at.strftime('%d/%m/%Y %H:%M')
            })
        
        # Respuesta
        return Response({
            'summary': {
                'total_results': total_results,
                'green_count': green_count,
                'yellow_count': yellow_count,
                'red_count': red_count,
                'success_rate': success_rate,
                'total_subjects': enrollments.count(),
                'total_pending': pending_exercises_queryset.count()
            },
            'subjects_progress': subjects_progress,
            'pending_exercises': pending_exercises,
            'recent_results': recent_results_data
        })
