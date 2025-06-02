from rest_framework import serializers
from .models import EnemResult
from seletivo.models.user_data_model import UserData
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import re
import os
import logging

logger = logging.getLogger(__name__)

class EnemResultSerializer(serializers.ModelSerializer):
    pdf_file = serializers.FileField()

    class Meta:
        model = EnemResult
        fields = [
            'id', 'inscription_number', 'name', 'cpf', 'foreign_language',
            'languages_score', 'human_sciences_score', 'natural_sciences_score',
            'math_score', 'essay_score', 'pdf_file', 'status', 'created_at'
        ]
        read_only_fields = [
            'inscription_number', 'name', 'cpf', 'foreign_language',
            'languages_score', 'human_sciences_score', 'natural_sciences_score',
            'math_score', 'essay_score', 'status', 'created_at'
        ]

    def validate_pdf_file(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Apenas arquivos PDF são permitidos.")
        return value

    def normalize_cpf(self, cpf):
        if not cpf:
            return None
        digits = re.sub(r'\D', '', cpf)  # Remove qualquer caractere não numérico
        if len(digits) == 11:
            return digits  # Retorna apenas dígitos, sem pontuação
        return None

    def extract_text_from_pdf(self, pdf_file):
        try:
            text = ""
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            logger.debug(f"Extracted text from PDF: {text[:1000]}...")
            return text if text.strip() else None
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise serializers.ValidationError(f"Erro ao extrair texto do PDF: {str(e)}")

    def extract_text_from_image(self, pdf_path):
        try:
            pages = convert_from_path(pdf_path)
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page, lang='por') + "\n"
            logger.debug(f"Extracted text from image (OCR): {text[:1000]}...")
            return text if text.strip() else None
        except Exception as e:
            logger.error(f"Error extracting text via OCR: {str(e)}")
            raise serializers.ValidationError(f"Erro ao extrair texto via OCR: {str(e)}")

    def extract_data_from_text(self, text):
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
            'inscription_number': inscription_match.group(1) if inscription_match else '',
            'name': name_match.group(1).strip() if name_match else '',
            'cpf': cpf_match.group(1) or cpf_match.group(2) if cpf_match else None,
            'foreign_language': language_match.group(1).capitalize() if language_match else '',
            'languages_score': float(languages_score_match.group(1).replace(',', '.')) if languages_score_match else 0.0,
            'human_sciences_score': float(human_sciences_score_match.group(1).replace(',', '.')) if human_sciences_score_match else 0.0,
            'natural_sciences_score': float(natural_sciences_score_match.group(1).replace(',', '.')) if natural_sciences_score_match else 0.0,
            'math_score': float(math_score_match.group(1).replace(',', '.')) if math_score_match else 0.0,
            'essay_score': float(essay_score_match.group(1)) if essay_score_match else 0.0
        }
        logger.debug(f"Extracted data from text: {data}")
        return data

    def create(self, validated_data):
        pdf_file = validated_data.pop('pdf_file')
        temp_pdf_path = None
        try:
            temp_pdf_path = os.path.join('/tmp', pdf_file.name)
            with open(temp_pdf_path, 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            text = self.extract_text_from_pdf(pdf_file)
            if not text:
                text = self.extract_text_from_image(temp_pdf_path)
                if not text:
                    raise serializers.ValidationError("Não foi possível extrair texto do PDF.")

            data = self.extract_data_from_text(text)
            if not data['cpf']:
                raise serializers.ValidationError("CPF não encontrado no PDF.")

            extracted_cpf = self.normalize_cpf(data['cpf'])
            if not extracted_cpf:
                raise serializers.ValidationError("CPF inválido no PDF.")

            logger.debug(f"Checking CPF: {extracted_cpf}")
            if EnemResult.objects.filter(cpf=extracted_cpf).exists():
                raise serializers.ValidationError(f"CPF já registrado no sistema: {extracted_cpf}")

            user_data = UserData.objects.filter(cpf=extracted_cpf).first()
            if not user_data:
                raise serializers.ValidationError(f"CPF não cadastrado no sistema: {extracted_cpf}")

            validated_data.update({
                'inscription_number': data['inscription_number'],
                'name': data['name'],
                'cpf': extracted_cpf,  # Armazena sem pontuação
                'foreign_language': data['foreign_language'],
                'languages_score': data['languages_score'],
                'human_sciences_score': data['human_sciences_score'],
                'natural_sciences_score': data['natural_sciences_score'],
                'math_score': data['math_score'],
                'essay_score': data['essay_score'],
                'pdf_file': pdf_file,
                'status': 'fileSent'  # Define o status inicial como "Arquivo Enviado"
            })

            return self.Meta.model.objects.create(**validated_data)

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise serializers.ValidationError(f"Erro ao processar PDF: {str(e)}")
        finally:
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

class EnemResultDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = EnemResult
        fields = [
            'id', 'user', 'inscription_number', 'name', 'cpf', 'foreign_language',
            'languages_score', 'human_sciences_score', 'natural_sciences_score',
            'math_score', 'essay_score', 'pdf_file', 'status', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'inscription_number', 'name', 'cpf', 'foreign_language',
            'languages_score', 'human_sciences_score', 'natural_sciences_score',
            'math_score', 'essay_score', 'pdf_file', 'created_at'
        ]