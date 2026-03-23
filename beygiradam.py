import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | KESİN ÇÖZÜM", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .header-style { color: #FF8C00; font-size: 30px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- AKILLI LİNK AYIKLAYICI ---
def veriyi_süz(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Sitenin içindeki tabloyu yakala
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # Karmaşık harfleri engellemek için sadece At ve HP kalıbına odaklan
        raw_text = soup.get_text()
        lines = raw_text.split('\n')
        
        final_data = []
        for line in lines:
            # Sadece Büyük Harf (At) ve yanındaki Sayıyı (HP) yakala
            horse = re.search(r'([A-ZÇĞİÖŞÜ]{4,})', line)
            score = re.findall(r'\d{2,3}', line)
            
            if horse and score:
                hp_val = int(score[-1])
                if 30 < hp_val < 130: # Mantıklı Handikap aralığı
                    final_data.append({
                        "AT ADI": horse.group(1),
                        "HANDİKAP": hp_val,
                        "B.ADAM PUANI": min(int(hp_val * 0.7 + 15), 99)
                    })
        return pd.DataFrame(final_data).drop_duplicates(subset=['AT ADI'])
    except:
        return None

# --- EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v23.0</div>', unsafe_allow_html=True)

target_url = st.text_input("Bülten Linkini Buraya Yapıştırın:", placeholder="https://www.ganyantime.com/at-yarisi-bulteni/")

if st.button("ANALİZ ET"):
    if target_url:
        # Eğer PDF linki atılırsa uyar
        if ".pdf" in target_url:
            st.error("⚠️ PDF linkleri doğrudan okunamaz. Lütfen bir web sayfası (HTML) bülten linki yapıştırın.")
        else:
            df = veriyi_süz(target_url)
            if df is not None and not df.empty:
                st.dataframe(df.sort_values(by="HANDİKAP", ascending=False), use_container_width=True, hide_index=True)
                st.success(f"🏆 Favori: {df.iloc[0]['AT ADI']}")
            else:
                st.error("Veri çekilemedi. Lütfen farklı bir bülten sitesi linki deneyin.")
