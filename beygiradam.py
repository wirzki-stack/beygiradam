import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="BEYGİR ADAM v70", layout="wide")
st.title("🏇 BEYGİR ADAM | MANUEL VERİ PANELİ")

# Yan menüde veri yapıştırma alanı
st.sidebar.header("📥 Veri Girişi")
manuel_veri = st.sidebar.text_area("Bülten JSON verisini buraya yapıştırın:", height=200)

if manuel_veri:
    try:
        data = json.loads(manuel_veri)
        st.success("✅ Veri başarıyla yüklendi!")
    except:
        st.error("❌ Geçersiz JSON formatı.")
        data = []
else:
    # Eğer manuel giriş yoksa dosyadan oku
    try:
        with open("veriler.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

if data:
    sehirler = list(set([r['raceCityName'] for r in data]))
    secilen = st.selectbox("📍 Şehir Seçin", sehirler)
    
    races = [r for r in data if r['raceCityName'] == secilen]
    for race in races:
        with st.expander(f"🏁 {race['raceNumber']}. Koşu - {race['raceTime']}"):
            st.table(pd.DataFrame(race['raceEntries']))
else:
    st.info("Bülten görmek için lütfen veri yükleyin.")
