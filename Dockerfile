# obraz bazowy
FROM python:3.11-slim

# ustawienia środowiska
ENV PYTHONUNBUFFERED=1

# katalog roboczy
WORKDIR /app

# instalacja zależności systemowych
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# skopiuj pliki
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# port dla Cloud Run
ENV PORT=8080

# uruchamianie serwera
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
