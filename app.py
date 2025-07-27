import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# --- Inisialisasi Aplikasi Dash ---
app = dash.Dash(__name__)
server = app.server # Untuk keperluan hosting

# --- Fungsi untuk Membaca Data ---
def load_data(filepath):
    df_dashboard = pd.read_excel(filepath, sheet_name="DASHBOARD", header=3, usecols="B:C")
    df_rangkum = pd.read_excel(filepath, sheet_name="Rangkum", header=1, usecols="B:S")
    df_rangkum['Tanggal'] = pd.to_datetime(df_rangkum['Tanggal'])
    return df_dashboard, df_rangkum

# --- Memuat Data ---
df_dashboard, df_rangkum = load_data("Daily_Water_Balance.xlsx")
default_date = df_rangkum['Tanggal'].max()

# --- Layout Aplikasi (Struktur HTML) ---
app.layout = html.Div(className="app-container", children=[
    # --- Sidebar ---
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
            min_date_allowed=df_rangkum['Tanggal'].min(),
            max_date_allowed=df_rangkum['Tanggal'].max(),
            initial_visible_month=default_date,
            date=default_date,
            display_format='DD MMMM YYYY'
        )
    ]),

    # --- Konten Utama ---
    html.Div(className="main-content", children=[
        html.H1("Water Balance Command Center"),
        html.P(f"Menampilkan Laporan Untuk Tanggal: {default_date.strftime('%d %B %Y')}", id='selected-date-text'),
        
        # --- Card untuk Status EWS ---
        html.Div(id='ews-card', className="card"),

        # --- Grid untuk Metrik Utama ---
        html.Div(className="row", style={'display': 'flex', 'gap': '1rem'}, children=[
            html.Div(id='metric-card-1', className="col-md-3", style={'flex': '1'}),
            html.Div(id='metric-card-2', className="col-md-3", style={'flex': '1'}),
            html.Div(id='metric-card-3', className="col-md-3", style={'flex': '1'}),
            html.Div(id='metric-card-4', className="col-md-3", style={'flex': '1'}),
        ]),

        # --- Grid untuk Grafik Harian ---
        html.Div(className="row", style={'display': 'flex', 'gap': '1rem'}, children=[
            html.Div(dcc.Graph(id='pie-chart'), className="col-md-5", style={'flex': '5'}),
            html.Div(dcc.Graph(id='bar-chart'), className="col-md-7", style={'flex': '7'}),
        ]),
    ])
])

# --- INTERAKTIVITAS (CALLBACK) ---
@app.callback(
    [Output('selected-date-text', 'children'),
     Output('ews-card', 'children'),
     Output('metric-card-1', 'children'),
     Output('metric-card-2', 'children'),
     Output('metric-card-3', 'children'),
     Output('metric-card-4', 'children'),
     Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure')],
    [Input('date-picker', 'date')]
)
def update_dashboard(selected_date):
    # Filter data berdasarkan tanggal yang dipilih
    df_daily = df_rangkum[df_rangkum['Tanggal'] == pd.to_datetime(selected_date)].copy()
    
    if df_daily.empty:
        # Jika tidak ada data, kembalikan tampilan kosong/pesan error
        return (f"Tidak ada data untuk tanggal: {selected_date}", 
                html.Div("Data tidak tersedia", className="card"),
                # ... kembalikan komponen kosong lainnya ...
               )

    # 1. Update Teks Tanggal
    date_text = f"Menampilkan Laporan Untuk Tanggal: {pd.to_datetime(selected_date).strftime('%d %B %Y')}"
    
    # 2. Update EWS
    status = df_dashboard.iloc[0]['STATUS'] # Diasumsikan EWS selalu dari data terbaru
    reason = df_dashboard.iloc[0]['Keterangan']
    ews_card = html.Div([html.H2(f"EWS: {status.upper()}", style={'margin': 0}), html.P(reason)])

    # 3. Update Metrik
    summary = df_daily.iloc[0]
    metric1 = html.Div([html.P("Water Level (PIT)", className="metric-label"), html.H3(f"{summary['Freeboard (Elevasi Actual) (Rl)']:.2f} m", className="metric-value")], className="card")
    metric2 = html.Div([html.P("Sisa Freeboard", className="metric-label"), html.H3(f"{summary['Sisa Freeboard (m)']:.2f} m", className="metric-value")], className="card")
    metric3 = html.Div([html.P("TSS Inflow", className="metric-label"), html.H3(f"{summary['TSS Inflow (ton)']:.2f} ton", className="metric-value")], className="card")
    metric4 = html.Div([html.P("TSS Outflow", className="metric-label"), html.H3(f"{summary['TSS Outflow (ton)']:.2f} ton", className="metric-value")], className="card")

    # 4. Update Grafik
    pie_fig = px.pie(df_daily['Kriteria'].value_counts().reset_index(), values='count', names='Kriteria', title="Proporsi Status SP")
    bar_fig = px.bar(df_daily, x='Max Rainfall to SP (mm)', y='Settling Pond', orientation='h', title='Curah Hujan Maksimal per SP')
    
    return date_text, ews_card, metric1, metric2, metric3, metric4, pie_fig, bar_fig

# --- Menjalankan Server ---
if __name__ == '__main__':
    app.run_server(debug=True)
