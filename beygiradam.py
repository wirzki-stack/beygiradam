import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="BEYGİR ADAM v5000", layout="wide")

# Tasarımı en üst seviyeye taşıdık
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextArea textarea { background-color: #1e2127; color: #00FF00; border: 1px solid #00FF00; }
    .stExpander { border: 1px solid #00FF00; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏇 BEYGİR ADAM | PROFESYONEL ANALİZ SİSTEMİ")

# Sol Panel
st.sidebar.header("📥 Analiz Başlat")
st.sidebar.info("Görsel yükleme sunucu hatalarına sebep olduğu için en güvenli yöntem metin analizidir.")

# ANA EKRAN: Kullanıcı dostu veri girişi
st.markdown("### 📝 Bülten Metnini Buraya Yapıştırın")
raw_text = st.text_area("TJK veya Fanatik sitesinden kopyaladığınız bülteni buraya bırakın:", height=300, placeholder="1. KOŞU... 1 AT ADI... 85 HP...")

if st.button("🚀 ANALİZİ ÇALIŞTIR"):
    if raw_text:
        with st.spinner('Yapay Zeka her ayağı ayrı ayrı analiz ediyor...'):
            # Koşuları Böl
            kosular = re.split(r"(\d+)\.\s*(?:KOŞU|Kosu)", raw_text, flags=re.IGNORECASE)
            
            if len(kosular) > 1:
                st.success(f"✅ {len(kosular)//2} Koşu Tespit Edildi.")
                
                # Her Koşu İçin Tablo Oluştur
                for i in range(1, len(kosular), 2):
                    k_no = kosular[i]
                    icerik = kosular[i+1]
                    
                    # At No - İsim - HP Puanı yakala
                    pattern = re.findall(r"(\d{1,2})\s+([A-ZÇĞİÖŞÜ\s]{3,25}).*?(\d{2,3})", icerik)
                    
                    if pattern:
                        df = pd.DataFrame(pattern, columns=['No', 'At İsmi', 'HP'])
                        df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
                        # Puanlama ve Sıralama
                        df = df[(df['HP'] >= 20) & (df['HP'] <= 115)].sort_values(by='HP', ascending=False).drop_duplicates('At İsmi')

                        with st.expander(f"🏁 {k_no}. AYAK ANALİZİ (En Muhtemel -> En Düşük)", expanded=True):
                            c1, c2 = st.columns([2, 1])
                            with c1:
                                st.write("**📊 AI Olasılık Sıralaması:**")
                                st.table(df[['No', 'At İsmi', 'HP']])
                            with c2:
                                banko = df.iloc[0]['At İsmi']
                                st.metric("🏆 AYAK BANKOSU", banko)
                                if len(df) > 1:
                                    st.write(f"🥈 **Plase:** {df.iloc[1]['At İsmi']}")
                    else:
                        st.warning(f"{k_no}. Koşu içeriği anlaşılamadı.")
            else:
                st.error("❌ Koşu başlıkları bulunamadı. Lütfen '1. KOŞU' yazısını içeren metni yapıştırın.")
    else:
        st.warning("Lütfen önce bülten verisini yapıştırın.")

st.divider()
st.caption("Beygir Adam v5000 | 2026 AI Analiz Sistemi")
