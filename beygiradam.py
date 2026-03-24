import streamlit as st
import pandas as pd
import re

# Dış bağımlılığı (Tesseract) kaldırıp en sade hale getirdik
st.set_page_config(page_title="BEYGİR ADAM AI v2500", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏇 BEYGİR ADAM | AKILLI GÖRSEL ANALİZ</h1>", unsafe_allow_html=True)

st.sidebar.header("📸 Analiz Yöntemi")
st.sidebar.info("TJK veya Fanatik'ten aldığınız bültenin metnini kopyalayıp buraya yapıştırın. Görsel okuma hatalarını bu yöntemle %100 aşarız.")

# Görsel okuma yerine en garanti yöntem: Metin Alanı
# (Çünkü sunucularda OCR motoru çalıştırmak çok zordur)
raw_text = st.sidebar.text_area("Bülten Metnini Buraya Yapıştırın:", height=300)
analiz_buton = st.sidebar.button("🚀 Analizi Başlat")

if raw_text and analiz_buton:
    with st.spinner('Yapay Zeka verileri işliyor...'):
        # Koşuları Böl
        kosu_bloklari = re.split(r"(\d+)\.\s*(?:KOŞU|Kosu)", raw_text, flags=re.IGNORECASE)
        
        if len(kosu_bloklari) > 1:
            for i in range(1, len(kosu_bloklari), 2):
                k_no = kosu_bloklari[i]
                icerik = kosu_bloklari[i+1]
                
                # At No - İsim - HP Yakalama
                pattern = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ\s]{3,25}).*?(\d{2,3})", icerik)
                
                if pattern:
                    df = pd.DataFrame(pattern, columns=['No', 'At İsmi', 'HP'])
                    df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                    df = df[(df['HP'] >= 20) & (df['HP'] <= 115)].sort_values(by='HP', ascending=False).drop_duplicates('At İsmi')

                    with st.expander(f"🏁 {k_no}. AYAK ANALİZİ", expanded=True):
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.table(df[['No', 'At İsmi', 'HP']])
                        with c2:
                            st.metric("🏆 FAVORİ", df.iloc[0]['At İsmi'])
                            if len(df) > 1:
