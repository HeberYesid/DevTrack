from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from exercises.models import Exercise, ExerciseSubmission, StudentGrade
import json


@login_required
def dashboard(request):
    """Vista principal del dashboard con estadísticas del usuario."""
    user = request.user
    
    # Estadísticas del usuario actual
    user_submissions = ExerciseSubmission.objects.filter(user=user)
    total_exercises = Exercise.objects.filter(is_active=True).count()
    user_total_submissions = user_submissions.count()
    
    # Conteo por estado
    green_count = user_submissions.filter(status='GREEN').count()
    yellow_count = user_submissions.filter(status='YELLOW').count()
    red_count = user_submissions.filter(status='RED').count()
    
    # Calcular porcentajes
    if user_total_submissions > 0:
        green_percentage = round((green_count / user_total_submissions) * 100, 1)
        yellow_percentage = round((yellow_count / user_total_submissions) * 100, 1)
        red_percentage = round((red_count / user_total_submissions) * 100, 1)
    else:
        green_percentage = yellow_percentage = red_percentage = 0
    
    # Obtener o crear la calificación del usuario
    user_grade, created = StudentGrade.objects.get_or_create(user=user)
    if created or user_total_submissions != user_grade.total_exercises:
        user_grade.calculate_grade()
    
    # Estadísticas generales para comparación
    all_grades = StudentGrade.objects.all()
    avg_grade = all_grades.aggregate(Avg('calculated_grade'))['calculated_grade__avg'] or 0
    
    # Últimas sumisiones
    recent_submissions = user_submissions.select_related('exercise').order_by('-submission_date')[:5]
    
    # Progreso por dificultad
    difficulty_stats = {}
    for difficulty, _ in Exercise._meta.get_field('difficulty').choices:
        exercises_by_difficulty = Exercise.objects.filter(difficulty=difficulty, is_active=True)
        total_by_difficulty = exercises_by_difficulty.count()
        completed_by_difficulty = user_submissions.filter(
            exercise__difficulty=difficulty,
            status__in=['GREEN', 'YELLOW']
        ).count()
        
        difficulty_stats[difficulty] = {
            'total': total_by_difficulty,
            'completed': completed_by_difficulty,
            'percentage': round((completed_by_difficulty / total_by_difficulty) * 100, 1) if total_by_difficulty > 0 else 0
        }
    
    context = {
        'user_grade': user_grade,
        'total_exercises': total_exercises,
        'user_total_submissions': user_total_submissions,
        'green_count': green_count,
        'yellow_count': yellow_count,
        'red_count': red_count,
        'green_percentage': green_percentage,
        'yellow_percentage': yellow_percentage,
        'red_percentage': red_percentage,
        'avg_grade': round(avg_grade, 2),
        'recent_submissions': recent_submissions,
        'difficulty_stats': difficulty_stats,
        'progress_percentage': round((user_total_submissions / total_exercises) * 100, 1) if total_exercises > 0 else 0,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def statistics_view(request):
    """Vista con estadísticas detalladas y gráficas."""
    user = request.user
    
    # Estadísticas del usuario
    user_submissions = ExerciseSubmission.objects.filter(user=user)
    user_grade, _ = StudentGrade.objects.get_or_create(user=user)
    
    # Rankings
    all_grades = StudentGrade.objects.select_related('user').order_by('-calculated_grade')
    user_rank = list(all_grades.values_list('user_id', flat=True)).index(user.id) + 1 if user.id in list(all_grades.values_list('user_id', flat=True)) else None
    
    # Estadísticas por mes (últimos 6 meses)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_submissions = user_submissions.filter(
        submission_date__gte=six_months_ago
    ).extra(
        select={'month': "strftime('%%Y-%%m', submission_date)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    context = {
        'user_grade': user_grade,
        'all_grades': all_grades[:10],  # Top 10
        'user_rank': user_rank,
        'total_students': all_grades.count(),
        'monthly_submissions': list(monthly_submissions),
    }
    
    return render(request, 'dashboard/statistics.html', context)


@login_required
def chart_data_api(request):
    """API para obtener datos para las gráficas del dashboard."""
    user = request.user
    chart_type = request.GET.get('type', 'status')
    
    if chart_type == 'status':
        # Datos para gráfica de estado de ejercicios
        user_submissions = ExerciseSubmission.objects.filter(user=user)
        data = {
            'labels': ['Verde', 'Amarillo', 'Rojo'],
            'data': [
                user_submissions.filter(status='GREEN').count(),
                user_submissions.filter(status='YELLOW').count(),
                user_submissions.filter(status='RED').count(),
            ],
            'backgroundColor': ['#28a745', '#ffc107', '#dc3545']
        }
    
    elif chart_type == 'difficulty':
        # Datos para gráfica por dificultad
        user_submissions = ExerciseSubmission.objects.filter(user=user)
        labels = []
        completed_data = []
        total_data = []
        
        for difficulty, display_name in Exercise._meta.get_field('difficulty').choices:
            labels.append(display_name)
            total_by_difficulty = Exercise.objects.filter(difficulty=difficulty, is_active=True).count()
            completed_by_difficulty = user_submissions.filter(
                exercise__difficulty=difficulty,
                status__in=['GREEN', 'YELLOW']
            ).count()
            
            total_data.append(total_by_difficulty)
            completed_data.append(completed_by_difficulty)
        
        data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Completados',
                    'data': completed_data,
                    'backgroundColor': '#28a745'
                },
                {
                    'label': 'Total',
                    'data': total_data,
                    'backgroundColor': '#e9ecef'
                }
            ]
        }
    
    elif chart_type == 'progress':
        # Datos para gráfica de progreso mensual
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_submissions = ExerciseSubmission.objects.filter(
            user=user,
            submission_date__gte=six_months_ago
        ).extra(
            select={'month': "strftime('%%Y-%%m', submission_date)"}
        ).values('month').annotate(count=Count('id')).order_by('month')
        
        labels = []
        data_values = []
        
        for item in monthly_submissions:
            try:
                month_date = datetime.strptime(item['month'], '%Y-%m')
                labels.append(month_date.strftime('%b %Y'))
                data_values.append(item['count'])
            except:
                continue
        
        data = {
            'labels': labels,
            'data': data_values,
            'borderColor': '#007bff',
            'backgroundColor': 'rgba(0, 123, 255, 0.1)'
        }
    
    elif chart_type == 'ranking':
        # Datos para comparación con otros estudiantes
        all_grades = StudentGrade.objects.select_related('user').order_by('-calculated_grade')[:10]
        
        labels = []
        data_values = []
        background_colors = []
        
        for i, grade in enumerate(all_grades):
            labels.append(grade.user.username)
            data_values.append(float(grade.calculated_grade))
            # Destacar al usuario actual
            if grade.user == user:
                background_colors.append('#007bff')
            else:
                background_colors.append('#e9ecef')
        
        data = {
            'labels': labels,
            'data': data_values,
            'backgroundColor': background_colors
        }
    
    else:
        data = {'error': 'Tipo de gráfica no válido'}
    
    return JsonResponse(data)
