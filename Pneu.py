import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# ======================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================
st.set_page_config(
    page_title="Gestão de Pneus",
    layout="wide",
    page_icon="🚛"
)

# Cores do tema Ambev
primary_color = "#0a5cb8"
secondary_color = "#00a0e1"
background_color = "#f0f8ff"
text_color = "#003366"

# Aplicar estilo personalizado
st.markdown(f"""
    <style>
        /* Configurações gerais */
        .main {{
            background-color: {background_color};
        }}
        .css-18e3th9 {{background-color: {background_color};}}
        .css-1d391kg {{background-color: {primary_color};}}
        .st-bb {{background-color: {primary_color};}}
        .st-at {{background-color: {secondary_color};}}
        .st-ae {{background-color: {secondary_color};}}
        .css-1v3fvcr {{color: {text_color};}}
        .css-1q8dd3e {{color: {text_color};}}
        
        /* Cards de métricas */
        .metric-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 15px;
            border-left: 5px solid {primary_color};
        }}
        .metric-title {{
            font-size: 14px;
            font-weight: 600;
            color: {text_color};
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            color: {primary_color};
            margin-bottom: 5px;
        }}
        .metric-subtitle {{
            font-size: 12px;
            color: {secondary_color};
        }}
    </style>
""", unsafe_allow_html=True)

# ======================================
# CARREGAMENTO DE DADOS
# ======================================

# Função para carregar os dados do arquivo
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

st.title("Carregar Dados do Arquivo")
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

# Inicialização de variáveis antes do upload
df = pd.DataFrame()

# Se o arquivo for carregado, executa o processamento
if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Conversão para float nos sulcos
    sulco_cols = [
        "SULCO INTERNO", "SULCO CENTRAL INTERNO",
        "SULCO CENTRAL EXTERNO", "SULCO EXTERNO", "MENOR SULCO"
    ]
    df["DATA E HORA"] = pd.to_datetime(df["DATA E HORA"])

    for col in sulco_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Exibe o DataFrame processado
    #st.write(df)

# Se o arquivo ainda não foi carregado
else:
    st.write("Por favor, faça o upload de um arquivo Excel para continuar.")
    st.stop()

# ======================================
# BARRA LATERAL - FILTROS
# ======================================
st.sidebar.header("🔍 Filtros")
st.sidebar.markdown("Selecione os critérios para análise:")

marca = st.sidebar.selectbox("Marca do Pneu", df["MARCA DO PNEU"].dropna().unique())
vida = st.sidebar.selectbox("Vida Atual", df["VIDA ATUAL"].dropna().unique())
banda = st.sidebar.selectbox("Banda Aplicada", df["BANDA APLICADA"].dropna().unique())
placa = st.sidebar.selectbox("Placa", df["PLACA"].dropna().unique())
pneu = st.sidebar.selectbox("Número do Pneu", df["PNEU"].dropna().unique())
km_adicional = st.sidebar.number_input("KM adicional para projeção", min_value=0, value=5000, step=500)

# ======================================
# FILTRAGEM DE DADOS
# ======================================
df_filtrado = df[
    (df["MARCA DO PNEU"] == marca) &
    (df["VIDA ATUAL"] == vida) &
    (df["BANDA APLICADA"] == banda) &
    (df["PLACA"] == placa) &
    (df["PNEU"] == pneu)
].copy()

# Verificação de Filtros: Se o DataFrame estiver vazio, interrompe o processo e exibe uma mensagem de aviso
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados. Verifique se todos os filtros foram configurados corretamente.")
    st.stop()

# Processamento dos dados
df_filtrado = df_filtrado.dropna(subset=["SULCO INTERNO", "SULCO CENTRAL INTERNO", 
                                        "SULCO CENTRAL EXTERNO", "SULCO EXTERNO", 
                                        "KM NO MOMENTO DA AFERIÇÃO"])
df_filtrado = df_filtrado.sort_values(by="DATA E HORA")

# Cálculo de KM rodado entre aferições
df_filtrado["KM ANTERIOR"] = df_filtrado["KM NO MOMENTO DA AFERIÇÃO"].shift(1)
df_filtrado["KM RODADO"] = df_filtrado["KM NO MOMENTO DA AFERIÇÃO"] - df_filtrado["KM ANTERIOR"]

# Cálculo de desgaste
desgaste_cols = ["SULCO INTERNO", "SULCO CENTRAL INTERNO", "SULCO CENTRAL EXTERNO", "SULCO EXTERNO"]
resultados = {}

for col in desgaste_cols:
    df_filtrado[f"{col}_ANT"] = df_filtrado[col].shift(1)
    df_filtrado[f"DESGASTE_{col}"] = df_filtrado[f"{col}_ANT"] - df_filtrado[col]
    df_filtrado[f"DESGASTE_POR_KM_{col}"] = df_filtrado[f"DESGASTE_{col}"] / df_filtrado["KM RODADO"]

