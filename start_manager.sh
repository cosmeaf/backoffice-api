#!/bin/bash

# Define paths and settings
APP_DIR="/opt/backoffice-api"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/manager.log"
DJANGO_PORT=7000
CELERY_WORKER="celery -A core worker --loglevel=info --logfile=$LOG_DIR/celery_worker.log --detach"
CELERY_BEAT="celery -A core beat --loglevel=info --logfile=$LOG_DIR/celery_beat.log --detach"

# Ensure log directory exists with correct permissions
mkdir -p "$LOG_DIR"
chmod 775 "$LOG_DIR"
touch "$LOG_FILE"
chmod 664 "$LOG_FILE"

# Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Erro: Virtualenv não encontrado em $VENV_DIR"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if netstat -tuln | grep ":$DJANGO_PORT " > /dev/null; then
        echo "Erro: Porta $DJANGO_PORT já está em uso."
        exit 1
    fi
}

# Function to gracefully stop a process
stop_process() {
    local pattern="$1"
    local name="$2"
    local pids
    pids=$(pgrep -f "$pattern")

    if [ -z "$pids" ]; then
        echo "$name não estava rodando."
        return 0
    fi

    # Try SIGTERM first
    pkill -f "$pattern"
    sleep 2

    # Check if process is still running
    if pgrep -f "$pattern" > /dev/null; then
        echo "Aviso: $name não terminou com SIGTERM, tentando SIGKILL..."
        pkill -9 -f "$pattern"
        sleep 1
        if pgrep -f "$pattern" > /dev/null; then
            echo "Erro: Falha ao parar $name mesmo com SIGKILL."
            return 1
        else
            echo "$name parado com SIGKILL."
            return 0
        fi
    else
        echo "$name parado com sucesso."
        return 0
    fi
}

start() {
    echo "Iniciando Django e Celery..."
    cd "$APP_DIR" || { echo "Erro: Falha ao acessar $APP_DIR"; exit 1; }

    # Check port
    check_port

    # Start Django
    if pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null; then
        echo "Django já está rodando na porta $DJANGO_PORT."
    else
        nohup python3 manage.py runserver 0.0.0.0:$DJANGO_PORT >> "$LOG_FILE" 2>&1 &
        sleep 2
        if pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null; then
            echo "Django iniciado na porta $DJANGO_PORT."
        else
            echo "Erro: Falha ao iniciar Django. Verifique $LOG_FILE."
            exit 1
        fi
    fi

    # Start Celery Worker
    if pgrep -f "celery -A core worker" > /dev/null; then
        echo "Celery Worker já está rodando."
    else
        $CELERY_WORKER
        sleep 2
        if pgrep -f "celery -A core worker" > /dev/null; then
            echo "Celery Worker iniciado. Logs em $LOG_DIR/celery_worker.log."
        else
            echo "Erro: Falha ao iniciar Celery Worker. Verifique $LOG_DIR/celery_worker.log."
            exit 1
        fi
    fi

    # Start Celery Beat
    if pgrep -f "celery -A core beat" > /dev/null; then
        echo "Celery Beat já está rodando."
    else
        $CELERY_BEAT
        sleep 2
        if pgrep -f "celery -A core beat" > /dev/null; then
            echo "Celery Beat iniciado. Logs em $LOG_DIR/celery_beat.log."
        else
            echo "Erro: Falha ao iniciar Celery Beat. Verifique $LOG_DIR/celery_beat.log."
            exit 1
        fi
    fi
}

stop() {
    echo "Parando Django e Celery..."
    stop_process "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" "Django"
    stop_process "celery -A core worker" "Celery Worker"
    stop_process "celery -A core beat" "Celery Beat"
}

restart() {
    echo "Reiniciando Django e Celery..."
    stop
    sleep 2
    start
}

status() {
    echo "Status dos serviços:"
    pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null && echo "Django: Rodando" || echo "Django: Parado"
    pgrep -f "celery -A core worker" > /dev/null && echo "Celery Worker: Rodando" || echo "Celery Worker: Parado"
    pgrep -f "celery -A core beat" > /dev/null && echo "Celery Beat: Rodando" || echo "Celery Beat: Parado"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0