import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objs as go


# Definir a configuração da página 'wide' para usar a largura total da tela
st.set_page_config(layout="wide")

# Carregando os ativos (AÇÕES) do Brasil 
CAMINHO_CSV_BRASIL = r"arquivo/acoes-listadas-b3.csv"

try:
    df_brasil = pd.read_csv(CAMINHO_CSV_BRASIL, sep =';')

    #Adicionando o sufixo ".SA" ao final dos ativos para funcionar no Yahoo Finance
    df_brasil['Ticker'] = df_brasil['Ticker'].apply(lambda x: f"{x}.SA" if not str(x).endswith('.SA') else x)

    # criaando um dicionario com a estrutura {Ticker: Nome} (COLUNAS PRESENTE LÁ NO CSV)
    tickers_brasil = dict(zip(df_brasil['Ticker'], df_brasil['Nome']))

# Se houver erro, mostrará uma mensagem e criará um dicionario vazio
except Exception as e:
    st.error(f"Erro ao carregar os dados do Brasil: {e}")
    tickers_brasil = {}

# Criando alguns ativos para o EUA
tickers_por_pais = {
    'Brazil': tickers_brasil,
    'United States': {
        'AAPL': 'Apple',
        'GOOGL': 'Alphabet (Google)',
        'MSFT': 'Microsoft',
        'AMZN': 'Amazon',
        'TSLA': 'Tesla'
    }
}

# Defindo intervalos de tempo para as consultas
# por defult, busca dados dos últimos 30 dias
intervals = ['1d', '1h', '1wk', '1mo']
start_date = datetime.today() - timedelta(days=30)
end_date = datetime.today()


# criando função para formatar data exigida pelo yfinance
def formatar_data(dt):
    return dt.strftime('%Y-%m-%d')

#criando o gráfico de velas usando o plotly com os preços de abertura, máxima, mínima e fechamento
def plot_candlestick(df, ticker):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker
    )])
    fig.update_layout(title=f'Candlestick - {ticker}', xaxis_title='Data', yaxis_title='Preço')
    return fig

### Interface do usuário
#definir o título da barra lateral
st.sidebar.title("Parâmetro de Análise")

# Menu para selecionar o país
selecionar_pais = st.sidebar.selectbox("Selecionar o País:", list(tickers_por_pais.keys()))

# Obter informações do ativos do país escolhido
tickers = tickers_por_pais.get(selecionar_pais, {})
if not tickers:
    st.error('Ativo não disponível para o esse País.')
    st.stop()

# Opções de seleção do usuário
selecionar_acao      = st.sidebar.selectbox("Selecione o Ativo:", list(tickers.keys()), format_func=lambda x: tickers[x])
from_date            = st.sidebar.date_input('De', start_date)
to_date              = st.sidebar.date_input('Até', end_date)
selecionar_intervalo = st.sidebar._selectbox('Intervalo de tempo:', intervals)
carregar_dados       = st.sidebar.checkbox("Exibir dados na tabela")

#Título da página
st.title("Monitor de Ações com yFinance")
st.subheader(f"Ativo Selecionado: {tickers[selecionar_acao]} ({selecionar_acao})")

## Download dos dados
#Valida se a data de início é anterior à data de fim
if from_date > to_date:
    st.sidebar.error("A data inicial é posterior à final.")
    st.stop()

#faz o download dos dados com yfinance conforme os filtros escolhidos
try:
    df = yf.download(selecionar_acao,
                     start     = formatar_data(from_date),
                     end       = formatar_data(to_date),
                     interval  = selecionar_intervalo)
    
    # verificando se os dados retornam vazios
    if df.empty:
        st.warning("Nenhum dado encontrado apra esse período.")
        st.stop()

    # As colunas do dataframe são multiIndex.
    #Tratamento para pegar só o nível dos nomes das colunas 
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = list(df.columns.get_level_values(0))

    colunas_necessarias = ['Open', 'High', 'Low', 'Close']
    for coluna in colunas_necessarias:
        if coluna not in df.columns:
            st.error(f"A coluna '{coluna}' está ausente nos dados.")
            st.stop()

except Exception as e:
    st.error(f"Ocorreu um erro ao carregar os dados: {e}")
    st.stop()

## Visualização dos dados
#Exibe o gráfico de vela
st.plotly_chart(plot_candlestick(df, selecionar_acao), use_container_width=True)

#Exibe o gráfico de linha com o preço de fechamento do ativo
st.line_chart(df['Close'], use_container_width=True)

#Se marcado "Exibir dados na tabela" (linha: 82), mostrará os dados em formato de tabela 
if carregar_dados:
    st.subheader("Dados históricos")
    st.dataframe(df, use_container_width=True)