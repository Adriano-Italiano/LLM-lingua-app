# 1) Python slim
FROM python:3.11-slim

WORKDIR /app

# 2) Zależności pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) (Opcjonalnie) zainstaluj helpers używane tylko przy buildzie
RUN pip install --no-cache-dir huggingface_hub transformers

# 4) Build args:
#    - HF_TOKEN (token HuggingFace użyty TYLKO w czasie builda)
#    - MODEL_REPO (repo modelu na HF)
#      Domyślnie klasyczny llmlingua-2; jeśli chcesz MeetingBank:
#      MODEL_REPO=microsoft/llmlingua-2-xlm-roberta-large-meetingbank
ARG HF_TOKEN
ARG MODEL_REPO=microsoft/llmlingua-2

# 5) Pobierz model DO OBRAZU (offline w runtime)
#    Zapisujemy do /app/model i NIE używamy symlinków (bezpieczniej na prod)
RUN python - <<'PY'
from huggingface_hub import snapshot_download
import os
repo = os.getenv("MODEL_REPO")
token = os.getenv("HF_TOKEN")
print(f"Downloading model: {repo}")
snapshot_download(
    repo_id=repo,
    local_dir="/app/model",
    local_dir_use_symlinks=False,
    token=token
)
print("Model downloaded to /app/model")
PY

# 6) Skopiuj aplikację
COPY . .

# 7) Ustaw zmienne środowiskowe dla serwera
ENV PORT=8080 \
    LLM_MODEL_DIR=/app/model
# Jeśli używasz MeetingBank (LLMLingua-2), możesz włączyć:
# ENV USE_LLMLINGUA2=true

# 8) Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
