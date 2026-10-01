#!/bin/bash
# Instalare inițială Jarvis.
set -e
cd "$(dirname "$0")"
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
echo "Gata. Completează CRM_API_TOKEN în .env, apoi rulează ./run.sh"
