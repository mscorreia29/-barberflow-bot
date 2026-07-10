FROM node:20-slim

WORKDIR /app

# Instalar Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Copiar dependências Node.js
COPY whatsapp-bridge/package*.json ./whatsapp-bridge/
RUN cd whatsapp-bridge && npm install

# Copiar dependências Python
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copiar código
COPY . .

# Porta da API
EXPOSE 5000

# Comando para rodar
CMD ["sh", -c, "python3 api_server.py & cd whatsapp-bridge && node index.js"]
