# Deploy no Oracle Cloud - BarberFlow Bot

## Passo 1: Criar conta Oracle Cloud

1. Acesse: https://cloud.oracle.com/free
2. Clique "Start for Free"
3. Preencha seus dados
4. Adicione cartão de crédito (apenas verificação, não cobra)
5. Confirme o e-mail

## Passo 2: Criar instância VM

1. No painel, vá em "Compute" > "Instances"
2. Clique "Create Instance"
3. Configure:
   - Name: barberflow-bot
   - Image: Ubuntu 22.04 (ou Oracle Linux)
   - Shape: VM.Standard.E2.1.Micro (grátis)
   - SSH Key: Gere ou cole sua chave pública
4. Clique "Create"
5. Anote o IP público

## Passo 3: Conectar via SSH

No PowerShell do Windows:
```powershell
# Se não tem chave SSH, gere uma:
ssh-keygen -t rsa -b 4096

# Conecte (substitua SEU_IP):
ssh ubuntu@SEU_IP
```

## Passo 4: Instalar dependências

No terminal SSH (copie e cole cada linha):
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar Python
sudo apt install -y python3 python3-pip

# Verificar versões
node --version
python3 --version
```

## Passo 5: Upload do bot

No PowerShell do Windows (fora da VM):
```powershell
# Copie o bot para a VM (substitua SEU_IP):
scp -r "C:\Users\Matheus\whatsapp-bot-barbearia" ubuntu@SEU_IP:~/bot
```

## Passo 6: Instalar dependências do bot

Na VM via SSH:
```bash
cd ~/bot

# Dependências Python
pip3 install flask groq python-dotenv

# Dependências Node.js
cd whatsapp-bridge
npm install
cd ..
```

## Passo 7: Configurar .env

```bash
nano .env
```

Cole:
```
GROQ_API_KEY=sua-chave-aqui
```

Salve com Ctrl+X, Enter.

## Passo 8: Criar serviço systemd

Para o bot rodar 24h e reiniciar automaticamente:

```bash
# Criar serviço
sudo nano /etc/systemd/system/barberflow-bot.service
```

Cole:
```ini
[Unit]
Description=BarberFlow WhatsApp Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bot
ExecStart=/usr/bin/python3 api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Salve com Ctrl+X, Enter.

## Passo 9: Iniciar o serviço

```bash
# Habilitar para iniciar com o sistema
sudo systemctl enable barberflow-bot

# Iniciar o serviço
sudo systemctl start barberflow-bot

# Verificar status
sudo systemctl status barberflow-bot
```

## Passo 10: Conectar WhatsApp

1. Na VM, rode o bridge:
```bash
cd ~/bot/whatsapp-bridge
node index.js
```

2. Escaneie o QR Code
3. Depois de conectar, o bridge pode rodar em background

Para rodar o bridge em background:
```bash
# Instalar screen
sudo apt install -y screen

# Criar sessão
screen -S whatsapp

# Rodar bridge
cd ~/bot/whatsapp-bridge
node index.js

# Para sair do screen: Ctrl+A, depois D
# Para voltar: screen -r whatsapp
```

## Verificando tudo

1. Acesse http://SEU_IP:5000/health
2. Deve mostrar: {"status": "ok"}

## Comandos úteis

```bash
# Ver logs
sudo journalctl -u barberflow-bot -f

# Reiniciar bot
sudo systemctl restart barberflow-bot

# Parar bot
sudo systemctl stop barberflow-bot

# Ver status
sudo systemctl status barberflow-bot
```

## IP da sua VM

Anote o IP público que aparece na página da instância Oracle Cloud.
Use para acessar: http://SEU_IP:5000/health
