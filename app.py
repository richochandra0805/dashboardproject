import pandas as pd
import plotly.express as px
import streamlit as st
import requests
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Adaro-ITB Water Command Center",
    page_icon="https://www.adaro.com/adaro-content/themes/adaro/assets/images/favicon.ico",
    layout="wide"
)

# --- 2. FUNGSI-FUNGSI BANTUAN ---
@st.cache_data
def load_data(filepath):
    """Memuat semua sheet yang diperlukan dari file Excel."""
    try:
        df_dashboard = pd.read_excel(filepath, sheet_name="DASHBOARD", header=3, usecols="B:C")
        df_rangkum = pd.read_excel(filepath, sheet_name="Rangkum", header=1, usecols="B:S")
        df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])
        return df_dashboard, df_rangkum
    except FileNotFoundError:
        st.error(f"File Excel '{filepath}' tidak ditemukan. Pastikan file tersebut berada di folder yang sama dengan app.py.")
        return None, None
    except Exception as e:
        st.error(f"Gagal memuat data dari Excel. Pastikan nama sheet ('DASHBOARD', 'Rangkum') sudah benar. Detail: {e}")
        return None, None

def get_status_style(status):
    """Memberikan style CSS berdasarkan status EWS."""
    status_lower = str(status).lower()
    color_map = {
        'aman': ("#28a745", "white"), 'waspada': ("#F9A825", "black"),
        'siaga': ("#fd7e14", "white"), 'awas': ("#dc3545", "white")
    }
    bg_color, text_color = color_map.get(status_lower, ("grey", "white"))
    return (f"background-color: {bg_color}; color: {text_color}; padding: 2rem; "
            f"text-align: center; border-radius: 12px; border: 2px solid {text_color};")

def fetch_weather_data(lat, lon):
    """Mengambil data cuaca dari API Open-Meteo (Gratis, tanpa API Key)."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['current']
        return {"suhu": data['temperature_2m'], "kelembapan": data['relative_humidity_2m'], "hujan": data['precipitation']}
    except requests.exceptions.RequestException:
        return None

# --- 3. MEMUAT DATA ---
excel_file = "Daily_Water_Balance.xlsx"
df_dashboard, df_rangkum = load_data(excel_file)

# --- 4. TAMPILAN UTAMA (UI) ---
if df_dashboard is not None:
    # --- HEADER ---
    col_logo1, col_title, col_logo2 = st.columns([1, 4, 1])
    with col_logo1:
        st.image("https://www.adaro.com/adaro-content/themes/adaro/assets/images/logo_adaro_energy.png", width=200)
    with col_title:
        st.title("Water Management Command Center")
        st.markdown("##### *A Partnership of Adaro Indonesia Project Development & ITB*")
    with col_logo2:
        try:
            st.image("assets/logo_itb.png", width=100)
        except Exception:
            st.error("Logo ITB tidak ditemukan di folder 'assets'")

    st.markdown("---")

    # --- KONTEN UTAMA DENGAN TABS ---
    tab_list = ["🚨 **EWS & Kesiagaan**", "📊 **Status Harian Pond**", "🌦️ **Cuaca & Proyeksi Iklim**", "📹 **Simulasi & Media**"]
    tab1, tab2, tab3, tab4 = st.tabs(tab_list)

    with tab1:
        st.header("Early Warning System (EWS) - Status Kedaruratan Tambang")
        latest_status = df_dashboard.iloc[0]['STATUS']
        latest_reason = df_dashboard.iloc[0]['Keterangan']
        st.markdown(f"<div style='{get_status_style(latest_status)}'><h2 style='margin:0; font-size: 3rem;'>{latest_status.upper()}</h2><p style='margin:0; font-size: 1.2rem;'>{latest_reason}</p></div>", unsafe_allow_html=True)

    with tab2:
        st.header("Pemantauan Harian Settling Pond")
        default_date = df_rangkum['Tanggal'].max()
        selected_date = st.date_input("Pilih Tanggal Laporan:", value=default_date, key="date_filter")
        df_daily = df_rangkum[df_rangkum['Tanggal'] == pd.to_datetime(selected_date)].copy()
        # ... (sisa kode tab 2 sama seperti sebelumnya)

    with tab3:
        st.header("Pantauan Cuaca dan Proyeksi Perubahan Iklim")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Cuaca Real-time per Jam")
            weather_data = fetch_weather_data(lat=-3.45, lon=115.58) # Koordinat Adaro
            if weather_data:
                st.metric("Suhu", f"{weather_data['suhu']} °C")
                st.metric("Curah Hujan (per jam)", f"{weather_data['hujan']} mm")
                st.metric("Kelembapan", f"{weather_data['kelembapan']} %")
            else:
                st.error("Gagal mengambil data cuaca.")
        with col2:
            st.subheader("Proyeksi Iklim Jangka Panjang")
            ssp_scenario = st.selectbox("Pilih Skenario Proyeksi Iklim:", ('SSP1-2.6', 'SSP2-4.5', 'SSP5-8.5'))
            try:
                st.image("assets/ssp_projection.gif", caption=f"Animasi proyeksi untuk skenario {ssp_scenario}")
            except FileNotFoundError:
                st.info("File 'ssp_projection.gif' akan ditampilkan di sini.")

    with tab4:
        st.header("Simulasi Luapan Void Paringin")
        st.info("Video simulasi ini menunjukkan potensi dampak jika terjadi luapan pada kondisi ekstrem.")
        try:
            video_file = open('assets/simulasi_luapan.mp4', 'rb')
            st.video(video_file.read())
        except FileNotFoundError:
            st.info("File video 'simulasi_luapan.mp4' akan ditampilkan di sini.")

    with st.expander("📂 Lihat Data Mentah Lengkap (Tabel Rangkuman)"):
        st.dataframe(df_rangkum)
