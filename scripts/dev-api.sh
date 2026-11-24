#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../services/api"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
export ENVIRONMENT="${ENVIRONMENT:-development}"
export ALLOW_DEMO_PAYMENTS="${ALLOW_DEMO_PAYMENTS:-true}"
exec uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