# Dados mais recentes
ultimo = df_filtrado.iloc[-1]

# ======================================
# SEÇÃO DE PREVISÃO
# ======================================
st.title(f"📊 Análise do Pneu {pneu} - Placa {placa}")

# Cabeçalho com informações básicas
st.markdown(f"""
    <div style="background-color:{primary_color};padding:15px;border-radius:10px;color:white;margin-bottom:20px;">
        <h4 style="color:white;margin:0;">Marca: {marca} | Vida: {vida} | Banda: {banda}</h4>
    </div>
""", unsafe_allow_html=True)

# Previsão de desgaste
st.subheader("🔮 Projeção de Desgaste - IA")
st.markdown(f"Previsão de desgaste após **{km_adicional} km** adicionais:")

col1, col2, col3, col4 = st.columns(4)

for idx, col in enumerate(desgaste_cols):
    with [col1, col2, col3, col4][idx]:
        desgaste_medio = df_filtrado[f"DESGASTE_POR_KM_{col}"].mean()
        sulco_atual = ultimo[col]
        
        if pd.isna(desgaste_medio) or desgaste_medio <= 0:
            st.error(f"Dados insuficientes para {col.split('_')[0]}")
            continue
            
        novo_sulco = round(sulco_atual - (desgaste_medio * km_adicional), 2)
        novo_sulco = max(0, min(sulco_atual, novo_sulco))
        percentual = round((1 - (novo_sulco/sulco_atual)) * 100, 1) if sulco_atual > 0 else 0
        
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{col.replace('SULCO ', '').title()}</div>
                <div class="metric-value">{novo_sulco} mm</div>
                <div class="metric-subtitle">
                    Atual: {sulco_atual} mm<br>
                    Redução: {percentual}%
                </div>
            </div>
        """, unsafe_allow_html=True)

# ======================================
# GRÁFICOS PRINCIPAIS
# ======================================
st.markdown("---")
st.subheader("📈 Análise Gráfica")

# Gráfico 1: Evolução histórica
fig1 = px.line(
    df_filtrado.sort_values("DATA E HORA"),
    x="DATA E HORA",
    y=desgaste_cols,
    title=f"Evolução dos Sulcos - Pneu {pneu}",
    labels={"value": "Medição (mm)", "variable": "Tipo de Sulco"},
    color_discrete_sequence=[primary_color, secondary_color, "#ff7f0e", "#2ca02c"]
)
fig1.update_layout(hovermode="x unified")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Correlação KM vs Sulcos
fig2 = px.scatter(
    df_filtrado,
    x="KM NO MOMENTO DA AFERIÇÃO",
    y="MENOR SULCO",
    title="Correlação entre KM Rodado e Menor Sulco",
    trendline="ols",
    color_discrete_sequence=[primary_color]
)
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Boxplot de distribuição
df_box = df_filtrado[desgaste_cols].melt(var_name="Sulco", value_name="Medição")
fig3 = px.box(
    df_box,
    x="Sulco",
    y="Medição",
    title="Distribuição das Medições por Sulco",
    color_discrete_sequence=[secondary_color]
)
st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Pairplot (Seaborn)
st.markdown("**Relação entre os Sulcos**")
fig4 = sns.pairplot(df_filtrado[desgaste_cols])
st.pyplot(fig4.fig)


# ======================================
# NOVOS GRÁFICOS PARA ANÁLISE
# ======================================
st.markdown("---")
st.subheader("📊 Análises Avançadas")

# Gráfico 5: Taxa de desgaste por KM
col1, col2 = st.columns(2)
with col1:
    desgaste_km_data = []
    for col in desgaste_cols:
        desgaste_medio = df_filtrado[f"DESGASTE_POR_KM_{col}"].mean() * 1000  # mm por 1000 km
        if not pd.isna(desgaste_medio) and desgaste_medio > 0:
            desgaste_km_data.append({
                "Sulco": col.replace("SULCO ", ""),
                "Desgaste (mm/1000km)": desgaste_medio
            })
    
    if desgaste_km_data:
        df_desgaste = pd.DataFrame(desgaste_km_data)
        fig5 = px.bar(
            df_desgaste,
            x="Sulco",
            y="Desgaste (mm/1000km)",
            title="Taxa de Desgaste por 1000 km",
            color="Sulco",
            color_discrete_sequence=[primary_color, secondary_color, "#ff7f0e", "#2ca02c"]
        )
        st.plotly_chart(fig5, use_container_width=True)

# Gráfico 6: Comparação entre sulcos
with col2:
    ultima_medicao = df_filtrado.iloc[-1][desgaste_cols].to_frame().reset_index()
    ultima_medicao.columns = ["Sulco", "Medição (mm)"]
    ultima_medicao["Sulco"] = ultima_medicao["Sulco"].str.replace("SULCO ", "")
    
    fig6 = px.bar(
        ultima_medicao,
        x="Sulco",
        y="Medição (mm)",
        title="Última Medição por Sulco",
        color="Sulco",
        color_discrete_sequence=[primary_color, secondary_color, "#ff7f0e", "#2ca02c"]
    )
    st.plotly_chart(fig6, use_container_width=True)

# Gráfico 7: Radar chart para comparação de sulcos
st.markdown("**Perfil de Desgaste**")
df_radar = df_filtrado.melt(id_vars="DATA E HORA", 
                           value_vars=desgaste_cols, 
                           var_name="Sulco", 
                           value_name="Medição")
df_radar["Sulco"] = df_radar["Sulco"].str.replace("SULCO ", "")

fig7 = px.line_polar(
    df_radar, 
    r="Medição", 
    theta="Sulco", 
    line_close=True,
    color="DATA E HORA",
    title="Evolução do Perfil de Desgaste",
    template="plotly_white",
    color_discrete_sequence=px.colors.sequential.Blues_r
)
st.plotly_chart(fig7, use_container_width=True)

# Gráfico 8: Heatmap de correlação
st.markdown("**Matriz de Correlação**")
corr_matrix = df_filtrado[desgaste_cols + ["KM NO MOMENTO DA AFERIÇÃO"]].corr()
fig8 = px.imshow(
    corr_matrix,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Blues",
    title="Correlação entre Variáveis"
)
st.plotly_chart(fig8, use_container_width=True)

# Gráfico 9: Desgaste acumulado
df_filtrado["DESGASTE_ACUMULADO"] = df_filtrado["KM NO MOMENTO DA AFERIÇÃO"] - df_filtrado["KM NO MOMENTO DA AFERIÇÃO"].min()
fig9 = px.scatter(
    df_filtrado,
    x="DESGASTE_ACUMULADO",
    y=desgaste_cols,
    title="Desgaste Acumulado por KM Rodado",
    labels={"value": "Medição (mm)", "variable": "Sulco"},
    color_discrete_sequence=[primary_color, secondary_color, "#ff7f0e", "#2ca02c"]
)
st.plotly_chart(fig9, use_container_width=True)

# ======================================
# Gráfico 10: Velocidade de desgaste por período - VERSÃO CORRIGIDA
# ======================================
df_filtrado["PERIODO"] = df_filtrado["DATA E HORA"].dt.to_period("M").astype(str)  # Correção na coluna PERIODO

# Agrupar os dados para o cálculo da velocidade de desgaste
df_velocidade = df_filtrado.groupby("PERIODO").agg({
    "KM NO MOMENTO DA AFERIÇÃO": ["first", "last"],
    **{col: ["first", "last"] for col in desgaste_cols}
}).reset_index()

# Renomear colunas multi-index
df_velocidade.columns = ['_'.join(col).strip() if col[1] else col[0] for col in df_velocidade.columns.values]

# Cálculo da velocidade de desgaste (mm/1000km)
for col in desgaste_cols:
    km_diff = df_velocidade[f"KM NO MOMENTO DA AFERIÇÃO_last"] - df_velocidade[f"KM NO MOMENTO DA AFERIÇÃO_first"]
    sulco_diff = df_velocidade[f"{col}_first"] - df_velocidade[f"{col}_last"]
    df_velocidade[f"VELOCIDADE_{col}"] = (sulco_diff / km_diff) * 1000

# Preparar dados para o gráfico
velocidade_cols = [f"VELOCIDADE_{col}" for col in desgaste_cols]

# A função melt precisa usar a coluna correta, ou seja, 'PERIODO' e não 'PERIODO_'
df_velocidade_melt = df_velocidade.melt(
    id_vars=["PERIODO"],  # Alterado para "PERIODO"
    value_vars=velocidade_cols,
    var_name="Sulco",
    value_name="Desgaste (mm/1000km)"
)

# Limpar nomes dos sulcos
df_velocidade_melt["Sulco"] = df_velocidade_melt["Sulco"].str.replace("VELOCIDADE_", "")

# Criar gráfico
fig10 = px.bar(
    df_velocidade_melt,
    x="PERIODO",
    y="Desgaste (mm/1000km)",
    color="Sulco",
    barmode="group",
    title="Velocidade de Desgaste por Período (mm/1000km)",
    color_discrete_sequence=[primary_color, secondary_color, "#ff7f0e", "#2ca02c"],
    labels={"PERIODO": "Período"}  # Corrigido o nome da coluna no gráfico
)

st.plotly_chart(fig10, use_container_width=True)



# ======================================
# RODAPÉ
# ======================================
st.markdown("---")
st.markdown(f"""
    <div style="text-align:center;color:{text_color};padding:10px;">
        Sistema de Monitoramento de Pneus •  {pd.Timestamp.now().year}
    </div>
""", unsafe_allow_html=True)