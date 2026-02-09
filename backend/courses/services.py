from __future__ import annotations
import csv
import io
from typing import Dict, List, Any, Tuple
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from .models import Subject, Enrollment, Exercise, StudentExerciseResult

User = get_user_model()


def process_enrollments_csv(subject: Subject, file_obj) -> Dict[str, Any]:
    """
    Process CSV file to enroll students in a subject.
    CSV format: email, [first_name], [last_name]
    """
    decoded = file_obj.read().decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(decoded))

    required_cols = {"email"}
    fieldnames = [c.strip().lower() for c in (reader.fieldnames or [])]
    if not required_cols.issubset(set(fieldnames)):
        raise ValidationError(
            {
                "detail": "CSV inválido. Debe tener columnas: email, (opcional) first_name, last_name."
            }
        )

    created, existed, errors = 0, 0, []

    for i, row in enumerate(reader, start=2):
        email = (row.get("email") or "").strip().lower()
        if not email:
            errors.append({"row": i, "error": "Email vacío"})
            continue

        first_name = (row.get("first_name") or "").strip()
        last_name = (row.get("last_name") or "").strip()

        # Create or verify user exists
        student, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": first_name,
                "last_name": last_name,
                "role": "STUDENT",
                "is_active": True,
            },
        )

        # update names if provided and different
        update_fields = []
        if first_name and student.first_name != first_name:
            student.first_name = first_name
            update_fields.append("first_name")
        if last_name and student.last_name != last_name:
            student.last_name = last_name
            update_fields.append("last_name")

        if update_fields:
            student.save(update_fields=update_fields)

        # Create enrollment
        _, was_created = Enrollment.objects.get_or_create(
            subject=subject, student=student
        )
        if was_created:
            created += 1
        else:
            existed += 1

    return {"created": created, "existed": existed, "errors": errors}


def normalize_result_status(val: str) -> str | None:
    """Normalize status string to Enum value"""
    v = (val or "").strip().lower()
    if v in {"green", "verde", "g", "1", "true"}:
        return StudentExerciseResult.Status.GREEN
    if v in {"yellow", "amarillo", "y"}:
        return StudentExerciseResult.Status.YELLOW
    if v in {"red", "rojo", "r", "0", "false"}:
        return StudentExerciseResult.Status.RED
    return None


def process_results_csv(subject: Subject, file_obj) -> Dict[str, Any]:
    """
    Process CSV file to upload student results.
    CSV format: student_email, exercise_name, status
    """
    decoded = file_obj.read().decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(decoded))

    required = {"student_email", "exercise_name", "status"}
    fieldnames = [c.strip().lower() for c in (reader.fieldnames or [])]
    if not required.issubset(set(fieldnames)):
        raise ValidationError(
            {
                "detail": "CSV inválido. Debe tener columnas: student_email, exercise_name, status."
            }
        )

    created, updated, skipped, errors = 0, 0, 0, []

    # Pre-fetch exercises to minimize DB hits
    exercise_cache: Dict[str, Exercise] = {
        ex.name.lower(): ex for ex in subject.exercises.all()
    }

    for i, row in enumerate(reader, start=2):
        email = (row.get("student_email") or "").strip().lower()
        ex_name = (row.get("exercise_name") or "").strip()
        status_val = normalize_result_status(row.get("status"))

        if not email or not ex_name or status_val is None:
            errors.append({"row": i, "error": "Datos inválidos en columnas requeridas"})
            continue

        try:
            student = User.objects.get(email=email)
        except User.DoesNotExist:
            errors.append({"row": i, "error": f"Estudiante no encontrado: {email}"})
            continue

        try:
            enrollment = Enrollment.objects.get(subject=subject, student=student)
        except Enrollment.DoesNotExist:
            errors.append(
                {"row": i, "error": f"Estudiante no inscrito en la materia: {email}"}
            )
            continue

        # Get or create exercise
        exercise = exercise_cache.get(ex_name.lower())
        if not exercise:
            exercise = Exercise.objects.create(
                subject=subject, name=ex_name, order=subject.exercises.count()
            )
            exercise_cache[ex_name.lower()] = exercise

        # Update or create result
        _, was_created = StudentExerciseResult.objects.update_or_create(
            enrollment=enrollment, exercise=exercise, defaults={"status": status_val}
        )

        if was_created:
            created += 1
        else:
            updated += 1

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }
