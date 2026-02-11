import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
import os
import requests
import tempfile
import re
from fpdf import FPDF # type: ignore

# ==========================================
# 0. CONFIGURAÇÃO
# ==========================================
MODO_DEV = False # Deixe False para ler o arquivo inteiro

st.set_page_config(
    page_title="Paciente 360 | ENAMED Analytics",
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cores da Marca
P360_NAVY = "#1E3A5F"
P360_ORANGE = "#FD5E11"

# Estilização CSS
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
# 1. FUNÇÕES AUXILIARES (RANKING, IA, PDF)
# ==========================================

def calcular_posicao_ranking(df_completo, col_agrupamento, alvo_label):
    """
    Calcula a posição considerando o agrupamento (IES_LABEL) para diferenciar cursos.
    """
    # Agrupa por Label (Código + Nome)
    ranking = df_completo.groupby(col_agrupamento)['ACERTO'].agg(['mean', 'count']).reset_index()
    
    # Filtra dados irrelevantes (<10 alunos), mas mantendo o alvo
    ranking = ranking[(ranking['count'] >= 10) | (ranking[col_agrupamento] == alvo_label)]
    
    # Ordena
    ranking = ranking.sort_values('mean', ascending=False).reset_index(drop=True)
    ranking['Rank'] = ranking.index + 1
    
    total = len(ranking)
    try:
        posicao = ranking.loc[ranking[col_agrupamento] == alvo_label, 'Rank'].values[0]
    except:
        posicao = "-" 
        
    return posicao, total

def preparar_portfolio_texto(df_port):
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
    if not texto_portfolio:
        return "GAP_ESCOLHIDO: Geral\nCASO: -\nPORQUE: Portfólio não carregado.\nDINAMICA: -\nCOMO FAZER: Carregue o arquivo de portfólio."
    
    api_key = "106510904080513630747_fa3102b65ef19b25"
    url = "https://chat.maritaca.ai/api/chat/completions"
    
    lista_gaps_txt = ""
    for i, row in df_top_gaps.iterrows():
        lista_gaps_txt += f"- {row['SUBESPECIALIDADE']} ({row['DIAGNOSTICO']})\n"
    
    prompt = f"""
    Você é o Curador Pedagógico Sênior de uma faculdade de medicina.
    GAPS IDENTIFICADOS: {lista_gaps_txt}
    ACERVO: {texto_portfolio}
    TAREFA: Escolha o gap crítico e sugira UM caso.
    FORMATO:
    GAP_ESCOLHIDO: ...
    CASO: ...
    PORQUE: ...
    DINAMICA: ...
    COMO FAZER: ...
    """
    try:
        headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
        data = {"messages": [{"role": "user", "content": prompt}], "model": "sabia-4", "max_tokens": 400, "temperature": 0.3} 
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 200: return response.json()['choices'][0]['message']['content']
        else: return "GAP_ESCOLHIDO: Erro API\nCASO: -\nPORQUE: -\nDINAMICA: -\nCOMO FAZER: -"
    except Exception as e: return f"GAP_ESCOLHIDO: Erro\nCASO: -\nPORQUE: {str(e)[:50]}\nDINAMICA: -\nCOMO FAZER: -"

def gerar_grafico_ranking_img(df_completo, col_agrupamento, alvo_label):
    # Agrupa usando a coluna passada (IES_LABEL)
    ranking = df_completo.groupby(col_agrupamento)['ACERTO'].agg(['mean', 'count']).reset_index()
    ranking.columns = [col_agrupamento, 'ACERTO', 'VOLUME']
    
    ranking = ranking[(ranking['VOLUME'] >= 10) | (ranking[col_agrupamento] == alvo_label)]
    
    # Ordena Ascendente para o Plotly desenhar como Leaderboard
    ranking = ranking.sort_values('ACERTO', ascending=True).reset_index(drop=True)
    ranking['Posicao_Real'] = ranking['ACERTO'].rank(ascending=False).astype(int)
    
    # Labels e Cores
    ranking['Label'] = ranking.apply(lambda x: "Sua IES" if x[col_agrupamento] == alvo_label else f"{x['Posicao_Real']}° Lugar", axis=1)
    ranking['Cor'] = ranking.apply(lambda x: '#FD5E11' if x[col_agrupamento] == alvo_label else '#E0E0E0', axis=1)
    ranking['Texto_Barra'] = ranking['ACERTO'].apply(lambda x: f" {x:.1%}")

    # Janela de Vizinhos
    try:
        idx = ranking[ranking[col_agrupamento] == alvo_label].index[0]
        total = len(ranking)
        indices_top = [total-1, total-2, total-3] 
        indices_vizinhos = [idx, idx-1, idx+1]
        indices_finais = sorted(list(set(indices_top + indices_vizinhos)))
        indices_finais = [i for i in indices_finais if 0 <= i < total]
        df_plot = ranking.iloc[indices_finais].copy()
    except: 
        df_plot = ranking.tail(6).copy()

    # Gráfico Barra Horizontal Clean
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_plot['ACERTO'], y=df_plot['Label'], orientation='h',
        marker=dict(color=df_plot['Cor'], line=dict(color=df_plot['Cor'], width=1)),
        text=df_plot['Texto_Barra'], textposition='outside',
        textfont=dict(size=14, family='Arial', color='#333333'), cliponaxis=False
    ))

    fig.update_layout(
        plot_bgcolor='white', height=400, margin=dict(l=120, r=60, t=10, b=10),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, df_plot['ACERTO'].max() * 1.25]),
        yaxis=dict(showgrid=False, showline=False, tickfont=dict(size=12, color='#1E3A5F', family="Helvetica", weight="bold")),
        showlegend=False, bargap=0.3
    )
    return fig

