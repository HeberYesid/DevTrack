import os
from google import genai
from django.conf import settings
import pypdf
import docx

def extract_text_from_file(file_obj, file_name):
    """
    Extracts text from PDF or DOCX files (file-like objects).
    """
    if not file_obj:
        return None
    
    ext = os.path.splitext(file_name)[1].lower()
    text = ""
    
    try:
        if ext == '.pdf':
            reader = pypdf.PdfReader(file_obj)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif ext in ['.docx', '.doc']:
            doc = docx.Document(file_obj)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            return None # Unsupported format for text extraction
            
        return text.strip()[:2000] # Limit to first 2000 chars to avoid token limits
    except Exception as e:
        print(f"Error extracting text from {file_name}: {e}")
        return None

def generate_grading_feedback(exercise_description, student_email, status, current_comment=None, submission_file=None, submission_file_name=None):
    """
    Generates feedback for a student submission using Google Gemini API.
    
    Args:
        exercise_description (str): Description of the exercise.
        student_email (str): Email of the student (used for context, but PII should be minimized).
        status (str): Current status (GREEN, YELLOW, RED).
        current_comment (str, optional): Existing comment if any.
        submission_file (file-like, optional): The student's submission file object.
        submission_file_name (str, optional): The name of the file (for extension detection).
        
    Returns:
        str: Generated feedback.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not configured."

    client = genai.Client(api_key=api_key)

    # Map status to readable text
    status_map = {
        'GREEN': 'Excellent/Passed (Verde)',
        'YELLOW': 'Needs Improvement (Amarillo)',
        'RED': 'Failed/Incomplete (Rojo)'
    }
    readable_status = status_map.get(status, status)

    # Extract text from submission if available
    submission_text = ""
    if submission_file and submission_file_name:
        extracted = extract_text_from_file(submission_file, submission_file_name)
        if extracted:
            submission_text = f"\n    - Contenido de la Entrega (Extracto): {extracted}"

    prompt = f"""
    Actúa como un profesor de apoyo pero estricto.
    Genera un comentario de retroalimentación corto y constructivo (máximo 50 palabras) para un estudiante, EN ESPAÑOL.
    
    Contexto:
    - Título/Descripción del Ejercicio: {exercise_description}
    - Nota/Estado: {readable_status}
    {f'- Comentario Anterior: {current_comment}' if current_comment else ''}{submission_text}
    
    Instrucciones:
    1. Si la nota es ROJO o AMARILLO, menciona explícitamente el tema del ejercicio (basado en la descripción) y sugiere repasar esos conceptos específicos.
    2. NUNCA uses marcadores de posición como "[insertar tema]" o "[tema específico]". Debes extraer el tema directamente de la descripción del ejercicio provista.
    3. Si hay contenido de la entrega, úsalo para señalar el error específico. Si no, basa tu consejo en los requisitos del ejercicio.
    4. Mantén el tono profesional y alentador.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating feedback: {str(e)}"

def grade_submission(exercise_description, submission_file=None, submission_file_name=None, submission_text=None):
    """
    Analyzes a student submission and assigns a grade (GREEN, YELLOW, RED) with feedback.
    
    Args:
        exercise_description (str): Description of the exercise.
        submission_file (file-like, optional): The student's submission file object.
        submission_file_name (str, optional): The name of the file.
        submission_text (str, optional): Text submission from the student.
        
    Returns:
        dict: {'status': 'GREEN'|'YELLOW'|'RED', 'feedback': str}
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {'status': 'YELLOW', 'feedback': "Error: GEMINI_API_KEY not configured."}

    client = genai.Client(api_key=api_key)

    # Prepare content to grade
    content_to_grade = ""
    
    if submission_text:
        content_to_grade += f"Contenido de Texto:\n{submission_text}\n\n"

    if submission_file and submission_file_name:
        extracted = extract_text_from_file(submission_file, submission_file_name)
        if extracted:
            content_to_grade += f"Contenido del Archivo (Extracto):\n{extracted}"
        else:
            content_to_grade += " (No se pudo extraer texto del archivo adjunto)."
    
    if not content_to_grade.strip():
        content_to_grade = "No se proporcionó contenido visible para calificar."

    prompt = f"""
    Actúa como un profesor evaluando una tarea.
    Tu objetivo es calificar la entrega del estudiante basándote en la descripción del ejercicio.
    
    Contexto:
    - Descripción del Ejercicio: {exercise_description}
    - {content_to_grade}
    
    Instrucciones:
    1. Analiza si la entrega cumple con lo solicitado en la descripción.
    2. Asigna una calificación:
       - 'GREEN': Si cumple correctamente con todos o la mayoría de los requisitos.
       - 'YELLOW': Si cumple parcialmente pero tiene errores o faltantes notables.
       - 'RED': Si no cumple, es incorrecto, o está muy incompleto.
    3. Genera un comentario de retroalimentación corto (máximo 40 palabras) en ESPAÑOL justificando la nota.
    
    Formato de Respuesta (SOLO JSON):
    {{
        "status": "GREEN" | "YELLOW" | "RED",
        "feedback": "Tu comentario aquí"
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        import json
        result = json.loads(response.text)
        
        # Validate status
        if result.get('status') not in ['GREEN', 'YELLOW', 'RED']:
            result['status'] = 'YELLOW' # Default fallback
            
        return result
    except Exception as e:
        print(f"AI Grading Error: {e}")
        return {'status': 'YELLOW', 'feedback': "No se pudo calificar automáticamente. Por favor revisa manualmente."}

