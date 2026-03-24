import streamlit as st
import requests
import io
import re
import pandas as pd

# PDF Okuma
try:
    import PyPDF2
except ImportError:
    st.error("Gereksinim hatası: requirements.txt dosyasına 'PyPDF2' ekleyin.")

st.set_page_config(page_title="BEYGİR ADAM AI v600", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🧠 AI PROFESYONEL BÜLTEN ANALİZİ</h1>", unsafe_allow_html=True)

# Yan Menü
pdf_url = st.sidebar.text_input("🔗 TJK PDF Linkini Yapıştırın:", value="https://medya-cdn.tjk.org/raportfp/TJKPDF/2026/2026-03-24/PDF/GunlukYarisProgrami/24.03.2026-Antalya-GunlukYarisProgrami-TR.pdf")
st.sidebar.warning("Not: TJK sunucusu bazen erişimi engeller. Eğer 'Okunamadı' derse metni kopyalayıp aşağıdaki kutuya atın.")
manuel_text = st.sidebar.text_area("Alternatif: Bülten Metnini Buraya Yapıştırın", height=150)
analiz_buton = st.sidebar.button("🚀 Analiz Motorunu Başlat")

def analiz_et(metin):
    # Koşuları Böl
    kosular = re.split(r"(\d+)\.\s*KOŞU", metin)
    if len(kosular) > 1:
        for i in range(1, len(kosular), 2):
            k_no = kosular[i]
            k_icerik = kosular[i+1]
            # At No, İsim ve HP Puanı (Örn: 1 ALPEREN... 85)
            pattern = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ ]{4,20})\s+.*?(\d{2,3})", k_icerik)
            if pattern:
                df = pd.DataFrame(pattern, columns=['No', 'At İsmi', 'HP'])
                df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                df = df[(df['HP'] > 20) & (df['HP'] <= 100)].sort_values(by='HP', ascending=False).drop_duplicates('At İsmi')
                
                with st.expander(f"🏁 {k_no}. AYAK ANALİZİ"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.table(df[['No', 'At İsmi', 'HP']])
                    with col2:
                        st.metric("🏆 FAVORİ", df.iloc[0]['At İsmi'])
                        st.write(f"🥈 Plase: {df.iloc[1]['At İsmi'] if len(df)>1 else '-'}")
    else:
        st.error("Koşu formatı bulunamadı. Lütfen '1. KOŞU' yazısını içeren metni yapıştırın.")

if analiz_buton:
    if manuel_text:
        analiz_et(manuel_text)
    elif pdf_url:
        with st.spinner('AI PDF üzerinden verileri çekmeye çalışıyor...'):
            try:
                r = requests.get(pdf_url, timeout=15)
                f = io.BytesIO(r.content)
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                if len(text) > 50: # Metin başarıyla çekildiyse
                    analiz_et(text)
                else:
                    st.error("TJK bu PDF'i şifrelemiş. Lütfen bülten sayfasındaki yazıları kopyalayıp yan taraftaki kutuya yapıştırın.")
            except Exception as e:
                st.error(f"Erişim Hatası: {e}")
