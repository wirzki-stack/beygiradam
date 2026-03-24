import streamlit as st
import pandas as pd
import json
import os

# 1. AYARLAR - Donmayı önlemek için en başa
st.set_page_config(page_title="BEYGİR ADAM | V43", layout="wide")

# 2. GÖRSEL BAŞLIK
st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM v43.0</h1>", unsafe_allow_html=True)
st.divider()

# 3. DOSYA KONTROLÜ
file_path = "veriler.json"

if not os.path.exists(file_path):
    st.error("🚨 KRİTİK HATA: veriler.json DOSYASI BULUNAMADI!")
    st.info("Lütfen GitHub Actions sekmesine gidin, robotu çalıştırın ve YEŞİL TİK olana kadar bekleyin.")
    # Beyaz ekranı kırmak için burada her şeyi durduruyoruz
    st.stop()

# 4. VERİ OKUMA
try:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
        if not raw_content:
            st.warning("⚠️ Dosya var ama içi bomboş. Robot henüz veri yazamamış.")
            st.stop()
        data = json.loads(raw_content)

    # Şehir Listesi Oluşturma
    sehirler = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
    
    if sehirler:
        secilen_sehir = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)
        st.sidebar.success(f"✅ {len(sehirler)} Şehir Aktif")
        
        # Seçilen Şehrin Koşularını Filtrele
        races = [r for r in data if r.get('raceCityName') == secilen_sehir]
        
        for race in races:
            with st.container():
                st.subheader(f"🏁 {secilen_sehir} - {race.get('raceNumber')}. KOŞU")
                entries = race.get('raceEntries', [])
                if entries:
                    df_data = []
                    for e in entries:
                        hp = e.get('handicapScore', 0) or 0
                        df_data.append({
                            "At": e.get('horseName'),
                            "Jokey": e.get('jockeyName'),
                            "HP": hp,
                            "B.Adam Skor": f"%{min(int(hp*0.7+15), 99)}" if hp > 0 else "%--"
                        })
                    
                    df = pd.DataFrame(df_data).sort_values(by="HP", ascending=False)
                    st.table(df) # DataFrame yerine en hafif gösterim olan table
                st.divider()
    else:
        st.error("⚠️ Dosya yüklendi ama içinde geçerli bir yarış bulunamadı.")

except Exception as e:
    st.error(f"❌ SİSTEM HATASI: {str(e)}")
    st.info("İpucu: veriler.json dosyasının formatı bozulmuş olabilir.")
