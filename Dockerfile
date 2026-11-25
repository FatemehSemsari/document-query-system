FROM python:3.12-slim

# Python environment settings

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Application directory

WORKDIR /app

# Install system dependencies

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip

RUN python -m pip install --no-cache-dir --upgrade pip

# Install CPU-only PyTorch

RUN python -m pip install --no-cache-dir torch \
    --index-url https://download.pytorch.org/whl/cpu

# Install project dependencies

COPY requirements-docker.txt .

RUN python -m pip install --no-cache-dir \
    -r requirements-docker.txt \
    && python -m pip check

# Copy project source code

COPY . .

# Create persistent data directory

RUN mkdir -p /data /models

# Application port

EXPOSE 8000

# Apply migrations and start Django

CMD ["sh", "-c", "python manage.py migrate --noinput && exec python manage.py runserver 0.0.0.0:8000 --noreload"]