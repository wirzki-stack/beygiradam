import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime

# --- HACKER STYLE UI ---
st.set_page_config(page_title="BEYGİR ADAM | BYPASS", page_icon="🕵️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF00; }
    .header-style { color: #FF8C00; font-family: 'Courier New'; text-align: center; border-bottom: 2px solid #00FF00; }
    .stDataFrame { border: 1px solid #00FF00; }
    .kosu-box { border: 1px solid #FF8C00; padding: 10px; margin: 10px 0; background: #111; }
    </style>
    """, unsafe_allow_html=True)

# --- BYPASS MOTORU ---
def bypass_tjk_security(city_name):
    # Bugünün tarihi
    today = datetime.now().strftime("%d-%m-%Y")
    
    # SIZMA PROTOKOLÜ: TJK'nın mobil uygulama gibi görünmesini sağlayan imza
    endpoints = [
        f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{today}",
        f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{datetime.now().strftime('%Y-%m-%d')}"
    ]
    
    # Gerçek bir mobil cihazın parmak izi
    headers = {
        "User-Agent": "TJK Mobil/3.2.1 (iPhone; iOS 16.5; Scale/3.00)",
        "X-Requested-With": "com.tjk.tjk_mobil",
        "Accept": "application/json",
        "Host": "online.tjk.org",
        "Connection": "keep-alive"
    }

    for url in endpoints:
        try:
            # Oturum simülasyonu
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                results = [r for r in data if city_name.upper() in r.get('raceCityName', '').upper()]
                if results: return results
            elif response.status_code == 404:
                continue # Diğer formatı dene
        except:
            continue
    
    return None

# --- UI ---
st.markdown('<h1 class="header-style">🕵️ BEYGİR ADAM v38.0 (BYPASS MODE)</h1>', unsafe_allow_html=True)

st.sidebar.warning("⚡ SIZMA PROTOKOLÜ AKTİF")
secilen_sehir = st.sidebar.selectbox("Hedef Şehir:", ["ADANA", "ANTALYA", "İZMİR", "İSTANBUL", "BURSA"])

if st.sidebar.button("🔓 SİSTEME SIZ VE VERİYİ ÇEK"):
    with st.status("TJK Güvenlik Duvarı Aşılıyor...", expanded=True) as status:
        st.write("🛰️ Proxy tünelleri oluşturuluyor...")
        data = bypass_tjk_security(secilen_sehir)
        
        if data:
            status.update(label="✅ Sızma Başarılı! Veriler Alındı.", state="complete")
            for race in data:
                with st.container():
                    st.markdown(f'<div class="kosu-box">🏁 {secilen_sehir} - KOŞU {race.get("raceNumber")}</div>', unsafe_allow_html=True)
                    horses = race.get('raceEntries', [])
                    if horses:
                        rows = [{"At": h['horseName'], "Jokey": h['jockeyName'], "HP": h['handicapScore'] or 0} for h in horses]
                        df = pd.DataFrame(rows).sort_values(by="HP", ascending=False)
                        df["Skor"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                        st.table(df) # DataFrame yerine daha basit Table (Hata riskini azaltır)
        else:
            status.update(label="❌ Güvenlik Duvarı Aşılamadı.", state="error")
            st.error("TJK bulut erişimini tamamen blokladı. Son çare: 'Local Tunnel' yöntemi.")
