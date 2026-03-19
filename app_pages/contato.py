from html import escape

import streamlit as st

from core.ui import COMO_FUNCIONA_ICON, HOME_ICON, asset_path, page_link_with_icon

st.title("Contato", anchor=False)

IG_URL = "https://www.instagram.com/ramoon.bastos?igsh=MTFiODlnZ28ybHFqdw%3D%3D&utm_source=qr"

PHOTO_CANDIDATES = ["ramoon.png", "ramoon.jpg", "ramoon.jpeg", "foto.png", "profile.png"]

photo_path = None
for name in PHOTO_CANDIDATES:
    p = asset_path(name)
    if p.exists():
        photo_path = p
        break

bio_parts = [
    "Sou formado em Arquitetura e Urbanismo e construí uma carreira sólida na área comercial. Mesmo vindo de outra área, sempre tive interesse por investimentos — mas cansei de encontrar informações superficiais quando o assunto era patrimônio e tomada de decisão financeira.",
    "O Retorno Real nasceu dessa inquietação: da vontade de construir uma plataforma de consulta e simulação financeira que trate os números com profundidade, rastreabilidade e transparência — sem atalhos visuais e sem simplificações enganosas.",
    "Minha intenção é transformar esse projeto em uma plataforma cada vez mais completa, agregando no futuro funcionalidades de carteira, simulações patrimoniais mais complexas, cenários de compra x aluguel, análises ligadas a imóveis e outras ferramentas que realmente ajudem na tomada de decisão.",
    "Meu compromisso é usar as melhores fontes possíveis e transformar esses dados em cálculos cada vez mais realistas, precisos e úteis no mundo prático. O foco sempre será precisão, rigor matemático, coerência com a vida real e transparência na leitura dos resultados.",
    "E o mais importante: não hesite em me chamar. Se você tiver uma ideia, uma crítica ou quiser construir algo melhor junto, vamos evoluir isso lado a lado — uma plataforma mais sólida, mais transparente e mais útil para um futuro mais próspero.",
]

st.markdown(
    """
<style>
div[data-testid="stVerticalBlockBorderWrapper"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.02) 100%);
  border: 1px solid rgba(148,163,184,0.16) !important;
  border-radius: 26px !important;
  padding: 12px !important;
  box-shadow: 0 20px 40px rgba(0,0,0,0.16);
}

[data-testid="stImage"] img{
  border-radius: 22px;
  border: 1px solid rgba(148,163,184,0.18);
}

.contact-kicker{
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.12em;
  color: #fca5a5;
  margin-bottom: 8px;
}

.contact-name{
  font-size: clamp(2rem, 3vw, 2.6rem);
  line-height: 1.05;
  font-weight: 900;
  color: #f8fafc;
  margin-bottom: 8px;
}

.contact-text{
  margin-top: 14px;
  font-size: 1rem;
  line-height: 1.75;
  color: rgba(226,232,240,0.86);
}

.contact-note{
  margin-top: 16px;
  font-size: 0.84rem;
  line-height: 1.6;
  color: rgba(226,232,240,0.68);
}

.contact-after{
  margin-top: 14px;
  font-size: 0.95rem;
  line-height: 1.65;
  color: rgba(226,232,240,0.82);
}
</style>
""",
    unsafe_allow_html=True,
)

with st.container(border=True):
    col_photo, col_text = st.columns([0.9, 1.7], gap="large", vertical_alignment="center")

    with col_photo:
        if photo_path:
            st.image(str(photo_path), use_container_width=True)
        else:
            st.info("Coloque sua foto em assets/ramoon.png")

    with col_text:
        st.markdown('<div class="contact-kicker">CRIADOR DO PROJETO</div>', unsafe_allow_html=True)
        st.markdown('<div class="contact-name">Ramon Bastos</div>', unsafe_allow_html=True)

        for paragraph in bio_parts:
            st.markdown(
                f'<div class="contact-text">{escape(paragraph)}</div>',
                unsafe_allow_html=True,
            )

        st.link_button("Abrir Instagram", IG_URL, type="primary", width="content")

        st.markdown(
            '<div class="contact-note">Observação: este app é uma ferramenta de simulação/análise e não é recomendação de investimento.</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="contact-after">Vamos construir isso juntos — sugestões, críticas e ideias são bem-vindas.</div>',
    unsafe_allow_html=True,
)

st.divider()

st.subheader("Continuar navegando", anchor=False)
c1, c2, c3 = st.columns(3, gap="large", vertical_alignment="center")
with c1:
    st.page_link("app_pages/home.py", label="Home", icon=HOME_ICON, width="content")
with c2:
    page_link_with_icon("app_pages/simulador.py", "Simulador", group_width=180)
with c3:
    st.page_link("app_pages/como_funciona.py", label="Como funciona", icon=COMO_FUNCIONA_ICON, width="content")