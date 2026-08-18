#!/usr/bin/env bash

NATS_DIR="D:/nats-server"

NATS_SERVER="$NATS_DIR/nats-server.exe"

NATS_CONFIG="$NATS_DIR/nats-server.conf"

NATS_LOG="D:/WorkspaceStore/nats_data/nats-server.log"

NATS_PID="$NATS_DIR/nats-server.pid"


start_nats()
{
    if [ -f "$NATS_PID" ]; then
        PID=$(cat "$NATS_PID")

        if kill -0 "$PID" 2>/dev/null; then
            echo "NATS server already running (PID $PID)."
            return
        fi

        rm -f "$NATS_PID"
    fi

    "$NATS_SERVER" \
        -c "$NATS_CONFIG" \
        > "$NATS_LOG" 2>&1 &

    PID=$!
    echo "$PID" > "$NATS_PID"

    disown

    echo "NATS server started (PID $PID)."
    echo "Log: $NATS_LOG"
}


stop_nats()
{
    if [ ! -f "$NATS_PID" ]; then
        echo "NATS server is not running."
        return
    fi

    PID=$(cat "$NATS_PID")

    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        rm -f "$NATS_PID"
        echo "NATS server stopped (PID $PID)."
    else
        rm -f "$NATS_PID"
        echo "NATS server is not running."
    fi
}


status_nats()
{
    if [ ! -f "$NATS_PID" ]; then
        echo "NATS server is stopped."
        return
    fi

    PID=$(cat "$NATS_PID")

    if kill -0 "$PID" 2>/dev/null; then
        echo "NATS server is running (PID $PID)."
    else
        rm -f "$NATS_PID"
        echo "NATS server is stopped."
    fi
}


case "$1" in
    start)
        start_nats
        ;;
    stop)
        stop_nats
        ;;
    status)
        status_nats
        ;;
    restart)
        stop_nats
        start_nats
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac