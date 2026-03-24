import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re

# OCR Ayarı (Tesseract kurulu olmalıdır)
# Not: GitHub/Streamlit sunucularında Tesseract kurulu gelmez.
# Bunu çalıştırmak için 'packages.txt' dosyasına 'tesseract-ocr' yazmalısın.

st.set_page_config(page_title="BEYGİR ADAM v1000", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🏇 BEYGİR ADAM | GÖRSEL ANALİZÖR v1000</h1>", unsafe_allow_html=True)

# Yan Menü: Görsel Yükleme
st.sidebar.header("📤 Bülten Görselini Yükle")
uploaded_file = st.sidebar.file_uploader("Ekran Görüntüsü Yükleyin (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
analiz_buton = st.sidebar.button("🚀 Görseli Analiz Et")

if uploaded_file and analiz_buton:
    with st.spinner('Yapay Zeka görseli parçalıyor ve dereceleri okuyor...'):
        try:
            # 1. Görseli Aç ve OCR ile Metne Çevir
            image = Image.open(uploaded_file)
            raw_text = pytesseract.image_to_string(image)
            
            if len(raw_text) > 100:
                # 2. Metni Temizle ve Koşuları Ayrıştır
                # (Daha önceki sürümlerde kullandığımız başarılı Regex mantığı)
                all_text = raw_text.replace("  ", " ").replace("\n\n", "\n")
                kosu_bloklari = re.split(r"(\d+)\.\s*(?:KOŞU|Kosu)", all_text, flags=re.IGNORECASE)
                
                if len(kosu_bloklari) > 1:
                    st.success(f"✅ {len(kosu_bloklari)//2} Koşu Tespit Edildi. AI Sıralaması Hazırlanıyor...")
                    
                    for i in range(1, len(kosu_bloklari), 2):
                        kosu_no = kosu_bloklari[i]
                        icerik = kosu_bloklari[i+1]
                        
                        # At No, İsim ve HP Puanı Yakala (Regex)
                        pattern = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ\s]{3,25}).*?(\d{2,3})", icerik)
                        
                        if pattern:
                            df = pd.DataFrame(pattern, columns=['No', 'At İsmi', 'HP'])
                            df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                            # Sadece mantıklı HP puanlarını (20-115) al ve sırala
                            df = df[(df['HP'] >= 20) & (df['HP'] <= 115)].sort_values(by='HP', ascending=False)
                            df = df.drop_duplicates(subset=['At İsmi'])

                            # Her Ayak İçin Ayrı Kutu (Oluşturulan Görseldeki Gibi)
                            with st.expander(f"🏁 {kosu_no}. AYAK ANALİZİ", expanded=True):
                                if not df.empty:
                                    # Kazanma Yüzdesi Hesapla (AI Mantığı)
                                    toplam_hp = df['HP'].sum()
                                    df['Şans %'] = df['HP'].apply(lambda x: f"%{round((x/toplam_hp)*100, 1)}")
                                    
                                    c1, c2 = st.columns([2, 1])
                                    with c1:
                                        st.write("**📊 AI Kazanma Olasılığı Sıralaması:**")
                                        st.table(df[['No', 'At İsmi', 'HP', 'Şans %']])
                                    with c2:
                                        banko = df.iloc[0]['At İsmi']
                                        st.metric("🏆 AYAK BANKOSU", banko)
                                        st.write(f"🥈 Plase: {df.iloc[1]['At İsmi'] if len(df)>1 else '-'}")
                                        st.write(f"🥉 Sürpriz: {df.iloc[2]['At İsmi'] if len(df)>2 else '-'}")
                                else:
                                    st.warning(f"{kosu_no}. Koşu'da atlar tespit edilemedi.")
                else:
                    st.error("❌ '1. KOŞU' formatında başlık bulunamadı. Lütfen görseli net çekin.")
            else:
                st.error("❌ Görselden yeterli metin okunamadı. Lütfen bülten tablosunun net bir ekran görüntüsünü yükleyin.")

        except Exception as e:
            st.error(f"Sistemsel Hata: {e}")
            st.info("💡 Not: Bu özelliği GitHub sunucularında çalıştırmak için 'packages.txt' dosyasına 'tesseract-ocr' eklenmelidir.")
else:
    st.info("👋 Başlamak için TJK bülten tablosunun ekran görüntüsünü alın, sol tarafa yükleyin ve 'Analiz Et'e basın.")
    st.image(image_0.png, width=400) # Oluşturulan görseli örnek olarak göster
