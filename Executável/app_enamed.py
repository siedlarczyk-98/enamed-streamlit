import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
import requests
import tempfile
import re
from fpdf import FPDF # type: ignore

# ==========================================
# 1. CONFIGURAÇÕES GERAIS
# ==========================================
st.set_page_config(
    page_title="Paciente 360 | ENAMED Analytics",
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cores da Marca
P360_NAVY = "#1E3A5F"
P360_ORANGE = "#FD5E11"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ background-color: {P360_NAVY}; }}
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{ color: white !important; }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color: {P360_ORANGE} !important; }}
    h1, h2, h3 {{ color: {P360_NAVY} !important; font-family: 'Helvetica', sans-serif; }}
    [data-testid="stMetricValue"] {{ color: {P360_ORANGE} !important; font-weight: bold; }}
    .stSelectbox label, .stMultiSelect label {{ color: {P360_NAVY} !important; font-weight: bold !important; }}
    div[data-baseweb="select"] > div {{ background-color: white !important; color: {P360_NAVY} !important; }}
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. INTEGRAÇÃO COM IA (MARITACA)
# ==========================================

def preparar_portfolio_texto(df_port):
    """ Converte o dataframe de portfólio em texto para o prompt """
    if df_port is None or df_port.empty: return ""
    try:
        cols_area = [c for c in df_port.columns if 'AREA' in str(c).upper()]
        col_area = cols_area[0] if cols_area else df_port.columns[0]
        cols_titulo = [c for c in df_port.columns if any(x in str(c).upper() for x in ['TITULO', 'CASO', 'NOME'])]
        col_titulo = cols_titulo[0] if cols_titulo else (df_port.columns[1] if len(df_port.columns) > 1 else df_port.columns[0])
        
        texto = "ACERVO DE CASOS CLÍNICOS DISPONÍVEIS:\n"
        grouped = df_port.groupby(col_area)[col_titulo].apply(lambda x: list(x.dropna().unique())[:10])
        for area, casos in grouped.items():
            texto += f"- {area}: {', '.join(map(str, casos))}\n"
        return texto
    except: return ""

def encontrar_match_inteligente(df_top_gaps, texto_portfolio):
    """ Chama a API para gerar recomendação pedagógica """
    if not texto_portfolio:
        return "GAP_ESCOLHIDO: Geral\nCASO: -\nPORQUE: Portfólio não carregado.\nDINAMICA: -\nCOMO FAZER: Carregue o arquivo de portfólio."
    api_key = "106510904080513630747_fa3102b65ef19b25"
    url = "https://chat.maritaca.ai/api/chat/completions"
    
    lista_gaps_txt = ""
    for i, row in df_top_gaps.iterrows():
        lista_gaps_txt += f"- {row['SUBESPECIALIDADE']} ({row['DIAGNOSTICO']})\n"
    
    prompt = f"""
    Você é o Curador Pedagógico Sênior de uma faculdade de medicina.
    
    GAPS IDENTIFICADOS NOS ALUNOS:
    {lista_gaps_txt}
    
    ACERVO DE CASOS:
    {texto_portfolio}
    
    TAREFA:
    Escolha o gap mais crítico e sugira UM caso do acervo para resolvê-lo.
    
    FORMATO DE RESPOSTA OBRIGATÓRIO:
    GAP_ESCOLHIDO: [Nome do Gap]
    CASO: [Nome do Caso]
    PORQUE: [Explicação em 1 frase]
    DINAMICA: [Sugestão de dinâmica de aula]
    COMO FAZER: [Instrução curta para o professor] - Considere que todos os casos podem ser realizados pelo aluno de maneira autônoma ou apresentados em sala de aula. Caso o caso seja feito pelo aluno, é possível identificar erros e acertos mais frequentes.
    """

    try:
        headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
        data = {
            "messages": [{"role": "user", "content": prompt}], 
            "model": "sabia-4",
            "max_tokens": 400, 
            "temperature": 0.3
        } 
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200: 
            return response.json()['choices'][0]['message']['content']
        else:
            return f"GAP_ESCOLHIDO: Erro API\nCASO: Status {response.status_code}\nPORQUE: {response.text[:50]}\nDINAMICA: -\nCOMO FAZER: -"
            
    except Exception as e:
        return f"GAP_ESCOLHIDO: Erro Conexão\nCASO: -\nPORQUE: {str(e)[:50]}\nDINAMICA: -\nCOMO FAZER: -"

# ==========================================
# 3. GERAÇÃO DE PDF (TEASER COMERCIAL)
# ==========================================

