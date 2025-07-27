import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime

# Inisialisasi Aplikasi Dash
app = dash.Dash(__name__, title="Adaro Water Command Center", suppress_callback_exceptions=True)
server = app.server

# --- Fungsi untuk Membaca Data ---
@app.callback(
    Output('data-store', 'data'),
    Input('interval-component', 'n_intervals')
)
def load_data_periodically(n):
    """Memuat ulang data dari Excel secara berkala untuk menjaga data tetap segar."""
    try:
        df_dashboard = pd.read_excel("Daily_Water_Balance.xlsx", sheet_name="DASHBOARD", header=3, usecols="B:C")
        df_rangkum = pd.read_excel("Daily_Water_Balance.xlsx", sheet_name="Rangkum", header=1, usecols="B:S")
        df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])
        return {'df_dashboard': df_dashboard.to_dict('records'), 'df_rangkum': df_rangkum.to_dict('records')}
    except FileNotFoundError:
        return {'df_dashboard': [], 'df_rangkum': []}

# --- Layout Aplikasi Utama ---
# Layout ini hanya berisi kerangka dan komponen input
app.layout = html.Div([
    dcc.Store(id='data-store'),
    dcc.Interval(id='interval-component', interval=10*60*1000, n_intervals=0),
    
    # --- Sidebar (Statis) ---
    html.Div(className="sidebar", children=[
        html.Div(className="sidebar-header", children=[
            html.Img(src="https://www.adaro.com/adaro-content/themes/adaro/assets/images/logo_adaro_energy.png"),
            html.Img(src="https://upload.wikimedia.org/wikipedia/id/thumb/8/8c/Logo_Institut_Teknologi_Bandung.png/220px-Logo_Institut_Teknologi_Bandung.png"),
            html.H5("Adaro-ITB Partnership", className="sidebar-title")
        ]),
        html.Hr(),
        html.P("Pilih Tanggal Laporan:", style={'font-weight': '600'}),
        dcc.DatePickerSingle(
            id='date-picker',
            display_format='DD MMMM YYYY',
            style={'width': '100%'}
        )
    ]),

    # --- Konten Utama (Awalnya kosong, diisi oleh callback) ---
    html.Div(id='main-content', className="main-content")
])

# --- Callback untuk mengisi dan memperbarui seluruh konten utama ---
@app.callback(
    Output('main-content', 'children'),
    [Input('date-picker', 'date'),
     Input('data-store', 'data')]
)
def update_main_content(selected_date, stored_data):
    # Jika data belum dimuat, tampilkan pesan
    if not stored_data or not stored_data.get('df_rangkum'):
        return html.Div("Memuat data atau file Excel tidak ditemukan...", className="card")

    # Konversi data dari store kembali ke DataFrame
    df_dashboard = pd.DataFrame(stored_data['df_dashboard'])
    df_rangkum = pd.DataFrame(stored_data['df_rangkum'])
    df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])

    # Atur tanggal default jika belum dipilih
    if selected_date is None:
        selected_date = df_rangkum['Tanggal'].max()

    df_daily = df_rangkum[df_rangkum['Tanggal'] == pd.to_datetime(selected_date)].copy()

    if df_daily.empty:
        return html.Div([
            html.H1("Water Management Command Center"),
            html.Div(f"Tidak ada data untuk tanggal: {pd.to_datetime(selected_date).strftime('%d %B %Y')}", className="card")
        ])

    # Ambil data EWS, Metrik, dan buat Grafik
    status = df_dashboard.iloc[0]['STATUS']
    reason = df_dashboard.iloc[0]['Keterangan']
    summary = df_daily.iloc[0]

    # Buat semua komponen visual
    ews_card = html.Div([html.H2(f"EWS: {status.upper()}", style={'margin': 0}), html.P(reason)], className="card")
    metric1 = html.Div([html.P("Water Level (PIT)", className="metric-label"), html.H3(f"{summary['Freeboard (Elevasi Actual) (Rl)']:.2f} m", className="metric-value")], className="card")
    metric2 = html.Div([html.P("Sisa Freeboard", className="metric-label"), html.H3(f"{summary['Sisa Freeboard (m)']:.2f} m", className="metric-value")], className="card")
    metric3 = html.Div([html.P("TSS Inflow", className="metric-label"), html.H3(f"{summary['TSS Inflow (ton)']:.2f} ton", className="metric-value")], className="card")
    metric4 = html.Div([html.P("TSS Outflow", className="metric-label"), html.H3(f"{summary['TSS Outflow (ton)']:.2f} ton", className="metric-value")], className="card")
    
    pie_fig = px.pie(df_daily['Kriteria'].value_counts().reset_index(), values='count', names='Kriteria', title="Proporsi Status SP", color='Kriteria', color_discrete_map={'Low': '#28a745', 'Medium': '#F9A825', 'High': '#dc3545'})
    bar_fig = px.bar(df_daily, x='Max Rainfall to SP (mm)', y='Settling Pond', orientation='h', title='Curah Hujan Maksimal per SP')

    # Kembalikan seluruh layout konten utama
    return html.Div([
        html.H1("Water Management Command Center"),
        html.P(f"Menampilkan Laporan Untuk Tanggal: {pd.to_datetime(selected_date).strftime('%d %B %Y')}"),
        ews_card,
        html.Div([metric1, metric2, metric3, metric4], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '1rem'}),
        html.Div([
            html.Div(dcc.Graph(figure=pie_fig), className="card"),
            html.Div(dcc.Graph(figure=bar_fig), className="card")
        ], style={'display': 'grid', 'gridTemplateColumns': '3fr 7fr', 'gap': '1rem'}),
    ])

# Callback untuk mengatur tanggal awal pada DatePicker setelah data dimuat
@app.callback(
    [Output('date-picker', 'date'),
     Output('date-picker', 'min_date_allowed'),
     Output('date-picker', 'max_date_allowed'),
     Output('date-picker', 'initial_visible_month')],
    Input('data-store', 'data')
)
def set_initial_date(data):
    if not data or not data.get('df_rangkum'):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    df_rangkum = pd.DataFrame(data['df_rangkum'])
    df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])
    
    min_date = df_rangkum['Tanggal'].min().date()
    max_date = df_rangkum['Tanggal'].max().date()
    
    return max_date, min_date, max_date, max_date

if __name__ == '__main__':
    app.run_server(debug=True)
