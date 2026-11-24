FROM node:22-bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 python3-venv \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY services/api/requirements.txt /app/services/api/requirements.txt
RUN python3 -m venv /opt/venv \
  && /opt/venv/bin/pip install --no-cache-dir -r /app/services/api/requirements.txt

COPY apps/web /app/apps/web
WORKDIR /app/apps/web
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm ci && npm run build \
  && cp -r public .next/standalone/public \
  && mkdir -p .next/standalone/.next \
  && cp -r .next/static .next/standalone/.next/static

WORKDIR /app
COPY services/api /app/services/api
COPY scripts/serve.sh /app/scripts/serve.sh
RUN chmod +x /app/scripts/serve.sh

ENV PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production \
    ALLOW_DEMO_PAYMENTS=false \
    PYTHONUNBUFFERED=1

EXPOSE 10000
CMD ["/app/scripts/serve.sh"]