def gerar_pdf_teaser(ies_nome, municipio, uf, conceito, media_ies, media_nac, media_top5, 
                     top_gaps, top_strengths, 
                     fig_ranking_reg, fig_ranking_nac, 
                     rank_nac_info, rank_reg_info):
    
    def sanitizar_texto(txt):
        if not isinstance(txt, str): return str(txt)
        mapa = {
            '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'", '\u2013': '-', '–': '-'
        }
        for o, d in mapa.items(): txt = txt.replace(o, d)
        return txt.encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.set_margins(15, 15, 15); pdf.set_auto_page_break(auto=True, margin=10); pdf.add_page()
    
    navy = (30, 58, 95); orange = (253, 94, 17); grey = (240, 240, 240)
    
   # ==============================================================================
    # PÁGINA 1
    # ==============================================================================
    pdf.set_fill_color(*navy); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_xy(15, 10); pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(255)
    pdf.cell(0, 8, sanitizar_texto('Diagnóstico Microdados ENAMED 2025'), 0, 1, 'L')
    pdf.set_xy(15, 19); pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, sanitizar_texto(f'IES: {ies_nome[:60]}...'), 0, 1, 'L')
    pdf.set_xy(15, 25); pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, sanitizar_texto(f"{municipio}/{uf}  |  Conceito ENAMED: {conceito}"), 0, 1, 'L')
    
    path_logo = os.path.join(os.path.dirname(__file__), "logo_branca.png")
    if os.path.exists(path_logo): pdf.image(path_logo, x=165, y=10, w=30)
    
    # --- NOVO: DISCLAIMER / FRASE INICIAL ---
    # Posicionado logo abaixo do cabeçalho azul (Y=42)
    pdf.set_y(42); pdf.set_x(15)
    pdf.set_font('Helvetica', 'I', 8); pdf.set_text_color(100, 100, 100) # Cinza e Itálico
    
    # Edite sua frase aqui:
    disclaimer_text = "Este relatório apresenta uma análise baseada nos microdados ENAMED 2025 da instituição. De caráter diagnóstico, o documento elucida forças e fragilidades, e os indicadores apresentados visam apoiar a gestão pedagógica e o direcionamento estratégico."
    pdf.multi_cell(180, 4, sanitizar_texto(disclaimer_text), 0, 'L')
    
    # --- SEÇÃO 1: PERFORMANCE (Ajustada para Y=52 para dar espaço ao disclaimer) ---
    pdf.set_y(60); pdf.set_text_color(*navy); pdf.set_font('Helvetica', 'B', 14); pdf.set_x(15)
    pdf.cell(0, 8, sanitizar_texto('1. Performance Comparativa'), 0, 1, 'L')
    
    y_c = pdf.get_y() + 2; w_c = 57.3; h_c = 25; gap = 4
    pdf.set_fill_color(*grey); pdf.rect(15, y_c, w_c, h_c, 'F')
    pdf.set_xy(15, y_c+4); pdf.set_font('Helvetica', '', 8); pdf.set_text_color(80)
    pdf.cell(w_c, 4, sanitizar_texto('Sua Média Geral'), 0, 2, 'C')
    pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(*navy)
    pdf.cell(w_c, 8, f"{media_ies:.1%}", 0, 2, 'C')
    pdf.set_fill_color(*grey); pdf.rect(15+w_c+gap, y_c, w_c, h_c, 'F')
    pdf.set_xy(15+w_c+gap, y_c+4); pdf.set_font('Helvetica', '', 8); pdf.set_text_color(80)
    pdf.cell(w_c, 4, sanitizar_texto('Média Nacional'), 0, 2, 'C')
    pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(*navy)
    pdf.cell(w_c, 8, f"{media_nac:.1%}", 0, 2, 'C')
    pdf.set_fill_color(*orange); pdf.rect(15+2*(w_c+gap), y_c, w_c, h_c, 'F')
    pdf.set_xy(15+2*(w_c+gap), y_c+4); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(255)
    pdf.cell(w_c, 4, sanitizar_texto('Referências Conceito 5'), 0, 2, 'C')
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(w_c, 8, f"{media_top5:.1%}", 0, 2, 'C')
    pdf.set_xy(15, y_c+h_c+2); pdf.set_font('Helvetica', 'I', 7); pdf.set_text_color(100)
    pdf.multi_cell(180, 3, sanitizar_texto(f"Comparativo da média de acertos de alunos vs Média Nacional e Cursos de Excelência (Conceito 5 ENAMED). Gap: {(media_top5-media_ies)*100:+.1f} pp."), 0, 'L')

    # --- SEÇÃO 2: POSICIONAMENTO ---
    # Aqui ganhamos espaço reduzindo a altura das imagens (Ranking)
    
    pdf.set_y(pdf.get_y() + 5); pdf.set_text_color(*navy); pdf.set_font('Helvetica', 'B', 14); pdf.set_x(15)
    pdf.cell(0, 8, sanitizar_texto('2. Posicionamento Competitivo'), 0, 1, 'L')
    
    # Ranking Nacional
    pos_n, tot_n = rank_nac_info
    pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(*navy); pdf.set_x(15)
    lbl_n = f'2.1. Cenário Nacional - {pos_n}º de {tot_n} Instituições' if tot_n > 0 else '2.1. Cenário Nacional'
    pdf.cell(0, 5, sanitizar_texto(lbl_n), 0, 1, 'L')
    
    y_img = pdf.get_y() + 1
    h_chart = 70 
    
    if fig_ranking_nac:
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False); tmp_name = tmp.name; tmp.close()
            fig_ranking_nac.write_image(tmp_name, scale=2)
            pdf.image(tmp_name, x=15, y=y_img, w=180, h=h_chart); os.remove(tmp_name)
        except: pass
    
    # Ranking Regional
    pdf.set_y(y_img + h_chart + 5); pdf.set_x(15) # Espaçamento dinâmico
    pos_r, tot_r = rank_reg_info
    lbl_r = f'2.2. Cenário Regional ({uf})' if uf else '2.2. Cenário Regional'
    lbl_r_final = f'{lbl_r} - {pos_r}º de {tot_r} Instituições' if tot_r > 0 else lbl_r
    pdf.cell(0, 5, sanitizar_texto(lbl_r_final), 0, 1, 'L')
    
    y_img = pdf.get_y() + 1
    if fig_ranking_reg:
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False); tmp_name = tmp.name; tmp.close()
            fig_ranking_reg.write_image(tmp_name, scale=2)
            pdf.image(tmp_name, x=15, y=y_img, w=180, h=h_chart); os.remove(tmp_name)
        except: pass

    # ==============================================================================
    # PÁGINA 2
    # ==============================================================================
    
    pdf.add_page()
    # 1. MARGEM SUPERIOR REDUZIDA (De 25 para 15) para ganhar espaço
    pdf.set_y(15)
    
    def desenhar_tabela_visual(titulo, df_dados, cor_tema_rgb, aplicar_blur=False):
        y_atual = pdf.get_y()
        pdf.set_fill_color(*cor_tema_rgb)
        pdf.rect(15, y_atual, 1.5, 8, 'F') 
        
        pdf.set_text_color(*navy); pdf.set_font('Helvetica', 'B', 14); pdf.set_x(18)
        pdf.cell(0, 8, sanitizar_texto(titulo), 0, 1, 'L')
        pdf.ln(2)
        
        cols = [28, 37, 75, 20, 20]
        headers = ["Grande Área", "Subespecialidade", "Diagnóstico", "Média", "Gap"]
        
        pdf.set_fill_color(*navy); pdf.set_text_color(255); pdf.set_font('Helvetica', 'B', 8); pdf.set_x(15)
        for i, h in enumerate(headers):
            align = 'C' if i >= 3 else 'L'
            pdf.cell(cols[i], 7, sanitizar_texto(h), 0, 0, align, 1)
        pdf.ln()
        
        pdf.set_font('Helvetica', '', 7)
        y_blur_start = 0 
        
        if df_dados.empty:
            pdf.set_text_color(0); pdf.set_x(15); pdf.cell(180, 8, "Sem dados.", 1, 1, 'C')
        else:
            for idx, (_, r) in enumerate(df_dados.iterrows()):
                pdf.set_x(15)
                blur_nesta_linha = aplicar_blur and (idx > 0)
                
                if blur_nesta_linha and y_blur_start == 0:
                    y_blur_start = pdf.get_y()
                
                if blur_nesta_linha:
                    pdf.set_fill_color(235, 235, 235)
                    pdf.rect(15, pdf.get_y(), 180, 6, 'F') 
                    pdf.set_fill_color(210, 210, 210)
                    for w in cols:
                        x_curr = pdf.get_x()
                        pdf.rect(x_curr + 1, pdf.get_y() + 1.5, w - 2, 3, 'F')
                        pdf.cell(w, 6, "", 0, 0)
                    pdf.ln()
                else:
                    if idx % 2 == 0: pdf.set_fill_color(255, 255, 255)
                    else: pdf.set_fill_color(248, 248, 248)
                    x_inicial = pdf.get_x(); y_inicial = pdf.get_y()
                    pdf.rect(x_inicial, y_inicial, 180, 6, 'F')
                    
                    pdf.set_text_color(50, 50, 50)
                    t1 = (r['GRANDE_AREA'][:18] + '..') if len(r['GRANDE_AREA']) > 18 else r['GRANDE_AREA']
                    t2 = (r['SUBESPECIALIDADE'][:24] + '..') if len(r['SUBESPECIALIDADE']) > 24 else r['SUBESPECIALIDADE']
                    t3 = (r['DIAGNOSTICO'][:55] + '..') if len(r['DIAGNOSTICO']) > 55 else r['DIAGNOSTICO']
                    
                    pdf.cell(cols[0], 6, sanitizar_texto(t1), 0, 0, 'L')
                    pdf.cell(cols[1], 6, sanitizar_texto(t2), 0, 0, 'L')
                    pdf.cell(cols[2], 6, sanitizar_texto(t3), 0, 0, 'L')
                    pdf.set_text_color(0); pdf.cell(cols[3], 6, f"{r['IES']:.1%}", 0, 0, 'C')
                    
                    x_gap = pdf.get_x(); y_gap = pdf.get_y()
                    pdf.set_fill_color(*cor_tema_rgb)
                    pdf.rect(x_gap + 2, y_gap + 1, 16, 4, 'F')
                    pdf.set_text_color(255, 255, 255); pdf.set_font('Helvetica', 'B', 7)
                    pdf.cell(cols[4], 6, f"{r['Diferença']:+.1f}", 0, 0, 'C')
                    
                    pdf.set_font('Helvetica', '', 7)
                    pdf.ln() 

        if aplicar_blur and y_blur_start > 0:
            altura_total_blur = (len(df_dados) - 1) * 6
            card_w = 120; card_h = 16
            card_x = (210 - card_w) / 2
            card_y = y_blur_start + (altura_total_blur / 2) - (card_h / 2)
            
            pdf.set_fill_color(200, 200, 200)
            pdf.rect(card_x + 1, card_y + 1, card_w, card_h, 'F')
            pdf.set_fill_color(255, 255, 255); pdf.set_draw_color(*navy)
            pdf.rect(card_x, card_y, card_w, card_h, 'DF')
            
            pdf.set_xy(card_x, card_y + 3)
            pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(*navy)
            pdf.cell(card_w, 4, sanitizar_texto(" ANÁLISE COMPLETA DISPONÍVEL PARA SUA INSTITUIÇÃO"), 0, 2, 'C')
            pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(*orange)
            pdf.cell(card_w, 5, sanitizar_texto("Entre em contato com nossa equipe para desbloquear"), 0, 0, 'C')
            
            pdf.set_y(y_blur_start + altura_total_blur)
        
        # 2. ESPAÇAMENTO ENTRE TABELAS AUMENTADO (De 3 para 8)
        pdf.ln(8)

    desenhar_tabela_visual("3. Pontos Críticos: 5 temas com maior defasagem", top_gaps, (200, 0, 0), aplicar_blur=False)
    desenhar_tabela_visual("4. Destaques: 5 temas com melhor desempenho frente à média nacional", top_strengths, (0, 128, 0), aplicar_blur=True)
    
    # ==============================================================================
    # ÁREA DE APRESENTAÇÃO
    # ==============================================================================
    
    y_plat = pdf.get_y() + 2 # Respiro menor aqui
    
    # 4. TRAVA DE SEGURANÇA: Calcula o fundo apenas até onde o Box Final vai começar (232)
    # Assim evita que o fundo cinza vaze por baixo do azul
    y_box_final = 205 
    h_restante = y_box_final - y_plat 
    
    if h_restante > 30:
        pdf.set_fill_color(252, 252, 252)
        pdf.rect(0, y_plat, 210, h_restante, 'F')
        
        pdf.set_y(y_plat + 6)
        
        # --- COLUNA ESQUERDA ---
        pdf.set_x(15)
        pdf.set_text_color(*navy); pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(90, 8, sanitizar_texto("      Inteligência para o dia a dia"), 0, 1, 'L')
        
        pdf.ln(2)
        pdf.set_x(15)
        pdf.set_font('Helvetica', '', 9); pdf.set_text_color(60, 60, 60)
        intro = (
            "Não basta identificar os erros: é preciso corrigi-los na prática. "
            "O Paciente 360 conecta aprendizagem, prática e avaliação."
        )
        pdf.multi_cell(90, 4.5, sanitizar_texto(intro))
        pdf.ln(4)

        # --- LISTA DE BENEFÍCIOS ---
        beneficios = [
            ("Feedback imediato", "para o estudante"),
            ("Apresentação interativa", "em sala de aula"),
            ("Raciocínio Clínico", "estruturado e guiado"),
            ("Matriz Curricular", "alinhada aos casos"),
            ("Correção por IA", "em avaliação individual")
        ]

        for destaque, resto in beneficios:
            pdf.set_x(15)
            x_check = pdf.get_x()
            
            # 3. CHECKMARK / BULLET MAIS ALTO (Removemos o +1, agora é direto no Y)
            y_check = pdf.get_y() # Subiu um pouco
            
            pdf.set_draw_color(*orange)
            pdf.set_line_width(0.7)
            pdf.line(x_check, y_check + 1.5, x_check + 1.2, y_check + 3)
            pdf.line(x_check + 1.2, y_check + 3, x_check + 3.5, y_check)
            
            # Texto
            pdf.set_x(x_check + 5)
            pdf.set_text_color(*navy); pdf.set_font('Helvetica', 'B', 8)
            pdf.write(5, sanitizar_texto(destaque)) 
            
            pdf.set_text_color(80, 80, 80); pdf.set_font('Helvetica', '', 8)
            pdf.write(5, sanitizar_texto(f" {resto}"))
            pdf.ln(6) 

