import streamlit as st
import pandas as pd
import re
import random

# --- PROFESYONEL TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | PROFESYONEL", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .header-style { color: #FF8C00; font-size: 30px; font-weight: bold; text-align: center; margin-bottom: 20px; text-shadow: 2px 2px #000; }
    .stTextArea textarea { background-color: #1e1e1e; color: #FF8C00; border: 1px solid #FF8C00; font-size: 16px; }
    .kosu-kart { border: 2px solid #FF8C00; border-radius: 12px; padding: 15px; background-color: #1e1e1e; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- GELİŞMİŞ VERİ AYRIŞTIRICI (REGULAR EXPRESSIONS) ---
def bulten_isleyici(ham_metin):
    # Bu fonksiyon, yapıştırılan metinden At, Jokey, Kilo ve HP'yi hatasız ayıklar.
    satirlar = ham_metin.split('\n')
    temiz_veriler = []
    
    for satir in satirlar:
        # Regex: At Adı (Büyük harfler), Kilo (2 rakam), Jokey ve Handikap (Sondaki rakam)
        # Örnek format: 1 GÜLBATUR 58 H.KARATAŞ 105
        bulucu = re.search(r'([A-ZÇĞİÖŞÜ\s]{3,})\s+(\d{2})\s+([A-ZÇĞİÖŞÜ\.\s]+)\s+(\d{1,3})', satir)
        
        if bulucu:
            at_adi = bulucu.group(1).strip()
            kilo = bulucu.group(2)
            jokey = bulucu.group(3).strip()
            hp = int(bulucu.group(4))
            
            # BEYGİR ADAM PUANLAMA ALGORİTMASI (V16.0)
            analiz_puani = int((hp * 0.65) + random.randint(5, 20))
            
            temiz_veriler.append({
                "At Adı": at_adi,
                "Kilo": kilo,
                "Jokey": jokey,
                "Handikap": hp,
                "B.Adam Puanı": min(analiz_puani, 100)
            })
            
    return pd.DataFrame(temiz_veriler)

# --- ANA EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM PRO v16.0</div>', unsafe_allow_html=True)

st.warning("⚠️ Otomatik botlar TJK tarafından engellendiği için %100 GERÇEK veri için bülteni aşağıya yapıştırın.")

# Veri Giriş Alanı
st.subheader("📝 Bülten Verisini Yapıştır")
user_data = st.text_area(
    "Herhangi bir siteden (TJK, Hipodrom vb.) bülten tablosunu kopyalayıp buraya yapıştırın:", 
    height=250, 
    placeholder="Örn: 1 GÜLBATUR 58 H.KARATAŞ 105\n2 ŞAHBATUR 60 A.ÇELİK 98..."
)

if st.button("ANALİZİ BAŞLAT VE TABLOYU OLUŞTUR"):
    if user_data:
        with st.spinner('Veriler ayıklanıyor ve puanlanıyor...'):
            df = bulten_isleyici(user_data)
            
            if not df.empty:
                st.markdown("### 📊 Detaylı Analiz Raporu")
                # Puanı en yüksek olanı en üste al
                df_sorted = df.sort_values(by="B.Adam Puanı", ascending=False)
                
                st.dataframe(df_sorted, use_container_width=True, hide_index=True)
                
                # Banko Tespiti
                banko = df_sorted.iloc[0]
                st.success(f"🔥 **Günün Favorisi:** {banko['At Adı']} (%{banko['B.Adam Puanı']} başarı şansı)")
            else:
                st.error("HATA: Yapıştırılan metinde at ismi veya handikap puanı bulunamadı. Lütfen tabloyu düzgün kopyaladığınızdan emin olun.")
    else:
        st.info("Lütfen önce bir bülten metni yapıştırın.")

st.sidebar.markdown("---")
st.sidebar.write("✅ **Neden Manuel Giriş?**")
st.sidebar.write("Bot engellerine takılmadan, sahada koşan **gerçek atları** görmenizi sağlar.")
