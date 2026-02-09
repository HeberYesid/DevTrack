import filetype
from rest_framework.exceptions import ValidationError


def validate_file_content(file_obj, allowed_types=["csv"]):
    """
    Validates file content using magic bytes.
    allowed_types: list of allowed extensions (e.g. ['csv', 'pdf', 'zip', 'jpg', 'png']).
    Note: 'csv' is treated as plain text inspection.
    """
    # Leer encabezado del archivo
    pos = file_obj.tell()
    file_obj.seek(0)
    head = file_obj.read(2048)
    file_obj.seek(pos)

    # Detectar tipo con filetype
    kind = filetype.guess(head)

    # 1. Rechazar explícitamente ejecutables (Windows PE, Mac Mach-O, Linux ELF)
    if kind and kind.extension in ["exe", "dll", "elf", "mach", "class", "jar"]:
        raise ValidationError(
            f"Archivo malicioso detectado ({kind.extension}). No se permiten ejecutables."
        )

    # Check for Windows PE header manually (MZ) just in case
    if head.startswith(b"MZ"):
        raise ValidationError("Archivo malicioso detectado (MZ Header).")

    # Si no se define allowed_types, solo bloqueamos ejecutables
    if not allowed_types:
        return

    # 2. Validar CSV (Texto plano)
    if "csv" in allowed_types:
        # Para CSV, esperamos que kind sea None (texto) o 'csv' si filetype lo soporta
        # Si filetype detecta otro binario (ej: zip, pdf, jpg) cuando solo esperamos CSV -> Error
        if kind and kind.extension not in allowed_types:
            # Si permitimos mixed types (ej: ['csv', 'pdf']), y detecta pdf, está bien.
            # Chequeamos si la extensión detectada está permitida.
            if kind.extension not in allowed_types:
                raise ValidationError(
                    f"Tipo de archivo no válido: {kind.extension}. Se esperaban: {allowed_types}"
                )

        # Validación extra para texto (CSV)
        # Si no detectó tipo binario, verificamos que sea texto
        if kind is None:
            try:
                head.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    head.decode("latin-1")
                except UnicodeDecodeError:
                    # Si contiene null bytes es muy sospechoso para un CSV
                    if b"\x00" in head:
                        raise ValidationError(
                            "El archivo parece ser binario, no un CSV válido."
                        )

    # 3. Validar otros tipos binarios (PDF, ZIP, IMG)
    # Si detectamos un tipo, verificamos que esté en allowed_types
    if kind and kind.extension not in allowed_types and "csv" not in allowed_types:
        # Si 'csv' estaba en allowed, ya lo manejamos arriba con la logica mixta.
        # Si NO estaba 'csv', entonces rechazamos estrictamente.
        raise ValidationError(
            f"Tipo de archivo detectado ({kind.extension}) no permitido. Permitidos: {allowed_types}"
        )

    # Fallback para PDF si filetype falla pero empieza con %PDF
    if "pdf" in allowed_types and not kind and head.startswith(b"%PDF-"):
        return

    return True
