#!/bin/bash

APP_DIR="/opt/backoffice-api"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/manager.log"
DJANGO_PORT=7000
STATIC_DIR="/var/www/backoffice-api/static"
MEDIA_DIR="/var/www/backoffice-api/media"
DOCKER_COMPOSE_FILE="$APP_DIR/docker-compose.yml"
REDIS_PORT=6480

CELERY_WORKER="celery -A core worker --loglevel=info --logfile=$LOG_DIR/celery_worker.log --detach"
CELERY_BEAT="celery -A core beat --loglevel=info --logfile=$LOG_DIR/celery_beat.log --detach"

export DJANGO_SETTINGS_MODULE=core.settings

# CORES ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica e sobe Redis se necessário
check_redis() {
    echo "Verificando container Redis..."

    cd "$APP_DIR" || exit 1

    if ! docker ps -a --format '{{.Names}}' | grep -q "^backoffice-redis$"; then
        echo -e "${YELLOW}Container backoffice-redis não existe. Criando com docker compose...${NC}"
        docker compose -f "$DOCKER_COMPOSE_FILE" up -d redis
        sleep 3
    fi

    if ! docker ps --format '{{.Names}}' | grep -q "^backoffice-redis$"; then
        echo -e "${RED}Erro: container backoffice-redis não está rodando.${NC}"
        exit 1
    fi

    if ! redis-cli -h localhost -p $REDIS_PORT ping | grep -q "PONG"; then
        echo -e "${RED}Erro: Não foi possível conectar ao Redis em localhost:$REDIS_PORT.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Redis está rodando e acessível.${NC}"
}

# Apenas cria diretórios se não existirem (sem reiniciar Nginx desnecessariamente)
setup_static_dirs() {
    changed=false
    if [ ! -d "$STATIC_DIR" ]; then
        sudo mkdir -p "$STATIC_DIR"
        changed=true
    fi
    if [ ! -d "$MEDIA_DIR" ]; then
        sudo mkdir -p "$MEDIA_DIR"
        changed=true
    fi

    sudo chown -R www-data:www-data "$STATIC_DIR" "$MEDIA_DIR"
    sudo chmod -R 755 "$STATIC_DIR" "$MEDIA_DIR"

    if $changed; then
        echo -e "${YELLOW}Diretórios criados. Validando configuração do Nginx...${NC}"
        sudo nginx -t >> "$LOG_FILE" 2>&1 && sudo systemctl restart nginx
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Nginx validado e reiniciado.${NC}"
        else
            echo -e "${RED}Erro ao reiniciar Nginx. Verifique $LOG_FILE.${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}Diretórios static/media já existentes e válidos.${NC}"
    fi
}

# Cria diretórios de log
mkdir -p "$LOG_DIR"
chmod 775 "$LOG_DIR"
touch "$LOG_FILE"
chmod 664 "$LOG_FILE"

# Ativa venv
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo -e "${RED}Erro: Virtualenv não encontrado em $VENV_DIR${NC}"
    exit 1
fi

# Valida SECRET_KEY
if ! python3 -c "from decouple import config; assert config('SECRET_KEY', default=None)" 2>/dev/null; then
    echo -e "${RED}Erro: SECRET_KEY não está definido no .env ou está vazio.${NC}"
    exit 1
fi

prepare_static() {
    echo "Executando collectstatic..."
    python3 manage.py collectstatic --noinput >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}collectstatic executado com sucesso.${NC}"
    else
        echo -e "${RED}Erro ao executar collectstatic. Verifique $LOG_FILE.${NC}"
        exit 1
    fi
}

check_port() {
    if netstat -tuln | grep ":$DJANGO_PORT " > /dev/null; then
        echo -e "${RED}Erro: Porta $DJANGO_PORT já está em uso.${NC}"
        exit 1
    fi
}

stop_process() {
    local pattern="$1"
    local name="$2"
    local pids
    pids=$(pgrep -f "$pattern")

    if [ -z "$pids" ]; then
        echo "$name não estava rodando."
        return 0
    fi

    echo "Parando $name..."
    kill $pids
    sleep 2

    if pgrep -f "$pattern" > /dev/null; then
        echo -e "${YELLOW}$name ainda ativo. Forçando com kill -9...${NC}"
        kill -9 $pids
        sleep 1
        if pgrep -f "$pattern" > /dev/null; then
            echo -e "${RED}Erro ao matar $name mesmo com kill -9.${NC}"
            return 1
        fi
    fi
    echo -e "${GREEN}$name parado com sucesso.${NC}"
}

start() {
    echo "Iniciando serviços..."
    cd "$APP_DIR" || exit 1

    check_redis
    setup_static_dirs
    check_port
    prepare_static

    if pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null; then
        echo "Django já está rodando."
    else
        nohup python3 manage.py runserver 0.0.0.0:$DJANGO_PORT >> "$LOG_FILE" 2>&1 &
        sleep 2
        pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null && \
            echo -e "${GREEN}Django iniciado na porta $DJANGO_PORT.${NC}" || \
            { echo -e "${RED}Erro ao iniciar Django.${NC}"; exit 1; }
    fi

    if pgrep -f "celery -A core worker" > /dev/null; then
        echo "Celery Worker já está rodando."
    else
        $CELERY_WORKER
        sleep 2
        pgrep -f "celery -A core worker" > /dev/null && \
            echo -e "${GREEN}Celery Worker iniciado.${NC}" || \
            { echo -e "${RED}Erro ao iniciar Celery Worker.${NC}"; exit 1; }
    fi

    if pgrep -f "celery -A core beat" > /dev/null; then
        echo "Celery Beat já está rodando."
    else
        $CELERY_BEAT
        sleep 2
        pgrep -f "celery -A core beat" > /dev/null && \
            echo -e "${GREEN}Celery Beat iniciado.${NC}" || \
            { echo -e "${RED}Erro ao iniciar Celery Beat.${NC}"; exit 1; }
    fi
}

stop() {
    echo "Parando serviços..."
    stop_process "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" "Django"
    stop_process "celery -A core worker" "Celery Worker"
    stop_process "celery -A core beat" "Celery Beat"
}

restart() {
    echo "Reiniciando serviços..."
    stop
    sleep 2
    start
}

status() {
    echo "Status dos serviços:"
    pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null && echo -e "${GREEN}Django: Rodando${NC}" || echo -e "${RED}Django: Parado${NC}"
    pgrep -f "celery -A core worker" > /dev/null && echo -e "${GREEN}Celery Worker: Rodando${NC}" || echo -e "${RED}Celery Worker: Parado${NC}"
    pgrep -f "celery -A core beat" > /dev/null && echo -e "${GREEN}Celery Beat: Rodando${NC}" || echo -e "${RED}Celery Beat: Parado${NC}"
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) restart ;;
    status) status ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
