# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

# === CONFIGURASI DASHBOARD ===
st.set_page_config(page_title='Adaro Water Monitoring', layout='wide')

# === GAYA ADMIN 2 ===
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# === SIDEBAR ===
st.sidebar.image("assets/logo_adaro.png", width=120)
st.sidebar.image("assets/logo_itb.png", width=120)
menu = st.sidebar.radio("Navigasi", [
    "Status Settling Pond",
    "Realtime Rainfall",
    "Climate Projection",
    "Void Paringin Video",
    "Early Warning System"
])

# === STATUS SETTLING POND ===
if menu == "Status Settling Pond":
    st.title('📊 Daily & Historical Status Settling Pond')
    excel_file = "data/Daily_Water_Balance.xlsx"
    df = pd.read_excel(excel_file, engine='openpyxl', sheet_name='Rangkum', usecols='B:S', header=1)

    ddate = st.date_input("Silakan pilih tanggal:", value=pd.to_datetime('2024-01-01'))
    ddate = pd.to_datetime(ddate)
    df_daily = df[df['Tanggal'] == ddate]

    # Pie Chart Status
    status_counts = df_daily['Kriteria'].value_counts().to_frame(name='Jumlah')
    pie_chart = px.pie(status_counts, title=f"Status SP {ddate.strftime('%d-%m-%Y')}", values='Jumlah', names=status_counts.index)
    pie_chart.update_traces(textinfo='value')

    # Bar Chart Rainfall
    daily_bar = px.bar(df_daily, x='Max Rainfall to SP (mm)', y='Settling Pond', orientation='h', title='Max Rainfall to SP')

    col1, col2 = st.columns(2)
    col1.plotly_chart(pie_chart)
    col2.plotly_chart(daily_bar)

    col1, col2, col3 = st.columns(3)
    for level, col in zip(['Low', 'Medium', 'High'], [col1, col2, col3]):
        sp_list = df_daily[df_daily['Kriteria'] == level]['Settling Pond'].tolist()
        col.write(f"**SP {level} Status:**")
        for i, sp in enumerate(sp_list):
            col.write(f"{i+1}. {sp}")

    # Historical
    st.subheader('📈 Historical Trend')
    sisa = px.line(df, x='Tanggal', y='Sisa Freeboard (m)', color='Settling Pond', title="Sisa Freeboard", line_shape='spline')
    debit = px.line(df, x='Tanggal', y='Debit Keluar Actual (m3/s)', color='Settling Pond', title="Debit Keluar", line_shape='spline')
    st.plotly_chart(sisa)
    st.plotly_chart(debit)
    st.subheader('🧾 Data Summary')
    st.dataframe(df)

# === REALTIME RAIN ===
elif menu == "Realtime Rainfall":
    st.title('🌧️ Realtime Rainfall Monitoring')
    from utils.fetch_weather import fetch_latest_rain
    rain_data = fetch_latest_rain()
    st.line_chart(rain_data.set_index('Time')['Rainfall (mm)'])
    st.dataframe(rain_data)

# === CLIMATE PROJECTION ===
elif menu == "Climate Projection":
    st.title('🌍 Climate Change Projection')
    col1, col2, col3 = st.columns(3)
    col1.image('climate_animation/ssp126.gif', caption='SSP1-2.6')
    col2.image('climate_animation/ssp245.gif', caption='SSP2-4.5')
    col3.image('climate_animation/ssp585.gif', caption='SSP5-8.5')

    with st.expander("Penjelasan Singkat"):
        st.write("Gambar di atas menunjukkan simulasi perubahan curah hujan di area tambang Adaro berdasarkan 3 skenario iklim CMIP6.")

# === VOID VIDEO ===
elif menu == "Void Paringin Video":
    st.title("🎥 Void Paringin Observation")
    st.video("assets/void_paringin.mp4")

# === EARLY WARNING ===
elif menu == "Early Warning System":
    st.title("🚨 Early Warning System")
    df = pd.read_excel("data/Daily_Water_Balance.xlsx", engine='openpyxl', sheet_name='Rangkum', usecols='B:S', header=1)
    latest = df[df['Tanggal'] == df['Tanggal'].max()]
    high_alert = latest[latest['Kriteria'] == 'High']

    if not high_alert.empty:
        st.error(f"⚠️ {len(high_alert)} Settling Pond dalam status HIGH!")
        for i, row in high_alert.iterrows():
            st.write(f"- {row['Settling Pond']}: {row['Sisa Freeboard (m)']} m, Rainfall: {row['Max Rainfall to SP (mm)']} mm")
    else:
        st.success("✅ Tidak ada SP dalam status HIGH saat ini.")
