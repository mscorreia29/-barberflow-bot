@echo off
title Deploy Oracle Cloud - BarberFlow Bot
color 0B

echo ========================================
echo  DEPLOY NO ORACLE CLOUD
echo ========================================
echo.
echo  Antes de comecar, voce precisa:
echo.
echo  1. Criar conta em cloud.oracle.com/free
echo  2. Criar uma instancia Ubuntu
echo  3. Ter o IP da instancia
echo.
echo ========================================
echo.

set /p IP="Digite o IP da sua instancia Oracle: "

if "%IP%"=="" (
    echo ERRO: IP nao pode ser vazio!
    pause
    exit /b 1
)

echo.
echo Testando conexao com %IP%...
echo.

ssh -o ConnectTimeout=5 ubuntu@%IP% "echo Conexao OK!" 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel conectar!
    echo Verifique se:
    echo  - O IP esta correto
    echo  - A instancia esta rodando
    echo  - Voce tem a chave SSH configurada
    pause
    exit /b 1
)

echo Conexao OK! Enviando bot...
echo.

echo [1/4] Copiando arquivos...
scp -r "C:\Users\Matheus\whatsapp-bot-barbearia" ubuntu@%IP%:~/bot
if %errorlevel% neq 0 (
    echo ERRO ao copiar arquivos!
    pause
    exit /b 1
)

echo [2/4] Instalando dependencias...
ssh ubuntu@%IP% "cd ~/bot && pip3 install flask groq python-dotenv && cd whatsapp-bridge && npm install"
if %errorlevel% neq 0 (
    echo ERRO ao instalar dependencias!
    pause
    exit /b 1
)

echo [3/4] Configurando servico...
ssh ubuntu@%IP% "sudo bash -c 'cat > /etc/systemd/system/barberflow-bot.service << EOF
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
'"
if %errorlevel% neq 0 (
    echo ERRO ao configurar servico!
    pause
    exit /b 1
)

echo [4/4] Iniciando bot...
ssh ubuntu@%IP% "sudo systemctl enable barberflow-bot && sudo systemctl start barberflow-bot"
if %errorlevel% neq 0 (
    echo ERRO ao iniciar bot!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  DEPLOY CONCLUIDO!
echo ========================================
echo.
echo  Bot rodando em: http://%IP%:5000/health
echo.
echo  Para conectar WhatsApp:
echo  1. SSH na VM: ssh ubuntu@%IP%
echo  2. Rode: cd ~/bot/whatsapp-bridge ^&^& node index.js
echo  3. Escaneie o QR Code
echo.
echo  Para ver logs:
echo  ssh ubuntu@%IP% "sudo journalctl -u barberflow-bot -f"
echo.
echo ========================================
echo.
pause
