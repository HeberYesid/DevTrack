from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from exercises.models import Exercise, ExerciseSubmission, UserProfile, StudentGrade
import random


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para probar el sistema'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de ejemplo...')

        # Crear ejercicios de ejemplo
        exercises_data = [
            {
                'title': 'Hola Mundo en Python',
                'description': 'Escribe un programa que imprima "Hola Mundo" en la consola.',
                'difficulty': 'EASY'
            },
            {
                'title': 'Calculadora Básica',
                'description': 'Crea una calculadora que realice operaciones básicas (suma, resta, multiplicación, división).',
                'difficulty': 'EASY'
            },
            {
                'title': 'Números Primos',
                'description': 'Programa que determine si un número es primo y genere los primeros N números primos.',
                'difficulty': 'MEDIUM'
            },
            {
                'title': 'Ordenamiento Burbuja',
                'description': 'Implementa el algoritmo de ordenamiento burbuja para una lista de números.',
                'difficulty': 'MEDIUM'
            },
            {
                'title': 'Fibonacci Recursivo',
                'description': 'Calcula la secuencia de Fibonacci usando recursión hasta el término N.',
                'difficulty': 'MEDIUM'
            },
            {
                'title': 'Árbol Binario de Búsqueda',
                'description': 'Implementa un árbol binario de búsqueda con operaciones de inserción, búsqueda y eliminación.',
                'difficulty': 'HARD'
            },
            {
                'title': 'Algoritmo de Dijkstra',
                'description': 'Implementa el algoritmo de Dijkstra para encontrar el camino más corto en un grafo.',
                'difficulty': 'HARD'
            },
            {
                'title': 'Sistema de Gestión de Archivos',
                'description': 'Crea un sistema que permita crear, leer, actualizar y eliminar archivos.',
                'difficulty': 'HARD'
            },
            {
                'title': 'Palíndromo',
                'description': 'Programa que verifique si una palabra o frase es un palíndromo.',
                'difficulty': 'EASY'
            },
            {
                'title': 'Contador de Palabras',
                'description': 'Cuenta la frecuencia de palabras en un texto dado.',
                'difficulty': 'MEDIUM'
            }
        ]

        created_exercises = []
        for exercise_data in exercises_data:
            exercise, created = Exercise.objects.get_or_create(
                title=exercise_data['title'],
                defaults=exercise_data
            )
            if created:
                self.stdout.write(f'✓ Ejercicio creado: {exercise.title}')
            else:
                self.stdout.write(f'- Ejercicio ya existe: {exercise.title}')
            created_exercises.append(exercise)

        # Crear usuarios de ejemplo
        users_data = [
            {'username': 'estudiante1', 'email': 'estudiante1@ejemplo.com', 'first_name': 'Juan', 'last_name': 'Pérez'},
            {'username': 'estudiante2', 'email': 'estudiante2@ejemplo.com', 'first_name': 'María', 'last_name': 'García'},
            {'username': 'estudiante3', 'email': 'estudiante3@ejemplo.com', 'first_name': 'Carlos', 'last_name': 'López'},
            {'username': 'estudiante4', 'email': 'estudiante4@ejemplo.com', 'first_name': 'Ana', 'last_name': 'Rodríguez'},
            {'username': 'estudiante5', 'email': 'estudiante5@ejemplo.com', 'first_name': 'Luis', 'last_name': 'Martínez'},
        ]

        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                # Crear perfil
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'student_id': f'STU_{user.id:06d}',
                        'bio': f'Estudiante de programación interesado en aprender.'
                    }
                )
                self.stdout.write(f'✓ Usuario creado: {user.username}')
            else:
                self.stdout.write(f'- Usuario ya existe: {user.username}')
            created_users.append(user)

        # Crear envíos de ejemplo
        statuses = ['GREEN', 'YELLOW', 'RED']
        sample_codes = [
            'print("Hola Mundo")',
            'def suma(a, b):\n    return a + b\n\nresult = suma(5, 3)\nprint(result)',
            'for i in range(10):\n    print(f"Número: {i}")',
            '# Código incompleto\n# TODO: Implementar función',
        ]

        for user in created_users:
            # Cada usuario resuelve entre 3 y 8 ejercicios
            num_exercises = random.randint(3, 8)
            selected_exercises = random.sample(created_exercises, num_exercises)
            
            for exercise in selected_exercises:
                # Probabilidades: 40% verde, 35% amarillo, 25% rojo
                status = random.choices(
                    statuses, 
                    weights=[40, 35, 25], 
                    k=1
                )[0]
                
                submission, created = ExerciseSubmission.objects.get_or_create(
                    user=user,
                    exercise=exercise,
                    defaults={
                        'status': status,
                        'code_submission': random.choice(sample_codes),
                        'onlinegdb_url': f'https://onlinegdb.com/example_{random.randint(1000, 9999)}',
                        'notes': f'Ejercicio {"completado" if status == "GREEN" else "con dificultades"}.'
                    }
                )
                
                if created:
                    self.stdout.write(f'  → Envío: {user.username} - {exercise.title} ({status})')

            # Calcular calificación del estudiante
            grade, created = StudentGrade.objects.get_or_create(user=user)
            grade.calculate_grade()
            self.stdout.write(f'  📊 Calificación de {user.username}: {grade.calculated_grade}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ ¡Datos de ejemplo creados exitosamente!\n'
                f'📚 Ejercicios: {len(created_exercises)}\n'
                f'👥 Usuarios: {len(created_users)}\n'
                f'📝 Total de envíos: {ExerciseSubmission.objects.count()}\n\n'
                f'Puedes usar estos usuarios para probar:\n'
                f'Usuario: estudiante1, Contraseña: password123\n'
                f'Usuario: estudiante2, Contraseña: password123\n'
                f'...(y así sucesivamente)\n\n'
                f'Admin: admin, Contraseña: admin123'
            )
        )
