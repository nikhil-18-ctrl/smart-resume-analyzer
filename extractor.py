import os
import tempfile
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document


def extract_text_from_resume(file):
    """
    Extracts text from an uploaded resume file (PDF or DOCX).
    Works safely with Flask FileStorage objects.
    """

    if not file or not file.filename:
        return ""

    filename = file.filename.lower()

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as tmp:
        file.save(tmp.name)
        temp_path = tmp.name

    try:
        # PDF extraction
        if filename.endswith(".pdf"):
            text = extract_pdf_text(temp_path)

        # DOCX extraction
        elif filename.endswith(".docx"):
            doc = Document(temp_path)
            text = " ".join(p.text for p in doc.paragraphs)

        else:
            text = ""

    finally:
        # Always clean up the temp file
        os.remove(temp_path)

    return text.strip()
