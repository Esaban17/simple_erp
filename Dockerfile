# Fija Python 3.11 — resuelve PAIN_LOG #2 (versión implícita)
FROM python:3.11-slim

WORKDIR /app

# Instala cabeceras de PostgreSQL a nivel de SO — resuelve PAIN_LOG #4
# libpq-dev: cabeceras necesarias para compilar psycopg2
# gcc: compilador C requerido por psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crea los directorios de salida — resuelve PAIN_LOG #11
RUN mkdir -p facturas albaranes

EXPOSE 8000
