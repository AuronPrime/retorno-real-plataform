import streamlit as st

from core.ui import (
    COMO_FUNCIONA_ICON,
    CONTATO_ICON,
    GLOSSARIO_ICON,
    HOME_ICON,
    page_link_with_icon,
)

st.title("Glossário", anchor=False)
st.caption("Definições rápidas dos principais termos do app. Use o filtro por categoria para navegar.")

c1, c2, c3, c4 = st.columns(4, gap="large", vertical_alignment="center")
with c1:
    st.page_link("app_pages/home.py", label="Home", icon=HOME_ICON, width="content")
with c2:
    page_link_with_icon("app_pages/simulador.py", "Simulador", group_width=180)
with c3:
    st.page_link("app_pages/como_funciona.py", label="Como funciona", icon=COMO_FUNCIONA_ICON, width="content")
with c4:
    st.page_link("app_pages/contato.py", label="Contato", icon=CONTATO_ICON, width="content")

st.divider()

TERMS = [
    {"termo": "Ações inteiras", "categoria": "Simulação",
     "definicao": "O app compra somente ações inteiras (sem frações). Se o dinheiro não dá para comprar mais 1 ação, ele fica em caixa (troco)."},
    {"termo": "Caixa (troco)", "categoria": "Simulação",
     "definicao": "Dinheiro que sobra após comprar ações inteiras. Também recebe proventos (dividendos/JCP) e pode ser usado em compras futuras."},
    {"termo": "Aporte mensal", "categoria": "Simulação",
     "definicao": "Valor recorrente investido todo mês (investimento recorrente). Se a data cair em dia sem pregão, o aporte é executado no próximo pregão."},
    {"termo": "Pregão", "categoria": "Simulação",
     "definicao": "Dia em que existe negociação e, portanto, preço para o ativo. O app usa os dias com dados de preço como referência de pregões."},
    {"termo": "Data de início efetivo", "categoria": "Simulação",
     "definicao": "Primeira data em que o app realmente consegue executar o aporte (se a data escolhida não tem pregão, vai para o próximo pregão)."},
    {"termo": "Data final usada no cálculo", "categoria": "Simulação",
     "definicao": "Último pregão disponível até a data final escolhida. Se a data escolhida não tiver pregão, o app usa o pregão anterior."},
    {"termo": "Patrimônio", "categoria": "Simulação",
     "definicao": "Total em cada data: (quantidade de ações × preço) + caixa (troco)."},
    {"termo": "Capital nominal investido", "categoria": "Retornos",
     "definicao": "Somatório bruto dos aportes (sem corrigir por inflação e sem considerar retorno). Ex.: 12 aportes de R$ 1.000 = R$ 12.000."},
    {"termo": "Rendimento nominal", "categoria": "Retornos",
     "definicao": "Diferença entre o valor final e o capital nominal investido. É nominal porque não desconta inflação (poder de compra)."},
    {"termo": "Retorno total (Total Return)", "categoria": "Retornos",
     "definicao": "Retorno que considera preço + proventos reinvestidos. É a medida mais completa do desempenho do investimento."},
    {"termo": "Valorização (preço)", "categoria": "Retornos",
     "definicao": "Parte do retorno que vem apenas do preço subir. No gráfico, aparece separado do efeito dos proventos."},
    {"termo": "Proventos", "categoria": "Proventos",
     "definicao": "Pagamentos feitos pela empresa ao acionista, como dividendos e JCP. No app, entram em caixa e são reinvestidos quando dá para comprar ações inteiras."},
    {"termo": "Dividendos", "categoria": "Proventos",
     "definicao": "Parcela do lucro distribuída aos acionistas. Na base do Yahoo, costuma aparecer no campo Dividends."},
    {"termo": "JCP (Juros sobre Capital Próprio)", "categoria": "Proventos",
     "definicao": "Tipo de provento comum no Brasil. O Yahoo pode reportar junto em Dividends, dependendo do ativo e do histórico."},
    {"termo": "Reinvestimento", "categoria": "Proventos",
     "definicao": "Usar proventos para comprar mais ações. Aqui é realista: só compra ações inteiras e mantém o resto em caixa."},
    {"termo": "Split (desdobramento)", "categoria": "Eventos corporativos",
     "definicao": "Evento em que a empresa aumenta o número de ações e reduz o preço proporcionalmente. Ex.: split 1:2 transforma 10 ações em 20."},
    {"termo": "Grupamento (reverse split)", "categoria": "Eventos corporativos",
     "definicao": "Evento inverso do split: reduz o número de ações e aumenta o preço proporcionalmente. Ex.: grupamento 10:1 transforma 100 ações em 10."},
    {"termo": "Bonificação", "categoria": "Eventos corporativos",
     "definicao": "Quando o acionista recebe ações adicionais. Depende da fonte informar corretamente para refletir no cálculo."},
    {"termo": "Fator acumulado (Price_Fact / Total_Fact)", "categoria": "Técnico",
     "definicao": "Número que cresce ao longo do tempo multiplicando variações diárias. Price_Fact segue só o preço; Total_Fact inclui preço + proventos."},
    {"termo": "cumprod (produto acumulado)", "categoria": "Técnico",
     "definicao": "Operação que multiplica valores em sequência para criar um acumulado (multiplica dia a dia)."},
    {"termo": "Hover", "categoria": "Técnico",
     "definicao": "Informação que aparece quando você passa o mouse no gráfico (tooltip = caixinha de dica)."},
    {"termo": "CDI", "categoria": "Benchmarks",
     "definicao": "Taxa de referência de renda fixa (juros), usada como comparação no app."},
    {"termo": "Selic", "categoria": "Benchmarks",
     "definicao": "Taxa básica de juros do Brasil. Se o CDI falhar, o app pode usar Selic como proxy (proxy = substituto aproximado)."},
    {"termo": "IPCA", "categoria": "Benchmarks",
     "definicao": "Índice de inflação mais usado no Brasil. No app, corrige os aportes para comparar poder de compra."},
    {"termo": "Ibovespa", "categoria": "Benchmarks",
     "definicao": "Principal índice da bolsa brasileira, usado como referência de mercado (ticker ^BVSP no Yahoo)."},
    {"termo": "BCB/SGS", "categoria": "Dados e fontes",
     "definicao": "Sistema de séries temporais do Banco Central. O app usa para CDI/Selic e IPCA."},
    {"termo": "Yahoo Finance / yfinance", "categoria": "Dados e fontes",
     "definicao": "Fonte prática para preços, proventos e splits. yfinance é a biblioteca (pacote Python) que acessa o Yahoo."},
    {"termo": "Projeção / estimativa", "categoria": "Dados e fontes",
     "definicao": "Quando falta dado recente (mês vigente), o app pode estimar usando média composta. O trecho estimado aparece tracejado no gráfico."},
    {"termo": "Fallback (plano B)", "categoria": "Dados e fontes",
     "definicao": "Estratégia alternativa quando a melhor fonte falha. Ex.: tentar CDI e, se falhar, usar Selic."},
    {"termo": "Cache (cache local / st.cache_data)", "categoria": "Dados e fontes",
     "definicao": "Guardar resultados para acelerar próximas consultas e reduzir instabilidade de rede (guardar no computador/servidor)."},
]

