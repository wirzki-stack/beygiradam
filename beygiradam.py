import streamlit as st
import pandas as pd
import json
import os

# Sayfa donmasını engellemek için en temel ayar
st.set_page_config(page_title="BEYGİR ADAM | V45", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM v45.0</h1>", unsafe_allow_html=True)
st.divider()

# DOSYA KONTROLÜ
file_path = "veriler.json"

if not os.path.exists(file_path):
    st.error("🚨 KRİTİK HATA: veriler.json dosyası henüz oluşturulmamış!")
    st.info("Bu beyaz ekranın geçmesi için GitHub'da robotu (Actions) bir kez çalıştırmanız şart.")
    st.markdown("""
    **Nasıl Düzeltilir?**
    1. GitHub sayfana git.
    2. **Actions** sekmesine tıkla.
    3. **TJK Data Scraper** -> **Run workflow** de.
    4. Yeşil tik olunca burayı yenile.
    """)
    st.stop() # Uygulamayı burada dondurarak beyaz ekranı kırıyoruz

# VERİ YÜKLEME
try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data:
        sehirler = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
        secilen_sehir = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)
        
        if st.sidebar.button("📊 ANALİZLERİ GÖSTER"):
            races = [r for r in data if r.get('raceCityName') == secilen_sehir]
            for race in races:
                st.subheader(f"🏁 {secilen_sehir} - {race.get('raceNumber')}. KOŞU")
                entries = race.get('raceEntries', [])
                if entries:
                    df = pd.DataFrame([{"At": e['horseName'], "Jokey": e['jockeyName'], "HP": e['handicapScore'] or 0} for e in entries])
                    df["Skor"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                    st.table(df.sort_values(by="HP", ascending=False))
                st.divider()
    else:
        st.warning("⚠️ Veri dosyası boş. Robot veriyi çekememiş.")

except Exception as e:
    st.error(f"❌ Sistem Hatası: {e}")
