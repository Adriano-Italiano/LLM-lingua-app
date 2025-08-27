FROM python:3.11-slim

WORKDIR /app

# 1) Zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir huggingface_hub transformers

# 2) Build args
ARG HF_TOKEN
ARG MODEL_REPO=microsoft/llmlingua-2

# 3) Pobranie modelu w czasie builda
RUN python -c "from huggingface_hub import snapshot_download; import os; snapshot_download(repo_id=os.getenv('MODEL_REPO'), local_dir='/app/model', local_dir_use_symlinks=False, token=os.getenv('HF_TOKEN'))"

# 4) Skopiuj aplikację
COPY . .

# 5) Zmienne środowiskowe
ENV PORT=8080 \
    LLM_MODEL_DIR=/app/model

# 6) Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
