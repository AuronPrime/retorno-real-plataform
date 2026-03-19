import streamlit as st


def render_methodology_content() -> None:
    st.info(
        "Resumo rápido: o app simula aportes mensais comprando apenas ações inteiras (sem frações) "
        "e guardando o excedente em caixa (troco). O patrimônio evolui com preço + proventos reinvestidos "
        "e considera splits/grupamentos quando a fonte informa. Benchmarks (CDI/Selic, IPCA e Ibovespa) "
        "entram para comparação."
    )

    st.header("1) O que o app calcula", anchor=False)
    st.markdown(
        """
O objetivo é mostrar a evolução realista do patrimônio ao longo do tempo.

O patrimônio em cada data é:

- **Patrimônio = (Quantidade de ações × Preço) + Caixa (troco)**

Onde:
- **Quantidade de ações** é sempre **inteira** (sem frações).
- **Caixa (troco)** é o dinheiro que sobra após comprar ações inteiras (e também pode receber proventos).
"""
    )

    with st.expander("Por que isso é mais realista? (explicação rápida)"):
        st.markdown(
            """
Muitos simuladores “compram frações” automaticamente. Na prática, você compra ações inteiras (dependendo do mercado/boleta).  
Aqui o app faz como no mundo real:

- Se você tem R$ 1.000 e a ação custa R$ 37, você compra **27 ações** e sobra **R$ 1,00** em caixa.
- Se entram proventos no caixa e passa a dar para comprar mais 1 ação, o app compra.
"""
        )

    st.divider()

    st.header("2) Dados do ativo (Yahoo Finance via yfinance)", anchor=False)
    st.markdown(
        """
O app busca dados do ativo usando Yahoo Finance via biblioteca yfinance (biblioteca = pacote Python que facilita acessar dados).

Em geral, usamos dados diários (dia a dia), como:
- Close (preço de fechamento)
- Dividends (proventos — o Yahoo pode agrupar dividendos/JCP nesse campo)
- Stock Splits (splits/grupamentos)

Esses dados são usados:
1) Para o gráfico (evolução do retorno total ao longo do tempo).  
2) Para a simulação de aportes (compra de ações inteiras + caixa).
"""
    )

    st.warning(
        "Importante: Yahoo Finance é uma fonte prática, mas não é “fonte oficial”. "
        "Pode haver atrasos, ajustes retroativos e eventos faltando (principalmente proventos e eventos corporativos)."
    )

    st.divider()

    st.header("3) Retorno total vs. preço (o que aparece no gráfico)", anchor=False)
    st.markdown(
        """
O diferencial do gráfico é separar o desempenho em camadas:

- **Valorização do preço**: mostra o quanto o resultado veio apenas da ação subir ou cair.
- **Proventos reinvestidos**: mostra o quanto do resultado veio de dividendos/JCP entrando no patrimônio ao longo do tempo.
- **Retorno total**: reúne essas duas forças e mostra o efeito acumulado.

Ou seja: em vez de entregar só um número final, o app tenta mostrar **de onde o resultado veio** e **como ele foi sendo construído** ao longo do período.
"""
    )

    with st.expander("Como o app transforma o dado do dia em retorno acumulado"):
        c1, c2 = st.columns(2, gap="large", vertical_alignment="top")

        with c1:
            with st.container(border=True):
                st.markdown("**1) Movimento do preço no dia**")
                st.write("O app mede como o preço evoluiu de um dia para o outro.")
                st.caption("Aqui ele observa apenas a variação do preço da ação.")

            with st.container(border=True):
                st.markdown("**3) Acumulado do período**")
                st.write("Depois, esses movimentos diários são encadeados para formar a trajetória completa do gráfico.")
                st.caption("É assim que o histórico passa a mostrar o caminho do patrimônio ao longo do tempo.")

        with c2:
            with st.container(border=True):
                st.markdown("**2) Movimento total no dia**")
                st.write("O app também mede o efeito combinado do preço com os proventos distribuídos no período.")
                st.caption("Aqui entra a visão de retorno total, e não apenas do preço isolado.")

        st.info(
            "Em linguagem simples: uma camada acompanha o avanço do preço, outra acompanha o avanço total, "
            "e a evolução acumulada surge da sequência desses movimentos ao longo do tempo."
        )

    st.divider()

    st.header("4) Simulação realista: ações inteiras + caixa (troco)", anchor=False)
    st.markdown(
        """
A simulação dos aportes mensais (aporte = investimento recorrente) segue esta lógica:

1) Você define uma data de início e uma data de fim.  
2) O app cria as datas de aporte mensal a partir do dia escolhido.
3) Se o dia escolhido não tem pregão (pregão = dia com negociação), o aporte vai para o próximo pregão disponível.
4) Em cada aporte:
   - soma o aporte ao caixa
   - compra o máximo possível de ações inteiras
   - o resto fica em caixa

Quando existem proventos:
- Proventos entram em caixa e só viram ações quando o caixa dá para comprar ações inteiras.

Quando existe split/grupamento:
- a quantidade de ações é ajustada
- se surgir fração, a fração é convertida em caixa (aproximação prática).
"""
    )

    st.divider()

    st.header("5) Benchmarks: CDI/Selic, IPCA e Ibovespa", anchor=False)
    st.markdown(
        """
O app sempre mostra benchmarks (benchmark = referência de comparação):

- CDI / Selic: retornos de renda fixa (renda fixa = juros).
- IPCA: inflação (inflação = perda do poder de compra).
- Ibovespa: referência de mercado (índice da bolsa brasileira).

Como os dados são obtidos:
- CDI/Selic e IPCA vêm do BCB/SGS (BCB/SGS = séries do Banco Central).
- Ibovespa vem do Yahoo via ticker ^BVSP.

Nos cards, o app calcula “quanto daria” se cada aporte mensal fosse corrigido pelo benchmark até a data final.
"""
    )

    st.divider()

    st.header("6) Estimativas para dados recentes (mês vigente)", anchor=False)
    st.markdown(
        """
Alguns dados (principalmente IPCA, e às vezes séries de juros) podem não ter o valor do mês vigente
(mês vigente = mês atual ainda não consolidado).

Para não “cortar” o gráfico antes do fim do período escolhido, o app pode projetar (projetar = estimar) o índice até a data final:

- calcula uma taxa média composta (média composta = “juros sobre juros”) baseada nos últimos 6 meses
- usa fallback (fallback = plano B) para 3 meses, se necessário
- aplica essa taxa como crescimento diário até alcançar a data final

No gráfico, o trecho estimado aparece como linha tracejada para transparência.
"""
    )

    st.warning(
        "Projeção não é dado oficial. Serve para dar continuidade visual e aproximar o comparativo — "
        "mas pode divergir do valor real quando o dado oficial é publicado."
    )

    st.divider()

    st.header("7) Limitações e cuidados", anchor=False)
    st.markdown(
        """
Para evitar surpresas, aqui estão limitações comuns:

**Fonte do ativo (Yahoo / yfinance)**
- pode faltar provento (dividendo/JCP), ou aparecer com atraso
- pode faltar evento corporativo (split/bonificação/grupamento), ou vir incompleto
- pode haver ajustes retroativos no histórico

**Custos e impostos (não incluídos por enquanto)**
- corretagem, emolumentos, spread, imposto de renda e regras de isenção não entram no cálculo nesta versão

**Não é recomendação**
- o app é uma ferramenta de simulação/análise e não substitui orientação profissional
"""
    )