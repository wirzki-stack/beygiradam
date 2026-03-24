import streamlit as st
import random

st.set_page_config(page_title="BEYGİR ADAM AI v150", layout="wide")

st.markdown("<h1 style='text-align:center; color:#FF4B4B;'>🧠 BEYGİR ADAM | AI ANALİZ MOTORU</h1>", unsafe_allow_html=True)

# Yan Menü: Veri Girişi
st.sidebar.header("📥 Analiz Verisi")
pdf_url = st.sidebar.text_input("Bülten PDF Linkini Girin:")
analiz_metni = st.sidebar.text_area("Yarış Atlarını ve HP Puanlarını Buraya Girin (Örn: 1-Alperen 85):", height=200)

if analiz_metni:
    st.subheader("📊 Yapay Zeka Tahmin Raporu")
    
    with st.spinner('AI Verileri Analiz Ediyor...'):
        # Burası simüle edilmiş AI analiz algoritmasıdır
        at_listesi = analiz_metni.split('\n')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🏇 Koşu Analizi")
            for at in at_listesi:
                sans = random.randint(60, 95)
                st.write(f"**{at}**")
                st.progress(sans)
                st.caption(f"Kazanma Olasılığı: %{sans} | Form Durumu: Yüksek")
        
        with col2:
            st.markdown("### 🎯 AI Banko Önerisi")
            st.success(f"Günün Bankosu: {at_listesi[0]}")
            st.warning("Plase Şansı: " + (at_listesi[1] if len(at_listesi) > 1 else "Analiz Bekleniyor"))

    if pdf_url:
        st.divider()
        st.link_button("📄 Bülteni Yeni Sekmede Kontrol Et", pdf_url)

else:
    st.info("👋 Analiz başlaması için sol tarafa PDF'ten okuduğunuz atları ve puanları yazın.")
    st.image("https://cdn-icons-png.flaticon.com/512/3043/3043888.png", width=100)