# --- COLUNA DIREITA: IMAGEM + LEGENDA (TEXTO CENTRALIZADO NA BARRA) ---
        x_img = 115
        y_img = y_plat + 6
        w_img = 80
        
        path_img_simulacao = "cenario_paciente.png" 
        if os.path.exists(path_img_simulacao):
            h_img = 45 
            pdf.image(path_img_simulacao, x=x_img, y=y_img, w=w_img, h=h_img)
            
            # Posição Y inicial da legenda
            y_legenda = y_img + h_img + 3
            
            # Altura total da barra lateral (Definimos como 12mm)
            h_bar = 12
            
            # 1. Desenha a Barra Laranja
            pdf.set_fill_color(*orange)
            pdf.rect(x_img, y_legenda, 1, h_bar, 'F')
            
            # 2. Centralização Vertical do Texto
            # O texto tem aprox. 2 linhas. Altura da linha = 3.5mm. Total Texto = 7mm.
            # Espaço livre = 12mm (barra) - 7mm (texto) = 5mm.
            # Offset (Margem superior) = 5mm / 2 = 2.5mm.
            y_texto_centralizado = y_legenda + 2.5
            
            pdf.set_xy(x_img + 3, y_texto_centralizado)
            pdf.set_font('Helvetica', 'I', 8); pdf.set_text_color(80, 80, 80)
            
            msg_legenda = (
                "Da análise de dados à prática: pacientes padronizados "
                "para correção imediata dos gaps identificados."
            )
            # Mantive alinhado à Esquerda ('L') pois combina mais com a barra lateral
            pdf.multi_cell(w_img - 3, 3.5, sanitizar_texto(msg_legenda), 0, 'L')
            
        else:
            pdf.set_fill_color(220, 220, 220)
            pdf.rect(x_img, y_img, w_img, 45, 'F')
            pdf.set_xy(x_img, y_img + 20)
            pdf.cell(w_img, 5, "Imagem não encontrada", 0, 1, 'C')
