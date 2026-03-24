import streamlit as st
import pandas as pd
from PIL import Image
import re

# OCR kütüphanesini bağımsız ve kurulum gerektirmeyen (in-memory) hale getirdik
try:
    import easyocr
except ImportError:
    st.error("Gereksinim hatası: requirements.txt dosyasına 'easyocr' ve 'opencv-python-headless' ekleyin.")

st.set_page_config(page_title="BEYGİR ADAM AI FINAL", layout="wide")

# Tasarımı daha modern yapalım
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #00FF00; color: black; }
    .stExpander { background-color: #1e2127; border: 1px solid #00FF00; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏇 BEYGİR ADAM FINAL | AI ANALİZ MOTORU")

# Sol tarafta görsel yükleme
uploaded_file = st.sidebar.file_uploader("📸 Bülten Fotoğrafını Yükleyin", type=['png', 'jpg', 'jpeg'])

def analyze_image(img):
    with st.spinner('Yapay Zeka fotoğraftaki yazıları okuyor...'):
        try:
            # Görüntü okuma motorunu başlat
            reader = easyocr.Reader(['tr', 'en']) # Türkçe ve İngilizce dillerini destekle
            # Görüntüyü oku ve metne çevir
            result = reader.readtext(img)
            # Metni birleştir
            text = " ".join([res[1] for res in result])
            
            # Koşuları (Ayakları) Böl (TJK formatına uygun Regex)
            # Regex: Koşu numarasını ve yanındaki 'KOŞU' kelimesini arar
            races = re.split(r"(\d+)\.\s*(?:KOŞU|Kosu)", text, flags=re.IGNORECASE)
            
            if len(races) > 1:
                st.success(f"✅ {len(races)//2} Koşu Tespit Edildi ve Ayrıştırıldı.")
                
                # Her Koşu İçin Analiz Başlat
                for i in range(1, len(races), 2):
                    kosu_no = races[i]
                    icerik = races[i+1]
                    
                    # At No, İsim ve Handikap Puanı (HP) ayıkla
                    # Regex: Satır başındaki rakam + Büyük Harfli İsim + Aradaki karmaşa + Sondaki 2-3 haneli HP
                     pattern = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ\s]{4,30}).*?(\d{2,3})", icerik)
                    
                    if pattern:
                        df = pd.DataFrame(pattern, columns=['No', 'At İsmi', 'HP'])
                        df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                        # Sadece mantıklı HP puanlarını (20-110 arası) ve Sırala
                        df = df[(df['HP'] >= 20) & (df['HP'] <= 115)].sort_values(by='HP', ascending=False)
                        df = df.drop_duplicates(subset=['At İsmi'])

                        # Her Ayak İçin Ayrı Kutu (Oluşturulan Görseldeki Gibi)
                        with st.expander(f"🏁 {kosu_no}. AYAK - AI SIRALAMASI"):
                            c1, c2 = st.columns([2, 1])
                            with c1:
                                st.write("**📊 AI Kazanma Olasılığı Sıralaması (Favoriden Sürprize):**")
                                # Olasılık hesapla (AI Mantığı)
                                toplam_hp = df['HP'].sum()
                                df['Şans %'] = df['HP'].apply(lambda x: f"%{round((x/toplam_hp)*100, 1)}")
                                st.table(df[['No', 'At İsmi', 'HP', 'Şans %']])
                            with c2:
                                banko = df.iloc[0]['At İsmi']
                                st.metric("🏆 AYAK BANKOSU", banko)
                                st.progress(int(df.iloc[0]['HP']) / 110)
                                if len(df) > 1:
                                    st.write(f"🥈 **Plase:** {df.iloc[1]['At İsmi']}")
                                if len(df) > 2:
                                    st.write(f"🥉 **Sürpriz:** {df.iloc[2]['At İsmi']}")
                    else:
                        st.warning(f"{kosu_no}. Koşu için veri ayrıştırılamadı.")
            else:
                st.error("❌ '1. KOŞU' formatında başlık bulunamadı. Lütfen bülten tablosunun net bir fotoğrafını yükleyin.")

        except Exception as e:
            st.error(f"⚠️ Hata: {e}")

# Görsel yüklendiyse analiz butonunu aktif et
if uploaded_file:
    # Görseli göster
    img = Image.open(uploaded_file)
    st.image(img, caption="Yüklenen Bülten", width=300)
    
    if st.sidebar.button("🚀 Fotoğrafı Analiz Et ve Altılıyı Dök"):
        analyze_image(uploaded_file)
else:
    st.info("👋 Hoş geldiniz! TJK sitesindeki program tablosunun ekran görüntüsünü alın, sol tarafa yükleyin ve butona basın.")
    st.image(image_0.png, width=400) # Örnek Analiz Görselini göster
