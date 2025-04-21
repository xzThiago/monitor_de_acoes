import streamlit as st
import pandas as pd
import investpy as ip
from datetime import datetime, timedelta
import plotly.graph_objs as go

countries = ['Brazil', 'United States']
intervals = ['Daily', 'Weekly', 'Monthly']

start_date = datetime.today() - timedelta(days=30)
end_date = datetime.today()

@st.cache #salvando os dados em cache para facilitar o carregamento
def consultar_acao(stock, country, from_date, to_date, interval):
    df = ip.get_stock_historical_data(stock=stock, country=country, from_date=from_date, to_date=to_date, interval=interval)
    return df

def formatar_data(dt, format='%d/%m/%Y'):
    return dt.strftime(format)


def plotCandleStick(df, acao='ticket'):
    tracel = {
        'x':     df.index,
        'open':  df.Open,
        'close': df.Close,
        'high':  df.High,
        'low':   df.Low,
        'type':  'candlestick',
        'name':  acao,
        'showlegend': False
    }

    data   = [tracel]
    layout = go.Layout()

    fig = go.Figure(data=data, layout=layout)
    return fig



## Criando Barra Lateral
barra_lateral = st.sidebar.empty()

## Criando elemento de seleção na barra lateral
selecionar_pais = st.sidebar.selectbox("Selecione o País:", countries)

## Salvando os ativos do País selecionado
acoes = ip.get_stocks_list(country=selecionar_pais)

## Criando elemento para escolher o Ativo
selecionar_acao = st.sidebar.selectbox("Selecione o Ativo:", acoes)

## Criando elemento para selecionar o período de data
from_date = st.sidebar.date_input('De', start_date)
to_date   = st.sidebar.date_input('Até', end_date)

## Criando elemento par selecionar o intervalo de data (dia, semana, mês)
selecionar_intervalo = st.sidebar.selectbox('Selecione o intervalo:', intervals)

## Criando elemento para carregar os dados
carregar_dados = st.sidebar.checkbox("Carregar dados")

## Criando elementos centrais da pagina
st.title('Stock Monitor')
st.header('Ativo')
st.subhe