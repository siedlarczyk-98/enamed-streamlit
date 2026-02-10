import pandas as pd

def gerar_parquet_mapeamento(caminho_input, caminho_output):
    """
    Lê o mapeamento de localidade em Excel e salva em Parquet otimizado.
    """
    try:
        # 1. Carregar o arquivo Excel
        # Se houver mais de uma aba, você pode especificar sheet_name='NomeDaAba'
        df = pd.read_excel(caminho_input)
        
        # 2. Padronizar nomes das colunas (Remover espaços e colocar em maiúsculo)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # 3. Tratamento de Tipos de Dados
        # CO_CURSO deve ser inteiro para um merge rápido e sem erros de ponto flutuante
        if 'CO_CURSO' in df.columns:
            df['CO_CURSO'] = pd.to_numeric(df['CO_CURSO'], errors='coerce').fillna(0).astype(int)
        
        # converter colunas de texto para 'category' economiza muito espaço no Parquet
        colunas_texto = ['IES_ESTADO', 'SIGLA_ESTADO', 'IES_MUNIC']
        for col in colunas_texto:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().astype('category')
        
        # 4. Salvar em Parquet usando compressão snappy (padrão e veloz)
        df.to_parquet(caminho_output, index=False, engine='pyarrow', compression='snappy')
        
        print(f"✅ Sucesso! Arquivo salvo em: {caminho_output}")
        print(f"📊 Colunas detectadas: {list(df.columns)}")
        
    except Exception as e:
        print(f"❌ Erro ao processar: {e}")

# Execução
gerar_parquet_mapeamento(r"C:\Users\Active\Desktop\Streamlit enamed\mapeamento_localidade.xlsx", "mapeamento_Estados.parquet")