# ==============================================================================
    # BOX FINAL: BIG NUMBERS + CLAIM (VERSÃO CLEAN / FUNDO BRANCO)
    # ==============================================================================
    
    # Posição Y (Mantemos a mesma altura para diagramação)
    y_box = 205 
    
    # [OPCIONAL] Uma linha fina cinza no topo para separar da seção anterior
    pdf.set_draw_color(*orange); pdf.set_line_width(0.2)
    pdf.line(15, y_box, 195, y_box)

    # --- LADO ESQUERDO (85%) ---
    
    # 1. Número 85% (Agora em NAVY para contrastar com o branco)
    pdf.set_xy(15, y_box + 6) 
    pdf.set_text_color(*navy); pdf.set_font('Helvetica', 'B', 40) # Aumentei um pouco fonte
    pdf.cell(35, 14, "85%", 0, 0, 'C') 
    
    # 2. Legenda "DAS QUESTÕES" (Mantém Laranja)
    pdf.set_xy(15, y_box + 20)
    pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(*orange)
    pdf.cell(35, 6, "DAS QUESTÕES", 0, 0, 'C')

    # 3. Texto Explicativo (Agora em CINZA ESCURO)
    pdf.set_xy(55, y_box + 8) 
    pdf.set_font('Helvetica', '', 10); pdf.set_text_color(60, 60, 60) # Cinza escuro
    msg_85 = "Do ENAMED 2025\nexigem raciocínio clínico\ne não memorização."
    pdf.multi_cell(45, 4.5, sanitizar_texto(msg_85), align='L')

    # --- LINHA DIVISÓRIA CENTRAL (Agora em CINZA CLARO) ---
    pdf.set_draw_color(200, 200, 200); pdf.set_line_width(0.5)
    pdf.line(105, y_box + 5, 105, y_box + 30)

   # --- LADO DIREITO (80%) ---
    
    # 1. Número 80% (Agora em NAVY)
    pdf.set_xy(110, y_box + 6)
    pdf.set_text_color(*navy); pdf.set_font('Helvetica', 'B', 40)
    pdf.cell(35, 14, "80%", 0, 0, 'C') 
    
    # 2. Legenda "DO PORTFÓLIO" (Mantém Laranja)
    pdf.set_xy(110, y_box + 20)
    pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(*orange)
    pdf.cell(35, 6, "DOS CASOS", 0, 0, 'C')

    # 3. Texto Explicativo (Agora em CINZA ESCURO)
    pdf.set_xy(150, y_box + 8)
    pdf.set_font('Helvetica', '', 10); pdf.set_text_color(60, 60, 60)
    msg_80 = "Cobrados no ENAMED\n2025 já estão prontos na\nplataforma Paciente 360."
    pdf.multi_cell(45, 4.5, sanitizar_texto(msg_80), align='L')

    pdf.set_draw_color(*orange); pdf.set_line_width(0.2)
    pdf.line(15, y_box + 36, 195, y_box + 36)

