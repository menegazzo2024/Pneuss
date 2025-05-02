import streamlit as st
import sweetviz as sv
import pandas as pd
from streamlit.components.v1 import html

# carrega DataFrame em st.session_state['df']
df = st.session_state.get('df')
if df is None:
    st.warning("Faça upload na página anterior.")
else:
    df["PRESSÃO"] = pd.to_numeric(df["PRESSÃO"], errors="coerce")
    report = sv.analyze(df)
    report_path = "sweetviz_report.html"
    report.show_html(report_path, open_browser=False)
    # injeta o HTML gerado na app
    with open(report_path, "r", encoding="utf-8") as f:
        html(f.read(), height=800, scrolling=True)
