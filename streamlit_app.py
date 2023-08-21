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
import datetime as dt
from calendar import monthrange

favicon = Image.open('logo.jfif')
st.set_page_config(page_title='BiruBeard',page_icon=favicon,layout="wide", initial_sidebar_state="collapsed")

@st.cache_data.clear()
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

dict_meses={1:'jan',2:'fev',3:'mar',4:'abr',5:'mai',6:'jun',7:'jul',8:'ago',9:'set',10:'out',11:'nov',12:'dez'}

col1,col2=st.columns([3,1])
with col1:
    ano_atual=df_agendamentos['ano'].max()
    ultimo_mes_ano_atual=df_agendamentos[df_agendamentos['ano']==ano_atual]['mes'].max()
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
    st.write('---')
    fat_projetado_ano=(faturamento_ate_mes_atual_ano_atual/ultimo_mes_ano_atual)*12
    tickets_ano_atual=df_agendamentos[(df_agendamentos['ano']==ano_atual) & (df_agendamentos['Status']=='Concluída')]['ID da Reserva'].count()
    st.write(f'Faturamento projetado {int(ano_atual)}: **R${fat_projetado_ano:,.2f}**')
    st.write(f'QTD de tickets {int(ano_atual)}: **{tickets_ano_atual}**')
    st.write(f'Ticket médio {int(ano_atual)}: **R${round(faturamento_ate_mes_atual_ano_atual/tickets_ano_atual,2)}**')

    
    

col1,col2=st.columns([3,1]) 
with col1:
    fig_fat_por_mes_ano_atual=px.bar(df_agendamentos[df_agendamentos['ano']==ano_atual][['mes','Receita total']].groupby(by=['mes']).sum().reset_index(), x="mes", y="Receita total",text_auto=True, title='Faturamento por mês')
    st.plotly_chart(fig_fat_por_mes_ano_atual, use_container_width=True,)
with col2:


    mes_atual_str=dict_meses[ultimo_mes_ano_atual]
    #st.write(mes_atual_str)
    fat_mes_atual=df_agendamentos[(df_agendamentos['mes']==ultimo_mes_ano_atual) & (df_agendamentos['ano']==ano_atual)]['Receita total'].sum()
    fat_mes_passado=df_agendamentos[(df_agendamentos['mes']==ultimo_mes_ano_atual-1) & (df_agendamentos['ano']==ano_atual)]['Receita total'].sum()
    crescimento_mes=(fat_mes_atual-fat_mes_passado)/fat_mes_passado
    fat_mes_atual_ano_passado=df_agendamentos[(df_agendamentos['mes']==ultimo_mes_ano_atual) & (df_agendamentos['ano']==ano_atual-1)]['Receita total'].sum()
    tickets_mes_atual=df_agendamentos[(df_agendamentos['mes']==ultimo_mes_ano_atual) & (df_agendamentos['ano']==ano_atual) & (df_agendamentos['Status']=='Concluída')]['ID da Reserva'].count()
    dia_atual=dt.date.today().day
    ultimo_dia_mes_atual=dt.date.today().replace(day=monthrange(dt.date.today().year,dt.date.today().month)[1]).day
    fat_projetado_mes_atual=(fat_mes_atual/dia_atual)*ultimo_dia_mes_atual
    #st.write(ultimo_dia_mes_atual)
    st.metric(label=f"Faturamento mês {mes_atual_str}:", value=f"R${fat_mes_atual:,.2f}", delta=f"{crescimento_mes:.2%} vs {dict_meses[ultimo_mes_ano_atual-1]}")
    st.write('---')
    #st.write(f'Faturamento do mês atual em {ano_atual-1:.0f}: **R${fat_mes_atual_ano_passado:,.2f}**')
    st.write(f'Faturamento projetado {mes_atual_str}: **R${fat_projetado_mes_atual:,.2f}**')
    #st.write(dia_atual)
    st.write(f'QTD de tickets {mes_atual_str}: **{tickets_mes_atual}**')
    st.write(f'Ticket médio {mes_atual_str}: **R${round(fat_mes_atual/tickets_mes_atual,2)}**')
    st.write('---')

    

num_colunas = df_agendamentos[(df_agendamentos['mes']==ultimo_mes_ano_atual) & (df_agendamentos['ano']==ano_atual)]['Funcionário'].nunique()
num_colunas
coluna=0

