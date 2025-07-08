FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    build-essential \
    pkg-config \
    && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN cat requirements.txt # <-- ДОБАВЬТЕ ЭТУ СТРОКУ
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]


