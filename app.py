import pandas as pd
import plotly.express as px
import streamlit as st
import requests
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN & GAYA ---
st.set_page_config(
    page_title="Adaro Water Command Center",
    page_icon="https://www.adaro.com/adaro-content/themes/adaro/assets/images/favicon.ico",
    layout="wide"
)

# --- FUNGSI UNTUK MEMBACA DAN MENYUNTIKKAN CSS ---
def load_css(file_name):
    """Membaca file CSS lokal dan menerapkannya."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' tidak ditemukan.")

# --- FUNGSI UNTUK MEMBACA DATA DARI EXCEL (SESUAI PERMINTAAN) ---
@st.cache_data
def load_data(filepath):
    """
    Memuat semua sheet yang diperlukan dari file Excel.
    Pembacaan sheet 'Rangkum' disesuaikan persis dengan skrip referensi Anda.
    """
    try:
        # Membaca sheet DASHBOARD untuk data EWS (sesuai poin 1 & 5)
        df_dashboard = pd.read_excel(filepath, sheet_name="DASHBOARD", header=3, usecols="B:C")
        # Membersihkan nama kolom untuk mencegah error
        df_dashboard.columns = df_dashboard.columns.str.strip().str.upper()

        # Membaca sheet Rangkum untuk data utama (sesuai skrip referensi Anda)
        df_rangkum = pd.read_excel(filepath, sheet_name="Rangkum", header=1, usecols="B:S", engine='openpyxl')
        df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])
        
        return df_dashboard, df_rangkum
    except Exception as e:
        st.error(f"Gagal memuat file Excel '{filepath}'. Pastikan nama sheet benar. Error: {e}")
        return None, None

# --- EKSEKUSI UTAMA ---
load_css("style.css")
df_dashboard, df_rangkum = load_data("Daily_Water_Balance.xlsx")

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.image("https://www.adaro.com/adaro-content/themes/adaro/assets/images/logo_adaro_energy.png", width=180)
    st.image("assets/logo_itb.png", width=90)
    st.header("Adaro-ITB Partnership")
    st.markdown("---")
    
    page = st.radio(
        "Pilih Halaman Navigasi:",
        ("Dashboard Utama", "Cuaca & Proyeksi Iklim", "Simulasi & Media")
    )
    st.markdown("---")
    st.info(f"© {datetime.now().year} Adaro Indonesia")

# --- KONTEN UTAMA ---
st.title(f"📊 {page}")

if df_dashboard is not None and df_rangkum is not None:
    if page == "Dashboard Utama":
        # --- EWS (Poin 1 & 5) ---
        latest_status = df_dashboard.get('STATUS', pd.Series(dtype='str')).iloc[0]
        latest_reason = df_dashboard.get('KETERANGAN', pd.Series(dtype='str')).iloc[0]
        
        if pd.isna(latest_status):
            st.error("Kolom 'STATUS' tidak ditemukan di sheet DASHBOARD.")
        else:
            st.markdown(f"""
                <div class="card" style="background-color: {'#1cc88a' if str(latest_status).lower() == 'aman' else '#f6c23e' if str(latest_status).lower() == 'waspada' else '#e74a3b'}; color: white; text-align: center;">
                    <h2 style='margin:0; font-size: 2.5rem;'>EWS: {str(latest_status).upper()}</h2>
                    <p style='margin:0; font-size: 1.1rem;'>{str(latest_reason)}</p>
                </div>
            """, unsafe_allow_html=True)

        # --- Filter Tanggal ---
        selected_date = st.date_input("Pilih Tanggal Laporan:", value=df_rangkum['Tanggal'].max())
        df_daily = df_rangkum[df_rangkum['Tanggal'] == pd.to_datetime(selected_date)].copy()

        if not df_daily.empty:
            summary = df_daily.iloc[0]
            # --- METRIK UTAMA DALAM KARTU ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="card"><p class="metric-label">Water Level (PIT)</p><p class="metric-value">{summary["Freeboard (Elevasi Actual) (Rl)"]:.2f} m</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="card"><p class="metric-label">Sisa Freeboard</p><p class="metric-value">{summary["Sisa Freeboard (m)"]:.2f} m</p></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="card"><p class="metric-label">TSS Inflow</p><p class="metric-value">{summary["TSS Inflow (ton)"]:.2f} ton</p></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="card"><p class="metric-label">TSS Outflow</p><p class="metric-value">{summary["TSS Outflow (ton)"]:.2f} ton</p></div>', unsafe_allow_html=True)
            
            # --- GRAFIK HARIAN DALAM KARTU ---
            col_chart1, col_chart2 = st.columns([2, 3])
            with col_chart1:
                st.markdown('<div class="card"><p class="card-title">Proporsi Status SP</p></div>', unsafe_allow_html=True)
                pie_fig = px.pie(df_daily['Kriteria'].value_counts().reset_index(), values='count', names='Kriteria', hole=.4, color='Kriteria', color_discrete_map={'Low': '#28a745', 'Medium': '#F9A825', 'High': '#dc3545'})
                st.plotly_chart(pie_fig, use_container_width=True)
            with col_chart2:
                st.markdown('<div class="card"><p class="card-title">Curah Hujan Maksimal per SP</p></div>', unsafe_allow_html=True)
                bar_fig = px.bar(df_daily, x='Max Rainfall to SP (mm)', y='Settling Pond', orientation='h')
                st.plotly_chart(bar_fig, use_container_width=True)
            
            # --- DAFTAR SP BERDASARKAN STATUS (FITUR DARI SCRIPT ASLI) ---
            st.markdown("---")
            st.markdown('<p class="card-title">Daftar Settling Pond Berdasarkan Status</p>', unsafe_allow_html=True)
            col_list1, col_list2, col_list3 = st.columns(3)
            for status, column in [('Low', col_list1), ('Medium', col_list2), ('High', col_list3)]:
                with column:
                    st.markdown(f'<div class="card"><h5>Status: {status}</h5></div>', unsafe_allow_html=True)
                    sp_list = df_daily[df_daily['Kriteria'] == status]['Settling Pond'].tolist()
                    if sp_list:
                        for sp in sp_list:
                            st.markdown(f"- {sp}")
                    else:
                        st.info("Tidak ada SP dengan status ini.")
        else:
            st.warning(f"Tidak ada data untuk tanggal {selected_date.strftime('%d-%m-%Y')}.")

    elif page == "Cuaca & Proyeksi Iklim":
        st.markdown('<div class="card"><p class="card-title">Pantauan Cuaca dan Proyeksi Perubahan Iklim</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Cuaca Saat Ini (Real-time)")
            st.info("Fitur ini memerlukan API Key dari Wunderground/Weather.com")
            st.metric("Suhu", "28°C", "Cerah Berawan")
            st.metric("Curah Hujan (1 jam terakhir)", "0.2 mm")
        with col2:
            st.subheader("Proyeksi Iklim Jangka Panjang")
            ssp_scenario = st.selectbox("Pilih Skenario Proyeksi:", ('SSP1-2.6', 'SSP2-4.5', 'SSP5-8.5'))
            st.image("assets/ssp_projection.gif", caption=f"Animasi proyeksi untuk skenario {ssp_scenario}")

    elif page == "Simulasi & Media":
        st.markdown('<div class="card"><p class="card-title">Simulasi Visual Luapan Void Paringin</p></div>', unsafe_allow_html=True)
        st.video("assets/simulasi_luapan.mp4")

else:
    st.error("Gagal memuat data. Pastikan file Daily_Water_Balance.xlsx ada di folder yang sama.")
