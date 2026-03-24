import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM v90", layout="wide")
st.title("🏇 BEYGİR ADAM | GÜVENLİ MOD")

# Sol Menü: Veri Girişi
st.sidebar.header("📥 Manuel Veri Aktarımı")
manuel_json = st.sidebar.text_area("TJK'dan kopyaladığınız JSON verisini buraya yapıştırın:", height=300)

data = []

if manuel_json:
    try:
        data = json.loads(manuel_json)
        # Gelen veri liste değilse 'data' anahtarına bak
        if isinstance(data, dict):
            data = data.get('data', [])
        st.sidebar.success("✅ Veri başarıyla yüklendi!")
    except:
        st.sidebar.error("❌ Geçersiz JSON formatı.")
else:
    # Eğer manuel giriş yoksa veriler.json'dan okumayı dene
    if os.path.exists("veriler.json"):
        with open("veriler.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []

# Görüntüleme Alanı
if data:
    try:
        # Şehirleri bul
        cities = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
        selected_city = st.selectbox("📍 Şehir Seçin", cities)
        
        city_races = [r for r in data if r.get('raceCityName') == selected_city]
        for r in city_races:
            with st.expander(f"🏁 {r.get('raceNumber')}. Koşu - {r.get('raceTime')}"):
                entries = r.get('raceEntries', [])
                if entries:
                    df = pd.DataFrame(entries)
                    cols = {'programNumber': 'No', 'horseName': 'At Adı', 'jockeyName': 'Jokey', 'weight': 'Kilo', 'handicapScore': 'HP'}
                    df_view = df.rename(columns=cols)[list(cols.values())]
                    st.table(df_view.sort_values(by='HP', ascending=False))
    except Exception as e:
        st.error(f"Görüntüleme hatası: {e}")
else:
    st.info("👋 Hoş geldiniz! TJK'dan veriyi çekemediğim için lütfen sol menüdeki alana bülten verisini yapıştırın.")
