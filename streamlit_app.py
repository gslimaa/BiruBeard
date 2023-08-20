import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
import plotly.graph_objects as go
from io import BytesIO
from PIL import Image
import io
from pyxlsb import open_workbook as open_xlsb
import numpy as np
from st_pages import show_pages_from_config
from plotly.subplots import make_subplots

favicon = Image.open('logo.jfif')
st.set_page_config(page_title='BiruBeard',page_icon=favicon,layout="wide", initial_sidebar_state="collapsed")
#ok
#@st.cache_data.clear()
@st.cache_data(ttl=3600)
def importar_agendamentos():
    df=pd.read_excel(r"lista_de_agendamentos.xlsx",header=7)
    df.drop('Unnamed: 0', axis=1,inplace=True)
    df.drop('Unnamed: 1', axis=1,inplace=True)
    df['Data e hora']=pd.to_datetime(df['Data e hora'],dayfirst=True)
    df['ano'] = pd.DatetimeIndex(df['Data e hora']).year
    df['mes'] = pd.DatetimeIndex(df['Data e hora']).month
    last_line=df.tail(1).index.values.astype(int)
    df.drop(last_line,inplace=True)
    #df_limpo= df.astype(str) # convertendo todas as colunas em str
    return df

@st.cache_data(ttl=3600)
def importar_clientes():
    df=pd.read_excel(r"base_clientes.xlsx",header=7)
    df.drop('Unnamed: 0', axis=1,inplace=True)
    df.drop('Unnamed: 1', axis=1,inplace=True)
    df['Primeira visita']=pd.to_datetime(df['Primeira visita'],dayfirst=True)
    df['Ultima visita']=pd.to_datetime(df['Ultima visita'],dayfirst=True)
    last_line=df.tail(1).index.values.astype(int)
    df.drop(last_line,inplace=True)
    #df_limpo= df.astype(str) # convertendo todas as colunas em str
    return df

df_agendamentos = importar_agendamentos()
df_clientes = importar_clientes()
st.title ('BiruBeard Analytics')

col1,col2=st.columns([3,1])
with col1:
    ano_atual=df_agendamentos['ano'].max()
    ultimo_mes_ano_atual=df_agendamentos[df_agendamentos['ano']==2023]['mes'].max()
    faturamento_ate_mes_atual=df_agendamentos[(df_agendamentos['mes']<=ultimo_mes_ano_atual)][['ano','Receita total']].groupby(by=['ano']).sum().reset_index()
    fat_por_ano = px.bar(df_agendamentos[['ano','Receita total']].groupby(by=['ano']).sum().reset_index(), x="ano", y="Receita total",text_auto=True, title='Faturamento por ano')
    fat_por_ano.add_trace(go.Scatter(x=faturamento_ate_mes_atual['ano'], y=faturamento_ate_mes_atual['Receita total'], mode='lines+markers', text='x', showlegend=False))
    fat_por_ano.update_traces(marker=dict(size=6,color='red'),selector=dict(mode='markers'))
    st.plotly_chart(fat_por_ano, use_container_width=True,)
with col2:
    faturamento_ate_mes_atual_ano_atual=faturamento_ate_mes_atual[faturamento_ate_mes_atual['ano']==ano_atual]['Receita total'].values[0]
    faturamento_ate_mes_atual_ano_anterior=faturamento_ate_mes_atual[faturamento_ate_mes_atual['ano']==ano_atual-1]['Receita total'].values[0]
    crescimento_ytd = (faturamento_ate_mes_atual_ano_atual-faturamento_ate_mes_atual_ano_anterior)/faturamento_ate_mes_atual_ano_anterior
    st.metric(label=f"Faturamento {int(ano_atual)}:", value=f"R${faturamento_ate_mes_atual_ano_atual:,.2f}", delta=f"{crescimento_ytd:.2%} vs {int(ano_atual)-1}")
col1,col2=st.columns([1,9])
with col1:
    col11,col22=st.columns([1,1])
    with col11:
        selecao_ano=st.radio("Selecione o ano:" ,df_agendamentos['ano'].unique().astype(int))
    with col22:
        selecao_mes=st.radio("Selecione o mês:" ,df_agendamentos[df_agendamentos['ano']==selecao_ano]['mes'].unique().astype(int))
with col2:
    df_vendas_por_categoria_barbeiro=df_agendamentos[(df_agendamentos['mes']==selecao_mes) & (df_agendamentos['ano']==selecao_ano)][['Funcionário','Categoria principal','Receita total']].groupby(['Funcionário','Categoria principal']).sum().reset_index()
    df_vendas_por_categoria_barbeiro['Porcentagem']=df_agendamentos[(df_agendamentos['mes']==ultimo_mes_ano_atual) & (df_agendamentos['ano']==ano_atual)][['Funcionário','Categoria principal','Receita total']].groupby(['Funcionário','Categoria principal']).sum().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
    df_vendas_por_categoria_barbeiro['Porcentagem']=round(df_vendas_por_categoria_barbeiro['Porcentagem']).astype(int)
    vendas_categoria_barbeiro=make_subplots(rows=1, cols=df_vendas_por_categoria_barbeiro['Funcionário'].nunique(), subplot_titles=df_vendas_por_categoria_barbeiro['Funcionário'].unique())
    i=1
    selecao_visao=st.radio("Ver por:" ,['Receita total','Porcentagem'])

    for funcionario in df_vendas_por_categoria_barbeiro['Funcionário'].unique():
        vendas_categoria_barbeiro.add_trace(go.Bar(
                name=funcionario,
                y=df_vendas_por_categoria_barbeiro[df_vendas_por_categoria_barbeiro['Funcionário']==funcionario][selecao_visao],
                x=df_vendas_por_categoria_barbeiro[df_vendas_por_categoria_barbeiro['Funcionário']==funcionario]['Categoria principal'],
                text=df_vendas_por_categoria_barbeiro[df_vendas_por_categoria_barbeiro['Funcionário']==funcionario][selecao_visao]),
                #marker=dict(color=cores_personalizadas[0])),
                row=1, col=i)
        if selecao_visao=='Porcentagem':
            vendas_categoria_barbeiro.update_traces(texttemplate='%{y}%', textposition='inside', textangle=0)
        if i>1:
            vendas_categoria_barbeiro.update_yaxes(showticklabels=False, row=1, col=i,range=[0,df_vendas_por_categoria_barbeiro[selecao_visao].max()*1.1])
        else:
            vendas_categoria_barbeiro.update_yaxes(row=1, col=i,range=[0,df_vendas_por_categoria_barbeiro[selecao_visao].max()*1.1])
        i+=1
    st.plotly_chart(vendas_categoria_barbeiro, use_container_width=True,)
#st.write(df_agendamentos.shape)
#df_agendamentos
st.write("----")
st.write("###")
#st.write(df_clientes.shape)
#df_clientes