# ==============================================================================
    # IMAGOTIPO NAVY (LOGO + FRASE)
    # ==============================================================================
    
    # 1. Desenha o Logo
    y_logo = 252  # Subi um pouquinho (era 255) para dar espaço para a frase
    w_logo = 70   
    x_logo = (210 - w_logo) / 2 
    
    path_logo_navy = "logo_navy.png" 
    
    if os.path.exists(path_logo_navy):
        pdf.image(path_logo_navy, x=x_logo, y=y_logo, w=w_logo)
    else:
        # Placeholder se não tiver imagem
        pdf.set_xy(x_logo, y_logo)
        pdf.set_draw_color(200); pdf.set_line_width(0.5); pdf.set_dash_pattern(1, 1)
        pdf.rect(x_logo, y_logo, w_logo, 15)
        pdf.set_dash_pattern()

    # 2. Nova Frase (Tagline) Abaixo do Logo
    # Logo tem ~15mm de altura visual. Y=252 + 15 = 267.
    # Vamos colocar a frase em Y=270 para ter um respiro.
    
    y_frase = y_logo + 22 # Ajuste conforme a altura real do seu logo
    pdf.set_xy(0, y_frase)
    
    # Configuração da Fonte (Navy, Itálico ou Normal, tamanho médio)
    pdf.set_text_color(*navy)
    pdf.set_font('Helvetica', 'I', 10) # B = Bold (Negrito). Use 'I' para Itálico se preferir.
    
    # A FRASE QUE VOCÊ QUER INSERIR:
    frase_abaixo_logo = "O saber médico na era da inovação" 
    pdf.cell(210, 6, sanitizar_texto(frase_abaixo_logo), 0, 0, 'C')


    # --- RODAPÉ MINIMALISTA (MANTIDO) ---
    y_footer = 285
    pdf.set_y(y_footer)
    pdf.set_draw_color(*orange); pdf.set_line_width(0.5)
    pdf.line(15, y_footer, 195, y_footer)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# ==========================================
# 2. CARREGAMENTO
# ==========================================

@st.cache_data(show_spinner=False)
def carregar_dados(file, default_path, is_excel=False):
    limite = 500 if MODO_DEV else None
    source = file if file else (default_path if os.path.exists(default_path) else None)
    if not source: return None
    try:
        name = getattr(source, 'name', str(source))
        if name.endswith('.parquet'): df = pd.read_parquet(source)
        elif is_excel or name.endswith('.xlsx'): df = pd.read_excel(source, nrows=limite)
        else: df = pd.read_csv(source, sep=None, engine='python', encoding='utf-8-sig', nrows=limite)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except: return None

