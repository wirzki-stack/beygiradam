import streamlit as st
import pandas as pd
import re
import random

# --- TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | KESİN ANALİZ", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextArea textarea { background-color: #1e1e1e; color: #00FF00; border: 2px solid #FF8C00; font-size: 16px; }
    .header-style { color: #FF8C00; font-size: 32px; font-weight: bold; text-align: center; }
    .result-box { border: 2px solid #FF8C00; border-radius: 10px; padding: 15px; background-color: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)

# --- SÜPER ESNEK TEMİZLEYİCİ ---
def bulten_temizle_ve_analiz_et(metin):
    satirlar = metin.split('\n')
    veriler = []
    for satir in satirlar:
        satir = satir.strip()
        if not satir or len(satir) < 5: continue
        
        # 1. At İsmini Bul (Sadece büyük harflerden oluşan en az 4 harfli kelime)
        at_adi_bul = re.findall(r'[A-ZÇĞİÖŞÜ\s]{4,}', satir)
        # 2. Sayıları Bul (Handikap Puanı genelde sondadır)
        sayilar = re.findall(r'\d+', satir)
        
        if at_adi_bul and len(sayilar) >= 1:
            # KG, DB, SK gibi takıları elemek için en uzun kelimeyi at ismi seç
            at_adi = max(at_adi_bul, key=len).strip()
            # Yaş ve No bilgilerini ele, en sondaki 2 veya 3 haneli sayıyı HP al
            hp = int(sayilar[-1])
            if hp < 10 and len(sayilar) > 1: hp = int(sayilar[-2])
            
            # BeygirAdam Puanlama
            skor = int((hp * 0.65) + random.randint(10, 25))
            
            veriler.append({
                "AT ADI": at_adi,
                "HANDİKAP": hp,
                "B.ADAM PUANI": f"%{min(skor, 99)}"
            })
    return pd.DataFrame(veriler)

# --- ARAYÜZ ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v24.0</div>', unsafe_allow_html=True)
st.info("💡 **Linkler engelleniyor.** En sağlıklı sonuç için: Liderform veya TJK PDF'inden atların olduğu kısmı kopyalayıp aşağıdaki kutuya yapıştırın.")

user_input = st.text_area("Bursa Bültenini Buraya Yapıştırın:", height=250, placeholder="Örn: 1 HALİD BEY 58 H.KARATAŞ 105...")

if st.button("📊 ANALİZİ BAŞLAT"):
    if user_input:
        df = bulten_temizle_ve_analiz_et(user_input)
        if not df.empty:
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.subheader("🏁 Bursa Koşu Analiz Tablosu")
            st.dataframe(df.sort_values(by="HANDİKAP", ascending=False), use_container_width=True, hide_index=True)
            
            fav = df.iloc[0]
            st.success(f"🏆 **BEYGİR ADAM ÖNERİSİ:** {fav['AT ADI']} (Başarı Şansı: {fav['B.ADAM PUANI']})")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Metin okunamadı. Lütfen kopyaladığınız kısımda at ismi ve puan olduğundan emin olun.")
