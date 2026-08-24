#!/usr/bin/env bash

get_user_lower() {
  printf '%s' "${USER:-$USERNAME}" | tr '[:upper:]' '[:lower:]'
}

export USER="$(get_user_lower)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/.lnav.${USER}.env"


start_lnav()
{
    if pgrep -f "$LNAV_BIN" > /dev/null 2>&1; then
        PID=$(pgrep -f "$LNAV_BIN" | head -1)
        echo "lnav already running (PID $PID)."
        return
    fi

    LOG_SOURCES=()

    while IFS= read -r name; do
        value="${!name}"

        if [ -z "$value" ]; then
            continue
        fi

        if [[ "$name" == *_LOG_DIR ]]; then
            LOG_SOURCES+=("$value")

        elif [[ "$name" == *_LOG ]]; then
            LOG_SOURCES+=("$value")
        fi

    done < <(compgen -A variable)

    if [ ${#LOG_SOURCES[@]} -eq 0 ]; then
        echo "No *_LOG or *_LOG_DIR variables found."
        return 1
    fi

    echo "Found ${#LOG_SOURCES[@]} log sources:"
    echo

    for source in "${LOG_SOURCES[@]}"; do
        if [ -d "$source" ]; then
            echo "✓ DIR  $source"
        elif [ -f "$source" ]; then
            echo "✓ FILE $source"
        else
            echo "✗ NOT FOUND: $source"
        fi
    done

    echo
    echo "Starting lnav..."
    echo "Press 'q' to exit."

    "$LNAV_BIN" "${LOG_SOURCES[@]}"
}

stop_lnav()
{
    if [ ! -f "$LNAV_PID" ]; then
        echo "lnav is not running."
        return
    fi

    PID=$(cat "$LNAV_PID")

    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$LNAV_PID"
        echo "lnav stopped (PID $PID)."
    else
        rm -f "$LNAV_PID"
        echo "lnav is not running."
    fi
}


status_lnav()
{
    if [ ! -f "$LNAV_PID" ]; then
        echo "lnav is stopped."
        return
    fi

    PID=$(cat "$LNAV_PID")

    if kill -0 "$PID" 2>/dev/null; then
        echo "lnav is running (PID $PID)."
    else
        rm -f "$LNAV_PID"
        echo "lnav is stopped."
    fi
}


case "$1" in
    start)
        start_lnav
        ;;
    stop)
        stop_lnav
        ;;
    status)
        status_lnav
        ;;
    restart)
        stop_lnav
        start_lnav
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac