# Deploy no Railway - BarberFlow Bot (Sem Cartão)

## Passo 1: Criar conta Railway

1. Acesse: https://railway.app
2. Clique "Login"
3. Faça login com **GitHub** (ou crie conta)
4. **Não precisa de cartão!**

## Passo 2: Criar projeto

1. Clique "New Project"
2. Selecione "Deploy from GitHub repo"
3. Se não tem o código no GitHub, faça o upload primeiro (próximo passo)

## Passo 3: Colocar código no GitHub

### Opção A: Pelo GitHub Web
1. Acesse: https://github.com/new
2. Nome: barberflow-bot
3. Não marque "Add README"
4. Clique "Create repository"
5. Faça upload dos arquivos da pasta `C:\Users\Matheus\whatsapp-bot-barbearia`

### Opção B: Pelo PowerShell
```powershell
cd C:\Users\Matheus\whatsapp-bot-barbearia
git init
git add .
git commit -m "BarberFlow Bot"
git remote add origin https://github.com/SEU_USUARIO/barberflow-bot.git
git push -u origin master
```

## Passo 4: Criar Dockerfile

Crie o arquivo `Dockerfile` na raiz do projeto:

```dockerfile
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
```

## Passo 5: Criar railway.json

Crie o arquivo `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python3 api_server.py & cd whatsapp-bridge && node index.js",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

## Passo 6: Variáveis de ambiente

No Railway, vá em "Variables" e adicione:

```
GROQ_API_KEY=sua-chave-aqui
```

## Passo 7: Deploy

1. No Railway, clique "Deploy"
2. Aguarde build (2-3 minutos)
3. O bot vai rodar 24h!

## Passo 8: Conectar WhatsApp

Após o deploy, o QR code vai aparecer nos logs do Railway.

Para ver os logs:
1. Clique no serviço
2. Vá em "Logs"
3. Escaneie o QR Code que aparecer

## Limitações do Railway Free

- 500 horas/mês (suficiente para rodar 24h)
- 1GB de RAM
- $5 de crédito mensal (mais que suficiente)

## Verificando se está rodando

Acesse: https://seu-app.up.railway.app/health
Deve mostrar: {"status": "ok"}

## Comandos úteis no Railway

- **Logs**: Clique no serviço > Logs
- **Restart**: Clique no serviço > Restart
- **Variables**: Clique no serviço > Variables
- **Settings**: Clique no serviço > Settings

## Solução de problemas

### Bot não inicia
- Verifique os logs
- Confirme se GROQ_API_KEY está configurada

### QR Code não aparece
- Reinicie o serviço
- Verifique se o WhatsApp Bridge está rodando

### Bot cai e não volta
- Railway reinicia automaticamente
- Verifique se não excedeu o limite de horas
