import base64
import io
from collections import deque

import numpy as np
import streamlit as st
from PIL import Image

from core.ui import (
    COMO_FUNCIONA_ICON,
    GLOSSARIO_ICON,
    asset_path,
    image_data_uri,
    page_link_with_icon,
)


def official_logo_uri_tight(max_side: int = 820, pad: int = 4) -> str | None:
    path = asset_path("RetornoRealLogoOficial.png")
    if not path.exists():
        return None

    img = Image.open(path).convert("RGBA")
    rgb = np.array(img.convert("RGB")).astype(np.int16)

    red_mask = (
        (rgb[:, :, 0] > 150)
        & (rgb[:, :, 0] > rgb[:, :, 1] + 20)
        & (rgb[:, :, 0] > rgb[:, :, 2] + 20)
    )

    if not red_mask.any():
        return image_data_uri("RetornoRealLogoOficial.png", max_width=max_side, crop_white=True)

    h, w = red_mask.shape
    visited = np.zeros_like(red_mask, dtype=bool)

    largest = None
    largest_count = 0

    ys, xs = np.where(red_mask)
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

    for y, x in zip(ys, xs):
        if visited[y, x]:
            continue

        queue = deque([(y, x)])
        visited[y, x] = True

        count = 0
        min_x = max_x = x
        min_y = max_y = y

        while queue:
            cy, cx = queue.popleft()
            count += 1

            if cx < min_x:
                min_x = cx
            if cx > max_x:
                max_x = cx
            if cy < min_y:
                min_y = cy
            if cy > max_y:
                max_y = cy

            for dy, dx in directions:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and red_mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    queue.append((ny, nx))

        if count > largest_count:
            largest_count = count
            largest = (min_x, max_x, min_y, max_y)

    if largest is None:
        return image_data_uri("RetornoRealLogoOficial.png", max_width=max_side, crop_white=True)

    left, right, top, bottom = largest

    width = right - left + 1
    height = bottom - top + 1
    side = max(width, height) + (pad * 2)

    cx = (left + right) / 2
    cy = (top + bottom) / 2

    x0 = int(round(cx - side / 2))
    y0 = int(round(cy - side / 2))
    x1 = x0 + side
    y1 = y0 + side

    if x0 < 0:
        x1 -= x0
        x0 = 0
    if y0 < 0:
        y1 -= y0
        y0 = 0
    if x1 > img.size[0]:
        shift = x1 - img.size[0]
        x0 -= shift
        x1 = img.size[0]
    if y1 > img.size[1]:
        shift = y1 - img.size[1]
        y0 -= shift
        y1 = img.size[1]

    crop = img.crop((x0, y0, x1, y1)).resize((max_side, max_side), Image.LANCZOS)

    buf = io.BytesIO()
    crop.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


banner_uri = image_data_uri("RetornoRealBanner.png", max_width=1800, crop_white=False)
logo_uri = official_logo_uri_tight(max_side=820, pad=4)

if not logo_uri:
    logo_uri = image_data_uri("RetornoRealLogo.png", max_width=500, crop_white=True)

hero_banner_bg = f'url("{banner_uri}")' if banner_uri else "none"
hero_logo_html = (
    f'<img class="rr-home-logo" src="{logo_uri}" alt="Retorno Real" />'
    if logo_uri
    else ""
)

hero_html = f"""
<style>
.rr-home-hero {{
  position: relative;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 26px;
  padding: 34px 36px;
  background: linear-gradient(135deg, #ffffff 0%, #fff7f7 100%);
}}

.rr-home-hero::before {{
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(500px circle at 0% 0%, rgba(239,68,68,0.08), transparent 45%);
  pointer-events: none;
}}

.rr-home-hero::after {{
  content: "";
  position: absolute;
  inset: 0;
  background-image: {hero_banner_bg};
  background-position: center 72%;
  background-size: cover;
  opacity: 0.14;
  pointer-events: none;
}}

.rr-home-grid {{
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  gap: 28px;
  align-items: center;
}}

.rr-home-badge {{
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(220,38,38,0.16);
  background: rgba(220,38,38,0.06);
  color: #dc2626;
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.12em;
}}

.rr-home-title {{
  margin-top: 14px;
  font-size: clamp(2rem, 4vw, 3.2rem);
  line-height: 1.05;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.03em;
  max-width: 860px;
}}

.rr-home-text {{
  margin-top: 16px;
  font-size: 1.02rem;
  line-height: 1.72;
  color: #475569;
  max-width: 760px;
}}

.rr-home-text strong {{
  color: #0f172a;
  font-weight: 900;
}}

.rr-home-visual {{
  display: flex;
  justify-content: center;
  align-items: center;
}}

.rr-home-logo-wrap {{
  width: min(340px, 36vw);
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  box-shadow: 0 24px 40px rgba(15,23,42,0.10);
}}

.rr-home-logo {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}

@media (max-width: 960px) {{
  .rr-home-grid {{
    grid-template-columns: 1fr;
  }}

  .rr-home-visual {{
    justify-content: flex-start;
  }}

  .rr-home-logo-wrap {{
    width: min(300px, 72vw);
  }}
}}
</style>

<div class="rr-home-hero">
  <div class="rr-home-grid">
    <div>
      <div class="rr-home-badge">RETORNO REAL</div>
      <div class="rr-home-title">Transparência para enxergar o retorno real do patrimônio em cada decisão financeira.</div>
      <div class="rr-home-text">
        O Retorno Real está sendo construído para se tornar uma plataforma de análise e simulação financeira
        com foco em precisão, transparência e utilidade prática. Hoje, o primeiro módulo disponível é o
        <strong>Simulador de Ações</strong>, e a ideia é expandir a plataforma com novos recursos patrimoniais,
        comparativos e ferramentas que façam diferença no dia a dia de quem investe.
      </div>
    </div>

    <div class="rr-home-visual">
      <div class="rr-home-logo-wrap">
        {hero_logo_html}
      </div>
    </div>
  </div>
</div>
"""

st.html(hero_html)

with st.container(border=True):
    st.subheader("Simulador de Ações", anchor=False)
    st.caption(
        "Primeiro módulo disponível da plataforma. Analise o retorno real de uma ação ao longo do tempo, "
        "com preço, proventos, desdobramentos e comparação com benchmarks."
    )

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("**Preço + Proventos + Desdobramentos**")
            st.write(
                "Veja de forma separada o que veio de valorização do preço, proventos reinvestidos "
                "e eventos corporativos que alteram a trajetória do investimento."
            )

    with c2:
        with st.container(border=True):
            st.markdown("**Simulação Operacional de Verdade**")
            st.write(
                "É o **único** app da proposta que considera os centavos e a existência de caixa "
                "quando, na prática, surgiriam ações fracionadas."
            )

    with c3:
        with st.container(border=True):
            st.markdown("**Comparação com Benchmarks**")
            st.write(
                "Coloque o resultado lado a lado com CDI/Selic, IPCA e Ibovespa para enxergar melhor "
                "a qualidade do desempenho."
            )

    st.markdown("")
    page_link_with_icon("app_pages/simulador.py", "Abrir Simulador", group_width=220)

st.divider()

st.subheader("Saiba mais", anchor=False)
st.page_link(
    "app_pages/como_funciona.py",
    label="Como funciona (metodologia)",
    icon=COMO_FUNCIONA_ICON,
    width="content",
)
st.page_link(
    "app_pages/glossario.py",
    label="Glossário",
    icon=GLOSSARIO_ICON,
    width="content",
)