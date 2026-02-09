from django.core.management.base import BaseCommand
from django.db import transaction
from courses.models import Subject, Exercise, Enrollment, StudentExerciseResult
from accounts.models import User
import csv
import os


class Command(BaseCommand):
    help = "Import student results from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def validate_status(self, status):
        """Validate status value"""
        valid_statuses = ["GREEN", "YELLOW", "RED"]
        status_upper = status.strip().upper()
        if status_upper not in valid_statuses:
            raise ValueError(f"Status inválido: {status}. Debe ser GREEN, YELLOW o RED")
        return status_upper

    def handle(self, *args, **options):
        csv_file_path = options["csv_file"]

        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f"Error: El archivo {csv_file_path} no existe")
            )
            return

        self.stdout.write(
            self.style.MIGRATE_HEADING("IMPORTACIÓN DE RESULTADOS DE ESTUDIANTES")
        )
        self.stdout.write(f"Archivo: {csv_file_path}\n")

        stats = {"total": 0, "created": 0, "updated": 0, "errors": 0, "skipped": 0}

        errors_detail = []

        try:
            with open(csv_file_path, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                # Validate headers
                required_headers = ["email", "subject_code", "exercise_name", "status"]
                if not all(header in reader.fieldnames for header in required_headers):
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error: El archivo debe tener las columnas: {', '.join(required_headers)}"
                        )
                    )
                    self.stdout.write(
                        f"Columnas encontradas: {', '.join(reader.fieldnames)}"
                    )
                    return

                self.stdout.write("Procesando resultados...\n")

                for line_num, row in enumerate(reader, start=2):
                    stats["total"] += 1

                    try:
                        email = row["email"].strip().lower()
                        subject_code = row["subject_code"].strip().upper()
                        exercise_name = row["exercise_name"].strip()
                        status = self.validate_status(row["status"])

                        with transaction.atomic():
                            try:
                                user = User.objects.get(email=email)
                            except User.DoesNotExist:
                                raise ValueError(f"Usuario no encontrado: {email}")

                            try:
                                subject = Subject.objects.get(code=subject_code)
                            except Subject.DoesNotExist:
                                raise ValueError(
                                    f"Materia no encontrada: {subject_code}"
                                )

                            try:
                                enrollment = Enrollment.objects.get(
                                    student=user, subject=subject
                                )
                            except Enrollment.DoesNotExist:
                                raise ValueError(
                                    f"El estudiante {email} no está inscrito en {subject_code}"
                                )

                            exercise, ex_created = Exercise.objects.get_or_create(
                                subject=subject,
                                name=exercise_name,
                                defaults={
                                    "order": Exercise.objects.filter(
                                        subject=subject
                                    ).count()
                                    + 1
                                },
                            )

                            if ex_created:
                                self.stdout.write(
                                    f"   ➕ Ejercicio creado: {exercise_name}"
                                )

                            result, created = (
                                StudentExerciseResult.objects.update_or_create(
                                    enrollment=enrollment,
                                    exercise=exercise,
                                    defaults={"status": status},
                                )
                            )

                            status_emoji = {
                                "GREEN": "🟢",
                                "YELLOW": "🟡",
                                "RED": "🔴",
                            }.get(status, "⚪")
                            if created:
                                stats["created"] += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"   ✅ Línea {line_num}: {email} | {subject_code} | {exercise_name} {status_emoji}"
                                    )
                                )
                            else:
                                stats["updated"] += 1
                                self.stdout.write(
                                    f"   🔄 Línea {line_num}: {email} | {subject_code} | {exercise_name} {status_emoji} (actualizado)"
                                )

                    except Exception as e:
                        stats["errors"] += 1
                        error_msg = f"Línea {line_num}: {str(e)} | Datos: {row}"
                        errors_detail.append(error_msg)
                        self.stdout.write(self.style.ERROR(f"   ❌ {error_msg}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al leer el archivo: {e}"))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("RESUMEN DE IMPORTACIÓN"))
        self.stdout.write(f"Total de filas procesadas: {stats['total']}")
        self.stdout.write(self.style.SUCCESS(f"Resultados creados: {stats['created']}"))
        self.stdout.write(f"Resultados actualizados: {stats['updated']}")
        self.stdout.write(self.style.ERROR(f"Errores: {stats['errors']}"))

        if stats["errors"] > 0:
            self.stdout.write("\nDetalles de errores:")
            for error in errors_detail:
                self.stdout.write(f"   - {error}")
