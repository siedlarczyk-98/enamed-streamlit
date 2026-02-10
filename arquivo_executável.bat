@echo off
title Sistema de Analise Medica
echo Instalando componentes necessarios (apenas na primeira vez)...
python -m venv venv
call venv\Scripts\activate
pip install streamlit pandas plotly xlsxwriter openpyxl
cls
echo Abrindo o sistema...
streamlit run app_enamed.py
pause