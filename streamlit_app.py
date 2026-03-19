import streamlit as st

from core.ui import (
    COMO_FUNCIONA_ICON,
    CONTATO_ICON,
    GLOSSARIO_ICON,
    HOME_ICON,
    PLANOS_ICON,
    SIMULADOR_ICON,
    image_data_uri,
)

st.set_page_config(
    page_title="Retorno Real",
    layout="wide",
    initial_sidebar_state="collapsed",
)

home = st.Page("app_pages/home.py", title="Home", icon=HOME_ICON, default=True)
simular = st.Page("app_pages/simulador.py", title="Simular", icon=SIMULADOR_ICON)
metodologia = st.Page("app_pages/como_funciona.py", title="Metodologia", icon=COMO_FUNCIONA_ICON)
glossario = st.Page("app_pages/glossario.py", title="Glossário", icon=GLOSSARIO_ICON)
planos = st.Page("app_pages/planos.py", title="Planos", icon=PLANOS_ICON)
contato = st.Page("app_pages/contato.py", title="Contato", icon=CONTATO_ICON)

pages = {
    "": [home],
    "Simulador": [simular, metodologia, glossario],
    "Sobre": [planos, contato],
}

selected_page = st.navigation(pages, position="top")

BASE_CSS = """
div[data-testid="stMainBlockContainer"] .block-container {
  max-width: 1200px;
  padding-top: 1.6rem;
  padding-bottom: 2rem;
  margin: 0 auto;
}

.stAppHeader{
  left: 0 !important;
  right: 0 !important;
  width: 100vw !important;
  z-index: 10000 !important;
  backdrop-filter: blur(8px);
}

h1, h2, h3 { letter-spacing: -0.02em; }
a { text-decoration: none; }

a.anchor-link,
a[aria-label="Anchor link"]{
  display: none !important;
}

[data-testid="stHeaderActionElements"]{
  display: none !important;
}

div[role="menu"]{
  background: #0f172a !important;
  border: 1px solid rgba(148,163,184,0.20) !important;
  box-shadow: 0 18px 40px rgba(2,6,23,0.22) !important;
}

div[role="menu"] *{
  color: #f8fafc !important;
}

div[role="menu"] [role="menuitem"],
div[role="menu"] button{
  background: transparent !important;
}

div[role="menu"] [role="menuitem"]:hover,
div[role="menu"] [role="menuitem"][data-highlighted],
div[role="menu"] button:hover{
  background: rgba(255,255,255,0.08) !important;
}
"""

LIGHT_THEME_CSS = """
:root { color-scheme: light; }

div[data-testid="stAppViewContainer"] {
  background: #ffffff !important;
}

.stAppHeader, div[data-testid="stHeader"]{
  background: rgba(255,255,255,0.96) !important;
  border-bottom: 1px solid rgba(0,0,0,0.06) !important;
}
"""

st.markdown(f"<style>{BASE_CSS}{LIGHT_THEME_CSS}</style>", unsafe_allow_html=True)

logo_file = "RetornoRealTransparente.png" if selected_page == contato else "RetornoRealLogo.png"
logo_uri = image_data_uri(logo_file, max_width=240, crop_white=True)

if logo_uri:
    st.markdown(
        f"""
        <style>
          #rr-top-logo {{
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            height: 34px;
            z-index: 10001;
            pointer-events: none;
            display: flex;
            align-items: center;
            justify-content: center;
          }}

          #rr-top-logo img {{
            height: 34px;
            width: auto;
            display: block;
          }}

          @media (max-width: 900px) {{
            #rr-top-logo {{
              display: none;
            }}
          }}
        </style>

        <div id="rr-top-logo">
          <img src="{logo_uri}" alt="Retorno Real" />
        </div>
        """,
        unsafe_allow_html=True,
    )

if selected_page == contato:
    DARK_THEME_CSS = """
    :root { color-scheme: dark; }

    div[data-testid="stAppViewContainer"] {
      background:
        radial-gradient(900px circle at 10% 0%, rgba(255,255,255,0.05), transparent 35%),
        linear-gradient(180deg, #0b1017 0%, #0a0f14 100%) !important;
      color: #e2e8f0 !important;
    }

    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stMarkdownContainer"] span,
    label {
      color: #e2e8f0 !important;
    }

    h1, h2, h3, h4 {
      color: #f8fafc !important;
    }

    a {
      color: #bfdbfe !important;
    }

    .stAppHeader, div[data-testid="stHeader"]{
      background: rgba(10,15,20,0.94) !important;
      border-bottom: 1px solid rgba(148,163,184,0.16) !important;
    }

    .stAppHeader *{
      color: #e2e8f0 !important;
    }

    div[data-testid="stSidebar"]{
      background: #0b1017 !important;
    }
    """
    st.markdown(f"<style>{DARK_THEME_CSS}</style>", unsafe_allow_html=True)

selected_page.run()