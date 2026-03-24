import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="BEYGİR ADAM AI v290", layout="wide")

# Tasarım Ayarları
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stExpander { border: 1px solid #00FF00; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🧠 BEYGİR ADAM | AI AYAK ANALİZİ</h1>", unsafe_allow_html=True)

# Yan Menü: Veri Girişi
st.sidebar.header("📥 Veri Merkezi")
raw_text = st.sidebar.text_area("TJK Bültenini Buraya Yapıştırın:", height=400)
analiz_et = st.sidebar.button("🚀 Tüm Ayakları Analiz Et")

if raw_text and analiz_et:
    # Koşuları (Ayakları) Böl
    kosu_bloklari = re.split(r"(\d+)\.\s*KOŞU", raw_text)
    
    if len(kosu_bloklari) > 1:
        st.success(f"✅ {len(kosu_bloklari)//2} Ayak Tespit Edildi. Sıralama Hazırlanıyor...")
        
        for i in range(1, len(kosu_bloklari), 2):
            kosu_no = kosu_bloklari[i]
            icerik = kosu_bloklari[i+1]
            
            # At No, İsim ve HP Puanı Yakala
            # Regex: (No) (İSİM) ... (HP)
            at_verileri = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ ]{3,25})\s+.*?(\d{2,3})", icerik)
            
            if at_verileri:
                df = pd.DataFrame(at_verileri, columns=['No', 'At İsmi', 'HP'])
                df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                # Sadece gerçek HP puanlarını al (20-100 arası) ve Sırala
                df = df[(df['HP'] > 20) & (df['HP'] <= 100)].sort_values(by='HP', ascending=False)
                df = df.drop_duplicates(subset=['At İsmi'])

                with st.expander(f"🏁 {kosu_no}. AYAK - AI Tahminleri (Sıralı Listesi)"):
                    if not df.empty:
                        # Olasılık Hesapla
                        toplam = df['HP'].sum()
                        df['Kazanma Şansı'] = df['HP'].apply(lambda x: f"%{round((x/toplam)*100, 1)}")
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write("**📊 Olasılık Sıralaması (Favoriden Sürprize):**")
                            st.table(df[['No', 'At İsmi', 'HP', 'Kazanma Şansı']])
                        
                        with col2:
                            banko = df.iloc[0]['At İsmi']
                            st.metric("🏆 AYAK BANKOSU", banko)
                            st.progress(int(df.iloc[0]['HP']) / 100)
                            if len(df) > 1:
                                st.write(f"🥈 **Plase:** {df.iloc[1]['At İsmi']}")
                            if len(df) > 2:
                                st.write(f"🥉 **Sürpriz:** {df.iloc[2]['At İsmi']}")
                    else:
                        st.warning("Bu ayakta analiz edilecek uygun veri bulunamadı.")
    else:
        st.error("❌ '1. KOŞU' formatında başlık bulunamadı. Lütfen bülteni tam kopyalayın.")
else:
    st.info("👋 Başlamak için TJK bülten metnini kopyalayıp sol tarafa yapıştırın ve butona basın.")
