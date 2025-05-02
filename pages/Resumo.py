import streamlit as st
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

st.set_page_config(page_title="Resumo EDA", layout="wide")

df = st.session_state.get("df")
if df is None:
    st.warning("Faça upload do DataFrame na página de upload.")
    st.stop()

profile = ProfileReport(df, title="Relatório de Perfil", explorative=True)
st_profile_report(profile)
