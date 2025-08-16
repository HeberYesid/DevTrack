from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Exercise(models.Model):
    """
    Modelo para representar un ejercicio de programación.
    """
    title = models.CharField(max_length=200, verbose_name="Título del ejercicio")
    description = models.TextField(verbose_name="Descripción")
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('EASY', 'Fácil'),
            ('MEDIUM', 'Medio'),
            ('HARD', 'Difícil'),
        ],
        default='EASY',
        verbose_name="Dificultad"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ['created_at']
    
    def __str__(self):
        return self.title


class ExerciseSubmission(models.Model):
    """
    Modelo para representar el estado de un ejercicio resuelto por un estudiante.
    """
    STATUS_CHOICES = [
        ('GREEN', 'Verde - Completado correctamente'),
        ('YELLOW', 'Amarillo - Completado con errores menores'),
        ('RED', 'Rojo - No completado o con errores graves'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Estudiante")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, verbose_name="Ejercicio")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='RED',
        verbose_name="Estado del ejercicio"
    )
    code_submission = models.TextField(blank=True, verbose_name="Código enviado")
    onlinegdb_url = models.URLField(blank=True, verbose_name="URL de OnlineGDB")
    notes = models.TextField(blank=True, verbose_name="Notas adicionales")
    submission_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de envío")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Envío de ejercicio"
        verbose_name_plural = "Envíos de ejercicios"
        unique_together = ['user', 'exercise']
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} ({self.get_status_display()})"


class StudentGrade(models.Model):
    """
    Modelo para almacenar las calificaciones calculadas de los estudiantes.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Estudiante")
    total_exercises = models.IntegerField(default=0, verbose_name="Total de ejercicios")
    green_exercises = models.IntegerField(default=0, verbose_name="Ejercicios verdes")
    yellow_exercises = models.IntegerField(default=0, verbose_name="Ejercicios amarillos")
    red_exercises = models.IntegerField(default=0, verbose_name="Ejercicios rojos")
    calculated_grade = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)],
        verbose_name="Nota calculada"
    )
    last_calculation = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Calificación del estudiante"
        verbose_name_plural = "Calificaciones de estudiantes"
        ordering = ['-calculated_grade']
    
    def calculate_grade(self):
        """
        Calcula la nota según los criterios especificados:
        - 100% verde = 5.0
        - 60% amarillo = 3.0  
        - Resto = cantidad_verde / cantidad_total
        """
        submissions = ExerciseSubmission.objects.filter(user=self.user)
        
        self.total_exercises = submissions.count()
        self.green_exercises = submissions.filter(status='GREEN').count()
        self.yellow_exercises = submissions.filter(status='YELLOW').count()
        self.red_exercises = submissions.filter(status='RED').count()
        
        if self.total_exercises == 0:
            self.calculated_grade = 0.00
        elif self.green_exercises == self.total_exercises:
            # 100% verde = 5.0
            self.calculated_grade = 5.00
        elif self.yellow_exercises >= (self.total_exercises * 0.6):
            # 60% o más amarillo = 3.0
            self.calculated_grade = 3.00
        else:
            # Resto = verde/total
            self.calculated_grade = round((self.green_exercises / self.total_exercises) * 5.0, 2)
        
        self.save()
        return self.calculated_grade
    
    def __str__(self):
        return f"{self.user.username} - Nota: {self.calculated_grade}"


class UserProfile(models.Model):
    """
    Extensión del modelo User para información adicional del estudiante.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Código estudiantil")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    bio = models.TextField(blank=True, verbose_name="Biografía")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    
    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
