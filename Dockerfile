# Use official Python 3.11 slim-bullseye image
FROM python:3.11-slim-bullseye

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "authentication.main:api", "--host", "0.0.0.0", "--port", "8000", "--reload"]
