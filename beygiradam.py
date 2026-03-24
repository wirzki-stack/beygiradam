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

# --- GERÇEK TJK VERİ MOTORU ---
def get_tjk_data(sehir_id):
    bugun = datetime.now().strftime("%d-%m-%Y")
    # TJK Resmi Proxy API ucu (GitHub README'den alınan mantık)
    url = f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{bugun}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            full_data = response.json()
            # Seçilen şehre ait koşuları filtrele
            sehir_kosulari = [r for r in full_data if r.get('raceCityName') == sehir_id]
            return sehir_kosulari
        return None
    except:
        return None

# --- ANA EKRAN ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v31.0 (CANLI VERİ)</div>', unsafe_allow_html=True)

st.sidebar.header("Yarış Seçimi")
sehirler = ["Adana", "Antalya", "İstanbul", "Bursa", "İzmir", "Şanlıurfa", "Kocaeli"]
secilen_sehir = st.sidebar.selectbox("Şehir Seçin", sehirler)

if st.sidebar.button("🚀 GERÇEK VERİLERİ GETİR"):
    with st.spinner(f"TJK sunucularından {secilen_sehir} verileri çekiliyor..."):
        races = get_tjk_data(secilen_sehir)
        
        if races:
            for race in races:
                race_no = race.get('raceNumber')
                st.markdown(f'<div class="kosu-card">🏁 {secilen_sehir.upper()} - {race_no}. KOŞU</div>', unsafe_allow_html=True)
                
                # At listesini çıkar
                horses = race.get('raceEntries', [])
                if horses:
                    df_list = []
                    for h in horses:
                        hp = h.get('handicapScore', 0)
                        df_list.append({
                            "At": h.get('horseName'),
                            "Jokey": h.get('jockeyName'),
                            "Kilo": h.get('weight'),
                            "HP": hp,
                            "Skor": f"%{min(int(hp * 0.75 + 10), 99)}" if hp > 0 else "%--"
                        })
                    
                    df = pd.DataFrame(df_list).sort_values(by="HP", ascending=False)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Favori belirle
                    if not df.empty:
                        st.success(f"🏆 Favori: {df.iloc[0]['At']}")
                st.divider()
        else:
            st.error("Şu an TJK servisinden veri çekilemiyor veya bu şehirde bugün yarış yok.")

st.sidebar.markdown("---")
st.sidebar.write("✅ **Bağlantı Durumu:** Canlı (TJK-API)")
