import streamlit as st
import pandas as pd
import json
import os

# Sayfa Ayarları
st.set_page_config(page_title="BEYGİR ADAM | CANLI", layout="wide")

# Başlık
st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM v54.0</h1>", unsafe_allow_html=True)

# 1. DOSYA KONTROLÜ
file_path = "veriler.json"
if not os.path.exists(file_path):
    st.error("🚨 Veri dosyası (veriler.json) henüz GitHub reponuzda oluşmamış.")
    st.info("Lütfen GitHub Actions sekmesinden robotu (TJK Data Scraper) tekrar çalıştırın.")
    st.stop()

# 2. VERİ YÜKLEME VE İŞLEME
try:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # TJK API verisi bazen bir sözlük içinde 'data' veya 'QueryResult' olarak gelir
    races_list = []
    if isinstance(raw_data, list):
        races_list = raw_data
    elif isinstance(raw_data, dict):
        # Olası tüm TJK anahtarlarını kontrol et
        races_list = raw_data.get('data', raw_data.get('QueryResult', raw_data.get('races', [])))

    if races_list and len(races_list) > 0:
        # Şehirleri bul (Benzersiz ve sıralı)
        sehirler = sorted(list(set([r.get('raceCityName') for r in races_list if r.get('raceCityName')])))
        
        # Yan menü (Sidebar)
        st.sidebar.header("⚙️ Menü")
        secilen_sehir = st.sidebar.selectbox("📍 Şehir Seçin:", sehirler)
        
        if secilen_sehir:
            # Seçilen şehre ait koşuları filtrele
            sehir_races = [r for r in races_list if r.get('raceCityName') == secilen_sehir]
            
            for race in sehir_races:
                kodu = race.get('raceNumber', '?')
                saat = race.get('raceTime', '--:--')
                mesafe = race.get('distance', '')
                pist = race.get('trackTypeDescription', '')
                
                with st.expander(f"🏁 {kodu}. KOŞU | Saat: {saat} | {mesafe}m {pist}", expanded=True):
                    entries = race.get('raceEntries', [])
                    if entries:
                        table_data = []
                        for e in entries:
                            hp = e.get('handicapScore') or 0
                            # Basit bir güç puanı algoritması
                            try:
                                guc = int(float(hp) * 0.75 + 12)
                                guc_str = f"%{min(guc, 99)}"
                            except:
                                guc_str = "%--"

                            table_data.append({
                                "No": e.get('programNumber', '-'),
                                "At Adı": e.get('horseName', 'Bilinmiyor'),
                                "Jokey": e.get('jockeyName', '-'),
                                "Kilo": e.get('weight', '-'),
                                "HP": hp,
                                "BEYGİR SKOR": guc_str
                            })
                        
                        df = pd.DataFrame(table_data)
                        # Tabloyu göster (HP'ye göre yüksekten düşüğe)
                        st.table(df.sort_values(by="HP", ascending=False))
                    else:
                        st.info("Bu koşu için henüz at listesi girilmemiş.")
    else:
        st.warning("⚠️ Bugün için henüz aktif bir yarış programı verisi bulunamadı.")
        st.info("TJK verileri bazen sisteme geç düşebilir. GitHub Actions'ın yeşil tik olduğundan emin olun.")

except Exception as e:
    st.error(f"❌ Veri işleme sırasında bir hata oluştu: {e}")
    st.info("Dosya içeriği okunurken bir problem yaşandı. Lütfen veriler.json dosyasını kontrol edin.")

# Alt Bilgi
st.markdown("---")
st.caption(f"📅 Son Güncelleme: {raw_data.get('lastUpdate', 'Bilinmiyor') if isinstance(raw_data, dict) else 'Canlı'}")
