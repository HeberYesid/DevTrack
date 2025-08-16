from django import forms
from django.contrib.auth.models import User
from .models import ExerciseSubmission, UserProfile


class ExerciseSubmissionForm(forms.ModelForm):
    """Formulario para enviar soluciones de ejercicios."""
    
    class Meta:
        model = ExerciseSubmission
        fields = ['status', 'code_submission', 'onlinegdb_url', 'notes']
        widgets = {
            'status': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'code_submission': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 10,
                    'placeholder': 'Pega aquí tu código...'
                }
            ),
            'onlinegdb_url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://onlinegdb.com/...'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Notas adicionales sobre tu solución...'
                }
            ),
        }
        labels = {
            'status': 'Estado del ejercicio',
            'code_submission': 'Código de la solución',
            'onlinegdb_url': 'URL de OnlineGDB',
            'notes': 'Notas adicionales',
        }


class UserProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario."""
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UserProfile
        fields = ['student_id', 'avatar', 'bio']
        widgets = {
            'student_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': True
                }
            ),
            'avatar': forms.FileInput(
                attrs={'class': 'form-control'}
            ),
            'bio': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Cuéntanos un poco sobre ti...'
                }
            ),
        }
        labels = {
            'student_id': 'Código estudiantil',
            'avatar': 'Foto de perfil',
            'bio': 'Biografía',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Actualizar también los campos del User
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
        return profile


class ExerciseFilterForm(forms.Form):
    """Formulario para filtrar ejercicios."""
    
    DIFFICULTY_CHOICES = [
        ('', 'Todas las dificultades'),
        ('EASY', 'Fácil'),
        ('MEDIUM', 'Medio'),
        ('HARD', 'Difícil'),
    ]
    
    STATUS_CHOICES = [
        ('', 'Todos los estados'),
        ('GREEN', 'Verde - Completado'),
        ('YELLOW', 'Amarillo - Con errores'),
        ('RED', 'Rojo - No completado'),
    ]
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Buscar ejercicios...'
            }
        )
    )
    
    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
