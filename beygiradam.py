import streamlit as st

st.set_page_config(page_title="BEYGİR ADAM v120", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🏇 BEYGİR ADAM | PDF GÖSTERİCİ</h1>", unsafe_allow_html=True)

# Manuel Link Girişi
st.sidebar.header("📥 Bülten Yükle")
pdf_url = st.sidebar.text_input(
    "TJK PDF Linkini Buraya Yapıştırın:", 
    placeholder="https://medya-cdn.tjk.org/...pdf"
)

if pdf_url:
    if pdf_url.endswith(".pdf"):
        st.success("✅ PDF Bağlantısı Kuruldu!")
        
        # PDF'i tam ekran iframe olarak göster
        pdf_display = f'<iframe src="{pdf_url}" width="100%" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        # İndirme Butonu
        st.sidebar.markdown(f"### [📥 Dosyayı İndir]({pdf_url})")
    else:
        st.sidebar.error("❌ Lütfen sonu '.pdf' ile biten geçerli bir link girin.")
else:
    st.info("👋 Hoş geldiniz! TJK sitesinden bülten PDF linkini kopyalayıp sol tarafa yapıştırın, bülteniniz burada anında açılsın.")
    
    st.markdown("""
    ### 💡 Linki Nasıl Alırsınız?
    1. [TJK Günlük Program](https://www.tjk.org/TR/YarisSever/Info/Page/GunlukYarisProgrami) sayfasına gidin.
    2. İstediğiniz şehrin yanındaki **PDF** ikonuna sağ tıklayın.
    3. **"Bağlantıyı Kopyala"** (Copy Link Address) seçeneğine basın.
    4. Buradaki kutuya yapıştırın.
    """)
