import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="BEYGİR ADAM | V42", page_icon="🏇", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM v42.0</h1>", unsafe_allow_html=True)

# DOSYA KONTROL VE YÜKLEME
file_path = "veriler.json"

if not os.path.exists(file_path):
    st.error("⚠️ VERİ DOSYASI BULUNAMADI!")
    st.info("Lütfen GitHub Actions sekmesinden robotu (Scraper) çalıştırın ve yeşil tik olmasını bekleyin.")
    st.stop() # Burada dur, beyaz ekrana düşme

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not data:
        st.warning("⚠️ Dosya bulundu ama içi boş. Robot henüz veriyi yazamamış.")
    else:
        # Şehirleri Çek
        sehirler = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
        
        if sehirler:
            secilen = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)
            
            # Koşuları Listele
            races = [r for r in data if r.get('raceCityName') == secilen]
            for race in races:
                with st.expander(f"🏁 {secilen} - {race.get('raceNumber')}. KOŞU", expanded=True):
                    entries = race.get('raceEntries', [])
                    if entries:
                        df = pd.DataFrame([{"At": e['horseName'], "Jokey": e['jockeyName'], "HP": e['handicapScore'] or 0} for e in entries])
                        df = df.sort_values(by="HP", ascending=False)
                        df["Skor"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                        st.table(df) # Donmayı engellemek için daha hafif olan table kullanıyoruz
        else:
            st.error("Şehir verisi ayıklanamadı.")

except Exception as e:
    st.error(f"⚠️ Bir hata oluştu: {e}")
    st.info("Robotun veriyi doğru çektiğinden emin olun.")
