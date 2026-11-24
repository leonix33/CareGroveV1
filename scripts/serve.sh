#!/bin/sh
set -eu

cd /app/services/api
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

python3 - <<'PY'
import time
import urllib.request

for _ in range(90):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as res:
            if res.status == 200:
                raise SystemExit(0)
    except SystemExit:
        raise
    except Exception:
        time.sleep(0.5)
raise SystemExit("API did not become ready")
PY

cd /app/apps/web
export HOSTNAME=0.0.0.0
export PORT="${PORT:-3000}"
exec node .next/standalone/server.js
