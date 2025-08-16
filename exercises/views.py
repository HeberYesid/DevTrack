from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from .models import Exercise, ExerciseSubmission, StudentGrade, UserProfile
from .forms import ExerciseSubmissionForm, UserProfileForm


def home(request):
    """Vista principal del sitio."""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    return render(request, 'exercises/home.html')


class ExerciseListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los ejercicios disponibles."""
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Exercise.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        difficulty = self.request.GET.get('difficulty')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el estado de cada ejercicio para el usuario actual
        user_submissions = ExerciseSubmission.objects.filter(
            user=self.request.user
        ).select_related('exercise')
        
        submission_status = {sub.exercise.id: sub.status for sub in user_submissions}
        
        # Agregar estado a cada ejercicio
        for exercise in context['exercises']:
            exercise.user_status = submission_status.get(exercise.id, 'RED')
            
        context['difficulty_choices'] = Exercise._meta.get_field('difficulty').choices
        return context


class ExerciseDetailView(LoginRequiredMixin, DetailView):
    """Vista detallada de un ejercicio específico."""
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    context_object_name = 'exercise'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener la sumisión del usuario para este ejercicio si existe
        try:
            submission = ExerciseSubmission.objects.get(
                user=self.request.user,
                exercise=self.object
            )
            context['user_submission'] = submission
        except ExerciseSubmission.DoesNotExist:
            context['user_submission'] = None
            
        context['form'] = ExerciseSubmissionForm()
        return context


@login_required
def submit_exercise(request, exercise_id):
    """Vista para enviar o actualizar la solución de un ejercicio."""
    exercise = get_object_or_404(Exercise, id=exercise_id, is_active=True)
    
    if request.method == 'POST':
        form = ExerciseSubmissionForm(request.POST)
        if form.is_valid():
            # Obtener o crear la sumisión
            submission, created = ExerciseSubmission.objects.get_or_create(
                user=request.user,
                exercise=exercise,
                defaults={
                    'status': form.cleaned_data['status'],
                    'code_submission': form.cleaned_data['code_submission'],
                    'onlinegdb_url': form.cleaned_data['onlinegdb_url'],
                    'notes': form.cleaned_data['notes'],
                }
            )
            
            if not created:
                # Actualizar sumisión existente
                submission.status = form.cleaned_data['status']
                submission.code_submission = form.cleaned_data['code_submission']
                submission.onlinegdb_url = form.cleaned_data['onlinegdb_url']
                submission.notes = form.cleaned_data['notes']
                submission.save()
            
            # Recalcular la calificación del estudiante
            grade, created = StudentGrade.objects.get_or_create(user=request.user)
            grade.calculate_grade()
            
            messages.success(request, 'Ejercicio enviado exitosamente.')
            return redirect('exercises:exercise_detail', pk=exercise.id)
    
    return redirect('exercises:exercise_detail', pk=exercise.id)


@login_required
def my_submissions(request):
    """Vista para mostrar todas las sumisiones del usuario."""
    submissions = ExerciseSubmission.objects.filter(
        user=request.user
    ).select_related('exercise').order_by('-submission_date')
    
    # Estadísticas del usuario
    total_submissions = submissions.count()
    green_count = submissions.filter(status='GREEN').count()
    yellow_count = submissions.filter(status='YELLOW').count()
    red_count = submissions.filter(status='RED').count()
    
    # Obtener o crear la calificación
    grade, created = StudentGrade.objects.get_or_create(user=request.user)
    if created or total_submissions != grade.total_exercises:
        grade.calculate_grade()
    
    context = {
        'submissions': submissions,
        'total_submissions': total_submissions,
        'green_count': green_count,
        'yellow_count': yellow_count,
        'red_count': red_count,
        'grade': grade,
    }
    
    return render(request, 'exercises/my_submissions.html', context)


@login_required
def profile_view(request):
    """Vista para mostrar y editar el perfil del usuario."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('exercises:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'exercises/profile.html', {'form': form, 'profile': profile})


def register_view(request):
    """Vista de registro de usuarios."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada para {username}!')
            
            # Crear perfil de usuario
            UserProfile.objects.create(
                user=user,
                student_id=f"STU_{user.id:06d}"  # Generar código estudiantil
            )
            
            # Autenticar y loguear al usuario
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user:
                login(request, user)
                return redirect('dashboard:dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """Vista personalizada de logout."""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


@login_required
def exercise_stats_api(request):
    """API para obtener estadísticas de ejercicios en formato JSON."""
    user_submissions = ExerciseSubmission.objects.filter(user=request.user)
    
    stats = {
        'green': user_submissions.filter(status='GREEN').count(),
        'yellow': user_submissions.filter(status='YELLOW').count(),
        'red': user_submissions.filter(status='RED').count(),
    }
    
    total = sum(stats.values())
    if total > 0:
        stats['green_percentage'] = round((stats['green'] / total) * 100, 1)
        stats['yellow_percentage'] = round((stats['yellow'] / total) * 100, 1)
        stats['red_percentage'] = round((stats['red'] / total) * 100, 1)
    else:
        stats['green_percentage'] = 0
        stats['yellow_percentage'] = 0
        stats['red_percentage'] = 0
    
    return JsonResponse(stats)
