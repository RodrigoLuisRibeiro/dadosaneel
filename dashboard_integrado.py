# dashboard_integrado.py
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
from urllib.parse import unquote

# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Análise Avançada de Continuidade - ANEEL")


# --- Funções de Lógica e Carregamento de Dados ---
@st.cache_data
def obter_lista_distribuidoras(path='dados_processados'):
    """
    Usa os.walk para varrer a estrutura de diretórios e encontrar as pastas
    de partição da distribuidora de forma explícita e robusta.
    """
    distribuidoras = set()
    try:
        if not os.path.isdir(path):
            st.error(f"A pasta '{path}' não foi encontrada. Execute o '1_processar_dados.py' primeiro.")
            return []

        for root, dirs, files in os.walk(path):
            for dirname in dirs:
                if dirname.startswith('Distribuidora='):
                    nome_bruto_codificado = dirname.split('=', 1)[1]
                    nome_decodificado = unquote(nome_bruto_codificado)
                    nome_limpo = nome_decodificado.strip()
                    if nome_limpo:
                        distribuidoras.add(nome_limpo)

        if not distribuidoras:
            st.warning(
                "Nenhuma partição de distribuidora foi encontrada na pasta 'dados_processados'. Verifique se o pipeline foi executado corretamente.")
            return []

        return sorted(list(distribuidoras))

    except Exception as e:
        st.error(f"Ocorreu um erro ao ler a estrutura de pastas em '{path}'. Detalhes: {e}")
        return []


