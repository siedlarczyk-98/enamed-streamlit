import streamlit as st
import pandas as pd
import os

st.title("🕵️ Detetive de Dados")

# 1. Carregue os dois arquivos
try:
    df_csv = pd.read_csv("base_alunos.csv", encoding='utf-8-sig', sep=None, engine='python')
    df_parquet = pd.read_parquet("base_alunos.parquet")
    
    st.write(f"📂 **CSV Original:** {len(df_csv)} linhas | {df_csv['IES_NOME'].nunique()} Instituições")
    st.write(f"📦 **Parquet Gerado:** {len(df_parquet)} linhas | {df_parquet['IES_NOME'].nunique()} Instituições")
    
    # 2. Verifica os Cadernos
    st.subheader("🔍 Análise da Coluna CO_CADERNO")
    
    col_cad_csv = next(c for c in df_csv.columns if 'CADERNO' in c)
    col_cad_parq = next(c for c in df_parquet.columns if 'CADERNO' in c)
    
    unique_csv = df_csv[col_cad_csv].unique()
    unique_parq = df_parquet[col_cad_parq].unique()
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"Cadernos no CSV ({df_csv[col_cad_csv].dtype}):")
        st.write(unique_csv)
        
    with c2:
        st.info(f"Cadernos no Parquet ({df_parquet[col_cad_parq].dtype}):")
        st.write(unique_parq)

    # 3. Verifica quem sumiu
    ies_csv = set(df_csv['IES_NOME'].unique())
    ies_parq = set(df_parquet['IES_NOME'].unique())
    
    missing = ies_csv - ies_parq
    
    if missing:
        st.error(f"🚨 ALERTA: {len(missing)} Instituições existem no CSV mas SUMIRAM no Parquet!")
        st.write(list(missing)[:10]) # Mostra as 10 primeiras
    else:
        st.success("✅ Todas as instituições do CSV estão no Parquet.")

except Exception as e:
    st.error(f"Erro ao ler arquivos: {e}")