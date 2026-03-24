import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="BEYGİR ADAM v5000", layout="wide")

st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏇 BEYGİR ADAM | PROFESYONEL ANALİZ</h1>", unsafe_allow_html=True)

# Yan tarafta metin girişi (Fotoğraf gibi hata vermez!)
st.sidebar.header("📥 Veri Girişi")
raw_text = st.sidebar.text_area("Bülten metnini kopyalayıp buraya yapıştırın:", height=400)
analiz_buton = st.sidebar.button("🚀 Analiz Et")

if raw_text and analiz_buton:
    # Koşuları Böl
    kosular = re.split(r"(\d+)\.\s*(?:KOŞU|Kosu)", raw_text, flags=re.IGNORECASE)
    
    if len(kosular) > 1:
        st.success(f"✅ {len(kosular)//2} Koşu Tespit Edildi.")
        for i in range(1, len(kosular), 2):
            k_no = kosular[i]
            icerik = kosular[i+1]
            # At No - İsim - HP Puanı
            pattern = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ\s]{3,25}).*?(\d{2,3})", icerik)
            if pattern:
                df = pd.DataFrame(pattern, columns=['No', 'At İsmi', 'HP'])
                df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                df = df[(df['HP'] >= 20)].sort_values(by='HP', ascending=False).drop_duplicates('At İsmi')

                with st.expander(f"🏁 {k_no}. AYAK ANALİZİ", expanded=True):
                    c1, c2 = st.columns([2, 1])
                    with c1: st.table(df[['No', 'At İsmi', 'HP']])
                    with c2: st.metric("🏆 FAVORİ", df.iloc[0]['At İsmi'])
    else:
        st.error("Metin okunamadı. Lütfen '1. Koşu' yazan yerden başlayarak kopyalayın.")
