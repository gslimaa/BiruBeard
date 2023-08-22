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
from datetime import datetime
from calendar import monthrange
import requests
from unicodedata import normalize


favicon = Image.open('logo.jfif')
st.set_page_config(page_title='BiruBeard',page_icon=favicon,layout="wide", initial_sidebar_state="collapsed")
#123
#@st.cache_data.clear()
@st.cache_data()
def importar_agendamentos():
    df=pd.read_excel(r"lista_fixa.xlsx",header=7)
    df.drop('Unnamed: 0', axis=1,inplace=True)
    df.drop('Unnamed: 1', axis=1,inplace=True)

    last_line=df.tail(1).index.values.astype(int)
    df.drop(last_line,inplace=True)
    return df

@st.cache_data(ttl=3540)
def importar_ao_vivo_agendamentos():

    hoje=datetime.today().strftime('%Y-%m-%d')
    #hoje=hoje.day
    headers = {
    'authority': 'br.booksy.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'pt',
    'baggage': 'sentry-transaction=appointments.details,sentry-public_key=8d02039ec46b4fc98b3f2fb292a10a1e,sentry-trace_id=a1bd457097d14fbcad8023438bab7721,sentry-sample_rate=2',
    'cache-control': 'no-cache',
    'origin': 'https://stats-and-reports.booksy.com',
    'pragma': 'no cache',
    'referer': 'https://stats-and-reports.booksy.com/',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sentry-trace': 'a1bd457097d14fbcad8023438bab7721-a707814464af3ec3-1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36',
    'x-access-token': 'nznw0hl6zohx464shiq5f8mgei3ex1xj',
    'x-api-key': 'frontdesk-76661e2b-25f0-49b4-b33a-9d78957a58e3',
    'x-app-version': '3.0',
    'x-fingerprint': 'de120e42-7f23-40f8-b1e0-63a7b928ce4c',
    }
    params = {
    'date_from': '2023-08-01',
    'date_till': hoje,
    'time_span': 'month',
    'report_key': 'appointments_list',
    }
    dados=[]
    response = requests.get('https://br.booksy.com/api/br/2/business_api/me/stats/businesses/60247/report',params=params,headers=headers)
    data = response.json()
    total_pages = data['sections'][0]['pagination']['last_page']
    #st.write(total_pages)
    for page in range(0, total_pages+1):
        response=requests.get('https://br.booksy.com/api/br/2/business_api/me/stats/businesses/60247/report?'+f"&page={page}",params=params,headers=headers).json()
        novos_resultados=response.get("sections",[])
        dados.extend(novos_resultados)
        #page+=1

    rows = []
    for section in dados:
        if "table" in section and "rows" in section["table"]:
            rows.extend(section["table"]["rows"])

    # Create a DataFrame from the extracted rows
    df = pd.DataFrame(rows)

    dict_troca_nome_header={'booking_date': 'Data e hora',
    'subbooking_id': 'ID da Reserva',
    'service_category_name': 'Categoria principal',
    'service_name': 'Serviço',
    'customer_name': 'Cliente',
    'staffer_name': 'Funcionário',
    'service_length': 'Comprimento do serviço',
    'service_value': 'Valor dos serviços',
    'addons_value': 'Valor dos complementos',
    'revenue_net': 'Receita líquida',
    'discount': 'Desconto',
    'tax_amount': 'Taxa',
    'tip_amount': 'Valor do troco',
    'total_revenue': 'Receita total',
    'status': 'Status'}
    df.rename(columns=dict_troca_nome_header,inplace=True)

    colunas_a_ajustar=['Valor dos serviços','Valor dos complementos','Receita líquida','Desconto','Taxa','Valor do troco','Receita total']

    for coluna in colunas_a_ajustar:
        df[coluna] = df[coluna].str.replace(r'[^\d.,]', '', regex=True)
        df[coluna] = df[coluna].str.replace(',', '.', regex=True)
        df[coluna] = df[coluna].astype(float)
    return df


df_agendamentos = importar_agendamentos()
df_agendamentos_ao_vivo=importar_ao_vivo_agendamentos()

somaaa=df_agendamentos_ao_vivo['Receita total'].sum()
st.write(somaaa)

df_agendamentos = pd.concat([df_agendamentos,df_agendamentos_ao_vivo],ignore_index=True)
df_agendamentos['Data e hora']=pd.to_datetime(df_agendamentos['Data e hora'],dayfirst=True)
df_agendamentos['ano'] = pd.DatetimeIndex(df_agendamentos['Data e hora']).year
df_agendamentos['mes'] = pd.DatetimeIndex(df_agendamentos['Data e hora']).month




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

coluna=0

col1,col2,col3,col4 = st.columns([1,1,1,1])
with col1:
    selecao_ano2=st.radio("Selecione o ano:  " ,df_agendamentos['ano'].unique().astype(int),horizontal=True)
with col2:
    selecao_mes2=st.radio("Selecione o mês:  " ,np.sort(df_agendamentos[df_agendamentos['ano']==selecao_ano2]['mes'].unique().astype(int))[::-1],horizontal=True)
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
