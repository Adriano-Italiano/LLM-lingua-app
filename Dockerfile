# 1) Baza
FROM python:3.11-slim

# 2) Katalog roboczy
WORKDIR /app

# 3) Zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir huggingface_hub llmlingua uvicorn fastapi

# 4) Skopiuj aplikację
COPY . .

# 5) Pobierz model podczas builda (OFFLINE w runtime!)
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='microsoft/llmlingua-2', local_dir='/app/model', local_dir_use_symlinks=False)"

# 6) Ustaw zmienne środowiskowe
ENV PORT=8080 \
    LLM_MODEL_DIR=/app/model \
    USE_LLMLINGUA2=false

# 7) Start serwera FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
