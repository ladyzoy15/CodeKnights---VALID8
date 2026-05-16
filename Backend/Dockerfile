FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --default-timeout=1000 --retries 10 --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --no-log-init appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["sh", "/app/scripts/run-service.sh"]
