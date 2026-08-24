#!/usr/bin/env bash

get_user_lower() {
    printf '%s' "${USER:-$USERNAME}" | tr '[:upper:]' '[:lower:]'
}

export USER="$(get_user_lower)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LNAV_ENV="$SCRIPT_DIR/.lnav.${USER}.env"

if [ ! -f "$LNAV_ENV" ]; then
    echo "lnav env not found: $LNAV_ENV"
    exit 1
fi

source "$LNAV_ENV"


get_log_name()
{
    echo "$1" | tr '-' '_'
}


get_env_name()
{
    echo "$1" | tr '[:lower:]-' '[:upper:]_'
}


get_pid_file()
{
    local service="$1"
    local name

    name=$(get_log_name "$service")

    echo "$WORKSPACE_DIR/.devrun/${name}.pid"
}


get_log_file()
{
    local service="$1"
    local name

    name=$(get_log_name "$service")

    echo "$WORKSPACE_DIR/aspynotifications/${name}.log"
}


start_service()
{
    local service="$1"

    if [ -z "$service" ]; then
        echo "Service name is required."
        exit 1
    fi

    local log_file
    local pid_file
    local pid

    log_file=$(get_log_file "$service")
    pid_file=$(get_pid_file "$service")

    mkdir -p "$(dirname "$pid_file")"
    mkdir -p "$(dirname "$log_file")"

    touch "$log_file"

    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")

        if kill -0 "$pid" 2>/dev/null; then
            echo "$service already running (PID $pid)."
            return
        fi

        rm -f "$pid_file"
    fi

    "$service" start --log-format json \
        1>"$log_file" \
        2>&1 &

    pid=$!

    echo "$pid" > "$pid_file"

    disown

    echo "$service started."
    echo "PID: $pid"
    echo "Log: $log_file"
}


stop_service()
{
    local service="$1"

    if [ -z "$service" ]; then
        echo "Service name is required."
        exit 1
    fi

    local pid_file
    local pid

    pid_file=$(get_pid_file "$service")

    pid=$(cat "$pid_file")

    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        rm -f "$pid_file"
        echo "$service stopped (PID $pid)."
    else
        rm -f "$pid_file"
        echo "$service is not running."
    fi

}


status_service()
{
    local service="$1"

    if [ -z "$service" ]; then
        echo "Service name is required."
        exit 1
    fi

    local pid_file
    local log_file
    local pid

    pid_file=$(get_pid_file "$service")
    log_file=$(get_log_file "$service")

    if [ ! -f "$pid_file" ]; then
        echo "$service is stopped."
        return
    fi

    pid=$(cat "$pid_file")

    if kill -0 "$pid" 2>/dev/null; then
        echo "$service is running."
        echo "PID: $pid"
        echo "Log: $log_file"
    else
        rm -f "$pid_file"
        echo "$service is stopped."
    fi
}


case "$1" in
    start)
        start_service "$2"
        ;;
    stop)
        stop_service "$2"
        ;;
    status)
        status_service "$2"
        ;;
    restart)
        stop_service "$2"
        start_service "$2"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart} <service>"
        exit 1
        ;;
esac