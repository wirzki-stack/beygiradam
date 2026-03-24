import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="BEYGİR ADAM v3000", layout="wide")

# Tasarımı siyah/yeşil yapalım
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stExpander { background-color: #1e2127; border: 1px solid #00FF00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏇 BEYGİR ADAM | PROFESYONEL ANALİZ")

# Sol tarafta sadece metin girişi
st.sidebar.header("📝 Veri Girişi")
raw_text = st.sidebar.text_area("Bülten metnini buraya yapıştırın (1. Koşu'dan başlayarak):", height=400)
analiz_buton = st.sidebar.button("🚀 ANALİZ ET")

if analiz_buton and raw_text:
    # Koşuları Böl
    kosular = re.split(r"(\d+)\.\s*(?:KOŞU|Kosu)", raw_text, flags=re.IGNORECASE)
    
    if len(kosular) > 1:
        st.success(f"✅ {len(kosular)//2} Koşu Tespit Edildi.")
        
        for i in range(1, len(kosular), 2):
            k_no = kosular[i]
            icerik = kosular[i+1]
            
            # At No - İsim - HP Puanı yakala
            pattern = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ\s]{3,25}).*?(\d{2,3})", icerik)
            
            if pattern:
                df = pd.DataFrame(pattern, columns=['No', 'At İsmi', 'HP'])
                df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                df = df[(df['HP'] >= 10) & (df['HP'] <= 120)].sort_values(by='HP', ascending=False).drop_duplicates('At İsmi')

                with st.expander(f"🏁 {k_no}. AYAK ANALİZİ", expanded=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.table(df[['No', 'At İsmi', 'HP']])
                    with c2:
                        st.metric("🏆 FAVORİ", df.iloc[0]['At İsmi'])
                        if len(df) > 1:
                            st.write(f"🥈 Plase: {df.iloc[1]['At İsmi']}")
    else:
        st.error("Metin içinde '1. Koşu' başlığı bulunamadı. Lütfen tüm bülteni kopyaladığınızdan emin olun.")
else:
    st.info("👋 Başlamak için TJK bültenindeki yazıları kopyalayıp sol kutuya yapıştırın.")
