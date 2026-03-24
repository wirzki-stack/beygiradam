import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="BEYGİR ADAM v800", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF4B4B;'>🧠 BEYGİR ADAM | FANATİK ANALİZ MERKEZİ</h1>", unsafe_allow_html=True)

# Yan Menü
st.sidebar.header("📥 Veri Girişi")
st.sidebar.info("Fanatik sitesindeki program tablosunu kopyalayıp aşağıya yapıştırın.")
raw_text = st.sidebar.text_area("Bülten Metnini Buraya Yapıştırın:", height=400)
analiz_buton = st.sidebar.button("🚀 Tüm Ayakları Sırala")

if raw_text and analiz_buton:
    # Fanatik formatında koşuları ayır (Genelde '1. Koşu', '2. Koşu' diye başlar)
    kosu_bloklari = re.split(r"(\d+)\.\s*Koşu", raw_text, flags=re.IGNORECASE)
    
    if len(kosu_bloklari) > 1:
        st.success(f"✅ {len(kosu_bloklari)//2} Koşu Tespit Edildi. AI Sıralaması Hazırlanıyor...")
        
        for i in range(1, len(kosu_bloklari), 2):
            kosu_no = kosu_bloklari[i]
            icerik = kosu_bloklari[i+1]
            
            # Fanatik'teki satır yapısını yakala: (At No) (At İsmi) ... (HP Puanı)
            # Fanatik'te HP puanı genelde satırın en sonunda olur.
            at_verileri = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ ]{4,25}).*?(\d{2,3})", icerik)
            
            if at_verileri:
                df = pd.DataFrame(at_verileri, columns=['No', 'At İsmi', 'HP'])
                df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                # Sadece gerçek HP puanlarını al (20-100 arası) ve Sırala
                df = df[(df['HP'] >= 20) & (df['HP'] <= 110)].sort_values(by='HP', ascending=False)
                df = df.drop_duplicates(subset=['At İsmi'])

                with st.expander(f"🏁 {kosu_no}. AYAK - AI ANALİZİ (Favoriden Sürprize)"):
                    if not df.empty:
                        # Kazanma Şansı Hesapla
                        toplam = df['HP'].sum()
                        df['Kazanma Şansı'] = df['HP'].apply(lambda x: f"%{round((x/toplam)*100, 1)}")
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write("**📊 AI Olasılık Tablosu:**")
                            st.table(df[['No', 'At İsmi', 'Kazanma Şansı']])
                        
                        with col2:
                            banko = df.iloc[0]['At İsmi']
                            st.metric("🏆 AYAK BANKOSU", banko)
                            st.progress(int(df.iloc[0]['HP']) / 110)
                            if len(df) > 1:
                                st.write(f"🥈 **Plase:** {df.iloc[1]['At İsmi']}")
                    else:
                        st.warning("Bu ayakta yeterli veri bulunamadı.")
    else:
        st.error("❌ Koşu başlıkları bulunamadı. Lütfen '1. Koşu' başlığıyla beraber kopyalayın.")
else:
    st.info("👋 **Nasıl Yapılır?** \n1. Fanatik Hipodrom sayfasında bülten tablosunu fareyle seçip kopyalayın. \n2. Sol kutuya yapıştırın. \n3. AI her ayağı ayrı ayrı analiz edecektir.")