def gerar_pdf_teaser(ies_nome, municipio, uf, conceito, media_atual, nova_media, top_gaps, fig_ranking_reg, fig_ranking_nac, recomendacao_ia_texto):
    
    # --- FUNÇÃO DE LIMPEZA ---
    def sanitizar_texto(txt):
        if not isinstance(txt, str): return str(txt)
        mapa = {
            '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
            '\u2013': '-', '\u2014': '-', '\u2022': '*', '\u2026': '...', '–': '-'
        }
        for orig, dest in mapa.items(): txt = txt.replace(orig, dest)
        return txt.encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    
    # --- TRUQUE: Margem de quebra quase zero para permitir uso total da página ---
    pdf.set_auto_page_break(auto=True, margin=2) 
    pdf.add_page()
    
    # Cores
    navy_r, navy_g, navy_b = 30, 58, 95
    orange_r, orange_g, orange_b = 253, 94, 17
    
    # --- 1. CABEÇALHO (40mm) ---
    pdf.set_fill_color(navy_r, navy_g, navy_b)
    pdf.rect(0, 0, 210, 40, 'F') 
    m_left = 15
    
    pdf.set_y(10); pdf.set_x(m_left)
    pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(255)
    pdf.cell(0, 8, sanitizar_texto('Diagnóstico Microdados ENAMED 2025'), 0, 1, 'L')
    
    pdf.set_y(19); pdf.set_x(m_left)
    pdf.set_font('Helvetica', 'B', 11)
    nome_exibicao = (ies_nome[:65] + '...') if len(ies_nome) > 65 else ies_nome
    pdf.cell(0, 6, sanitizar_texto(f'IES: {nome_exibicao}'), 0, 1, 'L')

    pdf.set_y(25); pdf.set_x(m_left)
    pdf.set_font('Helvetica', '', 9)
    txt_conc = f"Conceito ENAMED: {conceito}" if conceito and str(conceito) not in ["-", "nan"] else "Conceito: N/D"
    txt_loc = f"{municipio}/{uf}" if municipio and uf and str(municipio) != "-" else "Loc: N/D"
    pdf.cell(0, 6, sanitizar_texto(f"{txt_loc}  |  {txt_conc}"), 0, 1, 'L')

    # Busca logo de forma segura
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    path_logo = os.path.join(pasta_projeto, "logo_branca.png")
    if os.path.exists(path_logo):
        pdf.image(path_logo, x=165, y=10, w=30) 
    
    # --- INÍCIO DO CONTEÚDO (Y = 45) ---
    current_y = 45
    pdf.set_y(current_y)
    
    # --- 2. KPI CARDS (Altura 30mm) ---
    pdf.set_text_color(navy_r, navy_g, navy_b); pdf.set_font('Helvetica', 'B', 14)
    pdf.set_x(m_left)
    pdf.cell(0, 8, sanitizar_texto('1. Potencial de Evolução'), 0, 1, 'L')
    
    h_card = 30 
    w_card = 88
    y_cards = pdf.get_y() + 1
    
    # Card 1
    pdf.set_fill_color(235, 235, 235); pdf.rect(m_left, y_cards, w_card, h_card, 'F')
    pdf.set_xy(m_left, y_cards + 5); pdf.set_font('Helvetica', '', 9); pdf.set_text_color(80)
    pdf.cell(w_card, 5, sanitizar_texto('Performance Atual'), 0, 2, 'C')
    pdf.set_font('Helvetica', 'B', 24); pdf.set_text_color(navy_r, navy_g, navy_b)
    pdf.cell(w_card, 12, f"{media_atual:.1%}", 0, 2, 'C')
    
    # Card 2
    pdf.set_fill_color(orange_r, orange_g, orange_b); pdf.rect(m_left + w_card + 4, y_cards, w_card, h_card, 'F')
    pdf.set_xy(m_left + w_card + 4, y_cards + 5); pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(255)
    pdf.cell(w_card, 5, sanitizar_texto('Projetado (Com Ajustes)'), 0, 2, 'C')
    pdf.set_font('Helvetica', 'B', 24); pdf.cell(w_card, 12, f"{nova_media:.1%}", 0, 2, 'C')
    
    # Texto Metodologia
    pdf.set_xy(m_left, y_cards + h_card + 1)
    pdf.set_font('Helvetica', 'I', 7); pdf.set_text_color(100)
    ganho = (nova_media - media_atual) * 100
    pdf.multi_cell(180, 3, sanitizar_texto(f"Simulamos o impacto na nota geral caso a instituição eleve seu desempenho nos 5 diagnósticos críticos para a valores iguais à média nacional nesse mesmo tema. Ganho estimado: +{ganho:.1f} pp. na média de acertos dos alunos da instituição"), 0, 'C')
    
    # --- 3. RANKINGS (CONTROLE MANUAL DE Y) ---
    y_section_2 = y_cards + h_card + 9
    pdf.set_y(y_section_2)
    
    pdf.set_text_color(navy_r, navy_g, navy_b); pdf.set_font('Helvetica', 'B', 14)
    pdf.set_x(m_left)
    pdf.cell(0, 8, sanitizar_texto('2. Posicionamento Competitivo'), 0, 1, 'L')
    
    h_chart = 75 # Altura fixa dos gráficos
    
    # --- Gráfico 1: Nacional ---
    y_chart_1_title = pdf.get_y()
    pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(navy_r, navy_g, navy_b)
    pdf.set_x(m_left)
    pdf.cell(0, 5, sanitizar_texto('2.1. Cenário Nacional'), 0, 1, 'L')
    
    y_img_1 = pdf.get_y() + 1
    
    if fig_ranking_nac:
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                fig_ranking_nac.write_image(tmp.name, scale=2)
                pdf.image(tmp.name, x=m_left, y=y_img_1, w=180, h=h_chart) 
            os.unlink(tmp.name)
        except: pass

    # --- Gráfico 2: Regional ---
    y_chart_2_start = y_img_1 + h_chart + 2 
    
    pdf.set_y(y_chart_2_start)
    pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(navy_r, navy_g, navy_b)
    pdf.set_x(m_left)
    lbl_reg = f'2.2. Cenário Regional ({uf})' if uf else '2.2. Cenário Regional'
    pdf.cell(0, 5, sanitizar_texto(lbl_reg), 0, 1, 'L')
    
    y_img_2 = pdf.get_y() + 1
    
    if fig_ranking_reg:
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                fig_ranking_reg.write_image(tmp.name, scale=2)
                pdf.image(tmp.name, x=m_left, y=y_img_2, w=180, h=h_chart)
            os.unlink(tmp.name)
        except: pass

    # --- PÁGINA 2 ---
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15) 
    
    path_logo_cor = os.path.join(pasta_projeto, "logo_colorida.png")
    if os.path.exists(path_logo_cor): pdf.image(path_logo_cor, 165, 10, 33)
    pdf.set_y(25)
    
    # Tabela
    pdf.set_text_color(navy_r, navy_g, navy_b); pdf.set_font('Helvetica', 'B', 15)
    pdf.set_x(m_left)
    pdf.cell(0, 10, sanitizar_texto('3. Top 5 Pontos de Atenção'), 0, 1, 'L'); pdf.ln(2)
    pdf.set_fill_color(navy_r, navy_g, navy_b); pdf.set_text_color(255); pdf.set_font('Helvetica', 'B', 9)
    
    pdf.set_x(m_left)
    pdf.cell(110, 9, sanitizar_texto("  Diagnóstico"), 0, 0, 'L', 1) 
    pdf.cell(35, 9, sanitizar_texto("Sua Nota"), 0, 0, 'C', 1)
    pdf.cell(35, 9, sanitizar_texto("Gap"), 0, 1, 'C', 1)
    
    pdf.set_text_color(0); pdf.set_font('Helvetica', '', 9); fill = False
    for i, row in top_gaps.head(5).iterrows():
        d_name = (f"{row['SUBESPECIALIDADE']} - {row['DIAGNOSTICO']}")[:75] + "..."
        pdf.set_x(m_left)
        pdf.set_fill_color(248, 248, 248)
        pdf.cell(110, 9, sanitizar_texto(f"  {d_name}"), 0, 0, 'L', fill)
        pdf.cell(35, 9, f"{row['IES']:.1%}", 0, 0, 'C', fill)
        pdf.set_text_color(200, 0, 0); pdf.cell(35, 9, f"{row['Diferença']:+.1f} pp", 0, 1, 'C', fill)
        pdf.set_text_color(0); fill = not fill 
    pdf.ln(10)
    
    # --- 4. Prescrição Pedagógica (SEM CAIXA) ---
    pdf.set_text_color(navy_r, navy_g, navy_b); pdf.set_font('Helvetica', 'B', 15)
    pdf.set_x(m_left)
    pdf.cell(0, 10, sanitizar_texto('4. Prescrição Pedagógica - Uso personalizado de casos'), 0, 1, 'L')
    
    # Parse dos dados da IA
    dados_ia = { "GAP_ESCOLHIDO": "Geral", "CASO": "N/D", "PORQUE": "-", "DINAMICA": "-", "COMO FAZER": "-" }
    try:
        linhas = recomendacao_ia_texto.split('\n')
        for linha in linhas:
            if ':' in linha:
                k, v = linha.split(':', 1)
                dados_ia[k.strip().upper()] = v.strip()
    except: pass

    # Posição Y inicial do texto
    y = pdf.get_y() + 2
    pdf.set_y(y)

    # Largura útil do texto
    txt_width = 180 
    
    # --- RENDERIZA O TEXTO DIRETAMENTE NA PÁGINA ---
    
    # Título: Diagnóstico Alvo
    pdf.set_x(m_left); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(150)
    pdf.cell(0, 5, sanitizar_texto("DIAGNÓSTICO ALVO:"), 0, 1)
    
    # Conteúdo: Diagnóstico
    pdf.set_x(m_left); pdf.set_font('Helvetica', 'B', 11); pdf.set_text_color(200, 0, 0)
    pdf.multi_cell(txt_width, 5, sanitizar_texto(dados_ia.get("GAP_ESCOLHIDO", "N/D")))
    
    # Conteúdo: Caso Sugerido
    pdf.ln(2)
    pdf.set_x(m_left); pdf.set_font('Helvetica', 'B', 10); pdf.set_text_color(102, 51, 153)
    pdf.multi_cell(txt_width, 5, sanitizar_texto(f"Caso Sugerido: {dados_ia.get('CASO', '')}"))
    
    # Conteúdo: Por que (Itálico)
    pdf.ln(1)
    pdf.set_x(m_left); pdf.set_font('Helvetica', 'I', 9); pdf.set_text_color(80)
    pdf.multi_cell(txt_width, 4, sanitizar_texto(f"Por que: {dados_ia.get('PORQUE', '')}"))
    
    # Título: Dinâmica
    pdf.ln(3)
    pdf.set_x(m_left); pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(orange_r, orange_g, orange_b)
    pdf.multi_cell(txt_width, 4, sanitizar_texto(f"STATEMENT: {dados_ia.get('DINAMICA', '').upper()}"))
    
    # Conteúdo: Como Fazer
    pdf.ln(1)
    pdf.set_x(m_left); pdf.set_font('Helvetica', '', 9); pdf.set_text_color(0)
    pdf.multi_cell(txt_width, 4, sanitizar_texto(dados_ia.get("COMO FAZER", "")))

    # --- RODAPÉ (CTA) ---
    pdf.set_auto_page_break(False)
    
    y_base = 257 
    
    # Fundo Azul
    pdf.set_y(y_base)
    pdf.set_fill_color(navy_r, navy_g, navy_b)
    pdf.rect(0, y_base, 210, 40, 'F')
    
    # Texto 1 (Título)
    pdf.set_y(y_base + 8) 
    pdf.set_font('Helvetica', 'B', 12); pdf.set_text_color(255)
    pdf.cell(0, 6, sanitizar_texto("TRANSFORME DADOS EM ESTRATÉGIA PEDAGÓGICA REAL"), 0, 1, 'C')
    
    # Texto 2 (Subtítulo)
    pdf.set_y(y_base + 14)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, sanitizar_texto("Agende a demonstração completa da plataforma Paciente 360."), 0, 1, 'C')
    
    # Texto 3 (Link Laranja)
    pdf.set_y(y_base + 24)
    pdf.set_font('Helvetica', 'B', 11); pdf.set_text_color(orange_r, orange_g, orange_b)
    pdf.cell(0, 10, sanitizar_texto(">> CLIQUE AQUI PARA RECEBER O RELATÓRIO COMPLETO <<"), 0, 1, 'C', link="https://www.paciente360.com.br")

    return pdf.output(dest='S').encode('latin-1', 'replace')
   
