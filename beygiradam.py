import streamlit as st
import pandas as pd
import json
import os

# Sayfa donmasını engellemek için temel ayarlar
st.set_page_config(page_title="BEYGİR ADAM | V48", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM v48.0</h1>", unsafe_allow_html=True)

file_path = "veriler.json"

# --- DOSYA KONTROLÜ (BEYAZ EKRAN KATİLİ) ---
if not os.path.exists(file_path):
    st.error("🚨 DOSYA BULUNAMADI: veriler.json dosyası henüz GitHub reponda oluşmamış.")
    st.info("Bunun sebebi GitHub Actions'ın (robotun) veriyi kaydedememiş olmasıdır.")
    st.markdown("""
    **Çözüm İçin Şuraya Bak:**
    1. GitHub reponun ana sayfasına git, `veriler.json` dosyası orada var mı?
    2. Yoksa, **Actions** sekmesine git ve son çalışan robotun yanında **Kırmızı Çarpı** var mı kontrol et.
    """)
    st.stop() # Uygulamayı burada durdurarak beyaz ekranı kırar.

# --- VERİ YÜKLEME ---
try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data:
        sehirler = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
        secilen = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)
        
        if secilen:
            races = [r for r in data if r.get('raceCityName') == secilen]
            for race in races:
                with st.expander(f"🏁 {secilen} - {race.get('raceNumber')}. KOŞU", expanded=True):
                    entries = race.get('raceEntries', [])
                    if entries:
                        df = pd.DataFrame([{"At": e['horseName'], "Jokey": e['jockeyName'], "HP": e['handicapScore'] or 0} for e in entries])
                        df["Skor"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                        st.table(df.sort_values(by="HP", ascending=False))
    else:
        st.warning("⚠️ Dosya içi boş.")
except Exception as e:
    st.error(f"❌ HATA: {e}")
