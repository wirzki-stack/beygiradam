import streamlit as st
import requests
import io
import re
import pandas as pd

try:
    import PyPDF2
except ImportError:
    st.error("Lütfen requirements.txt dosyanıza 'PyPDF2' ekleyin!")

st.set_page_config(page_title="BEYGİR ADAM AI v270", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🧠 AI HASSAS KOŞU ANALİZİ</h1>", unsafe_allow_html=True)

pdf_url = st.sidebar.text_input("🔗 TJK PDF Linkini Yapıştırın:")
analiz_buton = st.sidebar.button("🚀 Bülteni Ayak Ayak Analiz Et")

if pdf_url and analiz_buton:
    with st.spinner("Yapay Zeka koşuları ve at performanslarını eşleştiriyor..."):
        try:
            response = requests.get(pdf_url, timeout=30)
            pdf_file = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            # PDF'i koşu başlıklarına göre parçala
            pages_text = ""
            for page in reader.pages:
                pages_text += page.extract_text() + "\n"

            # Koşuları "KOŞU" kelimesine göre böl
            kosu_parcalari = re.split(r"(\d+)\.\s*KOŞU", pages_text)
            
            if len(kosu_parcalari) > 1:
                st.success(f"✅ {len(kosu_parcalari)//2} Adet Koşu Tespit Edildi ve Ayrıştırıldı.")
                
                for i in range(1, len(kosu_parcalari), 2):
                    kosu_no = kosu_parcalari[i]
                    kosu_icerik = kosu_parcalari[i+1]
                    
                    # Bu kosu icindeki atları ve puanları bul
                    # Regex: Satır başındaki rakam, büyük harfli isim ve sonlardaki 2 haneli HP puanı
                    at_verileri = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ ]{4,20})\s+.*?(\d{2})\s*\n", kosu_icerik)
                    
                    if at_verileri:
                        df = pd.DataFrame(at_verileri, columns=['No', 'At İsmi', 'HP'])
                        df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                        # Puanı hatalı olanları (Örn: kilo ile karışanları) temizle ve 100 üstünü filtrele
                        df = df[df['HP'] <= 100].sort_values(by='HP', ascending=False)
                        
                        with st.expander(f"🏁 {kosu_no}. KOŞU (AYAK) ANALİZİ - Sıralı Liste"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write("**🏆 AI Tahmin Sıralaması (En İyi -> En Zayıf):**")
                                # Tabloyu renklendir ve göster
                                st.dataframe(df.assign(Durum=lambda x: ['Favori' if i==0 else 'Plase' if i==1 else 'Sürpriz' for i in range(len(x))]), use_container_width=True)
                            
                            with col2:
                                if not df.empty:
                                    banko = df.iloc[0]['At İsmi']
                                    st.metric("Günün Bankosu", banko)
                                    st.progress(int(df.iloc[0]['HP']) / 100)
                                    st.caption(f"Yapay Zeka Güven Endeksi: %{df.iloc[0]['HP']}")
                    else:
                        st.warning(f"{kosu_no}. Koşu içeriği karmaşık olduğu için ayrıştırılamadı.")
            else:
                st.error("⚠️ Koşu başlıkları bulunamadı. Lütfen PDF linkini kontrol edin.")

        except Exception as e:
            st.error(f"⚠️ Hata: {e}")
else:
    st.info("👋 Hoş geldiniz! PDF linkini yapıştırın; AI her ayağı favoriden sürprize doğru sizin için dizsin.")