@st.cache_data(show_spinner="Processando...")
def processar_base(df_a, df_g, df_m):
    # Carrega Mapa
    path_mapa = os.path.join(os.path.dirname(__file__), "mapeamento_Estados.parquet")
    if os.path.exists(path_mapa):
        try:
            df_loc = pd.read_parquet(path_mapa)
            df_loc.columns = [str(c).strip().upper() for c in df_loc.columns]
            col_curso = next((c for c in df_a.columns if c in ['CO_CURSO', 'COD_CURSO']), None)
            if col_curso:
                df_a[col_curso] = pd.to_numeric(df_a[col_curso], errors='coerce').fillna(0).astype('int64')
                df_loc['CO_CURSO'] = pd.to_numeric(df_loc['CO_CURSO'], errors='coerce').fillna(0).astype('int64')
                cols_drop = [c for c in ['SIGLA_ESTADO', 'IES_MUNIC'] if c in df_a.columns]
                if cols_drop: df_a.drop(columns=cols_drop, inplace=True)
                df_a = pd.merge(df_a, df_loc[['CO_CURSO', 'SIGLA_ESTADO', 'IES_MUNIC']], on=col_curso, how='left')
        except: pass

    col_ies = next(c for c in df_a.columns if 'IES_NOME' in c or 'NO_IES' in c)
    col_cad = next(c for c in df_a.columns if 'CADERNO' in c)
    col_p360 = next((c for c in df_a.columns if 'P360' in c), None)

    for d in [df_a, df_g, df_m]:
        if col_cad in d.columns: d[col_cad] = pd.to_numeric(d[col_cad], errors='coerce').fillna(1).astype('int16')

    q_cols = [c for c in df_a.columns if 'DS_VT_ESC_OBJ' in c]
    mapa_q = {col: int(re.search(r'\d+', col).group()) for col in q_cols if re.search(r'\d+', col)}
    
    # Inclui CO_CURSO no melt para o IES_LABEL
    id_vars = [col_ies, col_cad]
    if col_p360: id_vars.append(col_p360)
    if 'SIGLA_ESTADO' in df_a.columns: id_vars.append('SIGLA_ESTADO')
    if 'IES_MUNIC' in df_a.columns: id_vars.append('IES_MUNIC')
    if 'CO_CURSO' in df_a.columns: id_vars.append('CO_CURSO') 

    df_long = df_a.melt(id_vars=id_vars, value_vars=q_cols, var_name='ORIGEM', value_name='RESPOSTA')
    df_long['NU_QUESTAO'] = df_long['ORIGEM'].map(mapa_q).astype('int16')
    
    q_gab = [c for c in df_g.columns if 'DS_VT_GAB_OBJ' in c]
    mapa_gab = {col: int(re.search(r'\d+', col).group()) for col in q_gab if re.search(r'\d+', col)}
    df_gl = df_g.melt(id_vars=[col_cad], value_vars=q_gab, var_name='ORIGEM', value_name='GABARITO')
    df_gl['NU_QUESTAO'] = df_gl['ORIGEM'].map(mapa_gab).astype('int16')
    
    df_m_final = pd.merge(df_long.dropna(subset=['NU_QUESTAO']), df_gl.drop(columns=['ORIGEM']).dropna(subset=['NU_QUESTAO']), on=[col_cad, 'NU_QUESTAO'])
    
    if 'NU_QUESTAO' in df_m.columns:
        df_m['NU_QUESTAO'] = pd.to_numeric(df_m['NU_QUESTAO'], errors='coerce').fillna(0).astype('int16')
        df_m_final = pd.merge(df_m_final, df_m, on=[col_cad, 'NU_QUESTAO'], how='left')

    df_m_final['ACERTO'] = ((df_m_final['RESPOSTA'].str.upper() == df_m_final['GABARITO'].str.upper()) | (df_m_final['GABARITO'] == 'ANULADA')).astype('int8')

    return df_m_final, col_ies, col_cad, col_p360

# ==========================================
# 3. INTERFACE E LÓGICA
# ==========================================

# Sidebar Upload
with st.sidebar:
    path_logo = os.path.join(os.path.dirname(__file__), "logo_branca.png")
    if os.path.exists(path_logo): st.image(path_logo, use_container_width=True)
    st.divider(); st.markdown("### 📂 Importação")
    u_a = st.file_uploader("Alunos", type=["csv", "parquet"])
    u_g = st.file_uploader("Gabarito", type=["csv", "parquet"])
    u_m = st.file_uploader("Mapa", type=["xlsx"])
    u_p = st.file_uploader("Portfólio", type=["csv", "xlsx"])
    apenas_p360 = st.checkbox("Benchmark P360", value=False)

# Carrega Dados
df_a = carregar_dados(u_a, "base_alunos.csv")
df_g = carregar_dados(u_g, "base_gabarito.csv")
df_m = carregar_dados(u_m, "base_mapeamento.xlsx", True)
df_port = carregar_dados(u_p, "portfolio_casos.csv")
df_c_raw = carregar_dados(None, "conceitos_ies.csv")

