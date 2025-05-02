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



df = st.session_state.get("df")
if df is None:
    st.warning("Faça upload do DataFrame na página de upload.")
    st.stop()



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
    st.session_state['df'] = df

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


# ======================================
# RODAPÉ
# ======================================
st.markdown("---")
st.markdown(f"""
    <div style="text-align:center;color:{text_color};padding:10px;">
        Sistema de Monitoramento de Pneus •  {pd.Timestamp.now().year}
    </div>
""", unsafe_allow_html=True)
