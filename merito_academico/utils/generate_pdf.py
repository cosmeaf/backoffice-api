import os
import uuid
import subprocess
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def convert_to_pdf(docx_path):
    """Converte o DOCX para PDF usando LibreOffice."""
    logger.info(f"Iniciando conversão para PDF: {docx_path}")
    
    # Garante que o diretório MEDIA_ROOT existe
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    # Nome do PDF com UUID
    pdf_filename = f'recommendation_letter_{uuid.uuid4()}.pdf'
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
    
    # Nome esperado do PDF gerado pelo LibreOffice
    expected_pdf = os.path.join(settings.MEDIA_ROOT, os.path.splitext(os.path.basename(docx_path))[0] + '.pdf')
    
    try:
        # Executa a conversão
        result = subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf',
            docx_path, '--outdir', settings.MEDIA_ROOT
        ], check=True, capture_output=True, text=True)
        logger.info(f"Saída do LibreOffice: {result.stdout}")
        
        # Verifica se o PDF foi gerado e renomeia
        if os.path.exists(expected_pdf):
            os.rename(expected_pdf, pdf_path)
            logger.info(f"PDF renomeado: {expected_pdf} -> {pdf_path}")
        else:
            logger.error(f"PDF não encontrado: {expected_pdf}")
            raise Exception("Falha na geração do PDF")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Falha na conversão para PDF: {e.stderr}")
        raise Exception(f"Falha ao converter para PDF: {e.stderr}")

    # Verifica se o PDF final existe
    if not os.path.exists(pdf_path):
        logger.error(f"PDF não encontrado: {pdf_path}")
        raise Exception("Falha na geração do PDF")

    logger.info(f"PDF gerado: {pdf_path}")
    return pdf_path