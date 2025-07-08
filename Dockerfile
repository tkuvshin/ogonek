FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости, необходимые для сборки пакетов Python,
# включая те, которые нужны aiohttp, cryptography (используется некоторыми библиотеками ) и т.д.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
