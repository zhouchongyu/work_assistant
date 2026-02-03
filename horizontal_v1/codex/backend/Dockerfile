FROM python:3.11-slim

WORKDIR /app

# 纯 Python 依赖
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend

ENV WA_DATABASE_URL=sqlite+aiosqlite:////app/wa-dev.db \
    WA_REDIS_URL=redis://redis:6379/0 \
    WA_JWT_SECRET=dev-secret \
    WA_GRAPH_TENANT_ID=dummy-tenant \
    WA_GRAPH_CLIENT_ID=dummy-client \
    WA_GRAPH_CLIENT_SECRET=dummy-secret \
    WA_GRAPH_DRIVE_ID=dummy-drive \
    WA_GRAPH_SUPPLY_PATH=/ \
    WA_THIRD_PARTY_ANALYZE_URL=http://third-party:9000 \
    WA_CALLBACK_BASE_URL=http://backend:8000 \
    WA_THIRD_PARTY_CALLBACK_TOKEN=dev-token \
    WA_DIFY_API_BASE_URL=http://dify:9510 \
    WA_DIFY_API_KEY=dev-key

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
