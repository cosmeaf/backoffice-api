from celery import shared_task
import os
from .utils.generate_docx import generate_docx_and_pdf

@shared_task
def generate_recommendation_letter_task(data):
    """Generate recommendation letter as a PDF and save it temporarily."""
    temp_docx_path, pdf_path, pdf_filename = generate_docx_and_pdf(data)
    
    # Read PDF content
    with open(pdf_path, 'rb') as pdf_file:
        pdf_content = pdf_file.read()

    # Clean up temporary files
    os.remove(temp_docx_path)
    os.remove(pdf_path)

    # Return PDF content and filename
    return {'pdf_content': pdf_content, 'pdf_filename': pdf_filename}