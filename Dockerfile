FROM python:3.11-slim

# -- Przyspieszenie i mniejszy obraz
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/tmp/huggingface \
    TRANSFORMERS_CACHE=/tmp/huggingface/hub \
    HF_HUB_ENABLE_HF_TRANSFER=1 \
    PORT=8080

WORKDIR /app

# (opcjonalnie) narzędzia – zwykle niepotrzebne
# RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Cloud Run wymaga nasłuchu na $PORT
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
