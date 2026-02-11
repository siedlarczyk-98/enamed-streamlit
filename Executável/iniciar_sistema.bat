@echo off
title Sistema de Analise Medica - ENAMED

:: 1. Verifica se o Python esta instalado no computador da pessoa
python --version >nul 2>&1
if %errorlevel% neq 0 (
    cls
    echo ========================================================
    echo  ERRO CRITICO: PYTHON NAO ENCONTRADO
    echo ========================================================
    echo.
    echo  Para usar este sistema, voce precisa instalar o Python.
    echo  Baixe em: https://www.python.org/downloads/
    echo.
    pause
    exit
)

:: 2. Verifica se a pasta 'venv' ja existe. Se sim, pula a instalacao.
if exist venv (
    echo Ambiente detectado. Iniciando sistema...
    call venv\Scripts\activate
) else (
    echo ========================================================
    echo  CONFIGURACAO INICIAL (Apenas na primeira vez)
    echo  Aguarde, criando ambiente virtual e instalando bibliotecas...
    echo ========================================================
    
    python -m venv venv
    call venv\Scripts\activate
    
    :: Instala TODAS as bibliotecas necessarias (inclui fpdf e requests que faltavam)
    pip install streamlit pandas plotly xlsxwriter openpyxl fpdf requests pyarrow
    
    echo.
    echo Instalacao concluida com sucesso!
)

cls
echo ========================================================
echo       PACIENTE 360 | ENAMED ANALYTICS
echo ========================================================
echo.
echo  O sistema abrira no seu navegador em instantes...
echo  Nao feche esta janela preta enquanto usar o sistema.
echo.

:: 3. Roda o aplicativo
streamlit run app_enamed.py

pause