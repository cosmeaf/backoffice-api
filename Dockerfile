FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instala dependências do sistema para possíveis builds de pacotes Python
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    libffi-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn>=20.1.0

# Copia o restante da aplicação
COPY . .

# Expõe porta para Gunicorn
EXPOSE 7000

# Comando padrão para produção (Gunicorn)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:7000"]
