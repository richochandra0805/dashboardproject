import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
# import requests # Library untuk mengambil data API cuaca

# --- 1. KONFIGURASI HALAMAN DAN JUDUL ---
st.set_page_config(
    page_title="Adaro-ITB Water Balance Command Center",
    page_icon="https://www.adaro.com/adaro-content/themes/adaro/assets/images/favicon.ico",
    layout="wide"
)

# --- FUNGSI-FUNGSI BANTUAN ---
@st.cache_data
def load_data(filepath):
    """Memuat semua sheet yang diperlukan dari file Excel."""
    try:
        df_dashboard = pd.read_excel(filepath, sheet_name="DASHBOARD", header=3, usecols="B:C")
        df_rangkum = pd.read_excel(filepath, sheet_name="Rangkum", header=1, usecols="B:S")
        df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])
        return df_dashboard, df_rangkum
    except Exception as e:
        st.error(f"Gagal memuat file Excel '{filepath}'. Pastikan file ada dan nama sheet (DASHBOARD, Rangkum) sudah benar.")
        return None, None

def get_status_style(status):
    """Memberikan style CSS berdasarkan status EWS."""
    status_lower = str(status).lower()
    color_map = {
        'aman': ("#28a745", "white"),    # Hijau
        'waspada': ("#F9A825", "black"), # Kuning ITB
        'siaga': ("#fd7e14", "white"),   # Oranye
        'awas': ("#dc3545", "white")     # Merah
    }
    bg_color, text_color = color_map.get(status_lower, ("grey", "white"))
    return f"background-color: {bg_color}; color: {text_color}; padding: 2rem; text-align: center; border-radius: 12px;"

# --- MEMUAT DATA ---
excel_file = "Daily_Water_Balance.xlsx"
df_dashboard, df_rangkum = load_data(excel_file)

