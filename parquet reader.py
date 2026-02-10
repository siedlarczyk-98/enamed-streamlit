import pandas as pd

# 1. Converter Base de Alunos
print("Convertendo base_alunos...")
df_alunos = pd.read_csv('base_alunos.csv', sep=';', encoding='utf-8-sig')
# Força o caderno a ser inteiro para evitar erros no dashboard
df_alunos['CO_CADERNO'] = pd.to_numeric(df_alunos['CO_CADERNO'], errors='coerce').fillna(0).astype(int)
df_alunos.to_parquet('base_alunos.parquet', index=False)
print("✅ base_alunos.parquet criado!")

# 2. Converter Base de Gabarito
print("Convertendo base_gabarito...")
df_gab = pd.read_csv('base_gabarito.csv', sep=';', encoding='utf-8-sig')
df_gab['CO_CADERNO'] = pd.to_numeric(df_gab['CO_CADERNO'], errors='coerce').fillna(0).astype(int)
df_gab.to_parquet('base_gabarito.parquet', index=False)
print("✅ base_gabarito.parquet criado!")