if df_a is not None and df_g is not None and df_m is not None:
    
    # Processa
    df, col_ies, col_cad, col_p360 = processar_base(df_a, df_g, df_m)
    
    # --- IES_LABEL (Fundamental para 350 IES) ---
    if 'CO_CURSO' in df.columns:
        df['IES_LABEL'] = df['CO_CURSO'].astype(str) + " - " + df[col_ies].astype(str)
    else:
        df['IES_LABEL'] = df[col_ies].astype(str)
    
    # Médias
    MEDIA_GERAL = df['ACERTO'].mean()
    MEDIA_TOP = MEDIA_GERAL * 1.15

    if df_c_raw is not None:
        try:
            col_nota = next((c for c in df_c_raw.columns if c in ['CONCEITO', 'CPC', 'NOTA']), None)
            col_cod = next((c for c in df_c_raw.columns if c in ['CO_CURSO', 'COD_CURSO']), None)
            if col_nota and col_cod:
                s_notas = df_c_raw[col_nota].astype(str).str.replace(',', '.').str.strip()
                top_cods = df_c_raw[s_notas.isin(['5','5.0'])][col_cod].unique()
                col_cur_df = next((c for c in df.columns if c in ['CO_CURSO','COD_CURSO']), None)
                if col_cur_df:
                    m = df[col_cur_df].isin(top_cods)
                    if m.sum() > 0: MEDIA_TOP = df.loc[m, 'ACERTO'].mean()
        except: pass
    
    # Filtros Seguros (Sem erro de lista)
    c1, c2, c3 = st.columns([1, 1, 3])
    with c1: 
        ufs = sorted(df['SIGLA_ESTADO'].dropna().unique()) if 'SIGLA_ESTADO' in df.columns else []
        uf_sel = st.multiselect("UF", ufs)
    with c2:
        mask_m = pd.Series(True, index=df.index)
        if uf_sel: mask_m &= df['SIGLA_ESTADO'].isin(uf_sel)
        muns = sorted(df[mask_m]['IES_MUNIC'].dropna().unique()) if 'IES_MUNIC' in df.columns else []
        mun_sel = st.multiselect("Município", muns)
    with c3:
        mask_i = pd.Series(True, index=df.index)
        if uf_sel: mask_i &= df['SIGLA_ESTADO'].isin(uf_sel)
        if mun_sel: mask_i &= df['IES_MUNIC'].isin(mun_sel)
        ies_disp = sorted(df[mask_i]['IES_LABEL'].dropna().unique())
        if not ies_disp: st.error("Sem IES"); st.stop()
        ies_sel_label = st.selectbox("Instituição", ies_disp)

    with st.sidebar:
        st.divider()
        st.markdown("### 💼 Comercial")
        
        # Verifica se a variável existe e não está vazia (Mais seguro que locals())
        if 'ies_sel_label' in globals() and ies_sel_label:
            
            if st.button("📄 Teaser de Vendas", use_container_width=True):
                with st.spinner("Gerando PDF..."):
                    try:
                        # 1. Preparação das Bases
                        mask_nac = pd.Series(True, index=df.index)
                        if apenas_p360 and col_p360: 
                            mask_nac &= df[col_p360].astype(str).str.contains('S|Y|1|TRUE', case=False, na=False)
                        
                        df_nac = df[mask_nac].copy()
                        
                        # Validação de segurança
                        if df_nac[df_nac['IES_LABEL'] == ies_sel_label].empty:
                             st.error("Sem dados para esta IES nos filtros selecionados.")
                             st.stop()

                        row = df[df['IES_LABEL'] == ies_sel_label].iloc[0]
                        uf_i = row['SIGLA_ESTADO'] if 'SIGLA_ESTADO' in df.columns else None
                        mun_i = row['IES_MUNIC'] if 'IES_MUNIC' in df.columns else None
                        ies_pura = ies_sel_label.split(' - ', 1)[1] if ' - ' in ies_sel_label else ies_sel_label
                        
                        df_reg = df_nac[df_nac['SIGLA_ESTADO'] == uf_i].copy() if uf_i else df_nac.copy()
                        df_ies = df_nac[df_nac['IES_LABEL'] == ies_sel_label].copy()

                        # 2. Rankings
                        pos_n, tot_n = calcular_posicao_ranking(df_nac, 'IES_LABEL', ies_sel_label)
                        pos_r, tot_r = calcular_posicao_ranking(df_reg, 'IES_LABEL', ies_sel_label)
                        
                        # 3. Gráficos
                        fig_n = gerar_grafico_ranking_img(df_nac, 'IES_LABEL', ies_sel_label)
                        fig_r = gerar_grafico_ranking_img(df_reg, 'IES_LABEL', ies_sel_label)
                        
                        # 4. Gaps e Fortalezas
                        grp = ['GRANDE_AREA', 'SUBESPECIALIDADE', 'DIAGNOSTICO']
                        gaps = pd.merge(
                            df_ies.groupby(grp, observed=True)['ACERTO'].mean().reset_index(name='IES'),
                            df_reg.groupby(grp, observed=True)['ACERTO'].mean().reset_index(name='Nacional'),
                            on=grp
                        )
                        gaps['Diferença'] = (gaps['IES'] - gaps['Nacional']) * 100
                        
                        top_gaps = gaps.sort_values('Diferença', ascending=True).head(5)
                        top_strengths = gaps.sort_values('Diferença', ascending=False).head(5)
                        
                        # 5. Conceito MEC (Busca robusta pelo Código)
                        conc_t = "-"
                        if df_c_raw is not None:
                            try:
                                cod_sel = ies_sel_label.split(' - ')[0].strip()
                                # Tenta achar colunas de Código e Nota
                                col_cod_c = next((c for c in df_c_raw.columns if c in ['CO_CURSO', 'COD_CURSO', 'CO_IES', 'COD_IES', 'CODIGO_IES']), None)
                                col_nota_c = next((c for c in df_c_raw.columns if c in ['CONCEITO', 'NOTA', 'CPC', 'IGC', 'CONCEITO_ENADE']), None)
                                
                                if col_cod_c and col_nota_c:
                                    # Garante que ambos sejam string para comparar "100688" com "100688"
                                    df_c_raw[col_cod_c] = df_c_raw[col_cod_c].astype(str).str.strip()
                                    m = df_c_raw[df_c_raw[col_cod_c] == cod_sel]
                                    
                                    if not m.empty:
                                        conc_t = str(m[col_nota_c].values[0])
                            except Exception as e:
                                print(f"Erro ao buscar conceito: {e}")

                        # 6. Geração do PDF
                        # Removemos 'rec_ia' daqui pois a função def não pede mais
                        pdf_bytes = gerar_pdf_teaser(
                            ies_pura, mun_i, uf_i, conc_t, 
                            df_ies['ACERTO'].mean(), MEDIA_GERAL, MEDIA_TOP,
                            top_gaps, top_strengths,
                            fig_r, fig_n, 
                            (pos_n, tot_n), (pos_r, tot_r)
                        )
                        
                        st.download_button("⬇️ Baixar Teaser PDF", pdf_bytes, f"Teaser_{ies_pura}.pdf", "application/pdf")
                        st.success("Relatório gerado com sucesso!")
                        
                    except Exception as e: 
                        st.error(f"Erro ao gerar PDF: {e}")
                        print(e) # Imprime no terminal para debug
        else:
            st.info("Aguardando seleção da IES...")

    # --- DASHBOARD VISUAL (RESTAURADO) ---
    st.title(f"🩺 Dashboard | {ies_sel_label.split(' - ',1)[1]}")
    st.divider()
    
    # Aplica filtros do dashboard
    mask_dash = pd.Series(True, index=df.index)
    if uf_sel: mask_dash &= df['SIGLA_ESTADO'].isin(uf_sel)
    if mun_sel: mask_dash &= df['IES_MUNIC'].isin(mun_sel)
    if apenas_p360 and col_p360: mask_dash &= df[col_p360].astype(str).str.contains('S|Y|1|TRUE', case=False, na=False)

    df_d_ies = df[df['IES_LABEL'] == ies_sel_label].copy()
    df_d_nac = df[mask_dash].copy() # Benchmark comparativo selecionado
    
    if df_d_ies.empty: st.warning("Sem dados"); st.stop()

    # Métricas
    k1, k2, k3, k4, k5 = st.columns(5)
    m_ies = df_d_ies['ACERTO'].mean()
    m_nac = df_d_nac['ACERTO'].mean()
    gap = (m_ies - m_nac)*100
    
    k1.metric("Média IES", f"{m_ies:.1%}")
    k2.metric("Média Comparativa", f"{m_nac:.1%}")
    k3.metric("Gap", f"{gap:+.1f} pp", delta_color="normal" if gap>=0 else "inverse")
    
    # Info Extra
    conc_d, prof_d = "-", "-"
    if df_c_raw is not None:
        try:
            m = df_c_raw[df_c_raw['IES_NOME'].astype(str).str.contains(ies_sel_label.split(' - ',1)[1], case=False, na=False)]
            if not m.empty: 
                conc_d = str(m['CONCEITO'].values[0])
                prof_d = f"{m['PERCENTUAL_PROFICIENTES'].values[0]:.1%}"
        except: pass
    
    k4.metric("Conceito MEC", conc_d)
    k5.metric("Proficiência", prof_d)

    # Tabelas Fortalezas/Atenção
    grp = ['GRANDE_AREA', 'SUBESPECIALIDADE', 'DIAGNOSTICO']
    t_i = df_d_ies.groupby(grp, observed=True)['ACERTO'].mean().reset_index(name='IES')
    t_n = df_d_nac.groupby(grp, observed=True)['ACERTO'].mean().reset_index(name='Nacional')
    tab = pd.merge(t_i, t_n, on=grp)
    tab['Diferença'] = (tab['IES'] - tab['Nacional']) * 100
    
    c_lac, c_des = st.columns(2)
    with c_lac: 
        st.subheader("🚩 Pontos de Atenção")
        st.dataframe(tab.sort_values('Diferença').head(10).style.format({'IES':'{:.1%}','Nacional':'{:.1%}','Diferença':'{:+.1f}'}).map(lambda v: 'color:red;font-weight:bold' if v<0 else None, subset=['Diferença']), use_container_width=True)
    with c_des: 
        st.subheader("🏆 Fortalezas")
        st.dataframe(tab.sort_values('Diferença', ascending=False).head(10).style.format({'IES':'{:.1%}','Nacional':'{:.1%}','Diferença':'{:+.1f}'}).map(lambda v: 'color:green;font-weight:bold' if v>0 else None, subset=['Diferença']), use_container_width=True)

    # Gráfico de Bolhas (Matriz de Priorização)
    st.header("🎯 Matriz de Priorização")
    bubble_ies = df_d_ies.groupby(['GRANDE_AREA', 'SUBESPECIALIDADE'], observed=True).agg({'ACERTO':'mean','NU_QUESTAO':'nunique'}).reset_index()
    bubble_nac = df_d_nac.groupby(['GRANDE_AREA', 'SUBESPECIALIDADE'], observed=True)['ACERTO'].mean().reset_index(name='Nacional')
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
    
    # Download Excel da IES
    st.divider()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_d_ies.to_excel(writer, index=False)
    st.download_button("📊 Baixar Dados da IES (Excel)", output.getvalue(), "dados_ies.xlsx")

else:
    st.info("Aguardando upload dos arquivos.")