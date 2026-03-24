import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM | OTOMATİK", layout="wide")
st.title("🏇 BEYGİR ADAM v80.0")

if os.path.exists("veriler.json"):
    with open("veriler.json", "r", encoding="utf-8") as f:
        try:
            races_list = json.load(f)
            
            # Şehirleri ayıkla
            sehirler = sorted(list(set([r['raceCityName'] for r in races_list if 'raceCityName' in r])))
            secilen = st.sidebar.selectbox("📍 Şehir Seçin", sehirler)
            
            for race in races_list:
                if race.get('raceCityName') == secilen:
                    with st.expander(f"🏁 {race['raceNumber']}. Koşu ({race['raceTime']}) - {race.get('distance')}m {race.get('trackTypeDescription')}"):
                        entries = race.get('raceEntries', [])
                        if entries:
                            df = pd.DataFrame(entries)
                            # Önemli sütunları filtrele
                            df_view = df[['programNumber', 'horseName', 'jockeyName', 'weight', 'handicapScore']]
                            df_view.columns = ['No', 'At Adı', 'Jokey', 'Kilo', 'HP']
                            st.table(df_view.sort_values(by='HP', ascending=False))
        except:
            st.error("Veri okunurken bir hata oluştu.")
else:
    st.info("⌛ Veriler GitHub Actions tarafından çekiliyor, lütfen bekleyin...")
