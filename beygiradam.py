import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- TASARIM ---
st.set_page_config(page_title="BEYGİR ADAM | PROFESYONEL", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .header-style { color: #FF8C00; font-size: 32px; font-weight: bold; text-align: center; border-bottom: 3px solid #FF8C00; padding-bottom: 10px; }
    .kosu-card { background-color: #1e1e1e; padding: 15px; border-radius: 12px; border-left: 10px solid #FF8C00; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- AKILLI TJK API MOTORU ---
def tjk_akilli_baglanti(sehir_adi):
    bugun = datetime.now().strftime("%d-%m-%Y")
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Referer": "https://online.tjk.org/"
    }

    # 1. ADIM: Günlük Yarış Listesini Al (TJK'nın bugün hangi şehirlerde koşu olduğunu söylediği yer)
    list_url = f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{bugun}"
    
    try:
        resp = requests.get(list_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            all_races = resp.json()
            # Seçilen şehre ait koşu kayıtlarını bul
            city_races = [r for r in all_races if sehir_adi.upper() in r.get('raceCityName', '').upper()]
            
            if not city_races:
                return f"BİLGİ: Bugün {sehir_adi} şehrinde yarış kaydı bulunamadı."
            return city_races
        else:
            return f"HATA: TJK Servis hatası (Kod: {resp.status_code})"
    except Exception as e:
        return f"HATA: Bağlantı başarısız. ({str(e)})"

# --- ARAYÜZ ---
st.markdown('<div class="header-style">🏇 BEYGİR ADAM v37.0 (Smart-API)</div>', unsafe_allow_html=True)

st.sidebar.header("📍 Yarış Seçimi")
sehirler = ["ADANA", "ANTALYA", "İZMİR", "İSTANBUL", "BURSA", "ŞANLIURFA", "KOCAELİ"]
secilen_sehir = st.sidebar.selectbox("Şehir Seçin", sehirler)

if st.sidebar.button("🚀 ANALİZLERİ GETİR"):
    with st.spinner(f"TJK servislerinden {secilen_sehir} bülteni ayıklanıyor..."):
        races = tjk_akilli_baglanti(secilen_sehir)
        
        if isinstance(races, list):
            st.success(f"✅ {secilen_sehir} için veriler başarıyla alındı!")
            for race in races:
                r_no = race.get('raceNumber')
                st.markdown(f'<div class="kosu-card">🏁 {secilen_sehir} - {r_no}. KOŞU</div>', unsafe_allow_html=True)
                
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
                            "B.Adam Skoru": f"%{min(int(hp * 0.7 + 12), 99)}" if hp > 0 else "%--"
                        })
                    
                    df = pd.DataFrame(rows).sort_values(by="HP", ascending=False)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.info(f"🏆 Favori: {df.iloc[0]['At Adı']}")
                st.divider()
        else:
            st.error(races)

st.sidebar.markdown("---")
st.sidebar.write("🔗 **Bağlantı:** TJK Smart-Proxy Aktif")
