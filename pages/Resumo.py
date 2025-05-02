import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

if 'df' in st.session_state:
    df = st.session_state['df']
    profile = ProfileReport(df, title="Relatório de Perfil", explorative=True)
    st_profile_report(profile)
else:
    st.warning("Nenhum DataFrame disponível para análise.")
