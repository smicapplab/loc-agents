#!/bin/bash
# Script to run Job-Seek agent commands

# Ensure we are in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Run the command
PYTHONPATH=. ./job-seek/venv/bin/python job-seek/main.py "$@"
