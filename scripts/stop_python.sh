#!/bin/bash

# Find and count Python3 processes
PYTHON_PROCESSES=$(pgrep python3)
PROCESS_COUNT=$(echo "$PYTHON_PROCESSES" | grep -c "^")

if [ -z "$PYTHON_PROCESSES" ]; then
    echo "No Python3 processes found."
    exit 0
fi

echo "Found $PROCESS_COUNT Python3 process(es)."
echo "Killing Python3 processes..."

# Kill all Python3 processes
pkill -9 python3

# Check if kill was successful
if [ $? -eq 0 ]; then
    echo "Successfully killed all Python3 processes."
else
    echo "Error: Failed to kill some processes. Try running with sudo."
fi