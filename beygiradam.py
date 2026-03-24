import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="BEYGİR ADAM AI v280", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🧠 BEYGİR ADAM | AI TAM ANALİZ</h1>", unsafe_allow_html=True)

# Yan Menü
st.sidebar.header("📥 Veri Girişi")
raw_data = st.sidebar.text_area("TJK Bültenini Kopyalayıp Buraya Yapıştırın:", height=400, placeholder="Örn: 1. KOŞU ... 1 TABİP BEY ...")
analiz_buton = st.sidebar.button("🚀 Analiz Et")

if raw_data and analiz_buton:
    # Koşuları ayır
    kosu_bloklari = re.split(r"(\d+)\.\s*KOŞU", raw_data)
    
    if len(kosu_bloklari) > 1:
        st.success(f"✅ {len(kosu_bloklari)//2} Koşu Tespit Edildi. Analiz Başlıyor...")
        
        for i in range(1, len(kosu_bloklari), 2):
            kosu_no = kosu_bloklari[i]
            icerik = kosu_bloklari[i+1]
            
            # Satırları tara: Numara, At İsmi ve Handikap Puanını (HP) yakala
            # Regex: (At No) (At İsmi) ... (HP)
            at_bulucu = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ ]{3,20})\s+.*?(\d{2,3})", icerik)
            
            if at_bulucu:
                df = pd.DataFrame(at_bulucu, columns=['No', 'At İsmi', 'HP'])
                df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                # Kilo ile karışmaması için HP filtresi (Genelde 20-100 arasıdır)
                df = df[(df['HP'] > 20) & (df['HP'] <= 100)].sort_values(by='HP', ascending=False)
                
                with st.expander(f"🏁 {kosu_no}. AYAK ANALİZİ (Favoriden Sürprize)"):
                    if not df.empty:
                        # Kazanma Yüzdesi Hesaplama (Basit AI Algoritması)
                        toplam_hp = df['HP'].sum()
                        df['Kazanma Şansı'] = df['HP'].apply(lambda x: f"%{round((x/toplam_hp)*100 +
