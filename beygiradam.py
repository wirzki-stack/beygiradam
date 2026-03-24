import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM | FINAL", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM v53.0</h1>", unsafe_allow_html=True)

# 1. DOSYA KONTROLÜ
if not os.path.exists("veriler.json"):
    st.error("🚨 DOSYA HENÜZ OLUŞMADI!")
    st.info("GitHub Actions sekmesinden robotu çalıştırıp YEŞİL TİK olmasını bekleyin.")
    st.stop()

# 2. VERİ YÜKLEME
try:
    with open("veriler.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data and isinstance(data, list):
        sehirler = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
        secilen = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)
        
        if secilen:
            races = [r for r in data if r.get('raceCityName') == secilen]
            for race in races:
                with st.expander(f"🏁 {secilen} - {race.get('raceNumber')}. KOŞU", expanded=True):
                    entries = race.get('raceEntries', [])
                    df = pd.DataFrame([{"At": e['horseName'], "Jokey": e['jockeyName'], "HP": e['handicapScore'] or 0} for e in entries])
                    df["Skor"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                    st.table(df.sort_values(by="HP", ascending=False))
    else:
        st.warning("⚠️ Veri dosyası boş veya hatalı.")
except Exception as e:
    st.error(f"❌ Dosya Okuma Hatası: {e}")
