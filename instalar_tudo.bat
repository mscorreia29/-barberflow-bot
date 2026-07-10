@echo off
echo ========================================
echo  BarberFlow WhatsApp Bot
echo ========================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale em: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar se Node.js esta instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Node.js nao encontrado!
    echo Instale em: https://nodejs.org
    pause
    exit /b 1
)

echo Python e Node.js detectados!
echo.

REM Instalar dependencias Python
echo Instalando dependencias Python...
python -m pip install -r requirements.txt
echo.

REM Instalar dependencias Node.js
echo Instalando dependencias Node.js...
cd whatsapp-bridge
npm install
cd ..
echo.

echo ========================================
echo  Instalacao concluida!
echo ========================================
echo.
echo Para iniciar o bot:
echo   1. Execute: python main.py
echo   2. Escolha opcao 2 (API + WhatsApp Bridge)
echo   3. Escaneie o QR Code com seu WhatsApp
echo.
pause
