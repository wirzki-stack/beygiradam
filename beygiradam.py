import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | TJK API", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .header-style { color: #FF8C00; font-size: 30px; font-weight: bold; text-align: center; border-bottom: 3px solid #FF8C00; padding-bottom: 10px; }
    .kosu-card { background-color: #1e1e1e; padding: 15px; border-radius: 12px; border-left: 10px solid #FF8C00; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- TJK-API README ENTEGRASYONU ---
def tjk_api_get_data(city_name):
    # README'de belirtilen tarih formatı: dd-mm-yyyy
    today = datetime.now().strftime("%d-%m-%Y")
    
    # README'de belirtilen ana endpoint
    url = f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{today}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # README'deki veri yapısına göre şehir filtresi (raceCityName)
            filtered_data = [race for race in data if city_name.upper() in race.get('raceCityName', '').upper()]
            return filtered_data
        return None
    except Exception as e:
        return None

# --- ANA EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v35.0 (TJK-API)</div>', unsafe_allow_html=True)

st.sidebar.header("📍 Yarış Seçimi")
cities = ["ADANA", "ANTALYA", "İSTANBUL", "BURSA", "İZMİR", "ŞANLIURFA", "KOCAELİ"]
selected_city = st.sidebar.selectbox("Şehir Seçin", cities)

if st.sidebar.button("🚀 VERİLERİ ÇEK VE ANALİZ ET"):
    with st.spinner(f"TJK-API üzerinden {selected_city} verileri çekiliyor..."):
        races = tjk_api_get_data(selected_city)
        
        if races:
            st.success(f"✅ {selected_city} için {len(races)} koşu bulundu.")
            for race in races:
                race_no = race.get('raceNumber')
                st.markdown(f'<div class="kosu-card">🏁 {selected_city} - {race_no}. KOŞU</div>', unsafe_allow_html=True)
                
                # README'deki entry yapısı (raceEntries)
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
                st.divider()
        else:
            st.error("⚠️ TJK-API şu an yanıt vermiyor veya bu şehirde bugün yarış yok.")

st.sidebar.markdown("---")
st.sidebar.write("✅ **Kaynak:** `SezerFidanci/TJK-API` altyapısı")
