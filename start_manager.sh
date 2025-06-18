#!/bin/bash

APP_DIR="/opt/backoffice-api"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/manager.log"
DJANGO_PORT=7000
STATIC_DIR="$APP_DIR/static"

CELERY_WORKER="celery -A core worker --loglevel=info --logfile=$LOG_DIR/celery_worker.log --detach"
CELERY_BEAT="celery -A core beat --loglevel=info --logfile=$LOG_DIR/celery_beat.log --detach"

export DJANGO_SETTINGS_MODULE=core.settings

# CORES ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Cria diretórios e arquivos de log
mkdir -p "$LOG_DIR"
chmod 775 "$LOG_DIR"
touch "$LOG_FILE"
chmod 664 "$LOG_FILE"

# Ativa ambiente virtual
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo -e "${RED}Erro: Virtualenv não encontrado em $VENV_DIR${NC}"
    exit 1
fi

# Valida SECRET_KEY antes de rodar
if ! python3 -c "from decouple import config; assert config('SECRET_KEY', default=None)" 2>/dev/null; then
    echo -e "${RED}Erro: SECRET_KEY não está definido no .env ou está vazio.${NC}"
    exit 1
fi

# Executa collectstatic sempre
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

# Verifica se a porta está em uso
check_port() {
    if netstat -tuln | grep ":$DJANGO_PORT " > /dev/null; then
        echo -e "${RED}Erro: Porta $DJANGO_PORT já está em uso.${NC}"
        exit 1
    fi
}

# Mata processo por padrão, se necessário força kill -9
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

    # Verifica se ainda está ativo
    pids=$(pgrep -f "$pattern")
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}$name ainda ativo. Forçando com kill -9...${NC}"
        kill -9 $pids
        sleep 1

        # Verifica novamente
        if pgrep -f "$pattern" > /dev/null; then
            echo -e "${RED}Erro: Falha ao parar $name mesmo com kill -9.${NC}"
            return 1
        fi
    fi

    echo -e "${GREEN}$name parado com sucesso.${NC}"
}


start() {
    echo "Iniciando serviços..."
    cd "$APP_DIR" || { echo -e "${RED}Erro ao acessar $APP_DIR${NC}"; exit 1; }

    check_port
    prepare_static

    # Inicia Django
    if pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null; then
        echo "Django já está rodando na porta $DJANGO_PORT."
    else
        nohup python3 manage.py runserver 0.0.0.0:$DJANGO_PORT >> "$LOG_FILE" 2>&1 &
        sleep 2
        pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null && \
            echo -e "${GREEN}Django iniciado na porta $DJANGO_PORT.${NC}" || \
            { echo -e "${RED}Erro ao iniciar Django. Verifique $LOG_FILE.${NC}"; exit 1; }
    fi

    # Inicia Celery Worker
    if pgrep -f "celery -A core worker" > /dev/null; then
        echo "Celery Worker já está rodando."
    else
        $CELERY_WORKER
        sleep 2
        pgrep -f "celery -A core worker" > /dev/null && \
            echo -e "${GREEN}Celery Worker iniciado.${NC}" || \
            { echo -e "${RED}Erro ao iniciar Celery Worker.${NC}"; exit 1; }
    fi

    # Inicia Celery Beat
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
    sleep 3
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
