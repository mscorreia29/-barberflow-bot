@echo off
title WhatsApp Bridge - BarberFlow Bot
color 0A

echo ========================================
echo  WHATSAPP BRIDGE - BARBERFLOW BOT
echo ========================================
echo.

cd /d "C:\Users\Matheus\whatsapp-bot-barbearia\whatsapp-bridge"

echo Digite a URL do seu bot no Railway
echo (ex: https://barberflow-bot.up.railway.app)
echo.

set /p BOT_URL="URL do Railway: "

if "%BOT_URL%"=="" (
    echo ERRO: URL nao pode ser vazia!
    pause
    exit /b 1
)

echo.
echo Conectando a: %BOT_URL%
echo.

set BOT_API_URL=%BOT_URL%

node index.js

pause
