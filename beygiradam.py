import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | CANLI", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .header-style { color: #FF8C00; font-size: 30px; font-weight: bold; text-align: center; border-bottom: 3px solid #FF8C00; padding-bottom: 10px; }
    .kosu-card { background-color: #1e1e1e; padding: 15px; border-radius: 12px; border-left: 10px solid #FF8C00; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- TJK-API GERÇEK BAĞLANTI MOTORU ---
def veri_cek_kesin(sehir_adi):
    # README'deki tarih formatı: dd-mm-yyyy
    today = datetime.now().strftime("%d-%m-%Y")
    url = f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{today}"
    
    # TJK'nın "Sen botsun" dememesi için gereken gerçek kullanıcı kimliği
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://online.tjk.org",
        "Referer": "https://online.tjk.org/at-yarisi-programi"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Şehir ismini her türlü ihtimale karşı (Büyük/Küçük harf) eşleştir
            return [race for race in data if sehir_adi.upper() in race.get('raceCityName', '').upper()]
        return "HATA: Sunucu yanıt vermedi (Kod: " + str(response.status_code) + ")"
    except Exception as e:
        return "HATA: Bağlantı koptu (" + str(e) + ")"

# --- ANA EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v36.0 (KESİN BAĞLANTI)</div>', unsafe_allow_html=True)

st.sidebar.header("📍 Yarış Seçimi")
cities = ["ADANA", "ANTALYA", "İSTANBUL", "BURSA", "İZMİR", "ŞANLIURFA", "KOCAELİ"]
selected_city = st.sidebar.selectbox("Şehir Seçin", cities)

if st.sidebar.button("🚀 ANALİZLERİ GETİR"):
    with st.spinner(f"{selected_city} bülteni TJK servislerinden canlı çekiliyor..."):
        races = veri_cek_kesin(selected_city)
        
        if isinstance(races, list) and len(races) > 0:
            st.success(f"✅ {selected_city} Yarışları Başarıyla Yüklendi!")
            for race in races:
                race_no = race.get('raceNumber')
                st.markdown(f'<div class="kosu-card">🏁 {selected_city} - {race_no}. KOŞU</div>', unsafe_allow_html=True)
                
                entries = race.get('raceEntries', [])
                if entries:
                    rows = []
                    for e in entries:
                        hp = e.get('handicapScore', 0) or 0
                        rows.append({
                            "At Adı": e.get('horseName'),
                            "Jokey": e.get('jockeyName'),
                            "Kilo": e.get('weight'),
                            "HP": hp,
                            "B.Adam Skoru": f"%{min(int(hp * 0.7 + 15), 99)}" if hp > 0 else "%--"
                        })
                    
                    df = pd.DataFrame(rows).sort_values(by="HP", ascending=False)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.info(f"🏆 Favori: {df.iloc[0]['At Adı']}")
                st.divider()
        else:
            st.error(f"⚠️ {selected_city} için şu an veri alınamıyor. Hata: {races}")
            st.warning("Eğer Adana'da yarış olduğundan eminseniz, TJK sunucusu Streamlit erişimini kısıtlamış olabilir.")