categorias = sorted({t["categoria"] for t in TERMS})
sel_categorias = st.multiselect("Filtrar por categoria", categorias, default=categorias)

filtrados = [t for t in TERMS if t["categoria"] in sel_categorias]
st.caption(f"Termos exibidos: {len(filtrados)}")

for cat in sel_categorias:
    bloco = [t for t in filtrados if t["categoria"] == cat]
    if not bloco:
        continue
    st.subheader(cat, anchor=False)
    for t in bloco:
        with st.expander(t["termo"], expanded=False):
            st.markdown(t["definicao"])

st.divider()

st.subheader("Continuar navegando", anchor=False)
b1, b2, b3 = st.columns(3, gap="large", vertical_alignment="center")
with b1:
    st.page_link("app_pages/home.py", label="Home", icon=HOME_ICON, width="content")
with b2:
    st.page_link("app_pages/como_funciona.py", label="Como funciona", icon=COMO_FUNCIONA_ICON, width="content")
with b3:
    st.page_link("app_pages/contato.py", label="Contato", icon=CONTATO_ICON, width="content")

st.divider()
st.markdown(
    "Nota: custos (corretagem/emolumentos), impostos (IR) e regras específicas não estão incluídos nesta versão. "
    "Se algum evento/provento estiver ausente na fonte (Yahoo), ele não poderá ser refletido no resultado."
)