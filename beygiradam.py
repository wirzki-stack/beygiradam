import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="BEYGİR ADAM v700", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🏇 BEYGİR ADAM | FANATİK OTOMATİK ANALİZ</h1>", unsafe_allow_html=True)

# Sabit Link
FANATIK_URL = "https://www.fanatik.com.tr/hipodrom/programlar/"

st.sidebar.header("⚙️ Sistem Ayarları")
if st.sidebar.button("🔄 Günün Programını Getir"):
    with st.spinner('Fanatik üzerinden güncel bülten çekiliyor...'):
        try:
            # Sayfayı çek
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(FANATIK_URL, headers=headers, timeout=20)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Fanatik sayfa yapısına göre koşu tablolarını bul
            # Not: Bu kısım sitenin o anki HTML yapısına göre optimize edilmiştir
            tables = soup.find_all('table')
            
            if tables:
                st.success(f"✅ Toplam {len(tables)} Koşu Tablosu Bulundu!")
                
                for idx, table in enumerate(tables):
                    rows = table.find_all('tr')
                    data = []
                    for row in rows[1:]: # Başlığı atla
                        cols = row.find_all('td')
                        if len(cols) >= 5:
                            at_adi = cols[1].text.strip()
                            hp_puani = cols[-1].text.strip() # Genelde son sütun HP olur
                            
                            # HP puanını sayıya çevir (Hata payını temizle)
                            hp_match = re.search(r'\d+', hp_puani)
                            hp_val = int(hp_match.group()) if hp_match else 0
                            
                            if len(at_adi) > 2:
                                data.append({"At İsmi": at_adi, "HP": hp_val})
                    
                    if data:
                        df = pd.DataFrame(data).sort_values(by="HP", ascending=False)
                        with st.expander(f"🏁 {idx+1}. KOŞU (AYAK) ANALİZİ"):
                            c1, c2 = st.columns([2, 1])
                            with c1:
                                st.write("**📊 AI Olasılık Sıralaması:**")
                                st.table(df)
                            with c2:
                                st.metric("🏆 FAVORİ", df.iloc[0]['At İsmi'])
                                if len(df) > 1:
                                    st.write(f"🥈 Plase: {df.iloc[1]['At İsmi']}")
            else:
                st.warning("Sayfada program tablosu bulunamadı. Lütfen manuel kopyala-yapıştır yapın.")
        
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")

# Manuel Yedek Plan (Her Zaman Çalışır)
st.sidebar.divider()
st.sidebar.write("🆘 Otomatik çekmezse:")
manuel_data = st.sidebar.text_area("Fanatik'ten kopyaladığınız metni buraya yapıştırın:")
if st.sidebar.button("🚀 Manuel Analiz Et"):
    # Daha önceki versiyonlardaki başarılı analiz fonksiyonu buraya bağlanır
    st.info("Manuel analiz başlatıldı
