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

# --- TJK CANLI VERİ MOTORU ---
def tjk_canli_veri_cek(sehir_adi):
    bugun = datetime.now().strftime("%d-%m-%Y")
    # TJK Resmi Mobil API Ucu
    url = f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{bugun}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Şehir bazlı filtreleme
            return [r for r in data if sehir_adi.upper() in r.get('raceCityName', '').upper()]
        return None
    except:
        return None

# --- ANA EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v34.0 (CANLI ANALİZ)</div>', unsafe_allow_html=True)

st.sidebar.header("Yarış Seçimi")
sehirler = ["ADANA", "ANTALYA", "İSTANBUL", "BURSA", "İZMİR", "ŞANLIURFA", "KOCAELİ"]
secilen_sehir = st.sidebar.selectbox("Şehir Seçin", sehirler)

if st.sidebar.button("🚀 VERİLERİ OTOMATİK GETİR"):
    with st.spinner(f"{secilen_sehir} verileri çekiliyor..."):
        races = tjk_canli_veri_cek(secilen_sehir)
        
        if races:
            for race in races:
                r_no = race.get('raceNumber')
                st.markdown(f'<div class="kosu-card">🏁 {secilen_sehir} - {r_no}. KOŞU</div>', unsafe_allow_html=True)
                
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
                            "Skor": f"%{min(int(hp * 0.7 + 15), 99)}" if hp > 0 else "%--"
                        })
                    
                    df = pd.DataFrame(df_list).sort_values(by="HP", ascending=False)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    if not df.empty:
                        st.info(f"🏆 Favori: {df.iloc[0]['At']}")
                st.divider()
        else:
            st.error(f"⚠️ {secilen_sehir} için veri alınamadı. Lütfen internet bağlantısını kontrol edip tekrar deneyin.")

st.sidebar.markdown("---")
st.sidebar.write("✅ **Durum:** API Bağlantısı Hazır")
