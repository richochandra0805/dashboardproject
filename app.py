import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Adaro Water Command Center",
    page_icon="https://www.adaro.com/adaro-content/themes/adaro/assets/images/favicon.ico",
    layout="wide"
)

# --- 2. CSS KUSTOM UNTUK GAYA SB ADMIN 2 ---
def load_css():
    """Menyuntikkan CSS kustom untuk menciptakan layout berbasis kartu."""
    st.markdown("""
        <style>
            /* Mengubah warna latar belakang utama */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                background-color: #f8f9fc;
            }
            /* Style untuk komponen "Card" utama */
            .card {
                background-color: white;
                border-radius: 0.75rem;
                box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
                border: 1px solid #e3e6f0;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                height: 100%;
            }
            /* Style untuk judul di dalam card */
            .card-title {
                font-size: 1.1rem;
                font-weight: 700;
                color: #004D99; /* Biru Ganesha ITB */
                margin-bottom: 1rem;
                border-bottom: 2px solid #00AEEF; /* Biru Muda Adaro */
                padding-bottom: 0.5rem;
            }
            /* Style untuk nilai metrik yang besar */
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
                color: #3a3b45;
            }
            .metric-label {
                font-size: 1rem;
                font-weight: 500;
                color: #858796;
            }
        </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI-FUNGSI BANTUAN ---
@st.cache_data
def load_data(filepath):
    try:
        df_dashboard = pd.read_excel(filepath, sheet_name="DASHBOARD", header=3, usecols="B:C")
        df_rangkum = pd.read_excel(filepath, sheet_name="Rangkum", header=1, usecols="B:S")
        df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])
        return df_dashboard, df_rangkum
    except Exception as e:
        st.error(f"Gagal memuat file Excel '{filepath}'. Pastikan file ada dan nama sheet benar. Error: {e}")
        return None, None

def get_status_style(status):
    status_lower = str(status).lower()
    color_map = {'aman': "#1cc88a", 'waspada': "#f6c23e", 'siaga': "#e74a3b", 'awas': "#be2929"}
    return f"background-color: {color_map.get(status_lower, 'grey')}; color: white; border-radius: 0.75rem; padding: 1.5rem; text-align: center;"

# --- EKSEKUSI UTAMA ---
load_css()
df_dashboard, df_rangkum = load_data("Daily_Water_Balance.xlsx")

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.image("https://www.adaro.com/adaro-content/themes/adaro/assets/images/logo_adaro_energy.png", width=180)
    st.image("https://upload.wikimedia.org/wikipedia/id/thumb/8/8c/Logo_Institut_Teknologi_Bandung.png/220px-Logo_Institut_Teknologi_Bandung.png", width=90)
    st.header("Adaro-ITB Partnership")
    st.markdown("---")
    
    page = st.radio(
        "Pilih Halaman Navigasi:",
        ("Dashboard Utama", "Laporan Harian", "Analisis Historis", "Proyeksi & Media")
    )
    st.markdown("---")
    st.info(f"© {datetime.now().year} Adaro Indonesia")

# --- KONTEN UTAMA ---
st.title(f"📊 {page}")

if df_dashboard is not None and df_rangkum is not None:
    if page == "Dashboard Utama":
        latest_status = df_dashboard.iloc[0]['STATUS']
        latest_reason = df_dashboard.iloc[0]['Keterangan']
        st.markdown(f"<div style='{get_status_style(latest_status)}'><h2 style='margin:0; font-size: 2.5rem;'>EWS: {latest_status.upper()}</h2><p style='margin:0; font-size: 1.1rem;'>{latest_reason}</p></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        summary_data = df_rangkum[df_rangkum['Tanggal'] == df_rangkum['Tanggal'].max()].iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="card"><p class="metric-label">Water Level (PIT)</p><p class="metric-value">{:.2f} m</p></div>'.format(summary_data['Freeboard (Elevasi Actual) (Rl)']), unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card"><p class="metric-label">Sisa Freeboard</p><p class="metric-value">{:.2f} m</p></div>'.format(summary_data['Sisa Freeboard (m)']), unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="card"><p class="metric-label">TSS Inflow</p><p class="metric-value">{:.2f} ton</p></div>'.format(summary_data['TSS Inflow (ton)']), unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="card"><p class="metric-label">TSS Outflow</p><p class="metric-value">{:.2f} ton</p></div>'.format(summary_data['TSS Outflow (ton)']), unsafe_allow_html=True)

    elif page == "Laporan Harian":
        st.markdown('<div class="card" style="padding: 2rem;">'
                    '<p class="card-title">Filter Laporan Harian</p>'
                    '</div>', unsafe_allow_html=True) # Lengkapi logika di sini

    elif page == "Analisis Historis":
        st.markdown('<div class="card">'
                    '<p class="card-title">Grafik Tren Sisa Freeboard per Settling Pond</p>'
                    '</div>', unsafe_allow_html=True) # Lengkapi logika di sini
        
    elif page == "Proyeksi & Media":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">'
                        '<p class="card-title">Proyeksi Iklim Jangka Panjang</p>'
                        '</div>', unsafe_allow_html=True) # Lengkapi logika di sini
        with col2:
            st.markdown('<div class="card">'
                        '<p class="card-title">Simulasi Luapan Void Paringin</p>'
                        '</div>', unsafe_allow_html=True) # Lengkapi logika di sini
else:
    st.error("Gagal memuat data. Silakan periksa file Excel dan konfigurasi.")