# ==========================================
# 4. PROCESSAMENTO DE DADOS
# ==========================================

@st.cache_data(show_spinner=False)
def carregar_dados_otimizado(uploaded_file, default_path, is_excel=False):
    df = None
    file_source = uploaded_file if uploaded_file else (default_path if os.path.exists(default_path) else None)
    if file_source:
        try:
            name = getattr(file_source, 'name', str(file_source))
            if name.endswith('.parquet'): df = pd.read_parquet(file_source)
            elif is_excel or name.endswith(('.xlsx', '.xls')): df = pd.read_excel(file_source)
            else: df = pd.read_csv(file_source, sep=None, engine='python', encoding='utf-8-sig')
            
            if df is not None:
                df.columns = [str(c).strip().upper() for c in df.columns]
                for col in df.select_dtypes(include=['object']).columns:
                    if df[col].nunique() / len(df) < 0.5: df[col] = df[col].astype('category')
        except: return None
    return df

@st.cache_data(show_spinner="Processando base...")
def processar_base_consolidada(df_alunos, df_gab, df_mapa):
    # CORREÇÃO CRÍTICA DE PATH: Busca o parquet na pasta do projeto de forma segura
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    path_mapa_local = os.path.join(pasta_projeto, "mapeamento_Estados.parquet")
    
    if os.path.exists(path_mapa_local):
        try:
            df_loc = pd.read_parquet(path_mapa_local)
            df_loc.columns = [str(c).strip().upper() for c in df_loc.columns]
            
            col_curso = next((c for c in df_alunos.columns if c in ['CO_CURSO', 'COD_CURSO', 'CD_CURSO']), None)
            if col_curso:
                df_alunos[col_curso] = pd.to_numeric(df_alunos[col_curso], errors='coerce').fillna(0).astype('int64')
                df_loc['CO_CURSO'] = pd.to_numeric(df_loc['CO_CURSO'], errors='coerce').fillna(0).astype('int64')
                
                drop_cols = [c for c in ['SIGLA_ESTADO', 'IES_MUNIC'] if c in df_alunos.columns]
                if drop_cols: df_alunos.drop(columns=drop_cols, inplace=True)
                
                df_alunos = pd.merge(df_alunos, df_loc[['CO_CURSO', 'SIGLA_ESTADO', 'IES_MUNIC']], left_on=col_curso, right_on='CO_CURSO', how='left')
        except: pass

    col_ies = next(c for c in df_alunos.columns if 'IES_NOME' in c or 'NO_IES' in c)
    col_cad = next(c for c in df_alunos.columns if 'CADERNO' in c)
    col_p360 = next((c for c in df_alunos.columns if 'P360' in c), None)

    for d in [df_alunos, df_gab, df_mapa]:
        if col_cad in d.columns: d[col_cad] = pd.to_numeric(d[col_cad], errors='coerce').fillna(0).astype('int16')

    q_cols = [c for c in df_alunos.columns if 'DS_VT_ESC_OBJ' in c]
    mapa_q = {col: int(re.search(r'\d+', col).group()) for col in q_cols if re.search(r'\d+', col)}
    
    id_vars = [col_ies, col_cad]
    if col_p360: id_vars.append(col_p360)
    if 'SIGLA_ESTADO' in df_alunos.columns: id_vars.append('SIGLA_ESTADO')
    if 'IES_MUNIC' in df_alunos.columns: id_vars.append('IES_MUNIC')
    if 'CO_CURSO' in df_alunos.columns: id_vars.append('CO_CURSO')

    df_long = df_alunos.melt(id_vars=id_vars, value_vars=q_cols, var_name='COL_ORIGEM', value_name='RESPOSTA')
    df_long['NU_QUESTAO'] = df_long['COL_ORIGEM'].map(mapa_q).astype('int16')
    df_long.drop(columns=['COL_ORIGEM'], inplace=True)

    q_gab = [c for c in df_gab.columns if 'DS_VT_GAB_OBJ' in c]
    mapa_gab = {col: int(re.search(r'\d+', col).group()) for col in q_gab if re.search(r'\d+', col)}
    df_gab_l = df_gab.melt(id_vars=[col_cad], value_vars=q_gab, var_name='COL_ORIGEM', value_name='GABARITO')
    df_gab_l['NU_QUESTAO'] = df_gab_l['COL_ORIGEM'].map(mapa_gab).astype('int16')
    
    df_m = pd.merge(df_long.dropna(subset=['NU_QUESTAO']), df_gab_l.drop(columns=['COL_ORIGEM']).dropna(subset=['NU_QUESTAO']), on=[col_cad, 'NU_QUESTAO'])
    
    if 'NU_QUESTAO' in df_mapa.columns:
        df_mapa['NU_QUESTAO'] = pd.to_numeric(df_mapa['NU_QUESTAO'], errors='coerce').fillna(0).astype('int16')
        df_m = pd.merge(df_m, df_mapa, on=[col_cad, 'NU_QUESTAO'], how='left')

    resp = df_m['RESPOSTA'].astype(str).str.strip().str.upper()
    gab = df_m['GABARITO'].astype(str).str.strip().str.upper()
    df_m['ACERTO'] = ((resp == gab) | (gab == 'ANULADA')).astype('int8')

    return df_m, col_ies, col_cad, col_p360

