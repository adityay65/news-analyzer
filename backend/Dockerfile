FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and setuptools first
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python packages from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip check  # Verify no dependency conflicts

# Verify spaCy installation before model download
RUN python -c "import spacy; print(f'spaCy version: {spacy.__version__}')" && \
    python -m spacy download en_core_web_sm

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
