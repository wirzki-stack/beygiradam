import streamlit as st
import requests
import io
import re
import pandas as pd

try:
    import PyPDF2
except ImportError:
    st.error("Lütfen requirements.txt dosyasına 'PyPDF2' ekleyin!")

st.set_page_config(page_title="BEYGİR ADAM v500", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🧠 AI DERİN PDF ANALİZÖRÜ</h1>", unsafe_allow_html=True)

pdf_url = st.sidebar.text_input("🔗 TJK PDF Linkini Buraya Yapıştırın:", value="https://medya-cdn.tjk.org/raportfp/TJKPDF/2026/2026-03-24/PDF/GunlukYarisProgrami/24.03.2026-Antalya-GunlukYarisProgrami-TR.pdf")
analiz_buton = st.sidebar.button("🚀 PDF'i Zorla Oku ve Analiz Et")

if pdf_url and analiz_buton:
    with st.spinner('Yapay Zeka PDF katmanlarını dijital olarak parçalıyor...'):
        try:
            # 1. PDF'i indir
            response = requests.get(pdf_url, timeout=30)
            pdf_file = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text() + "\n"

            # 2. PDF içindeki karmaşayı temizle (TJK PDF'ine özel temizlik)
            all_text = all_text.replace("  ", " ") # Çift boşlukları sil
            
            # 3. Koşuları Tespit Et
            kosu_parcalari = re.split(r"(\d+)\.\s*KOŞU", all_text)

            if len(kosu_parcalari) > 1:
                st.success(f"✅ {len(kosu_parcalari)//2} Koşu Tespit Edildi.")
                
                for i in range(1, len(kosu_parcalari), 2):
                    kosu_no = kosu_parcalari[i]
                    icerik = kosu_parcalari[i+1]
                    
                    # TJK PDF Tablo Yapısına Uygun Regex (No - İsim - Puan)
                    # Genelde: "1 AT_ISMI 58 JOKEY_ISMI 85"
                    veriler = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ ]{4,20})\s+.*?(\d{2,3})", icerik)
                    
                    if veriler:
                        df = pd.DataFrame(veriler, columns=['No', 'At İsmi', 'HP'])
                        df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                        # Sadece 20-100 arası gerçek puanları al ve sırala
                        df = df[(df['HP'] >= 20) & (df['HP'] <= 100)].sort_values(by='HP', ascending=False)
                        df = df.drop_duplicates(subset=['At İsmi'])

                        with st.expander(f"🏁 {kosu_no}. AYAK ANALİZİ"):
                            c1, c2 = st.columns([2, 1])
                            with c1:
                                st.write("**📊 AI Sıralaması (Favoriden Sürprize):**")
                                st.table(df[['No', 'At İsmi', 'HP']])
                            with c2:
                                if not df.empty:
                                    st.metric("🏆 BANKO", df.iloc[0]['At İsmi'])
                                    st.write(f"🥈 Plase: {df.iloc[1]['At İsmi'] if len(df)>1 else '-'}")
                    else:
                        st.warning(f"{kosu_no}. Koşu'da atlar tespit edilemedi (PDF tablo yapısı çok karmaşık).")
            else:
                st.error("❌ PDF metin katmanı okunmadı. TJK bu PDF'i şifrelemiş olabilir.")

        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
else:
    st.info("👋 Link hazır, sadece butona basın. Eğer 'Okunmadı' hatası alırsak, TJK PDF'i resim olarak yüklemiş demektir.")
