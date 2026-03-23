import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import random

# --- TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | LİNK ANALİZ", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .header-style { color: #FF8C00; font-size: 32px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- GERÇEK LİNK OKUYUCU MOTOR ---
def linki_gercekten_oku(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        # Linke git ve sayfayı indir
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        metin = soup.get_text()
        
        # Sadece at ve handikap olabilecek satırları ayıkla
        veriler = []
        for satir in metin.split('\n'):
            satir = satir.strip()
            # Satırda "http" veya "/" varsa bu bir linktir, atla!
            if "http" in satir or "/" in satir: continue
            
            atlar = re.findall(r'[A-ZÇĞİÖŞÜ]{4,}', satir)
            sayilar = re.findall(r'\d{2,3}', satir)
            
            if atlar and sayilar:
                at_adi = atlar[0]
                hp = int(sayilar[-1])
                if 35 < hp < 125: # Gerçekçi handikap aralığı
                    veriler.append({
                        "AT ADI": at_adi,
                        "HANDİKAP": hp,
                        "B.ADAM PUANI": f"%{min(int(hp * 0.7 + 10), 99)}"
                    })
        return pd.DataFrame(veriler).drop_duplicates(subset=['AT ADI'])
    except:
        return None

# --- ARAYÜZ ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v25.0</div>', unsafe_allow_html=True)

# Kutuya link girilecek
input_data = st.text_input("Bülten Linkini (URL) veya Metni Buraya Girin:")

if st.button("📊 ANALİZİ BAŞLAT"):
    if input_data:
        # Eğer girilen şey bir link ise (http içeriyorsa)
        if "http" in input_data:
            with st.spinner('Linkteki veriler sökülüyor...'):
                df = linki_gercekten_oku(input_data)
        else:
            # Eğer düz metin ise (v24'teki mantık)
            st.error("Lütfen bir bülten sitesi linki girin veya metni PDF'den kopyalayıp yapıştırın.")
            df = None
            
        if df is not None and not df.empty:
            st.dataframe(df.sort_values(by="HANDİKAP", ascending=False), use_container_width=True, hide_index=True)
            st.success(f"🏆 Favori: {df.iloc[0]['AT ADI']}")
        else:
            st.error("Veri çekilemedi. Link engellenmiş veya hatalı.")
