FROM python:3.11-slim

# Instalar Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar dependências Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar dependências Node.js
COPY whatsapp-bridge/package*.json ./whatsapp-bridge/
RUN cd whatsapp-bridge && npm install

# Copiar código
COPY . .

# Criar pasta para sessão do WhatsApp
RUN mkdir -p whatsapp-bridge/auth_state

# Porta da API
EXPOSE 5000

# Rodar API e WhatsApp Bridge juntos
CMD ["sh", "-c", "python3 api_server.py & cd whatsapp-bridge && node index.js"]
