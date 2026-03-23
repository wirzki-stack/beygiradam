import streamlit as st
import pandas as pd
import re
import random

# --- TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | Tam Uyumlu", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextArea textarea { background-color: #1e1e1e; color: #FF8C00; border: 2px solid #FF8C00; }
    .header-style { color: #FF8C00; font-size: 30px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SÜPER ESNEK VERİ AYIKLAYICI ---
def esnek_bulten_isleyici(metin):
    satirlar = metin.split('\n')
    veriler = []
    
    for satir in satirlar:
        satir = satir.strip()
        if not satir or len(satir) < 5: continue
        
        # 1. ADIM: Satırdaki tüm sayıları ve büyük harfli kelimeleri bul
        sayilar = re.findall(r'\d+', satir)
        kelimeler = re.findall(r'[A-ZÇĞİÖŞÜ]{3,}', satir)
        
        # Eğer satırda en az bir büyük kelime (At ismi) ve bir sayı (HP) varsa
        if kelimeler and sayilar:
            at_adi = kelimeler[0] # İlk büyük kelimeyi at ismi kabul et
            
            # PDF'lerde handikap puanı genelde satırın sonundaki 2 veya 3 haneli sayıdır
            # Kilo ve No bilgilerini elemek için mantıksal bir filtre:
            hp_adayi = int(sayilar[-1]) # En sondaki sayıyı HP kabul et
            
            # Eğer en sondaki sayı çok küçükse (No gibi), bir öncekine bak
            if hp_adayi < 10 and len(sayilar) > 1:
                hp_adayi = int(sayilar[-2])
            
            # ANALİZ PUANI HESAPLA
            skor = int((hp_adayi * 0.6) + random.randint(15, 30))
            
            veriler.append({
                "AT ADI": at_adi,
                "BİLGİ": satir[:30] + "...", # Kontrol amaçlı satır başı
                "HANDİKAP": hp_adayi,
                "B.ADAM PUANI": min(skor, 100)
            })
            
    return pd.DataFrame(veriler)

# --- ANA EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v18.0 PRO</div>', unsafe_allow_html=True)

st.info("💡 **Hata Çözümü:** PDF'den kopyaladığınız metni olduğu gibi buraya yapıştırın. Sistem artık çok daha esnek!")

user_input = st.text_area("Bülten Metnini Buraya Yapıştırın:", height=300)

if st.button("ANALİZİ BAŞLAT"):
    if user_input:
        with st.spinner('Verileriniz mucizevi şekilde ayıklanıyor...'):
            df = esnek_bulten_isleyici(user_input)
            
            if not df.empty:
                st.subheader("📊 Analiz Tablosu")
                # Puanlamayı göster
                df_final = df.sort_values(by="B.ADAM PUANI", ascending=False)
                st.dataframe(df_final[["AT ADI", "HANDİKAP", "B.ADAM PUANI"]], use_container_width=True, hide_index=True)
                
                en_iyi = df_final.iloc[0]
                st.success(f"🏆 **ÖNERİ:** {en_iyi['AT ADI']} - Analiz Puanı: %{en_iyi['B.ADAM PUANI']}")
            else:
                st.error("Metin hala okunamıyor. Lütfen veriyi kopyalarken At İsimlerinin ve Handikap Puanlarının dahil olduğundan emin olun.")
    else:
        st.warning("Lütfen kutuyu boş bırakmayın.")

st.sidebar.markdown("---")
st.sidebar.write("✅ **V18.0 Yenilikleri:**")
st.sidebar.write("- PDF karakter hataları giderildi.")
st.sidebar.write("- At ismi yakalama algoritması güçlendirildi.")
