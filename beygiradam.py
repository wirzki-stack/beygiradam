import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BEYGİR ADAM v900", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏇 BEYGİR ADAM | TAM OTOMATİK SİSTEM</h1>", unsafe_allow_html=True)

# 1. Otomatik Tarih Belirleme
bugun = datetime.now().strftime("%Y%m%d")
url = f"https://api.tjk.org/v1/race/program/{bugun}"

if st.button("🔄 GÜNÜN TÜM BÜLTENLERİNİ ÇEK VE ANALİZ ET"):
    with st.spinner('TJK Sunucularından veriler alınıyor...'):
        try:
            # TJK API'sine istek gönder
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Şehirleri bul
                races = data.get('data', [])
                if races:
                    cities = sorted(list(set([r['raceCityName'] for r in races])))
                    selected_city = st.selectbox("📍 Şehir Seçin", cities)
                    
                    city_races = [r for r in races if r['raceCityName'] == selected_city]
                    
                    for r in city_races:
                        with st.expander(f"🏁 {r['raceNumber']}. KOŞU (Saat: {r['raceTime']})"):
                            # Atları DataFrame'e çevir
                            entries = r.get('raceEntries', [])
                            df = pd.DataFrame(entries)
                            
                            # Analiz için gerekli sütunları temizle ve sırala
                            if not df.empty:
                                df['handicapScore'] = pd.to_numeric(df['handicapScore'], errors='coerce').fillna(0)
                                df = df.sort_values(by='handicapScore', ascending=False)
                                
                                c1, c2 = st.columns([2, 1])
                                with c1:
                                    st.write("**📊 AI Olasılık Sıralaması:**")
                                    st.table(df[['programNumber', 'horseName', 'handicapScore']])
                                with c2:
                                    st.metric("🏆 BANKO", df.iloc[0]['horseName'])
                                    st.write(f"🥈 Plase: {df.iloc[1]['horseName'] if len(df)>1 else '-'}")
                else:
                    st.error("Bugün için bülten verisi bulunamadı.")
            else:
                st.error(f"TJK Sunucusu yanıt vermedi (Hata: {response.status_code}). Lütfen 5 dk sonra tekrar deneyin.")
        
        except Exception as e:
            st.error(f"Sistemsel Hata: {e}")
            st.info("💡 Not: TJK sunucusu bazen botları engeller. Bu durumda sayfayı yenileyip tekrar deneyebilirsiniz.")
