import streamlit as st
import pandas as pd

st.set_page_config(page_title="BEYGİR ADAM AI v300", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF4B4B;'>🏇 BEYGİR ADAM | AKILLI ANALİZ</h1>", unsafe_allow_html=True)

# Yan Menü
st.sidebar.header("📊 Veri Girişi")
st.sidebar.info("PDF'ten gördüğünüz At No ve Puanları (HP) aralarında boşluk bırakarak yazın.")

# Her ayak için giriş kutuları
tahminler = {}
for i in range(1, 7):
    tahminler[i] = st.sidebar.text_input(f"{i}. Ayak (Örn: 1 85, 2 74, 5 90):", key=f"ayak_{i}")

if st.sidebar.button("🚀 Altılıyı Analiz Et"):
    st.success("✅ Analiz Tamamlandı! İşte Yapay Zeka Sıralaması:")
    
    cols = st.columns(3) # 2 satırda 3'er kolon (Toplam 6 ayak)
    for i in range(1, 7):
        with cols[(i-1)%3]:
            st.markdown(f"### 🏁 {i}. AYAK")
            data = tahminler[i]
            if data:
                try:
                    # Girişi işle: "1 85, 2 74" -> Listeye çevir
                    items = [x.strip().split() for x in data.split(',')]
                    df = pd.DataFrame(items, columns=['No', 'HP'])
                    df['HP'] = pd.to_numeric(df['HP'])
                    
                    # Sırala ve Olasılık Hesapla
                    df = df.sort_values(by='HP', ascending=False)
                    toplam = df['HP'].sum()
                    df['Şans %'] = df['HP'].apply(lambda x: round((x/toplam)*100, 1))
                    
                    st.table(df[['No', 'Şans %']])
                    st.write(f"🏆 **Banko:** {df.iloc[0]['No']} Numara")
                except:
                    st.error("Hatalı format! (Örn: 1 85, 2 70)")
            else:
                st.write("Veri girilmedi.")
else:
    st.info("👋 Başlamak için sol taraftaki kutulara PDF'ten okuduğunuz at numaralarını ve puanlarını yazıp butona basın.")
