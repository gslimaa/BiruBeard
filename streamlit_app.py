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
    #df_limpo= df.astype(str) # convertendo todas as colunas em str
    return df

@st.cache_data
def importar_clientes():
    df=pd.read_excel(r"base_clientes.xlsx",header=7)
    #df_limpo= df.astype(str) # convertendo todas as colunas em str
    return df

df_agendamentos = importar_agendamentos()

df_clientes = importar_clientes()

st.write(df_agendamentos.shape)
df_agendamentos
st.write("----")
st.write("###")
st.write(df_clientes.shape)
df_clientes
