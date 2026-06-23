@echo off
REM Lancador de scripts do Tree Risk AI
REM Uso: executar.bat <nome_do_script>
REM Ex:  executar.bat scripts\preparar_dados.py

REM --- Detecta Python: venv local > PATH python > py launcher ---
set SCRIPT=%1

if exist "%~dp0.venv\Scripts\python.exe" (
    set PYTHON=%~dp0.venv\Scripts\python.exe
    goto :found
)
if exist "%~dp0venv\Scripts\python.exe" (
    set PYTHON=%~dp0venv\Scripts\python.exe
    goto :found
)
where python >nul 2>&1
if %ERRORLEVEL%==0 (
    set PYTHON=python
    goto :found
)
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    set PYTHON=py
    goto :found
)
echo ERRO: Python nao encontrado. Instale o Python ou crie um venv em .venv\
exit /b 1

:found
if "%SCRIPT%"=="" (
    echo.
    echo  Tree Risk AI - Scripts disponiveis:
    echo  ------------------------------------
    echo  executar.bat scripts\verificar_estrutura_completa.py
    echo  executar.bat scripts\preparar_dados.py
    echo  executar.bat scripts\treinar_otimizado.py
    echo  executar.bat scripts\testar_imagem.py
    echo  executar.bat scripts\analisar_resultados.py
    echo.
    echo  Python detectado: %PYTHON%
    echo.
    exit /b 0
)

echo Usando Python: %PYTHON%
echo Executando: %SCRIPT%
echo.
"%PYTHON%" %SCRIPT% %2 %3 %4
