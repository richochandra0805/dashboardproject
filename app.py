import pandas as pd
import plotly.express as px
import streamlit as st
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

# --- FUNGSI UNTUK MEMBACA DATA DARI EXCEL ---
@st.cache_data
def load_data(filepath):
    """
    Memuat semua sheet yang diperlukan dari file Excel.
    Fungsi ini dibuat lebih andal untuk mencegah error saat deploy.
    """
    try:
        # Menggunakan logika dari skrip Anda untuk data utama
        df_rangkum = pd.read_excel(filepath, sheet_name="Rangkum", header=1, usecols="B:S", engine='openpyxl')
        df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])
        
        # Membaca sheet DASHBOARD secara terpisah untuk EWS
        df_dashboard = pd.read_excel(filepath, sheet_name="DASHBOARD", header=3, usecols="B:C")
        
        return df_dashboard, df_rangkum
    except Exception as e:
        st.error(f"Gagal memuat file Excel '{filepath}'. Pastikan file ada dan nama sheet (Rangkum, DASHBOARD) sudah benar. Error: {e}")
        return None, None

# --- EKSEKUSI UTAMA ---
load_css("style.css")
# Menggunakan variabel 'df' seperti di skrip asli Anda untuk data utama
df_dashboard, df = load_data("Daily_Water_Balance.xlsx")

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.image("https://www.adaro.com/adaro-content/themes/adaro/assets/images/logo_adaro_energy.png", width=180)
    st.image("assets/logo_itb.png", width=90)
    st.header("Adaro-ITB Partnership")
    st.markdown("---")
    
    page = st.radio(
        "Pilih Halaman Navigasi:",
        ("Laporan Harian", "Laporan Historis", "Cuaca & Proyeksi Iklim", "Simulasi & Media")
    )
    st.markdown("---")
    st.info(f"© {datetime.now().year} Adaro Indonesia")

# --- KONTEN UTAMA ---
st.title(f"📊 {page}")

# Pemeriksaan data setelah dimuat untuk mencegah error
if df is not None and df_dashboard is not None:
    if page == "Laporan Harian":
        # --- EWS (Poin 1 & 5) ---
        latest_status = df_dashboard.iloc[0]['STATUS']
        latest_reason = df_dashboard.iloc[0]['Keterangan']
        st.markdown(f"""
            <div class="card" style="background-color: {'#1cc88a' if str(latest_status).lower() == 'aman' else '#f6c23e' if str(latest_status).lower() == 'waspada' else '#e74a3b'}; color: white; text-align: center;">
                <h2 style='margin:0; font-size: 2.5rem;'>EWS: {str(latest_status).upper()}</h2>
                <p style='margin:0; font-size: 1.1rem;'>{str(latest_reason)}</p>
            </div>
        """, unsafe_allow_html=True)

        # --- Filter Tanggal (dari skrip asli Anda) ---
        ddate = st.date_input("Silahkan pilih tanggal yang ingin diamati:", value=df['Tanggal'].max())
        ddate = pd.to_datetime(ddate)
        df_daily = df[df['Tanggal'] == ddate]

        if not df_daily.empty:
            # --- GRAFIK HARIAN DALAM KARTU ---
            col_chart1, col_chart2 = st.columns([2, 3])
            with col_chart1:
                st.markdown('<div class="card"><p class="card-title">Proporsi Status SP</p></div>', unsafe_allow_html=True)
                # Menggunakan logika dari skrip asli Anda
                status_counts = df_daily['Kriteria'].value_counts().to_frame(name='Jumlah')
                pie_chart = px.pie(status_counts, title=f"Status SP {ddate.strftime('%d-%m-%Y')}", values='Jumlah', names=status_counts.index, hole=.4,
                                   color=status_counts.index, color_discrete_map={'Low': '#28a745', 'Medium': '#F9A825', 'High': '#dc3545'})
                st.plotly_chart(pie_chart, use_container_width=True)
            with col_chart2:
                st.markdown('<div class="card"><p class="card-title">Curah Hujan Maksimal per SP</p></div>', unsafe_allow_html=True)
                daily_bar = px.bar(df_daily, x='Max Rainfall to SP (mm)', y='Settling Pond', orientation='h', title='Max Rainfall to SP')
                st.plotly_chart(daily_bar, use_container_width=True)
            
            # --- DAFTAR SP BERDASARKAN STATUS (dari skrip asli Anda) ---
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
            st.warning(f"Tidak ada data untuk tanggal {ddate.strftime('%d-%m-%Y')}.")

    elif page == "Laporan Historis":
        st.markdown('<div class="card"><p class="card-title">Tren Historis Sisa Freeboard</p></div>', unsafe_allow_html=True)
        sisa_fig = px.line(df, x='Tanggal', y='Sisa Freeboard (m)', color='Settling Pond', title="Sisa Freeboard", line_shape='spline')
        st.plotly_chart(sisa_fig, use_container_width=True)

        st.markdown('<div class="card"><p class="card-title">Tren Historis Debit Keluar Aktual</p></div>', unsafe_allow_html=True)
        debit_fig = px.line(df, x='Tanggal', y='Debit Keluar Actual (m3/s)', color='Settling Pond', title="Debit Keluar", line_shape='spline')
        st.plotly_chart(debit_fig, use_container_width=True)

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
    st.error("Gagal memuat data. Pastikan file Daily_Water_Balance.xlsx ada di folder yang sama dan tidak rusak.")