@st.cache_data
def carregar_dados_distribuidora(distribuidora):
    """
    Carrega dados de uma distribuidora específica do Data Lakehouse (Delta/Parquet).
    O filtro de partição torna esta operação extremamente rápida.
    """
    try:
        df = pd.read_parquet('dados_processados', filters=[('Distribuidora', '==', distribuidora)])
        df['Data'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mes'].astype(str))
        return df
    except Exception as e:
        st.error(f"Não foi possível carregar os dados para {distribuidora}. Detalhes: {e}")
        return pd.DataFrame()


# --- Layout da Aplicação ---
st.sidebar.title("Navegação e Filtros")

tipo_analise = st.sidebar.radio(
    "Selecione o Tipo de Análise:",
    ["Sobre o Projeto", "Visão Geral (KPIs)", "Análise de Conjuntos", "Séries Temporais e Previsões",
     "Simulação de Cenário"]
)

if tipo_analise == "Sobre o Projeto":
    st.title("💡 Sobre o Projeto de Análise de Indicadores da ANEEL")
    st.markdown("---")

    st.header("Transformando Dados Abertos em Insights Acionáveis")
    st.markdown("""
      Este projeto demonstra um fluxo completo de **Engenharia e Análise de Dados**, desde a coleta de dados brutos até a criação de um dashboard interativo. 
      O objetivo é extrair valor estratégico dos dados públicos da ANEEL sobre a qualidade da energia elétrica no Brasil, aplicando as melhores práticas e ferramentas do mercado.
      """)

    st.markdown("---")
    st.subheader("🏛️ Arquitetura e Boas Práticas Implementadas")

    # Layout em colunas para os cards de features
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("##### ⚙️ Pipeline de Dados Híbrido")
            st.write(
                "Extração de dados de arquivos CSV locais e consumo em tempo real da API da ANEEL, unificando as fontes para uma visão completa.")

    with col2:
        with st.container(border=True):
            st.markdown("##### ✅ Qualidade de Dados Garantida")
            st.write(
                "Uso da biblioteca **Pandera** para validar o esquema e a integridade dos dados, garantindo a confiabilidade de cada análise.")

    with col3:
        with st.container(border=True):
            st.markdown("##### 🗄️ Data Lakehouse com Delta Lake")
            st.write(
                "Armazenamento dos dados em formato **Delta Lake**, que oferece transações ACID, performance e escalabilidade.")

    col4, col5, col6 = st.columns(3)

    with col4:
        with st.container(border=True):
            st.markdown("##### 🐳 Containerização com Docker")
            st.write(
                "A aplicação é empacotada em um contêiner **Docker**, garantindo reprodutibilidade e facilitando o deploy em qualquer ambiente.")

    with col5:
        with st.container(border=True):
            st.markdown("##### 📊 Múltiplas Análises Avançadas")
            st.write(
                "O dashboard oferece desde KPIs e rankings até detecção de anomalias, previsão de séries temporais e simulação de cenários.")

    with col6:
        with st.container(border=True):
            st.markdown("##### 🔧 Estrutura Profissional")
            st.write(
                "O projeto utiliza logging, gestão de configuração (`config.yaml`) e `requirements.txt` para ser robusto e fácil de manter.")

    st.markdown("---")
    st.subheader("🧭 Como Navegar no Dashboard")
    st.markdown("""
      1.  **Selecione uma Análise:** Use o menu na barra lateral à esquerda para escolher o que você quer explorar.
      2.  **Aplique os Filtros:** Após escolher uma análise, a barra lateral mostrará os filtros de Distribuidora, Indicador e Ano.
      3.  **Interaja com os Gráficos:** Passe o mouse sobre os gráficos para ver detalhes, use o zoom e explore os dados de forma dinâmica.
      """)

    st.markdown("---")

    st.subheader("🔗 Links Úteis")
    col_gh, col_li = st.columns(2)
    with col_gh:
        st.link_button("Ver o Código no GitHub", "https://github.com/RodrigoLuisRibeiro/dadosaneel")
    with col_li:
        st.link_button("Conectar no LinkedIn",
                       "https://www.linkedin.com/in/rodrigo-luis-ribeiro-9b5837139/")  # (Sugestão, altere para seu link)


else:
    lista_distribuidoras = obter_lista_distribuidoras()
    if lista_distribuidoras:
        distribuidora_selecionada = st.sidebar.selectbox(
            "Selecione a Distribuidora:", lista_distribuidoras,
            index=lista_distribuidoras.index('CRELUZ-D') if 'CRELUZ-D' in lista_distribuidoras else 0
        )
        df_distribuidora = carregar_dados_distribuidora(distribuidora_selecionada)
        if not df_distribuidora.empty:
            indicadores_disponiveis = [col for col in ['DEC', 'FEC', 'DIC', 'FIC'] if
                                       col in df_distribuidora.columns and df_distribuidora[col].sum() > 0]
            indicador_selecionado = st.sidebar.selectbox("Selecione o Indicador:", indicadores_disponiveis)
            anos_disponiveis = sorted(df_distribuidora['Ano'].unique(), reverse=True)
            ano_selecionado = st.sidebar.selectbox("Selecione o Ano:", anos_disponiveis)

            st.title(f"Dashboard ANEEL: {distribuidora_selecionada}")
            st.subheader(f"{tipo_analise} - Indicador {indicador_selecionado}")
            df_analise_ano = df_distribuidora[df_distribuidora['Ano'] == ano_selecionado].copy()

            if tipo_analise == "Visão Geral (KPIs)":
                st.markdown(f"### Desempenho em {ano_selecionado}")
                valores_sem_zero = df_analise_ano[df_analise_ano[indicador_selecionado] > 0][indicador_selecionado]
                melhor_valor = valores_sem_zero.min()
                if pd.isna(melhor_valor):
                    melhor_valor = 0.0

                col1, col2, col3 = st.columns(3)
                col1.metric("Valor Médio", f"{df_analise_ano[indicador_selecionado].mean():.2f}")
                col2.metric("Pior Valor (Máx)", f"{df_analise_ano[indicador_selecionado].max():.2f}")
                col3.metric("Melhor Valor (Mín)", f"{melhor_valor:.2f}")

                st.markdown("### Evolução Histórica do Indicador")
                evolucao_anual = df_distribuidora.groupby('Ano')[indicador_selecionado].mean().reset_index()
                fig = px.line(evolucao_anual, x='Ano', y=indicador_selecionado,
                              title=f'Média Anual de {indicador_selecionado}', markers=True)
                st.plotly_chart(fig, use_container_width=True)

            elif tipo_analise == "Análise de Conjuntos":
                ranking_piores = df_analise_ano.groupby(['NomConjunto', 'ConjuntoID'])[
                    indicador_selecionado].mean().sort_values(ascending=False).reset_index()

                st.markdown(f"### Piores Conjuntos em {ano_selecionado}")
                fig_piores = px.bar(ranking_piores.head(20), x=indicador_selecionado, y='NomConjunto', orientation='h',
                                    title=f"Top 20 Piores Conjuntos por {indicador_selecionado}",
                                    labels={indicador_selecionado: f'Valor Médio de {indicador_selecionado}',
                                            'NomConjunto': 'Conjunto'})
                fig_piores.update_layout(yaxis={'categoryorder': 'total descending'}, height=500, margin=dict(l=300))
                st.plotly_chart(fig_piores, use_container_width=True, key="piores_conjuntos_bar")

                with st.expander("🔍 Análise de Anomalias Estatísticas"):
                    st.info(
                        "Esta análise destaca conjuntos cujo desempenho no ano selecionado foi estatisticamente incomum em comparação com seu próprio histórico.")
                    stats_historico = df_distribuidora.groupby('ConjuntoID')[indicador_selecionado].agg(
                        ['mean', 'std']).reset_index()
                    stats_historico.rename(columns={'mean': 'MediaHistorica', 'std': 'DesvioPadraoHistorico'},
                                           inplace=True)
                    stats_historico = stats_historico.fillna(0)

                    df_anomalia = pd.merge(df_analise_ano, stats_historico, on='ConjuntoID')
                    epsilon = 1e-6
                    df_anomalia['Z_Score'] = (df_anomalia[indicador_selecionado] - df_anomalia['MediaHistorica']) / (
                                df_anomalia['DesvioPadraoHistorico'] + epsilon)

                    anomalias = df_anomalia[df_anomalia['Z_Score'].abs() > 2.5].sort_values('Z_Score', ascending=False)
                    if not anomalias.empty:
                        st.write("Conjuntos com desempenho estatisticamente anômalo (pior ou melhor que sua média):")
                        st.dataframe(anomalias[['NomConjunto', indicador_selecionado, 'MediaHistorica', 'Z_Score']])
                    else:
                        st.success("Nenhuma anomalia estatística significativa encontrada para o ano selecionado.")

                st.markdown("### Comparação Histórica do Pior Conjunto")
                if not ranking_piores.empty:
                    pior_conjunto_nome = ranking_piores['NomConjunto'].iloc[0]
                    pior_conjunto_id = ranking_piores['ConjuntoID'].iloc[0]
                    st.write(
                        f"Analisando a evolução para o pior conjunto de {ano_selecionado}: **{pior_conjunto_nome}**")
                    df_pior_conjunto = df_distribuidora[df_distribuidora['ConjuntoID'] == pior_conjunto_id]
                    evolucao_pior = df_pior_conjunto.groupby('Ano')[indicador_selecionado].mean().reset_index()
                    fig2 = px.bar(evolucao_pior, x='Ano', y=indicador_selecionado,
                                  title=f"Evolução Histórica de {indicador_selecionado} para {pior_conjunto_nome}")
                    st.plotly_chart(fig2, use_container_width=True, key="pior_conjunto_hist")

                st.markdown("---")
                ranking_melhores = df_analise_ano.groupby(['NomConjunto', 'ConjuntoID'])[
                    indicador_selecionado].mean().sort_values(ascending=True).reset_index()
                st.markdown(f"### Melhores Conjuntos em {ano_selecionado}")
                fig_melhores = px.bar(ranking_melhores.head(20), x=indicador_selecionado, y='NomConjunto',
                                      orientation='h',
                                      title=f"Top 20 Melhores Conjuntos por {indicador_selecionado}",
                                      labels={indicador_selecionado: f'Valor Médio de {indicador_selecionado}',
                                              'NomConjunto': 'Conjunto'})
                fig_melhores.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500, margin=dict(l=300))
                st.plotly_chart(fig_melhores, use_container_width=True, key="melhores_conjuntos_bar")

                st.markdown("### Comparação Histórica do Melhor Conjunto")
                if not ranking_melhores.empty:
                    melhor_conjunto_nome = ranking_melhores['NomConjunto'].iloc[0]
                    melhor_conjunto_id = ranking_melhores['ConjuntoID'].iloc[0]
                    st.write(
                        f"Analisando a evolução para o melhor conjunto de {ano_selecionado}: **{melhor_conjunto_nome}**")
                    df_melhor_conjunto = df_distribuidora[df_distribuidora['ConjuntoID'] == melhor_conjunto_id]
                    evolucao_melhor = df_melhor_conjunto.groupby('Ano')[indicador_selecionado].mean().reset_index()
                    fig_melhor2 = px.bar(evolucao_melhor, x='Ano', y=indicador_selecionado,
                                         title=f"Evolução Histórica de {indicador_selecionado} para {melhor_conjunto_nome}")
                    st.plotly_chart(fig_melhor2, use_container_width=True, key="melhor_conjunto_hist")

                st.markdown("### Ranking Completo dos Conjuntos (Ordenado do Pior ao Melhor)")
                st.dataframe(ranking_piores, use_container_width=True)

            elif tipo_analise == "Séries Temporais e Previsões":
                ts_data = df_distribuidora.groupby('Data')[indicador_selecionado].mean().resample('MS').asfreq()
                ts_data.fillna(ts_data.mean(), inplace=True)
                st.markdown("### Série Temporal Mensal Histórica")
                fig_hist = px.line(ts_data, x=ts_data.index, y=ts_data.values, labels={'x': 'Data', 'y': 'Valor Médio'},
                                   title=f"Média Mensal de {indicador_selecionado}")
                st.plotly_chart(fig_hist, use_container_width=True)
                st.markdown("### Previsões para os Próximos 12 Meses")
                if len(ts_data.dropna()) < 24:
                    st.warning(
                        "Não há dados históricos suficientes (mínimo de 24 meses) para gerar uma previsão confiável.")
                elif st.button("Gerar Previsões (Pode levar um minuto)"):
                    try:
                        with st.spinner("Treinando modelo SARIMAX e gerando previsão..."):
                            model_sarimax = SARIMAX(ts_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12),
                                                    enforce_stationarity=False, enforce_invertibility=False)
                            results = model_sarimax.fit(disp=False)
                            forecast_object = results.get_forecast(steps=12)
                            forecast_ci = forecast_object.conf_int()
                            forecast_mean = forecast_object.predicted_mean
                            fig_forecast = go.Figure()
                            fig_forecast.add_trace(
                                go.Scatter(x=ts_data.index, y=ts_data.values, mode='lines', name='Histórico'))
                            fig_forecast.add_trace(
                                go.Scatter(x=forecast_mean.index, y=forecast_mean.values, mode='lines', name='Previsão',
                                           line=dict(dash='dash')))
                            fig_forecast.add_trace(
                                go.Scatter(x=forecast_ci.index, y=forecast_ci.iloc[:, 0], fill=None, mode='lines',
                                           line_color='rgba(255,255,255,0)', showlegend=False))
                            fig_forecast.add_trace(
                                go.Scatter(x=forecast_ci.index, y=forecast_ci.iloc[:, 1], fill='tonexty',
                                           fillcolor='rgba(0,176,246,0.4)', mode='lines',
                                           line_color='rgba(255,255,255,0)', name='Intervalo de Confiança'))
                            fig_forecast.update_layout(
                                title=f"Histórico vs. Previsão SARIMAX para {indicador_selecionado}",
                                xaxis_title="Data", yaxis_title=f"Valor do {indicador_selecionado}")
                            st.plotly_chart(fig_forecast, use_container_width=True)
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao gerar a previsão: {e}")
                        st.info(
                            "Isso pode acontecer se os dados históricos não forem adequados para o modelo (ex: pouca variação, muitos zeros).")

            elif tipo_analise == "Simulação de Cenário":
                st.markdown("### Análise de Cenário 'What-if'")
                st.write(
                    "Insira um valor para o indicador e veja qual seria sua posição em relação aos dados históricos da distribuidora.")
                valor_simulado = st.number_input(f"Insira um valor para {indicador_selecionado}:",
                                                 value=float(df_distribuidora[indicador_selecionado].mean()), step=1.0,
                                                 format="%.2f")
                if st.button("Analisar Cenário"):
                    valores_historicos = df_distribuidora[indicador_selecionado].dropna()
                    percentil = (valores_historicos < valor_simulado).mean() * 100
                    st.success(
                        f"Um valor de **{valor_simulado:.2f}** seria melhor que **{percentil:.2f}%** dos registros históricos para esta distribuidora.")

            st.sidebar.markdown("---")
            st.sidebar.subheader("Exportar Dados")
            csv = df_distribuidora.to_csv(index=False).encode('utf-8')
            st.sidebar.download_button(
                label="Baixar dados da distribuidora (.csv)",
                data=csv,
                file_name=f"{distribuidora_selecionada}_dados_completos.csv",
                mime='text/csv',
            )