col1,col2,col3,col4 = st.columns([1,1,1,1])
with col1:
    selecao_ano2=st.radio("Selecione o ano:  " ,df_agendamentos['ano'].unique().astype(int),horizontal=True)
with col2:
    selecao_mes2=st.radio("Selecione o mês:  " ,df_agendamentos[df_agendamentos['ano']==selecao_ano2]['mes'].unique().astype(int),horizontal=True)
with col3:
    selecao_visao=st.radio("Ver por:" ,['Valor','Porcentagem'], horizontal=True)
    dict_visao={'Valor':'Receita total','Porcentagem':'Porcentagem'}
with col4:
    selecao_visao2=st.radio("Ver por:  ",['Receita total','QTD'], horizontal=True)
st.write('###')
st.write('###')
mes_selecionado_str=dict_meses[selecao_mes2]

selecao_func_para_iterar=np.sort(df_agendamentos[(df_agendamentos['mes']==selecao_mes2) & (df_agendamentos['ano']==selecao_ano2)]['Funcionário'].unique())
#selecao_func_para_iterar

colunas=st.columns(num_colunas)
for func in selecao_func_para_iterar:

    with colunas[coluna]:
        st.write(f"**{func}** - **{mes_selecionado_str}/{int(selecao_ano2)}**")
        df_func_atual=df_agendamentos[(df_agendamentos['mes']==selecao_mes2) & (df_agendamentos['ano']==selecao_ano2) & (df_agendamentos['Funcionário']==func)]


        #Criação da tabela pro gráfico
        if selecao_visao2=='QTD':
            df_vendas_por_categoria_barbeiro=df_func_atual[['Funcionário','Categoria principal','Receita total']].groupby(['Funcionário','Categoria principal']).count().reset_index()
            df_vendas_por_categoria_barbeiro['Porcentagem']=df_func_atual[['Funcionário','Categoria principal','Receita total']].groupby(['Funcionário','Categoria principal']).count().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
            df_vendas_por_categoria_barbeiro['Porcentagem']=round(df_vendas_por_categoria_barbeiro['Porcentagem']).astype(int)
        else:

            df_vendas_por_categoria_barbeiro=df_func_atual[['Funcionário','Categoria principal','Receita total']].groupby(['Funcionário','Categoria principal']).sum().reset_index()
            df_vendas_por_categoria_barbeiro['Porcentagem']=df_func_atual[['Funcionário','Categoria principal','Receita total']].groupby(['Funcionário','Categoria principal']).sum().groupby(level=0).apply(lambda x: 100 * x / float(x.sum())).values
            df_vendas_por_categoria_barbeiro['Porcentagem']=round(df_vendas_por_categoria_barbeiro['Porcentagem']).astype(int)

        #Criação do gráfico por funcionario

        fig_vendas_categoria_barbeiro=px.bar(
                df_vendas_por_categoria_barbeiro,
                #name=funcionario,
                y=dict_visao[selecao_visao],
                x='Categoria principal',
                text=dict_visao[selecao_visao])
        fig_vendas_categoria_barbeiro.update_yaxes(title_text='')
        fig_vendas_categoria_barbeiro.update_xaxes(title_text='')
        if dict_visao[selecao_visao]=='Porcentagem':
            fig_vendas_categoria_barbeiro.update_traces(texttemplate='%{y}%', textposition='inside', textangle=0)
        else:
            fig_vendas_categoria_barbeiro.update_traces(texttemplate='%{text:.2s}', textposition='inside', textangle=0)
        st.plotly_chart(fig_vendas_categoria_barbeiro, use_container_width=True)











        
        qtd_tickets_atual_func=df_func_atual[df_func_atual['Status']=='Concluída']['ID da Reserva'].count()
        faturamento_atual_func=df_func_atual['Receita total'].sum()
        st.write(f'Faturamento {mes_selecionado_str}/{int(selecao_ano2)}: **R${faturamento_atual_func:,.2f}**')
        st.write(f'Qtd Tickets {mes_selecionado_str}/{int(selecao_ano2)}: **{qtd_tickets_atual_func}**')
        st.write(f'Ticket médio {mes_selecionado_str}/{int(selecao_ano2)}: **R{faturamento_atual_func/qtd_tickets_atual_func:,.2f}**')
       




        
        




        st.write('-----')
    coluna=coluna+1

#st.write(df_agendamentos.shape)
#df_agendamentos
st.write("----")
st.write("###")
#st.write(df_clientes.shape)
#df_clientes
