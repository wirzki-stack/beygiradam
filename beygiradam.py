import streamlit as st
import pandas as pd
import re
import random
from datetime import datetime

# --- TEMA AYARLARI ---
st.set_page_config(page_title="BEYGİR ADAM | PROFESYONEL ANALİZ", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextArea textarea { background-color: #1e1e1e; color: #00FF00; border: 1px solid #FF8C00; }
    .kosu-header { background-color: #FF8C00; color: black; padding: 10px; border-radius: 8px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- PDF/METİN OKUYUCU ZEKA ---
def bulten_analiz_et(metin):
    satirlar = metin.split('\n')
    veriler = []
    for satir in satirlar:
        # Satırdaki büyük harfli kelimeleri (At İsmi) ve sayıları (HP) bulur
        at_adi_bul = re.findall(r'[A-ZÇĞİÖŞÜ]{3,}', satir)
        sayilar = re.findall(r'\d+', satir)
        
        if at_adi_bul and len(sayilar) >= 1:
            at = at_adi_bul[0]
            # PDF formatına göre sondaki sayı genelde HP'dir
            hp = int(sayilar[-1])
            if hp < 10 and len(sayilar) > 1: hp = int(sayilar[-2]) # No ile HP karışırsa düzelt
            
            # BeygirAdam Puanlama (Handikap %70 + Şans %30)
            puan = int((hp * 0.6) + random.randint(15, 30))
            
            veriler.append({
                "At Adı": at,
                "Handikap": hp,
                "B.Adam Puanı": f"%{min(puan, 99)}"
            })
    return pd.DataFrame(veriler)

# --- ARAYÜZ ---
st.markdown('<h1 style="color:#FF8C00; text-align:center;">🏇 BEYGİR ADAM v20.0</h1>', unsafe_allow_html=True)
st.write(f"📅 **Bugünün Yarışları:** {datetime.now().strftime('%d.%m.%Y')} | Bursa / Şanlıurfa")

# PDF'den Veri Alma Alanı
st.subheader("📝 Bursa PDF Verisini Buraya Yapıştır")
raw_data = st.text_area("Bursa PDF'ini aç, bir koşuyu kopyala ve buraya yapıştır:", height=200, placeholder="Örn: 1 HALİD BEY 58 H.KARATAŞ 105...")

if st.button("📊 ANALİZİ BAŞLAT"):
    if raw_data:
        df = bulten_analiz_et(raw_data)
        if not df.empty:
            st.markdown('<div class="kosu-header">GÜNCEL KOŞU ANALİZ TABLOSU</div>', unsafe_allow_html=True)
            st.dataframe(df.sort_values(by="Handikap", ascending=False), use_container_width=True, hide_index=True)
            
            en_iyi = df.iloc[0]
            st.success(f"🔥 **Günün Favorisi:** {en_iyi['At Adı']} (Puan: {en_iyi['B.Adam Puanı']})")
        else:
            st.error("Veri formatı anlaşılamadı. Lütfen at isimlerinin olduğu satırları kopyaladığınızdan emin olun.")

st.sidebar.markdown("---")
st.sidebar.info("Otomatik botlar TJK tarafından engellendiği için bu yöntemle %100 GERÇEK at isimlerine ulaşırsınız.")
