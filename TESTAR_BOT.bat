@echo off
title Teste - BarberFlow Bot
color 0C

echo ========================================
echo  TESTE DO BOT
echo ========================================
echo.

cd /d "C:\Users\Matheus\whatsapp-bot-barbearia"

echo [1] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)
echo OK!
echo.

echo [2] Verificando imports...
python -c "from bot import bot; print('Bot: OK')"
if %errorlevel% neq 0 (
    echo ERRO ao importar bot!
    pause
    exit /b 1
)

python -c "from ai_handler import get_ai_response; print('AI: OK')"
if %errorlevel% neq 0 (
    echo ERRO ao importar AI!
    pause
    exit /b 1
)

python -c "from api_server import app; print('API: OK')"
if %errorlevel% neq 0 (
    echo ERRO ao importar API!
    pause
    exit /b 1
)

echo.
echo [3] Testando bot...
python -c "from bot import bot; r=bot.handle_message('5511999999999','/ajuda'); print('Resposta:', r[:50] if r else 'FALHOU')"
if %errorlevel% neq 0 (
    echo ERRO ao testar bot!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  TODOS OS TESTES PASSARAM!
echo ========================================
echo.
echo Para iniciar o bot, execute:
echo   INICIAR_BOT.bat
echo.
pause
