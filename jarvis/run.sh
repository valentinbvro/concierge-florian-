#!/bin/bash
# Pornește Jarvis (Faza 0).
cd "$(dirname "$0")"
exec ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "${JARVIS_PORT:-8001}"
