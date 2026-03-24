import streamlit as st
import pandas as pd
import json
import os

# Sayfa donmasını engellemek için en temel ayarlar
st.set_page_config(page_title="BEYGİR ADAM | V46", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM v46.0</h1>", unsafe_allow_html=True)
st.divider()

file_path = "veriler.json"

# DOSYA VAR MI KONTROLÜ
if not os.path.exists(file_path):
    st.error("🚨 DOSYA BULUNAMADI: veriler.json henüz oluşturulmamış.")
    st.stop()

# VERİ YÜKLEME FONKSİYONU
@st.cache_data(ttl=300)
def load_data():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                return "BOŞ"
            return json.loads(content)
    except Exception as e:
        return f"HATA: {str(e)}"

data = load_data()

# DURUM KONTROLÜ
if data == "BOŞ":
    st.warning("⚠️ Dosya bulundu ama içi boş. Robot (Action) veriyi yazamamış.")
    st.stop()
elif isinstance(data, str) and "HATA" in data:
    st.error(data)
    st.stop()

# GÖRÜNTÜLEME
if data:
    sehirler = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
    secilen = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)
    
    races = [r for r in data if r.get('raceCityName') == secilen]
    for race in races:
        with st.expander(f"🏁 {secilen} - {race.get('raceNumber')}. KOŞU", expanded=True):
            entries = race.get('raceEntries', [])
            if entries:
                df = pd.DataFrame([{"At": e['horseName'], "Jokey": e['jockeyName'], "HP": e['handicapScore'] or 0} for e in entries])
                df["Skor"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                st.table(df.sort_values(by="HP", ascending=False))
