# ── Backend Dockerfile ──────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY app/ ./app/
COPY core/ ./core/
COPY models/ ./models/
COPY repositories/ ./repositories/
COPY services/ ./services/
COPY utils/ ./utils/
COPY data/ ./data/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
