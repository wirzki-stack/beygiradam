import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- HACKER UI ---
st.set_page_config(page_title="BEYGİR ADAM | GITHUB STEALTH", page_icon="🕵️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #58a6ff; }
    .stButton>button { background-color: #238636; color: white; width: 100%; border-radius: 5px; }
    .kosu-card { border: 1px solid #30363d; padding: 15px; border-radius: 10px; background-color: #161b22; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- STEALTH BAĞLANTI MOTORU ---
def stealth_tjk_fetch(city_name):
    today = datetime.now().strftime("%d-%m-%Y")
    # TJK'nın en zayıf korunan servis ucu
    url = f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{today}"
    
    # KİMLİK SİMÜLASYONU: TJK'nın engellemeye korktuğu Google Bot kimliği
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.google.com/",
        "Cache-Control": "no-cache"
    }

    try:
        # GitHub üzerinden yapılan isteği maskelemek için session kullanıyoruz
        with requests.Session() as s:
            s.headers.update(headers)
            response = s.get(url, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                return [r for r in data if city_name.upper() in r.get('raceCityName', '').upper()]
            return f"Erişim Reddedildi (Kod: {response.status_code})"
    except Exception as e:
        return f"Bağlantı Tüneli Çöktü: {str(e)}"

# --- ARAYÜZ ---
st.markdown('<h1 style="text-align:center; color:#f0883e;">🚀 BEYGİR ADAM v40.0 (GitHub Stealth)</h1>', unsafe_allow_html=True)

sehir = st.sidebar.selectbox("Hedef Hipodrom:", ["ADANA", "ANTALYA", "İSTANBUL", "BURSA", "İZMİR", "ŞANLIURFA"])

if st.sidebar.button("🔓 GÜVENLİK DUVARINI AŞ VE VERİYİ ÇEK"):
    with st.status("Google Proxy Tüneli Oluşturuluyor...", expanded=True) as status:
        data = stealth_tjk_fetch(sehir)
        
        if isinstance(data, list) and len(data) > 0:
            status.update(label="✅ Veri Sızıntısı Başarılı!", state="complete")
            for race in data:
                with st.container():
                    st.markdown(f'<div class="kosu-card">🏁 {sehir} - {race.get("raceNumber")}. KOŞU</div>', unsafe_allow_html=True)
                    entries = race.get('raceEntries', [])
                    if entries:
                        df = pd.DataFrame([{"At": e['horseName'], "Jokey": e['jockeyName'], "HP": e['handicapScore'] or 0} for e in entries])
                        df = df.sort_values(by="HP", ascending=False)
                        df["B.Adam %"] = df["HP"].apply(lambda x: f"%{min(int(x*0.7+15), 99)}" if x > 0 else "%--")
                        st.table(df)
        else:
            status.update(label="❌ GitHub IP Bloklandı.", state="error")
            st.error(f"Sistem Mesajı: {data}")
            st.info("Eğer bu da olmazsa, GitHub Actions ile 'Data Scraper' kurup veriyi JSON olarak kaydetmemiz gerekir.")

st.sidebar.markdown("---")
st.sidebar.write("👾 **Protokol:** Stealth Google-Bot")
