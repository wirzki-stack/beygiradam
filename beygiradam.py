import streamlit as st
import pandas as pd
import json
import os

# 1. AYARLAR - Sayfa donmasın diye en başa
st.set_page_config(page_title="BEYGİR ADAM | V44", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM v44.0</h1>", unsafe_allow_html=True)
st.divider()

# 2. DOSYA YOLU KONTROLÜ
file_path = "veriler.json"

if not os.path.exists(file_path):
    st.error("🚨 DOSYA BULUNAMADI: veriler.json henüz oluşturulmamış.")
    st.info("GitHub -> Actions -> Run Workflow yaparak robotu çalıştırın.")
    st.stop() # Beyaz ekranı burada kırıyoruz

# 3. VERİ YÜKLEME (HATA YEMEZ MOD)
@st.cache_data(ttl=600) # Veriyi hafızaya al ki sürekli okuyup donmasın
def veriyi_oku():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return str(e)

data = veriyi_oku()

if isinstance(data, str):
    st.error(f"❌ Dosya okuma hatası: {data}")
    st.stop()

# 4. GÖRÜNTÜLEME
if data:
    sehirler = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
    
    if sehirler:
        secilen_sehir = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)
        st.sidebar.success(f"✅ {len(sehirler)} Şehir Bulundu")
        
        races = [r for r in data if r.get('raceCityName') == secilen_sehir]
        for race in races:
            with st.expander(f"🏁 {secilen_sehir} - {race.get('raceNumber')}. KOŞU", expanded=True):
                entries = race.get('raceEntries', [])
                if entries:
                    df_list = []
                    for e in entries:
                        hp = e.get('handicapScore', 0) or 0
                        df_list.append({
                            "At": e.get('horseName'),
                            "Jokey": e.get('jockeyName'),
                            "HP": hp,
                            "B.Adam Skor": f"%{min(int(hp*0.7+15), 99)}" if hp > 0 else "%--"
                        })
                    st.table(pd.DataFrame(df_list).sort_values(by="HP", ascending=False))
    else:
        st.warning("Dosya boş veya şehir verisi içermiyor.")
else:
    st.info("Veriler yükleniyor...")
