#!/bin/bash
# Script to synchronize resume PDF with structured profile files

# Ensure we are in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Run the sync command
PYTHONPATH=. ./job-seek/venv/bin/python job-seek/main.py sync "$@"
