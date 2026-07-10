FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY whatsapp-bridge/package*.json ./whatsapp-bridge/
RUN cd whatsapp-bridge && npm install

COPY . .

RUN mkdir -p whatsapp-bridge/auth_state

ENV PORT=5000
EXPOSE 5000

CMD ["python3", "api_server.py"]
