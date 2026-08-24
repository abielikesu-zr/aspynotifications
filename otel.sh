#!/usr/bin/env bash

get_user_lower() {
  printf '%s' "${USER:-$USERNAME}" | tr '[:upper:]' '[:lower:]'
}

export USER="$(get_user_lower)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/.otel.${USER}.env"


start_otel()
{
    if [ -f "$OTEL_PID" ]; then
        PID=$(cat "$OTEL_PID")

        if kill -0 "$PID" 2>/dev/null; then
            echo "OTel Desktop Viewer already running (PID $PID)."
            return
        fi

        rm -f "$OTEL_PID"
    fi

    "$OTEL_BIN" > "$OTEL_LOG" 2>&1 &

    PID=$!
    echo "$PID" > "$OTEL_PID"

    disown

    echo "OTel Desktop Viewer started (PID $PID)."
    echo "Log: $OTEL_LOG"
}


stop_otel()
{
    if [ ! -f "$OTEL_PID" ]; then
        echo "OTel Desktop Viewer is not running."
        return
    fi

    PID=$(cat "$OTEL_PID")

    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$OTEL_PID"
        echo "OTel Desktop Viewer stopped (PID $PID)."
    else
        rm -f "$OTEL_PID"
        echo "OTel Desktop Viewer is not running."
    fi
}


status_otel()
{
    if [ ! -f "$OTEL_PID" ]; then
        echo "OTel Desktop Viewer is stopped."
        return
    fi

    PID=$(cat "$OTEL_PID")

    if kill -0 "$PID" 2>/dev/null; then
        echo "OTel Desktop Viewer is running."
        echo "PID:  $PID"
        echo "Web:  $OTEL_URL"
        echo "Log:  $OTEL_LOG"
    else
        rm -f "$OTEL_PID"
        echo "OTel Desktop Viewer is stopped."
    fi
}


case "$1" in
    start)
        start_otel
        ;;
    stop)
        stop_otel
        ;;
    status)
        status_otel
        ;;
    restart)
        stop_otel
        start_otel
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac