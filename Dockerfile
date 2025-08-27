# 1) Wybierz lekką bazę
FROM python:3.11-slim

# 2) Ustaw katalog roboczy
WORKDIR /app

# 3) Skopiuj wymagania i zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Skopiuj aplikację (FastAPI + main.py itd.)
COPY . .

# 5) Pobierz model podczas buildu (cache w obrazie, nie w runtime)
RUN python -c "from huggingface_hub import snapshot_download; import os; repo=os.getenv('MODEL_REPO','microsoft/llmlingua-2'); token=os.getenv('HF_TOKEN'); print(f'Downloading {repo}'); snapshot_download(repo_id=repo, local_dir='/app/model', local_dir_use_symlinks=False, token=token); print('✅ Model ready in /app/model')"

# 6) Ustaw zmienne środowiskowe
ENV PORT=8080 \
    LLM_MODEL_DIR=/app/model

# 7) Start FastAPI przez uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