def calcular_potencial_evolucao(df_ies, df_nac, top_gaps):
    if df_ies.empty: return 0.0, 0.0
    media_atual = df_ies['ACERTO'].mean()
    
    df_ies['CHAVE'] = df_ies['GRANDE_AREA'].astype(str) + "|" + df_ies['SUBESPECIALIDADE'].astype(str)
    keys_gap = (top_gaps['GRANDE_AREA'].astype(str) + "|" + top_gaps['SUBESPECIALIDADE'].astype(str)).tolist()
    
    mask_gap = df_ies['CHAVE'].isin(keys_gap)
    n_questoes_gap = mask_gap.sum()
    media_nac_gaps = top_gaps['Nacional'].mean()
    
    acertos_sem_gap = df_ies.loc[~mask_gap, 'ACERTO'].sum()
    novos_acertos = n_questoes_gap * media_nac_gaps
    
    nova_media = (acertos_sem_gap + novos_acertos) / len(df_ies)
    return media_atual, max(nova_media, media_atual + 0.01)

def gerar_grafico_ranking_img(df_completo, col_ies, ies_alvo):
    # 1. Agrupamento e Ordenação
    ranking = df_completo.groupby(col_ies)['ACERTO'].agg(['mean', 'count']).reset_index()
    ranking.columns = [col_ies, 'ACERTO', 'VOLUME']
    ranking = ranking[ranking['VOLUME'] >= 20] 
    
    # Garante que a IES Alvo esteja no ranking
    if ies_alvo not in ranking[col_ies].values:
        row = df_completo[df_completo[col_ies] == ies_alvo].groupby(col_ies)['ACERTO'].agg(['mean', 'count']).reset_index()
        if not row.empty:
            row.columns = [col_ies, 'ACERTO', 'VOLUME']
            ranking = pd.concat([ranking, row])

    ranking = ranking.sort_values('ACERTO', ascending=False).reset_index(drop=True)
    ranking['Posicao'] = ranking.index + 1
    ranking['Label'] = ranking.apply(lambda x: "Sua IES" if x[col_ies] == ies_alvo else f"IES {x['Posicao']}", axis=1)
    
    # Lógica de Cores Clássica (Cinza vs Laranja)
    ranking['Cor'] = ranking.apply(lambda x: '#FD5E11' if x[col_ies] == ies_alvo else '#E0E0E0', axis=1)

    # 2. Seleção dos Vizinhos
    try:
        idx = ranking[ranking[col_ies] == ies_alvo].index[0]
        indices = sorted(list(set([0, 1, 2, idx, idx-1, idx+1])))
        indices = [i for i in indices if 0 <= i < len(ranking)]
        df_plot = ranking.iloc[indices].copy()
    except: 
        df_plot = ranking.head(6).copy()

    # 3. Geração do Gráfico
    fig = px.bar(
        df_plot, 
        x='Label', 
        y='ACERTO', 
        text_auto='.1%', 
        color='Cor', 
        color_discrete_map="identity"
    )
    
    # 4. Ajustes de Layout (Mantendo a margem inferior corrigida)
    fig.update_layout(
        plot_bgcolor='white', 
        height=350, 
        margin=dict(l=10, r=10, t=20, b=50), 
        xaxis_title=None,
        yaxis_title='Percentual médio de acertos',
        yaxis_showticklabels=False,
        font=dict(size=12, family="Arial")
    )
    
    return fig

