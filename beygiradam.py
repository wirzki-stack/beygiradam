import streamlit as st

st.set_page_config(page_title="BEYGİR ADAM v130", layout="wide")

# Tasarım Düzenlemesi
st.markdown("""
    <style>
    .main { background-color: #1e1e1e; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #FF8C00; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM | PDF PANELİ</h1>", unsafe_allow_html=True)

# Yan Menü
st.sidebar.header("📥 Bülten Ayarları")
pdf_url = st.sidebar.text_input("TJK PDF Linkini Buraya Yapıştırın:", placeholder="https://medya-cdn.tjk.org/...")

if pdf_url:
    if pdf_url.startswith("http") and pdf_url.endswith(".pdf"):
        st.success("✅ Bağlantı Tanımlandı!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Doğrudan tarayıcıda açma butonu (En güvenli yol)
            st.link_button("📄 Bülteni Yeni Sekmede Aç", pdf_url)
            
        with col2:
            # İndirme bilgisi
            st.info("💡 PDF açılmazsa yukarıdaki butona basarak yeni sekmede görüntüleyebilirsiniz.")

        # PDF Görüntüleme Denemesi (Genişletilmiş)
        st.divider()
        st.write("🔍 **Bülten Önizleme:**")
        pdf_html = f'<embed src="{pdf_url}" width="100%" height="1000" type="application/pdf">'
        st.markdown(pdf_html, unsafe_allow_html=True)
        
    else:
        st.sidebar.error("❌ Geçersiz link! Link 'https' ile başlamalı ve '.pdf' ile bitmelidir.")
else:
    st.info("👋 Başlamak için TJK sitesinden kopyaladığınız PDF linkini sol menüye yapıştırın.")
    st.image("https://www.tjk.org/TR/YarisSever/Static/Images/logo.png", width=100)
