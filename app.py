
import pandas as pd

import plotly.express as px

import streamlit as st

import numpy as np



# Base Web

st.set_page_config(page_title='Dashboard Water Balance',

                   page_icon=":bar_chart",

                   layout="wide",

                   )

st.title('DASHBOARD WATER BALANCE FOR LW AREA')



# Import Dataset

excel_file = "Daily_Water_Balance.xlsx"

sheet_name = "Rangkum"

df = pd.read_excel(io=excel_file,

                   engine='openpyxl',

                   sheet_name=sheet_name,

                   usecols='B:S',

                   header=1,

                )





# Daily Dashboard

st.subheader('Daily Report')



# Filter tanggal

ddate = st.date_input("Silahkan pilih tanggal yang ingin diamati:",value=pd.to_datetime('2024/01/01'))

ddate = pd.to_datetime(ddate)

df_daily = df[df['Tanggal'] == ddate]



# Buat dataframe untuk status SP

low = df_daily.loc[df_daily['Kriteria'] == 'Low']

low = low['Settling Pond'].tolist()

medium = df_daily.loc[df_daily['Kriteria'] == 'Medium']

medium = medium['Settling Pond'].tolist()

high = df_daily.loc[df_daily['Kriteria'] == 'High']

high = high['Settling Pond'].tolist()

daily_bar = px.bar(

    df_daily,

    x='Max Rainfall to SP (mm)',

    y='Settling Pond',

    orientation='h',

    title='Max Rainfall to SP',

)



# Buat dataframe untuk Piechart

status_counts = df_daily['Kriteria'].value_counts()

status_counts = status_counts.to_frame(name='Jumlah')



# Plot Piechart

pie_chart = px.pie(status_counts,

                   title="SP Status "+str(ddate.strftime('%d-%m-%Y')),

                   values='Jumlah',

                   names=status_counts.index,

                #    width=350

                   )

pie_chart.update_traces(textinfo='value')



# Visualisasi

# Plot

col1,col2 = st.columns(2)

col1.plotly_chart(pie_chart)

col2.plotly_chart(daily_bar)

# Keterangan

col1, col2, col3 = st.columns(3)

col1.write("SP Low Status:")

for i in range(len(low)):

    col1.write(str(i+1)+". "+str(low[i]))

col2.write("SP Medium Status:")

for i in range(len(medium)):

    col2.write(str(i+1)+". "+str(medium[i]))

col3.write("SP High Status:")

for i in range(len(high)):

    col3.write(str(i+1)+". "+str(high[i]))





# Historical Dashboard

st.subheader('Historical Report')

sisa=px.line(df,

        x='Tanggal',

        y='Sisa Freeboard (m)',

        color='Settling Pond',

        width=1250,

        title="Sisa Freeboard",

        line_shape='spline'

        )

debit=px.line(df,

        x='Tanggal',

        y='Debit Keluar Actual (m3/s)',

        color='Settling Pond',

        width=1250,

        title="Debit Keluar",

        line_shape='spline'

        )

st.plotly_chart(sisa)

st.plotly_chart(debit)



st.subheader('Data Summary')

st.dataframe(df)
