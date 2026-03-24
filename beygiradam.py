import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM v60", layout="wide")
st.title("🏇 BEYGİR ADAM - CANLI BÜLTEN")

if not os.path.exists("veriler.json"):
    st.warning("⚠️ Veri dosyası bekleniyor... Lütfen GitHub Actions'ı çalıştırın.")
    st.stop()

try:
    with open("veriler.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if data:
        cities = list(set([r['raceCityName'] for r in data]))
        selected_city = st.sidebar.selectbox("📍 Şehir Seç", cities)
        
        races = [r for r in data if r['raceCityName'] == selected_city]
        for race in races:
            with st.expander(f"🏁 {race['raceNumber']}. Koşu - {race['raceTime']}", expanded=True):
                df = pd.DataFrame(race['raceEntries'])
                st.table(df)
    else:
        st.error("Bülten verisi şu an için işlenemedi.")
except Exception as e:
    st.error(f"Sistem Hatası: {e}")
