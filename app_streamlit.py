# -*- coding: utf-8 -*-
"""
App web de fases lunares (Streamlit)
  Local: streamlit run app_streamlit.py
"""
from datetime import datetime

import streamlit as st

from luna_lib import TZ, render_fig, resumen_md

st.set_page_config(page_title="Fases de la Luna — San Juan", page_icon="🌙")
st.title("🌙 Fases de la Luna — San Juan, Argentina")
st.caption("Lat 31°32′13″ S · Lon 68°31′32″ O · 650 m s.n.m. · UTC−3")

with st.sidebar:
    st.header("⚙️ Parámetros")
    usa_ahora = st.checkbox("Usar fecha y hora actual", value=True)
    ahora = datetime.now(TZ).replace(second=0, microsecond=0)
    if usa_ahora:
        local = ahora
        st.info(local.strftime("%d/%m/%Y %H:%M"))
    else:
        f = st.date_input("Fecha", value=ahora.date())
        h = st.time_input("Hora", value=ahora.replace(minute=0).time())
        local = datetime(f.year, f.month, f.day, h.hour, h.minute, tzinfo=TZ)
    sur = st.checkbox("Vista hemisferio Sur", value=True)

st.pyplot(render_fig(local, sur))
st.markdown(resumen_md(local))