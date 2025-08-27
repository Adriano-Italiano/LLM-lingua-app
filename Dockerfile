# 1) Baza
FROM python:3.11-slim

# 2) Katalog roboczy
WORKDIR /app

# 3) Zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Skopiuj aplikację
COPY . .

# 5) Pobierz model już w trakcie builda
RUN python - <<'PY'
from huggingface_hub import snapshot_download
import os
repo = "microsoft/llmlingua-2"   # <-- możesz zmienić na xlm-roberta-large-meetingbank
print(f"Downloading model: {repo}")
snapshot_download(
    repo_id=repo,
    local_dir="/app/model",
    local_dir_use_symlinks=False
)
print("✅ Model downloaded to /app/model")
PY

# 6) Ustaw zmienne środowiskowe
ENV PORT=8080 \
    LLM_MODEL_DIR=/app/model

# 7) Start serwera FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
