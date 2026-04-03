# syntax=docker/dockerfile:1
FROM python:3.11-slim

# graphviz binary required by the graphviz Python package
RUN apt-get update && apt-get install -y --no-install-recommends \
        graphviz \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install PyTorch CPU-only FIRST to avoid pip pulling the CUDA build (~2.5 GB)
RUN pip install --no-cache-dir \
        torch \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data

EXPOSE 8001 8501

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
