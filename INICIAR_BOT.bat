@echo off
title BarberFlow WhatsApp Bot
color 0A

echo ========================================
echo  BARBERFLOW WHATSAPP BOT
echo ========================================
echo.

cd /d "C:\Users\Matheus\whatsapp-bot-barbearia"

echo Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo Verificando dependencias...
python -c "import flask; import groq; print('Dependencias OK')"
if %errorlevel% neq 0 (
    echo Instalando dependencias...
    python -m pip install flask groq python-dotenv
)

echo.
echo Iniciando bot...
echo.

python main.py

echo.
echo Bot encerrado.
pause
