#!/usr/bin/env bash


# Set up the development environment.
set -euo pipefail

cd "$(dirname "$0")/.."
PYTHON=${PYTHON:-python3}

if [ ! -d .venv ]; then
    echo "Creating virtual environment with $($PYTHON --version)"
    "$PYTHON" -m venv .venv
fi

.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

mkdir -p instance logs backups data/raw data/processed reports

echo "Setup done. Run:"
echo "  source .venv/bin/activate"
echo "  flask --app app run --debug"
