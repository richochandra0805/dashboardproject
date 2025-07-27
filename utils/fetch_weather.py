# Simpan di utils/fetch_weather.py
'''
import pandas as pd
from datetime import datetime, timedelta

def fetch_latest_rain():
    # Simulasi data sementara
    now = datetime.now()
    times = [now - timedelta(hours=i) for i in range(24)][::-1]
    rainfall = [round(abs(5 * np.sin(i.timestamp() / 30000)), 1) for i in times]  # Simulasi sinus
    df = pd.DataFrame({"Time": times, "Rainfall (mm)": rainfall})
    return df
'''
