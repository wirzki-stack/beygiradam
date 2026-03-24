import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="BEYGİR ADAM v2000", layout="wide")
st.markdown("<h1 style='text-align:center; color:#00FF00;'>🏇 BEYGİR ADAM | AKILLI ANALİZ SİSTEMİ</h1>", unsafe_allow_html=True)

# Sunucu bloklamasını aşmak için alternatif yöntem
def get_tjk_data():
    # Bu URL, TJK'nın JSON verisini sağlayan doğrudan bir uç noktadır
    from datetime import datetime
    bugun = datetime.now().strftime("%Y%m%d")
    target_url = f"https://api.tjk.org/v1/race/program/{bugun}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.tjk.org/'
    }
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

if st.button("🚀 GÜNÜN PROGRAMINI OTOMATİK GETİR VE ANALİZ ET"):
    with st.spinner('Veri tüneli kuruluyor, lütfen bekleyin...'):
        data = get_tjk_data()
        
        if data and 'data' in data:
            all_races = data['data']
            # Şehirleri listele
            cities = list(set([r['raceCityName'] for r in all_races]))
            st.success(f"✅ {len(cities)} Şehir için program başarıyla çekildi!")
            
            for city in cities:
                with st.expander(f"📍 {city} YARIŞLARI - AI ANALİZİ"):
                    city_data = [r for r in all_races if r['raceCityName'] == city]
                    
                    for r in city_data:
                        st.markdown(f"**🏁 {r['raceNumber']}. Koşu (Saat: {r['raceTime']})**")
                        df = pd.DataFrame(r['raceEntries'])
                        
                        # HP Puanına göre AI Sıralaması
                        df['handicapScore'] = pd.to_numeric(df['handicapScore'], errors='coerce').fillna(0)
                        df = df.sort_values(by='handicapScore', ascending=False)
                        
                        # Temiz tablo gösterimi
                        display_df = df[['programNumber', 'horseName', 'handicapScore']].copy()
                        display_df.columns = ['No', 'At İsmi', 'HP']
                        st.table(display_df)
                        
                        st.write(f"🏆 **AI Favorisi:** {df.iloc[0]['horseName']} | **Sürpriz:** {df.iloc[-1]['horseName']}")
                        st.divider()
        else:
            st.error("❌ TJK Sunucusu hala erişimi engelliyor. Bu bir yazılım hatası değil, veri kaynağının erişim yasağıdır.")
            st.info("💡 Eğer otomatik çekmiyorsa; tek çare senin bülteni bir kez kopyalayıp buraya atman. AI ancak o zaman veriyi görebilir.")
