from celery import shared_task
from .models import EnemResult
from seletivo.models.user_data_model import UserData
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import re
import os
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_enem_pdf(enem_result_id):
    try:
        # Obter o registro EnemResult
        enem_result = EnemResult.objects.get(id=enem_result_id)
        pdf_file = enem_result.pdf_file.path

        # Função para normalizar CPF
        def normalize_cpf(cpf):
            if not cpf:
                return None
            digits = re.sub(r'\D', '', cpf)
            if len(digits) == 11:
                return digits
            return None

        # Função para extrair texto do PDF
        def extract_text_from_pdf(pdf_path):
            try:
                text = ""
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                logger.debug(f"Extracted text from PDF: {text[:1000]}...")
                return text if text.strip() else None
            except Exception as e:
                logger.error(f"Error extracting text from PDF: {str(e)}")
                return None

        # Função para extrair texto via OCR
        def extract_text_from_image(pdf_path):
            try:
                pages = convert_from_path(pdf_path)
                text = ""
                for page in pages:
                    text += pytesseract.image_to_string(page, lang='por') + "\n"
                logger.debug(f"Extracted text from image (OCR): {text[:1000]}...")
                return text if text.strip() else None
            except Exception as e:
                logger.error(f"Error extracting text via OCR: {str(e)}")
                return None

        # Função para extrair dados do texto
        def extract_data_from_text(text):
            inscription_match = re.search(r'Número de Inscrição: (\d+)', text, re.IGNORECASE)
            name_match = re.search(r'Nome: ([A-Z\s\-]+)', text, re.IGNORECASE)
            cpf_match = re.search(r'CPF: (?:(\d{3}\.\d{3}\.\d{3}-\d{2})|(\d{11}))', text, re.IGNORECASE)
            language_match = re.search(r'Língua Estrangeira:?\s*([A-Za-zê]+)', text, re.IGNORECASE)
            languages_score_match = re.search(r'Linguagens, Códigos e suas Tecnologias\s+(\d+,\d)', text, re.IGNORECASE)
            human_sciences_score_match = re.search(r'Ciências Humanas e suas Tecnologias\s+(\d+,\d)', text, re.IGNORECASE)
            natural_sciences_score_match = re.search(r'Ciências da Natureza e suas Tecnologias\s+(\d+,\d)', text, re.IGNORECASE)
            math_score_match = re.search(r'Matemática e suas Tecnologias\s+(\d+,\d)', text, re.IGNORECASE)
            essay_score_match = re.search(r'Redação\s+(\d+)', text, re.IGNORECASE)

            data = {
                'inscription_number': inscription_match.group(1) if inscription_match else None,
                'name': name_match.group(1).strip() if name_match else None,
                'cpf': cpf_match.group(1) or cpf_match.group(2) if cpf_match else None,
                'foreign_language': language_match.group(1).capitalize() if language_match else None,
                'languages_score': float(languages_score_match.group(1).replace(',', '.')) if languages_score_match else None,
                'human_sciences_score': float(human_sciences_score_match.group(1).replace(',', '.')) if human_sciences_score_match else None,
                'natural_sciences_score': float(natural_sciences_score_match.group(1).replace(',', '.')) if natural_sciences_score_match else None,
                'math_score': float(math_score_match.group(1).replace(',', '.')) if math_score_match else None,
                'essay_score': float(essay_score_match.group(1)) if essay_score_match else None
            }
            logger.debug(f"Extracted data from text: {data}")
            return data

        # Processamento do PDF
        text = extract_text_from_pdf(pdf_file)
        if not text:
            text = extract_text_from_image(pdf_file)
            if not text:
                enem_result.status = 'invalid'
                enem_result.save()
                logger.error(f"Failed to extract text from PDF for EnemResult ID {enem_result_id}")
                return

        data = extract_data_from_text(text)
        if not data['cpf'] or not data['languages_score'] or not data['human_sciences_score'] or \
           not data['natural_sciences_score'] or not data['math_score'] or not data['essay_score']:
            enem_result.status = 'invalid'
            enem_result.save()
            logger.error(f"Missing required fields in PDF for EnemResult ID {enem_result_id}")
            return

        extracted_cpf = normalize_cpf(data['cpf'])
        if not extracted_cpf:
            enem_result.status = 'invalid'
            enem_result.save()
            logger.error(f"Invalid CPF in PDF for EnemResult ID {enem_result_id}")
            return

        logger.debug(f"Checking CPF: {extracted_cpf}")
        if EnemResult.objects.filter(cpf=extracted_cpf).exclude(id=enem_result_id).exists():
            enem_result.status = 'invalid'
            enem_result.save()
            logger.error(f"CPF already registered: {extracted_cpf}")
            return

        user_data = UserData.objects.filter(cpf=extracted_cpf).first()
        if not user_data:
            enem_result.status = 'invalid'
            enem_result.save()
            logger.error(f"CPF not found in UserData: {extracted_cpf}")
            return

        # Atualizar o registro com os dados extraídos
        enem_result.inscription_number = data['inscription_number']
        enem_result.name = data['name']
        enem_result.cpf = extracted_cpf
        enem_result.foreign_language = data['foreign_language']
        enem_result.languages_score = data['languages_score']
        enem_result.human_sciences_score = data['human_sciences_score']
        enem_result.natural_sciences_score = data['natural_sciences_score']
        enem_result.math_score = data['math_score']
        enem_result.essay_score = data['essay_score']
        enem_result.status = 'processed'
        enem_result.save()

        logger.info(f"Successfully processed EnemResult ID {enem_result_id}")

    except Exception as e:
        logger.error(f"Error processing EnemResult ID {enem_result_id}: {str(e)}")
        if EnemResult.objects.filter(id=enem_result_id).exists():
            enem_result = EnemResult.objects.get(id=enem_result_id)
            enem_result.status = 'invalid'
            enem_result.save()