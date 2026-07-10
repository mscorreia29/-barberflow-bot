FROM python:3.11-slim

# Instalar Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar dependências Python primeiro
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar dependências Node.js
COPY whatsapp-bridge/package*.json ./whatsapp-bridge/
RUN cd whatsapp-bridge && npm install

# Copiar código
COPY . .

# Porta da API
EXPOSE 5000

# Apenas API Server (WhatsApp Bridge roda separado depois)
CMD ["python3", "api_server.py"]
