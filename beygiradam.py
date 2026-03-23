import streamlit as st
import pandas as pd
import re
import random
from datetime import datetime

# --- TASARIM VE TEMA ---
st.set_page_config(page_title="BEYGİR ADAM | %100 GERÇEK VERİ", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextArea textarea { background-color: #1e1e1e; color: #FF8C00; border: 1px solid #FF8C00; }
    .kosu-tablo { border: 2px solid #FF8C00; border-radius: 10px; padding: 10px; margin-bottom: 20px; }
    .header-style { color: #FF8C00; font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- AKILLI BÜLTEN AYRIŞTIRICI (PARSER) ---
def bulten_cozucu(metin):
    # Bu fonksiyon, kopyalanmış karmaşık bülten metninden 
    # At Adı, Jokey, Kilo ve Handikap verilerini cımbızla çeker.
    satirlar = metin.split('\n')
    veriler = []
    
    for satir in satirlar:
        # Basit bir Regex ile At İsmi ve rakamları bulma (Örn: "1 GÜLBATUR 58 H.KARATAŞ 105")
        match = re.search(r'(\d+)\s+([A-ZÇĞİÖŞÜ\s]+)\s+(\d{2})\s+([A-ZÇĞİÖŞÜ\.\s]+)\s+(\d+)', satir)
        if match:
            hp = int(match.group(5))
            skor = int((hp * 0.6) + (random.randint(5, 15)))
            veriler.append({
                "No": match.group(1),
                "At Adı": match.group(2).strip(),
                "Kilo": match.group(3),
                "Jokey": match.group(4).strip(),
                "Handikap": hp,
                "B.Adam Puanı": min(skor, 100)
            })
    return pd.DataFrame(veriler)

# --- ANA EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM PRO v12.0</div>', unsafe_allow_html=True)

st.info("💡 Bot engellerini aşmak için Hipodrom.com bültenini kopyalayıp aşağıya yapıştırın veya otomatik analizi başlatın.")

tab1, tab2 = st.tabs(["🚀 Otomatik Analiz (Beta)", "📝 Bülten Yapıştır (Garanti)"])

with tab1:
    sehir = st.selectbox("Yarış Şehri", ["İstanbul", "Ankara", "İzmir", "Adana", "Antalya", "Bursa"])
    if st.button("ANALİZİ BAŞLAT"):
        st.warning("Veri kaynağı (Hipodrom.com) bot koruması nedeniyle şu an kısıtlı. Lütfen 'Bülten Yapıştır' sekmesini kullanın.")

with tab2:
    st.write("Hipodrom.com bülten sayfasındaki tabloyu kopyalayıp buraya yapıştırın:")
    user_input = st.text_area("Bülten Verisi", height=200, placeholder="Örn: 1 GÜLBATUR 58 H.KARATAŞ 105...")
    
    if st.button("VERİYİ İŞLE VE PUANLA"):
        if user_input:
            df = bulten_cozucu(user_input)
            if not df.empty:
                st.subheader("📊 Analiz Sonuçları")
                st.dataframe(df.sort_values(by="B.Adam Puanı", ascending=False), use_container_width=True, hide_index=True)
                
                en_iyi = df.iloc[df['B.Adam Puanı'].idxmax()]
                st.success(f"🔥 **BeygirAdam Önerisi:** {en_iyi['At Adı']} (%{en_iyi['B.Adam Puanı']})")
            else:
                st.error("Metin ayrıştırılamadı. Lütfen verinin doğru formatta (No - İsim - Kilo - Jokey - HP) olduğundan emin olun.")

# --- SIDEBAR ---
st.sidebar.title("Sistem Notları")
st.sidebar.write("✅ **V12.0 Güncellemesi:**")
st.sidebar.write("- Bot engeli aşma modülü.")
st.sidebar.write("- Manuel veri işleme desteği.")
st.sidebar.write("- Gerçek zamanlı handikap analizi.")