# ==========================================
# 5. EXECUÇÃO PRINCIPAL
# ==========================================
@st.fragment
def renderizar_acoes_finais(df_f):
    st.divider()
    c1, c2 = st.columns([1, 4])
    with c1:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_f.to_excel(writer, index=False)
        st.download_button("📊 Baixar Excel", output.getvalue(), "dados.xlsx", use_container_width=True)

# --- SIDEBAR: IMPORTAÇÃO ---
with st.sidebar:
    # Correção de path logo sidebar
    pasta_projeto = os.path.dirname(os.path.abspath(__file__))
    path_logo_sidebar = os.path.join(pasta_projeto, "logo_branca.png")
    if os.path.exists(path_logo_sidebar): st.image(path_logo_sidebar, use_container_width=True)
    
    st.divider()
    st.markdown("### 📂 Importação")
    u_alunos = st.file_uploader("Alunos", type=["csv", "parquet"])
    u_gab = st.file_uploader("Gabarito", type=["csv", "parquet"])
    u_mapa = st.file_uploader("Mapa", type=["xlsx"])
    u_port = st.file_uploader("Portfólio", type=["csv", "xlsx"])
    apenas_p360 = st.checkbox("Benchmark P360", value=False)

# Carrega Dados
df_a = carregar_dados_otimizado(u_alunos, "base_alunos.csv")
df_g = carregar_dados_otimizado(u_gab, "base_gabarito.csv")
df_m = carregar_dados_otimizado(u_mapa, "base_mapeamento.xlsx", is_excel=True)
df_port = carregar_dados_otimizado(u_port, "portfolio_casos.csv")
df_c_raw = carregar_dados_otimizado(None, "conceitos_ies.csv")

