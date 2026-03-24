import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM v95", layout="wide")
st.title("🏇 BEYGİR ADAM | GÜVENLİ MOD")

# Sol Menü: Veri Girişi
st.sidebar.header("📥 Manuel Veri Girişi")
manuel_json = st.sidebar.text_area("TJK'dan aldığınız veriyi buraya yapıştırın:", height=300)

data = []

if manuel_json:
    try:
        data = json.loads(manuel_json)
        # TJK API yapısına göre ayıkla
        if isinstance(data, dict):
            data = data.get('data', data.get('QueryResult', []))
        st.sidebar.success("✅ Veri Yüklendi!")
    except:
        st.sidebar.error("❌ Geçersiz JSON formatı.")
else:
    # Veri yoksa dosyadan oku
    if os.path.exists("veriler.json"):
        with open("veriler.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except: data = []

# Görüntüleme
if data:
    cities = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
    selected_city = st.selectbox("📍 Şehir Seçin", cities)
    
    city_races = [r for r in data if r.get('raceCityName') == selected_city]
    for r in city_races:
        with st.expander(f"🏁 {r.get('raceNumber')}. Koşu - {r.get('raceTime')}"):
            entries = r.get('raceEntries', [])
            if entries:
                df = pd.DataFrame(entries)
                cols = {'programNumber': 'No', 'horseName': 'At Adı', 'jockeyName': 'Jokey', 'weight': 'Kilo', 'handicapScore': 'HP'}
                # Mevcut sütunları kontrol et ve tabloyu bas
                present_cols = [c for c in cols.keys() if c in df.columns]
                st.table(df[present_cols].rename(columns=cols).sort_values(by='HP', ascending=False))
else:
    st.info("👋 Hoş geldiniz! TJK verisi için lütfen sol taraftaki alana bülten verisini yapıştırın.")
