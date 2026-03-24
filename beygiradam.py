import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re

st.set_page_config(page_title="BEYGİR ADAM v4000", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FFD700;'>📸 BEYGİR ADAM | FOTOĞRAF ANALİZÖRÜ</h1>", unsafe_allow_html=True)

# Görsel Yükleme Alanı
uploaded_file = st.file_uploader("Bülten Ekran Görüntüsünü Yükleyin", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # Görseli göster
    img = Image.open(uploaded_file)
    st.image(img, caption="Yüklenen Bülten", width=300)
    
    if st.button("🚀 Fotoğrafı Tara ve Analiz Et"):
        with st.spinner('AI fotoğraftaki yazıları okuyor...'):
            try:
                # OCR ile metni oku
                text = pytesseract.image_to_string(img, lang='tur')
                
                # Koşuları Böl
                kosular = re.split(r"(\d+)\.\s*(?:KOŞU|Kosu)", text, flags=re.IGNORECASE)
                
                if len(kosular) > 1:
                    for i in range(1, len(kosular), 2):
                        k_no = kosular[i]
                        icerik = kosular[i+1]
                        
                        # At No - İsim - Puan ayıkla
                        pattern = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ\s]{3,25}).*?(\d{2,3})", icerik)
                        
                        if pattern:
                            df = pd.DataFrame(pattern, columns=['No', 'At İsmi', 'HP'])
                            df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                            df = df[(df['HP'] >= 10)].sort_values(by='HP', ascending=False).drop_duplicates('At İsmi')

                            with st.expander(f"🏁 {k_no}. AYAK ANALİZİ", expanded=True):
                                c1, c2 = st.columns([2, 1])
                                with c1: st.table(df[['No', 'At İsmi', 'HP']])
                                with c2: st.metric("🏆 FAVORİ", df.iloc[0]['At İsmi'])
                else:
                    st.warning("Fotoğraftaki yazılar net okunamadı. Lütfen daha yakından ve net bir çekim yükleyin.")
            
            except Exception as e:
                st.error("Sistemde 'Görüntü Okuma Modülü' eksik.")
                st.info("💡 ÇÖZÜM: GitHub'da 'packages.txt' dosyası oluşturun ve içine 'tesseract-ocr' yazın. Veya bülten metnini kopyalayıp yapıştırın.")

else:
    st.info("👋 Fotoğraf yükleme moduna geri döndük. Lütfen bülten görselini buraya bırakın.")