if df_a is not None and df_g is not None and df_m is not None:
    # 1. Processamento
    df, col_ies, col_cad, col_p360 = processar_base_consolidada(df_a, df_g, df_m)
    
    # 2. Cria Label (Cod - Nome)
    if 'CO_CURSO' in df.columns:
        df['CO_CURSO_STR'] = df['CO_CURSO'].fillna(0).astype('int64').astype(str)
        df['IES_LABEL'] = df['CO_CURSO_STR'] + " - " + df[col_ies].astype(str)
    else:
        df['IES_LABEL'] = df[col_ies].astype(str)

    # 3. FILTROS (Layout: UF -> Mun -> IES)
    c_uf, c_mun, c_ies = st.columns([1, 1.5, 4])
    uf_sel, mun_sel = [], []

    with c_uf:
        if 'SIGLA_ESTADO' in df.columns:
            ufs = sorted(df['SIGLA_ESTADO'].astype(str).replace('nan', 'N/A').unique())
            uf_sel = st.multiselect("UF", ufs)
        else: st.warning("UF n/d")

    with c_mun:
        if 'IES_MUNIC' in df.columns:
            mask = df['SIGLA_ESTADO'].isin(uf_sel) if uf_sel else [True]*len(df)
            muns = sorted(df[mask]['IES_MUNIC'].astype(str).unique())
            mun_sel = st.multiselect("Município", muns)
        else: st.warning("Mun n/d")

    with c_ies:
        mask = pd.Series([True]*len(df), index=df.index)
        if uf_sel: mask &= df['SIGLA_ESTADO'].isin(uf_sel)
        if mun_sel: mask &= df['IES_MUNIC'].isin(mun_sel)
        
        ies_disp = sorted(df[mask]['IES_LABEL'].astype(str).unique())
        if not ies_disp: st.error("Sem IES"); st.stop()
        ies_sel_label = st.selectbox("Instituição", ies_disp)

    # 4. SIDEBAR - TEASER PDF
    with st.sidebar:
        st.divider(); st.markdown("### 💼 Comercial")
        if st.button("📄 Teaser de Vendas", use_container_width=True):
            with st.spinner("Gerando PDF..."):
                try:
                    # -- A. Identifica IES e Localização (Ignora filtros de tela para contexto) --
                    row_ies = df[df['IES_LABEL'] == ies_sel_label].iloc[0]
                    uf_ies = row_ies['SIGLA_ESTADO'] if 'SIGLA_ESTADO' in df.columns else None
                    mun_ies = row_ies['IES_MUNIC'] if 'IES_MUNIC' in df.columns else None
                    ies_pura = ies_sel_label.split(' - ', 1)[1] if ' - ' in ies_sel_label else ies_sel_label

                    # -- B. Prepara Bases --
                    # Base Global: Todo o Brasil (com filtro P360 opcional)
                    mask_nac = pd.Series([True] * len(df), index=df.index)
                    if apenas_p360 and col_p360: mask_nac &= df[col_p360].astype(str).str.contains('S|Y|1|TRUE', case=False, na=False)
                    df_nt_nac = df[mask_nac].copy()

                    # Base Regional: Apenas a UF da IES selecionada (Autodetectado)
                    if uf_ies: df_nt_reg = df_nt_nac[df_nt_nac['SIGLA_ESTADO'] == uf_ies].copy()
                    else: df_nt_reg = df_nt_nac.copy()

                    # Base IES Alvo
                    df_ft = df_nt_nac[df_nt_nac['IES_LABEL'] == ies_sel_label].copy()

                    if df_ft.empty: st.error("IES sem dados"); st.stop()

                    # -- C. Cálculos --
                    # Compara IES x Regional para Gaps
                    grp = ['GRANDE_AREA', 'SUBESPECIALIDADE', 'DIAGNOSTICO']
                    t_i = df_ft.groupby(grp, observed=True)['ACERTO'].mean().reset_index(name='IES')
                    t_n = df_nt_reg.groupby(grp, observed=True)['ACERTO'].mean().reset_index(name='Nacional')
                    t_mer = pd.merge(t_i, t_n, on=grp)
                    t_mer['Diferença'] = (t_mer['IES'] - t_mer['Nacional']) * 100
                    top_gaps = t_mer.sort_values('Diferença', ascending=True).head(10)
                    ma, mn = calcular_potencial_evolucao(df_ft, df_nt_reg, top_gaps.head(5))

                    # IA
                    rec_ia = "Indisponível"
                    if not top_gaps.empty:
                        txt_p = preparar_portfolio_texto(df_port) if df_port is not None else ""
                        rec_ia = encontrar_match_inteligente(top_gaps.head(5), txt_p)

                    # Conceito
                    conc_t = "-"
                    if df_c_raw is not None:
                        m = df_c_raw[df_c_raw['IES_NOME'] == ies_pura]
                        if not m.empty: conc_t = str(m['CONCEITO'].values[0])

                    # -- D. Gráficos --
                    fig_nac = gerar_grafico_ranking_img(df_nt_nac, col_ies, ies_pura)
                    fig_reg = gerar_grafico_ranking_img(df_nt_reg, col_ies, ies_pura)

                    # -- E. PDF --
                    pdf_bytes = gerar_pdf_teaser(ies_pura, mun_ies, uf_ies, conc_t, ma, mn, top_gaps, fig_reg, fig_nac, rec_ia)
                    st.download_button("⬇️ Baixar Teaser", pdf_bytes, f"Teaser_{ies_pura}.pdf", 'application/pdf')
                    st.success("Sucesso!")
                except Exception as e: st.error(f"Erro: {e}")

    # 5. DASHBOARD PRINCIPAL
    ies_pura = ies_sel_label.split(' - ', 1)[1] if ' - ' in ies_sel_label else ies_sel_label
    st.title(f"🩺 Dashboard | {ies_pura}")
    st.divider()

    # Aplica filtros de tela (UF/Mun) para o Benchmark visualizado na tela
    mask_dash_ies = (df['IES_LABEL'] == ies_sel_label)
    mask_dash_nac = pd.Series([True]*len(df), index=df.index)
    
    if uf_sel and 'SIGLA_ESTADO' in df.columns: mask_dash_nac &= df['SIGLA_ESTADO'].isin(uf_sel)
    if mun_sel and 'IES_MUNIC' in df.columns: mask_dash_nac &= df['IES_MUNIC'].isin(mun_sel)
    if apenas_p360 and col_p360: mask_dash_nac &= df[col_p360].astype(str).str.contains('S|Y|1|TRUE', case=False, na=False)

    df_f = df[mask_dash_ies].copy()
    df_n = df[mask_dash_nac].copy()

    if df_f.empty: st.warning("Sem dados"); st.stop()

    # Métricas
    k1, k2, k3, k4, k5 = st.columns(5)
    m_ies = df_f['ACERTO'].mean()
    m_nac = df_n['ACERTO'].mean()
    gap = (m_ies - m_nac)*100
    
    k1.metric("Média IES", f"{m_ies:.1%}")
    k2.metric("Média Comparativa", f"{m_nac:.1%}")
    k3.metric("Gap", f"{gap:+.1f} pp", delta_color="normal" if gap>=0 else "inverse")
    
    # Busca Metadados Reais
    try:
        row = df_f.iloc[0]
        uf_d = row['SIGLA_ESTADO'] if 'SIGLA_ESTADO' in df.columns else "-"
        mun_d = row['IES_MUNIC'] if 'IES_MUNIC' in df.columns else "-"
    except: uf_d, mun_d = "-", "-"

    conc_d, prof_d = "-", "-"
    if df_c_raw is not None:
        m = df_c_raw[df_c_raw['IES_NOME'] == ies_pura]
        if not m.empty: 
            conc_d = str(m['CONCEITO'].values[0])
            prof_d = f"{m['PERCENTUAL_PROFICIENTES'].values[0]:.1%}"

    k4.metric("Conceito MEC", conc_d)
    
    # --- CORREÇÃO DE OVERLAP ---
    # Removi a margin-bottom negativa e diminuí a fonte para 11px
    with k5:
        st.markdown(f"<div style='color:#FD5E11;font-size:11px;font-weight:bold;margin-bottom:0px'>📍 {mun_d}/{uf_d}</div>", unsafe_allow_html=True)
        st.metric("% Profic.", prof_d)

    # Tabelas
    grp = ['GRANDE_AREA', 'SUBESPECIALIDADE', 'DIAGNOSTICO']
    t_i = df_f.groupby(grp, observed=True)['ACERTO'].mean().reset_index(name='IES')
    t_n = df_n.groupby(grp, observed=True)['ACERTO'].mean().reset_index(name='Nacional')
    tab = pd.merge(t_i, t_n, on=grp)
    tab['Diferença'] = (tab['IES'] - tab['Nacional']) * 100
    
    c_lac, c_des = st.columns(2)
    with c_lac: 
        st.subheader("🚩 Pontos de Atenção")
        st.dataframe(tab.sort_values('Diferença').head(10).style.format({'IES':'{:.1%}','Nacional':'{:.1%}','Diferença':'{:+.1f}'}).map(lambda v: 'color:red;font-weight:bold' if v<0 else None, subset=['Diferença']), use_container_width=True)
    with c_des: 
        st.subheader("🏆 Fortalezas")
        st.dataframe(tab.sort_values('Diferença', ascending=False).head(10).style.format({'IES':'{:.1%}','Nacional':'{:.1%}','Diferença':'{:+.1f}'}).map(lambda v: 'color:green;font-weight:bold' if v>0 else None, subset=['Diferença']), use_container_width=True)

    # Bolhas
    st.header("🎯 Matriz de Priorização")
    bubble_ies = df_f.groupby(['GRANDE_AREA', 'SUBESPECIALIDADE'], observed=True).agg({'ACERTO':'mean','NU_QUESTAO':'nunique'}).reset_index()
    bubble_nac = df_n.groupby(['GRANDE_AREA', 'SUBESPECIALIDADE'], observed=True)['ACERTO'].mean().reset_index(name='Nacional')
    viz = pd.merge(bubble_ies, bubble_nac, on=['GRANDE_AREA','SUBESPECIALIDADE'])
    viz['Gap'] = (viz['ACERTO'] - viz['Nacional']) * 100
    
    areas = sorted([str(a) for a in viz['GRANDE_AREA'].unique() if str(a)!='nan'])
    if areas:
        tabs = st.tabs(areas)
        for i, area in enumerate(areas):
            with tabs[i]:
                da = viz[viz['GRANDE_AREA'] == area]
                fig = px.scatter(da, x='NU_QUESTAO', y='Gap', size='NU_QUESTAO', color='Gap', hover_name='SUBESPECIALIDADE', color_continuous_scale=px.colors.diverging.RdYlGn, range_color=[-20,20])
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig, use_container_width=True)

    renderizar_acoes_finais(df_f)
else:
    st.info("Aguardando upload dos arquivos.")