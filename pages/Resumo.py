import streamlit as st
from dataprep.eda import create_report
from streamlit.components.v1 import html

st.set_page_config(page_title="Resumo EDA", layout="wide")

df = st.session_state.get("df")
if df is None:
    st.warning("Faça upload do DataFrame na página de upload.")
    st.stop()

report = create_report(df)
report_html = report.to_html()
html(report_html, height=800, scrolling=True)
