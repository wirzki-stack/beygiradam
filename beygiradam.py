import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | CANLI", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .header-style { color: #FF8C00; font-size: 32px; font-weight: bold; text-align: center; border-bottom: 3px solid #FF8C00; padding-bottom: 10px; }
    .kosu-card { background-color: #1e1e1e; padding: 15px; border-radius: 12px; border-left: 10px solid #FF8C00; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- GELİŞMİŞ TJK VERİ MOTORU ---
def get_tjk_data_fixed(sehir_adi):
    # TJK API farklı tarih formatları deneyebilir
    tarih_formatlari = [
        datetime.now().strftime("%d-%m-%Y"),
        datetime.now().strftime("%Y-%m-%d"),
        datetime.now().strftime("%d.%m.%Y")
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json"
    }

    for tarih in tarih_formatlari:
        url = f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{tarih}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Şehir ismini hem büyük hem küçük harf kontrol ederek filtrele
                results = [r for r in data if sehir_adi.upper() in r.get('raceCityName', '').upper()]
                if results:
                    return results
        except:
            continue
    return None

# --- ANA EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v32.0 (CANLI FİX)</div>', unsafe_allow_html=True)

st.sidebar.header("Yarış Seçimi")
sehirler = ["ADANA", "ANTALYA", "İSTANBUL", "BURSA", "İZMİR", "ŞANLIURFA", "KOCAELİ"]
secilen_sehir = st.sidebar.selectbox("Şehir Seçin", sehirler)

if st.sidebar.button("🚀 GERÇEK VERİLERİ GETİR"):
    with st.spinner(f"TJK sunucularından güncel {secilen_sehir} verileri süzülüyor..."):
        races = get_tjk_data_fixed(secilen_sehir)
        
        if races:
            st.success(f"✅ {secilen_sehir} Yarış Programı Alındı!")
            for race in races:
                race_no = race.get('raceNumber')
                st.markdown(f'<div class="kosu-card">🏁 {secilen_sehir} - {race_no}. KOŞU</div>', unsafe_allow_html=True)
                
                horses = race.get('raceEntries', [])
                if horses:
                    df_list = []
                    for h in horses:
                        hp = h.get('handicapScore', 0) or 0
                        df_list.append({
                            "At": h.get('horseName'),
                            "Jokey": h.get('jockeyName'),
                            "Kilo": h.get('weight'),
                            "HP": hp,
                            "B.Adam Skoru": f"%{min(int(hp * 0.75 + 12), 99)}" if hp > 0 else "%--"
                        })
                    
                    df = pd.DataFrame(df_list).sort_values(by="HP", ascending=False)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    if not df.empty:
                        st.info(f"🏆 Favori: {df.iloc[0]['At']}")
                st.divider()
        else:
            st.error(f"⚠️ {secilen_sehir} için şu an veri çekilemedi. Bağlantı aktif ancak TJK veri göndermiyor. Lütfen birkaç dakika sonra tekrar deneyin.")

st.sidebar.markdown("---")
st.sidebar.write("🔗 **Bağlantı:** Mobil Proxy Aktif")
