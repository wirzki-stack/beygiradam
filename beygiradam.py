import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- PREMİUM TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | LİNK ANALİZ", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextInput input { background-color: #1e1e1e; color: #FF8C00; border: 1px solid #FF8C00; }
    .header-style { color: #FF8C00; font-size: 30px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LİNK OKUMA MOTORU ---
def linkten_veri_cek(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Sitedeki tüm metni çek ve temizle
        metin = soup.get_text()
        satirlar = metin.split('\n')
        
        analiz_listesi = []
        for satir in satirlar:
            satir = satir.strip()
            # Satırda At İsmi (Büyük Harf) ve Handikap (Sayı) ara
            at_adi = re.findall(r'[A-ZÇĞİÖŞÜ]{4,}', satir)
            sayilar = re.findall(r'\d+', satir)
            
            if at_adi and len(sayilar) >= 1:
                hp = int(sayilar[-1])
                if hp > 10: # No veya Yaş değilse HP kabul et
                    analiz_listesi.append({
                        "AT ADI": at_adi[0],
                        "HANDİKAP": hp,
                        "B.ADAM PUANI": min(int(hp * 0.7 + 15), 99)
                    })
        return pd.DataFrame(analiz_listesi).drop_duplicates(subset=['AT ADI'])
    except Exception as e:
        return f"Hata: {e}"

# --- ARAYÜZ ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v22.0 (Link Okuyucu)</div>', unsafe_allow_html=True)

# Kullanıcıdan Link Alma
bulten_linki = st.text_input("Bülten Linkini Buraya Yapıştırın (Örn: GanyanTime veya Hipodrom bülten linki):")

if st.button("LİNKİ ANALİZ ET"):
    if bulten_linki:
        with st.spinner('Linkteki veriler taranıyor...'):
            df = linkten_veri_cek(bulten_linki)
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                st.success("✅ Veriler linkten başarıyla çekildi!")
                st.dataframe(df.sort_values(by="HANDİKAP", ascending=False), use_container_width=True, hide_index=True)
                
                fav = df.sort_values(by="HANDİKAP", ascending=False).iloc[0]
                st.info(f"🏆 **Analiz Sonucu Favori:** {fav['AT ADI']} (%{fav['B.ADAM PUANI']})")
            else:
                st.error("Linkten veri çekilemedi. Site bot koruması kullanıyor olabilir.")
    else:
        st.warning("Lütfen bir link girin.")

st.sidebar.info("Bu sürüm verdiğiniz URL üzerinden otomatik tarama yapar.")
