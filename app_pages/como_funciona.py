import streamlit as st

from core.methodology_content import render_methodology_content
from core.ui import (
    CONTATO_ICON,
    GLOSSARIO_ICON,
    HOME_ICON,
    page_link_with_icon,
)

st.title("Metodologia", anchor=False)
st.caption(
    "Metodologia, fontes de dados e limitações — para você entender o que o simulador considera "
    "e o que depende da fonte de dados."
)

c1, c2, c3, c4 = st.columns(4, gap="large", vertical_alignment="center")
with c1:
    st.page_link("app_pages/home.py", label="Home", icon=HOME_ICON, width="content")
with c2:
    page_link_with_icon("app_pages/simulador.py", "Simular", group_width=170)
with c3:
    st.page_link("app_pages/glossario.py", label="Glossário", icon=GLOSSARIO_ICON, width="content")
with c4:
    st.page_link("app_pages/contato.py", label="Contato", icon=CONTATO_ICON, width="content")

st.divider()

render_methodology_content()

st.divider()

st.header("Atalhos", anchor=False)
b1, b2, b3 = st.columns(3, gap="large", vertical_alignment="center")
with b1:
    page_link_with_icon("app_pages/simulador.py", "Abrir o Simulador", group_width=210)
with b2:
    st.page_link("app_pages/glossario.py", label="Ver Glossário", icon=GLOSSARIO_ICON, width="content")
with b3:
    st.page_link("app_pages/contato.py", label="Contato", icon=CONTATO_ICON, width="content")