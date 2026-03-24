import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM v60", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM | YENİ NESİL</h1>", unsafe_allow_html=True)

if not os.path.exists("veriler.json"):
    st.info("⌛ Veriler hazırlanıyor... Lütfen Actions sekmesinden robotu çalıştırın.")
    st.stop()

try:
    with open("veriler.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if data and len(data) > 0:
        sehirler = sorted(list(set([r['raceCityName'] for r in data])))
        secilen = st.sidebar.selectbox("📍 Şehir Seçin", sehirler)
        
        races = [r for r in data if r['raceCityName'] == secilen]
        for race in races:
            with st.expander(f"🏁 {race['raceNumber']}. Koşu - Saat: {race['raceTime']}", expanded=True):
                df = pd.DataFrame(race['raceEntries'])
                st.table(df)
    else:
        st.warning("⚠️ Bülten şu an boş görünüyor.")

except Exception as e:
    st.error(f"❌ Görüntüleme Hatası: {e}")
