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

favicon = Image.open('logo.jfif')
st.set_page_config(page_title='BiruBeard',page_icon=favicon,layout="wide", initial_sidebar_state="collapsed")

#@st.cache_data.clear()
@st.cache_data
def importar_agendamentos():
    df=pd.read_excel(r"base_agendamentos.xlsx",header=7)
    df.drop('Unnamed: 0', axis=1,inplace=True)
    df.drop('Unnamed: 1', axis=1,inplace=True)
    df['Data e hora']=pd.to_datetime(df['Data e hora'],dayfirst=True)
    df['ano'] = pd.DatetimeIndex(df['Data e hora']).year
    df['mes'] = pd.DatetimeIndex(df['Data e hora']).month
    #df_limpo= df.astype(str) # convertendo todas as colunas em str
    return df

@st.cache_data
def importar_clientes():
    df=pd.read_excel(r"base_clientes.xlsx",header=7)
    df.drop('Unnamed: 0', axis=1,inplace=True)
    df.drop('Unnamed: 1', axis=1,inplace=True)
    df['Primeira visita']=pd.to_datetime(df['Primeira visita'],dayfirst=True)
    df['Ultima visita']=pd.to_datetime(df['Ultima visita'],dayfirst=True)
    #df_limpo= df.astype(str) # convertendo todas as colunas em str
    return df

df_agendamentos = importar_agendamentos()
df_clientes = importar_clientes()
st.title ('BiruBeard Analytics')
df_agendamentos
fat_por_ano = px.bar(df_agendamentos[['ano','Receita total']].groupby(by=['ano']).sum().reset_index(), x="ano", y="Receita total",text_auto=True, title='Faturamento por ano')
st.plotly_chart(fat_por_ano, use_container_width=True,)
#st.write(df_agendamentos.shape)
#df_agendamentos
st.write("----")
st.write("###")
#st.write(df_clientes.shape)
#df_clientes