# --- TAMPILAN UTAMA (UI) ---
if df_dashboard is not None:
    # --- HEADER ---
    col_logo1, col_title, col_logo2 = st.columns([1, 4, 1])
    with col_logo1:
        st.image("https://www.adaro.com/adaro-content/themes/adaro/assets/images/logo_adaro_energy.png", width=200)
    with col_title:
        st.title("Water Balance Command Center")
        st.subheader("Project Development Section - Adaro Indonesia & ITB")
    with col_logo2:
        # Anda bisa menyimpan logo ITB di folder assets
        # st.image("assets/logo_itb.png", width=100) 
        st.write("**ITB**")

    st.markdown("---")

    # --- 2. EARLY WARNING SYSTEM (EWS) ---
    st.subheader("🚨 Early Warning System (EWS) - Kesiagaan Kedaruratan")
    latest_status = df_dashboard.iloc[0]['STATUS']
    latest_reason = df_dashboard.iloc[0]['Keterangan']
    style = get_status_style(latest_status)
    st.markdown(f"<div style='{style}'><h2 style='margin:0; font-size: 3rem;'>{latest_status.upper()}</h2><p style='margin:0; font-size: 1.2rem;'>{latest_reason}</p></div>", unsafe_allow_html=True)
    st.markdown("---")

    # --- KONTEN UTAMA DENGAN TABS ---
    tab1, tab2, tab3 = st.tabs([
        "📊 Status Settling Pond", 
        "🌦️ Cuaca & Proyeksi Iklim", 
        "📹 Simulasi Visual"
    ])

    # --- TAB 1: STATUS SETTLING POND ---
    with tab1:
        st.header("Pemantauan Harian Settling Pond")
        
        # Filter tanggal
        default_date = df_rangkum['Tanggal'].max()
        selected_date = st.date_input("Pilih Tanggal Laporan:", value=default_date, key="date_filter")
        df_daily = df_rangkum[df_rangkum['Tanggal'] == pd.to_datetime(selected_date)].copy()

        if df_daily.empty:
            st.warning(f"Tidak ada data untuk tanggal {selected_date.strftime('%d-%m-%Y')}.")
        else:
            col1, col2 = st.columns([1, 2])
            with col1:
                status_counts = df_daily['Kriteria'].value_counts().reset_index()
                pie_chart = px.pie(status_counts, title="Proporsi Status SP", values='count', names='Kriteria', hole=.4,
                                   color='Kriteria', color_discrete_map={'Low': '#28a745', 'Medium': '#F9A825', 'High': '#dc3545'})
                st.plotly_chart(pie_chart, use_container_width=True)
            with col2:
                daily_bar = px.bar(df_daily, x='Max Rainfall to SP (mm)', y='Settling Pond', orientation='h',
                                   title='Curah Hujan Maksimal per SP', color='Max Rainfall to SP (mm)', color_continuous_scale='Blues')
                st.plotly_chart(daily_bar, use_container_width=True)

    # --- TAB 2: CUACA & PROYEKSI IKLIM ---
    with tab2:
        st.header("Pantauan Cuaca Real-time dan Proyeksi Iklim Masa Depan")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cuaca Saat Ini (Real-time)")
            st.info("Fitur ini memerlukan API Key dari Wunderground/Weather.com")
            # --- CONTOH KODE UNTUK MENGAMBIL DATA CUACA (perlu API KEY) ---
            # api_key = "KUNCI_API_ANDA"
            # lat, lon = -3.45, 115.58 # Perkiraan koordinat Adaro
            # url = f"https://api.weather.com/v3/wx/observations/current?geocode={lat},{lon}&format=json&apiKey={api_key}"
            # try:
            #     response = requests.get(url).json()
            #     st.metric("Suhu", f"{response['temperature']}°C")
            #     st.metric("Curah Hujan (1 Jam)", f"{response['precip1Hour']} mm")
            #     st.metric("Kelembapan", f"{response['relativeHumidity']}%")
            # except Exception:
            #     st.error("Gagal mengambil data cuaca real-time.")
            st.metric("Suhu", "28°C", "Cerah Berawan")
            st.metric("Curah Hujan (1 jam terakhir)", "0.2 mm")

        with col2:
            st.subheader("Proyeksi Perubahan Iklim")
            ssp_scenario = st.selectbox("Pilih Skenario Proyeksi Iklim:", ('SSP1-2.6 (Optimis)', 'SSP2-4.5 (Moderat)', 'SSP5-8.5 (Pesimis)'))
            
            # Anda bisa menyimpan gambar .gif atau .png di folder assets
            if "SSP1-2.6" in ssp_scenario:
                # st.image("assets/ssp126.gif")
                st.success("Pada skenario ini, kenaikan suhu dan curah hujan ekstrem dapat ditekan secara signifikan setelah tahun 2050.")
            elif "SSP2-4.5" in ssp_scenario:
                # st.image("assets/ssp245.gif")
                st.warning("Pada skenario ini, kenaikan curah hujan ekstrem diproyeksikan terus meningkat moderat, menuntut peningkatan kapasitas manajemen air.")
            else:
                # st.image("assets/ssp585.gif")
                st.error("Pada skenario ini, frekuensi dan intensitas hujan ekstrem diproyeksikan meningkat tajam, berisiko tinggi terhadap luapan.")

    # --- TAB 3: SIMULASI VISUAL ---
    with tab3:
        st.header("Simulasi Luapan Void Paringin")
        st.info("Video simulasi ini menunjukkan potensi dampak jika terjadi luapan pada kondisi ekstrem.")
        # Simpan file video di folder assets atau gunakan link YouTube/Vimeo
        # video_file = open('assets/simulasi_luapan.mp4', 'rb')
        # video_bytes = video_file.read()
        # st.video(video_bytes)
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Ganti dengan link video Anda

    # --- DATA EXPLORER ---
    with st.expander("📂 Lihat Data Mentah"):
        st.dataframe(df_rangkum)
