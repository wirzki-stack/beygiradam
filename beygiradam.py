import streamlit as st
import requests
import io
import re
import pandas as pd
import random

# PDF okuyucu kütüphanesi
try:
    import PyPDF2
except ImportError:
    st.error("HATA: Lütfen requirements.txt dosyasına 'PyPDF2' ekleyin!")

st.set_page_config(page_title="BEYGİR ADAM AI v400", layout="wide")

# Şık Arayüz
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏇 BEYGİR ADAM | OTOMATİK LİNK ANALİZİ</h1>", unsafe_allow_html=True)

# Yan Menü: Sadece Link
pdf_url = st.sidebar.text_input("🔗 TJK PDF Bülten Linkini Yapıştırın:", placeholder="https://medya-cdn.tjk.org/...")
analiz_buton = st.sidebar.button("🚀 Bülteni Çek ve Ayak Ayak Analiz Et")

if pdf_url and analiz_buton:
    with st.spinner('AI bültene bağlanıyor ve tüm ayakları analiz ediyor...'):
        try:
            # 1. PDF'i Linkten Çek
            response = requests.get(pdf_url, timeout=20)
            pdf_file = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            # 2. Tüm Metni Oku
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            # 3. Koşuları (Ayakları) Tespit Et
            # TJK PDF'lerinde genellikle "1. KOŞU", "2. KOŞU" başlıkları kullanılır
            kosu_bloklari = re.split(r"(\d+)\.\s*KOŞU", full_text)

            if len(kosu_bloklari) > 1:
                st.success(f"✅ Analiz Başarılı! {len(kosu_bloklari)//2} Koşu Tespit Edildi.")
                
                # Her Koşu İçin Analiz Başlat
                for i in range(1, len(kosu_bloklari), 2):
                    kosu_no = kosu_bloklari[i]
                    icerik = kosu_bloklari[i+1]
                    
                    # At No, İsim ve Handikap Puanı (HP) ayıkla
                    # Regex: Satır başı rakam + Büyük Harfli İsim + Aradaki karmaşa + Sondaki 2-3 haneli HP
                    atlar = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ ]{4,25})\s+.*?(\d{2,3})", icerik)
                    
                    if atlar:
                        df = pd.DataFrame(atlar, columns=['No', 'At İsmi', 'HP'])
                        df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                        # Hatalı puanları ve 100 üstünü temizle, HP'ye göre sırala
                        df = df[(df['HP'] > 20) & (df['HP'] <= 100)].sort_values(by='HP', ascending=False)
                        df = df.drop_duplicates(subset=['At İsmi'])

                        # Her Ayak İçin Ayrı Kutu (Expander)
                        with st.expander(f"🏁 {kosu_no}. AYAK ANALİZİ (Favoriden Sürprize Sıralı)"):
                            c1, c2 = st.columns([2, 1])
                            with c1:
                                st.write("**📊 AI Kazanma Olasılığı Sıralaması:**")
                                # Olasılık hesapla (Basit AI Mantığı)
                                toplam_hp = df['HP'].sum()
                                df['Şans %'] = df['HP'].apply(lambda x: f"%{round((x/toplam_hp)*100, 1)}")
                                st.table(df[['No', 'At İsmi', 'Şans %']])
                            
                            with c2:
                                if not df.empty:
                                    banko = df.iloc[0]['At İsmi']
                                    st.metric("🏆 AYAK BANKOSU", banko)
                                    st.write(f"🥈 **Plase:** {df.iloc[1]['At İsmi'] if len(df)>1 else '---'}")
                                    st.write(f"🥉 **Sürpriz:** {df.iloc[2]['At İsmi'] if len(df)>2 else '---'}")
                    else:
                        st.warning(f"{kosu_no}. Koşu için at verisi ayrıştırılamadı.")
            else:
                st.error("❌ PDF içinde '1. KOŞU' formatında başlık bulunamadı. Linki kontrol edin.")

        except Exception as e:
            st.error(f"⚠️ Bağlantı veya Okuma Hatası: {e}")
else:
    st.info("👋 TJK sitesinden kopyaladığınız PDF linkini yapıştırın, 'Analiz Et'e basın. Gerisini AI halletsin!")
