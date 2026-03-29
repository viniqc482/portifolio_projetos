# app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ===============================
# 1️⃣ Carregar dados
# ===============================
@st.cache_data  # caching para não recarregar toda hora
def load_data():
    df = pd.read_csv("train.csv")
    
    # Limpeza numérica
    col_num = ['Delivery_person_Age','Vehicle_condition','Delivery_person_Ratings',
               'Time_taken(min)','Restaurant_latitude','Restaurant_longitude',
               'Delivery_location_latitude','Delivery_location_longitude']
    for c in col_num:
        df[c] = pd.to_numeric(df[c].astype(str).str.strip().str.replace(r'[^0-9.]','',regex=True), errors='coerce')
    
    # Limpeza texto
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip().replace(['nan','NaN','None',''], np.nan)
    
    # Criar coluna de distância (Euclidiana simples)
    df['distancia'] = np.sqrt((df['Restaurant_latitude'] - df['Delivery_location_latitude'])**2 +
                              (df['Restaurant_longitude'] - df['Delivery_location_longitude'])**2)
    return df

df = load_data()

# ===============================
# 2️⃣ Título e sidebar
# ===============================
st.title("Dashboard de Entregas")
st.sidebar.title("Filtros")

# Filtros
city_filter = st.sidebar.multiselect("Selecione a cidade:", df['City'].unique(), default=df['City'].unique())
traffic_filter = st.sidebar.multiselect("Tipo de tráfego:", df['Road_traffic_density'].unique(), default=df['Road_traffic_density'].unique())

# Aplicando filtros
df_filtered = df[df['City'].isin(city_filter) & df['Road_traffic_density'].isin(traffic_filter)]

# ===============================
# 3️⃣ Gráfico: Pedidos por dia
# ===============================
pedidos_por_dia = df_filtered.groupby('Order_Date').size().reset_index(name='Quantidade')
fig_dia = px.bar(pedidos_por_dia, x='Order_Date', y='Quantidade', title="Pedidos por Dia")
st.plotly_chart(fig_dia)

# ===============================
# 4️⃣ Gráfico: Pedidos por semana
# ===============================
df_filtered['Order_Date'] = pd.to_datetime(df_filtered['Order_Date'], errors='coerce')
df_filtered['Semana'] = df_filtered['Order_Date'].dt.isocalendar().week
pedidos_por_semana = df_filtered.groupby('Semana').size().reset_index(name='Quantidade')
fig_semana = px.bar(pedidos_por_semana, x='Semana', y='Quantidade', title="Pedidos por Semana")
st.plotly_chart(fig_semana)

# ===============================
# 5️⃣ Gráfico: Entregadores por semana
# ===============================
entregadores_semana = df_filtered.groupby('Semana')['Delivery_person_ID'].nunique().reset_index(name='Entregadores')
fig_entregadores = px.line(entregadores_semana, x='Semana', y='Entregadores', title="Entregadores Únicos por Semana")
st.plotly_chart(fig_entregadores)

# ===============================
# 6️⃣ Gráfico: Pedidos por tipo de tráfego
# ===============================
pedidos_trafego = df_filtered.groupby('Road_traffic_density').size().reset_index(name='Quantidade')
fig_trafego = px.pie(pedidos_trafego, names='Road_traffic_density', values='Quantidade', title="Distribuição de Pedidos por Tráfego")
st.plotly_chart(fig_trafego)

# ===============================
# 7️⃣ Gráfico: Pedidos por cidade e tipo de tráfego
# ===============================
pedidos_cidade_trafego = df_filtered.groupby(['City','Road_traffic_density']).size().reset_index(name='Quantidade')
fig_cidade_trafego = px.bar(pedidos_cidade_trafego, x='City', y='Quantidade', color='Road_traffic_density', barmode='group',
                            title="Pedidos por Cidade e Tipo de Tráfego")
st.plotly_chart(fig_cidade_trafego)

# ===============================
# 8️⃣ Mapa: Localização central por cidade e tráfego
# ===============================
# Calculando mediana das coordenadas
mapa_data = df_filtered.groupby(['City','Road_traffic_density'])[['Delivery_location_latitude','Delivery_location_longitude']].median().reset_index()
fig_mapa = px.scatter_mapbox(
    mapa_data,
    lat='Delivery_location_latitude',
    lon='Delivery_location_longitude',
    color='Road_traffic_density',
    size_max=15,
    zoom=10,
    hover_name='City',
    hover_data=['Road_traffic_density']
)
fig_mapa.update_layout(mapbox_style='open-street-map', title='Localização Central por Cidade e Tráfego')
st.plotly_chart(fig_mapa)
