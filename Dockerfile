FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# LibreOffice + fontconfig (para cache de fuentes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-calc \
    fontconfig \
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tu app
COPY . .

# --- Montserrat fonts (desde repo) ---
# Asegúrate de tener /fonts en el repo
RUN mkdir -p /usr/local/share/fonts/custom
COPY fonts/ /usr/local/share/fonts/custom/
RUN fc-cache -f -v

CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
