FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости для сборки aiohttp
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
