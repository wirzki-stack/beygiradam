import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM | CANLI", page_icon="🏇", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏆 BEYGİR ADAM v41.3</h1>", unsafe_allow_html=True)

if not os.path.exists("veriler.json") or os.stat("veriler.json").st_size == 0:
    st.warning("🔄 Veri deposu boş veya henüz dolmadı. GitHub Actions'ı 'Run Workflow' yaparak tetikleyin.")
else:
    try:
        with open("veriler.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        if data and isinstance(data, list):
            # Şehir listesini temizle ve çıkar
            sehir_listesi = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
            
            if sehir_listesi:
                secilen = st.sidebar.selectbox("📍 Şehir Seçin:", sehir_listesi)
                st.sidebar.success(f"{len(sehir_listesi)} Şehir Yüklendi")

                races = [r for r in data if r.get('raceCityName') == secilen]
                for race in races:
                    st.markdown(f"### 🏁 {secilen} - {race.get('raceNumber')}. KOŞU")
                    entries = race.get('raceEntries', [])
                    if entries:
                        df = pd.DataFrame([{"At": e['horseName'], "Jokey": e['jockeyName'], "HP": e['handicapScore'] or 0} for e in entries])
                        df["Skor"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                        st.dataframe(df.sort_values(by="HP", ascending=False), use_container_width=True, hide_index=True)
            else:
                st.error("Dosya var ama içinde şehir verisi bulunamadı.")
        else:
            st.error("Veriler okunamıyor veya formatı hatalı.")
    except Exception as e:
        st.error(f"❌ HATA: {e}")
