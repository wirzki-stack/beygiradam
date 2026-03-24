import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM | FINAL", page_icon="🏇", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏆 BEYGİR ADAM v41.2</h1>", unsafe_allow_html=True)

# Dosya kontrolü
if not os.path.exists("veriler.json"):
    st.warning("🔄 Veri deposu hazırlanıyor... Lütfen GitHub Actions'ı manuel tetikleyin ve 1 dakika bekleyin.")
    st.info("GitHub -> Actions -> TJK Data Scraper -> Run Workflow yolunu izleyin.")
else:
    try:
        with open("veriler.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        if data:
            sehirler = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
            secilen = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)

            if st.sidebar.button("📊 ANALİZ ET"):
                races = [r for r in data if r.get('raceCityName') == secilen]
                for race in races:
                    st.subheader(f"🏁 {secilen} - {race.get('raceNumber')}. KOŞU")
                    entries = race.get('raceEntries', [])
                    if entries:
                        df = pd.DataFrame([{"At": e['horseName'], "Jokey": e['jockeyName'], "HP": e['handicapScore'] or 0} for e in entries])
                        df["Skor"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                        st.dataframe(df.sort_values(by="HP", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.error("⚠️ Veri dosyası boş. Robot veriyi çekememiş olabilir.")
    except Exception as e:
        st.error(f"❌ Dosya okuma hatası: {e}")
