#!/usr/bin/env python
"""
Script para importar resultados de estudiantes desde un archivo CSV

Uso:
    python import_student_results.py ../samples/student_results.csv
"""

import os
import sys
import csv
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Subject, Exercise, Enrollment, StudentExerciseResult
from accounts.models import User
from django.db import transaction


def validate_status(status):
    """Validate status value"""
    valid_statuses = ['GREEN', 'YELLOW', 'RED']
    status_upper = status.strip().upper()
    if status_upper not in valid_statuses:
        raise ValueError(f"Status inválido: {status}. Debe ser GREEN, YELLOW o RED")
    return status_upper


def import_results(csv_file_path):
    """Import student results from CSV file"""
    
    if not os.path.exists(csv_file_path):
        print(f"❌ Error: El archivo {csv_file_path} no existe")
        return
    
    print(f"\n{'='*60}")
    print(f"📊 IMPORTACIÓN DE RESULTADOS DE ESTUDIANTES")
    print(f"{'='*60}")
    print(f"Archivo: {csv_file_path}\n")
    
    stats = {
        'total': 0,
        'created': 0,
        'updated': 0,
        'errors': 0,
        'skipped': 0
    }
    
    errors_detail = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            # Validate headers
            required_headers = ['email', 'subject_code', 'exercise_name', 'status']
            if not all(header in reader.fieldnames for header in required_headers):
                print(f"❌ Error: El archivo debe tener las columnas: {', '.join(required_headers)}")
                print(f"   Columnas encontradas: {', '.join(reader.fieldnames)}")
                return
            
            print("🔄 Procesando resultados...\n")
            
            for line_num, row in enumerate(reader, start=2):  # start=2 because line 1 is header
                stats['total'] += 1
                
                try:
                    # Clean data
                    email = row['email'].strip().lower()
                    subject_code = row['subject_code'].strip().upper()
                    exercise_name = row['exercise_name'].strip()
                    status = validate_status(row['status'])
                    
                    # Validate and get objects
                    with transaction.atomic():
                        # Get user
                        try:
                            user = User.objects.get(email=email)
                        except User.DoesNotExist:
                            raise ValueError(f"Usuario no encontrado: {email}")
                        
                        # Get subject
                        try:
                            subject = Subject.objects.get(code=subject_code)
                        except Subject.DoesNotExist:
                            raise ValueError(f"Materia no encontrada: {subject_code}")
                        
                        # Get enrollment
                        try:
                            enrollment = Enrollment.objects.get(student=user, subject=subject)
                        except Enrollment.DoesNotExist:
                            raise ValueError(
                                f"El estudiante {email} no está inscrito en {subject_code}"
                            )
                        
                        # Get or create exercise
                        exercise, ex_created = Exercise.objects.get_or_create(
                            subject=subject,
                            name=exercise_name,
                            defaults={'order': Exercise.objects.filter(subject=subject).count() + 1}
                        )
                        
                        if ex_created:
                            print(f"   ➕ Ejercicio creado: {exercise_name}")
                        
                        # Create or update result
                        result, created = StudentExerciseResult.objects.update_or_create(
                            enrollment=enrollment,
                            exercise=exercise,
                            defaults={'status': status}
                        )
                        
                        if created:
                            stats['created'] += 1
                            status_emoji = {'GREEN': '🟢', 'YELLOW': '🟡', 'RED': '🔴'}.get(status, '⚪')
                            print(f"   ✅ Línea {line_num}: {email} | {subject_code} | {exercise_name} {status_emoji}")
                        else:
                            stats['updated'] += 1
                            status_emoji = {'GREEN': '🟢', 'YELLOW': '🟡', 'RED': '🔴'}.get(status, '⚪')
                            print(f"   🔄 Línea {line_num}: {email} | {subject_code} | {exercise_name} {status_emoji} (actualizado)")
                
                except Exception as e:
                    stats['errors'] += 1
                    error_msg = f"Línea {line_num}: {str(e)} | Datos: {row}"
                    errors_detail.append(error_msg)
                    print(f"   ❌ {error_msg}")
    
    except Exception as e:
        print(f"\n❌ Error al leer el archivo: {e}")
        return
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📈 RESUMEN DE IMPORTACIÓN")
    print(f"{'='*60}")
    print(f"Total de filas procesadas: {stats['total']}")
    print(f"✅ Resultados creados: {stats['created']}")
    print(f"🔄 Resultados actualizados: {stats['updated']}")
    print(f"❌ Errores: {stats['errors']}")
    print(f"{'='*60}\n")
    
    if stats['errors'] > 0:
        print("⚠️  Detalles de errores:")
        for error in errors_detail:
            print(f"   - {error}")
        print()
    
    if stats['created'] > 0 or stats['updated'] > 0:
        print("🎉 Importación completada exitosamente!")
        print("💡 Los estudiantes pueden ver sus resultados en el dashboard")
    else:
        print("⚠️  No se importaron resultados nuevos")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python import_student_results.py <archivo_csv>")
        print("\nEjemplo:")
        print("  python import_student_results.py ../samples/student_results.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    import_results(csv_file)
