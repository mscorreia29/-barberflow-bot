@echo off
echo ========================================
echo  Instalando Python para o Bot
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado!
    echo.
    echo Por favor, instale Python primeiro:
    echo 1. Acesse: https://www.python.org/downloads/
    echo 2. Baixe a versao mais recente
    echo 3. Durante a instalacao, marque "Add Python to PATH"
    echo 4. Reinicie o computador
    echo 5. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo Python encontrado!
echo.

REM Instalar dependências
echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo  Instalacao concluida!
echo ========================================
echo.
echo Para testar o bot:
echo   python main.py
echo.
pause
