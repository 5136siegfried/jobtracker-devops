FROM python:3.13-slim

WORKDIR /app

# Deps système minimaux
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Volume pour la DB SQLite
VOLUME ["/data"]

EXPOSE 8001

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["python", "app.py"]
