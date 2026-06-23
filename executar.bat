@echo off
REM Lançador de scripts do Tree Risk AI
REM Uso: executar.bat <nome_do_script>
REM Ex:  executar.bat scripts\preparar_dados.py

set PYTHON=C:\Users\Arthur\Envs\tree_risk_ai\Scripts\python.exe
set SCRIPT=%1

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
    exit /b 0
)

echo Usando Python: %PYTHON%
echo Executando: %SCRIPT%
echo.
"%PYTHON%" %SCRIPT% %2 %3 %4
