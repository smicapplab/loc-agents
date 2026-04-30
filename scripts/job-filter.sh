#!/bin/bash
# Script to run Job-Filter agent process

# Ensure we are in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Run the process
PYTHONPATH=.:job-filter ./job-seek/venv/bin/python job-filter/main.py "$@"
