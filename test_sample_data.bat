@echo off
REM Script para verificar y crear datos de prueba

echo Verificando estado actual de la base de datos...
.venv\Scripts\python.exe manage.py shell -c "from exercises.models import Exercise, ExerciseSubmission, User; print(f'Ejercicios: {Exercise.objects.count()}'); print(f'Usuarios: {User.objects.count()}'); print(f'Envios: {ExerciseSubmission.objects.count()}')"

echo.
echo Ejecutando comando de creacion de datos de prueba...
.venv\Scripts\python.exe manage.py create_sample_data

echo.
echo Verificando estado final de la base de datos...
.venv\Scripts\python.exe manage.py shell -c "from exercises.models import Exercise, ExerciseSubmission, User; print(f'Ejercicios: {Exercise.objects.count()}'); print(f'Usuarios: {User.objects.count()}'); print(f'Envios: {ExerciseSubmission.objects.count()}')"

pause
