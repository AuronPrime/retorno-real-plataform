import streamlit as st

from core.ui import (
    COMO_FUNCIONA_ICON,
    CONTATO_ICON,
    GLOSSARIO_ICON,
    HOME_ICON,
    SIMULADOR_ICON,
)

st.title("Planos", anchor=False)
st.caption(
    "Um acesso atual aberto e, no futuro, um único plano premium com cobrança mensal ou anual "
    "para ajudar na evolução contínua da plataforma."
)

c1, c2, c3, c4, c5 = st.columns(5, gap="medium", vertical_alignment="center")
with c1:
    st.page_link("app_pages/home.py", label="Home", icon=HOME_ICON, width="content")
with c2:
    st.page_link("app_pages/simulador.py", label="Simular", icon=SIMULADOR_ICON, width="content")
with c3:
    st.page_link("app_pages/como_funciona.py", label="Metodologia", icon=COMO_FUNCIONA_ICON, width="content")
with c4:
    st.page_link("app_pages/glossario.py", label="Glossário", icon=GLOSSARIO_ICON, width="content")
with c5:
    st.page_link("app_pages/contato.py", label="Contato", icon=CONTATO_ICON, width="content")

st.divider()

st.markdown(
    """
A proposta desta página é simples e transparente:

- **Hoje**, mostrar claramente o que já está disponível
- **No futuro**, evoluir para um único plano premium
- Usar esse plano como forma de **sustentar os custos** e acelerar a construção de ferramentas realmente úteis
"""
)

col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("Acesso Atual", anchor=False)
        st.markdown(
            """
**Inclui**
- Simulador com foco em retorno real de cada ação
- Gráfico de análise com retorno total de performance da ação
- Glossário de termos do produto
- Metodologia explicada em linguagem acessível

**Perfil**
Para quem está iniciando no mercado de ações e quer fazer comparações simples entre possibilidades de investimento.
"""
        )

with col2:
    with st.container(border=True):
        st.subheader("Plano Premium Futuro", anchor=False)
        st.markdown(
            """
**Formato**
- Um único plano premium
- Cobrança mensal ou anual
- Objetivo principal: ajudar nos custos da plataforma e financiar novas implementações

**Próximas Funcionalidades**
- Recurso avançado de pesquisa, como comparação de rentabilidade de ações e criação de **Carteiras Compostas**
- Indexação da carteira para acompanhamento de **Evolução Patrimonial**
- Ferramenta para controle de **Gastos Mensais**
- Ferramenta de análise para **Cenários Imobiliários** (compra x aluguel)
- Acesso à **IA da Plataforma**, treinada com todas as ferramentas disponíveis
- **Acesso Antecipado** a novas implementações
- Grupo no Discord/WhatsApp para feedbacks, sugestões e proposição de novas ferramentas
- Participação nas tomadas de decisão por votação da comunidade para implementação de novos recursos
"""
        )

st.divider()

with st.container(border=True):
    st.subheader("Mais do que um acesso exclusivo", anchor=False)
    st.markdown(
        """
Mais do que um acesso premium, a proposta é construir uma comunidade de investidores que querem uma ferramenta
sendo aprimorada continuamente, com recursos que realmente importam no dia a dia.

A ideia não é adicionar funcionalidades “por volume”, mas evoluir com foco em:

- **Precisão**
- **Rigor Matemático**
- **Transparência**
- **Utilidade Prática**
- **Escuta Real da Comunidade**
"""
    )

st.divider()

st.subheader("Atalhos", anchor=False)
a1, a2, a3 = st.columns(3, gap="large", vertical_alignment="center")
with a1:
    st.page_link("app_pages/simulador.py", label="Abrir Simulador", icon=SIMULADOR_ICON, width="content")
with a2:
    st.page_link("app_pages/glossario.py", label="Ver Glossário", icon=GLOSSARIO_ICON, width="content")
with a3:
    st.page_link("app_pages/contato.py", label="Falar com Ramon", icon=CONTATO_ICON, width="content")