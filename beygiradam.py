import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM v85", layout="wide")
st.title("🏇 BEYGİR ADAM | CANLI BÜLTEN")

if os.path.exists("veriler.json"):
    try:
        with open("veriler.json", "r", encoding="utf-8") as f:
            races = json.load(f)
        
        if races and len(races) > 0:
            # Şehir listesini temizle
            cities = sorted(list(set([r.get('raceCityName') for r in races if r.get('raceCityName')])))
            selected_city = st.sidebar.selectbox("📍 Şehir Seçin", cities)
            
            city_races = [r for r in races if r.get('raceCityName') == selected_city]
            for r in city_races:
                with st.expander(f"🏁 {r.get('raceNumber')}. Koşu - {r.get('raceTime')}"):
                    entries = r.get('raceEntries', [])
                    if entries:
                        df = pd.DataFrame(entries)
                        # Sütunları Türkçeleştir ve düzenle
                        view_cols = {
                            'programNumber': 'No',
                            'horseName': 'At Adı',
                            'jockeyName': 'Jokey',
                            'weight': 'Kilo',
                            'handicapScore': 'HP'
                        }
                        df_view = df.rename(columns=view_cols)[list(view_cols.values())]
                        st.table(df_view)
        else:
            st.warning("⚠️ TJK'dan henüz veri gelmedi. Lütfen Actions sekmesinden robotu çalıştırın.")
    except Exception as e:
        st.error(f"Veri işleme hatası: {e}")
else:
    st.info("⌛ Sistem hazırlanıyor, veriler.json bekleniyor...")
