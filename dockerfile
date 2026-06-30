FROM python:3.12-slim

# libs de sistema que o opencv (cv2) e o pillow precisam
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# deps primeiro (aproveita cache de layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# só o código entra na imagem
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY config.py .

# default: treina. Dá pra sobrescrever no run (ver abaixo)
CMD ["python", "scripts/treinar_otimizado.py"]