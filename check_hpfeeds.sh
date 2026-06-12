#!/bin/bash
# Check if hpfeeds broker on localhost:10000 is responding
# If connection fails, trigger restart script

set -e

TIMEOUT=5
HOST="localhost"
PORT=10000
RESTART_SCRIPT="./restart.sh"

# Try to connect with timeout
if timeout "${TIMEOUT}" nc -z "${HOST}" "${PORT}" 2>/dev/null; then
    # Connection successful
    exit 0
else
    # Connection failed - trigger restart
    echo "$(date): Failed to connect to ${HOST}:${PORT}, triggering restart"

    # Check if restart script exists and is executable
    if [ -f "${RESTART_SCRIPT}" ]; then
        if [ -x "${RESTART_SCRIPT}" ]; then
            "${RESTART_SCRIPT}"
        else
            echo "Error: ${RESTART_SCRIPT} is not executable"
            exit 1
        fi
    else
        echo "Error: ${RESTART_SCRIPT} not found"
        exit 1
    fi
fi
