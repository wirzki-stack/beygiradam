import streamlit as st

st.set_page_config(page_title="BEYGİR ADAM PDF v110", layout="wide")
st.title("🏇 BEYGİR ADAM | PDF BÜLTEN MERKEZİ")

st.info("TJK'nın resmi PDF bültenlerini aşağıdan seçerek anında görüntüleyebilirsiniz.")

# Güncel PDF Linkleri (TJK'nın günlük link yapısı)
import datetime
bugun = datetime.datetime.now().strftime("%d.%m.%Y")

pdf_listesi = {
    "Adana Bülteni": f"https://medya-cdn.tjk.org/raportfp/TJKPDF/2026/2026-03-24/PDFOzet/GunlukYarisProgrami/24.03.2026-Adana-GunlukYarisProgrami-TR.pdf",
    "İstanbul Bülteni": f"https://medya-cdn.tjk.org/raportfp/TJKPDF/2026/2026-03-24/PDFOzet/GunlukYarisProgrami/24.03.2026-Istanbul-GunlukYarisProgrami-TR.pdf",
    "Antalya Bülteni": f"https://medya-cdn.tjk.org/raportfp/TJKPDF/2026/2026-03-24/PDFOzet/GunlukYarisProgrami/24.03.2026-Antalya-GunlukYarisProgrami-TR.pdf"
}

secim = st.selectbox("📍 Görüntülemek İstediğiniz Bülteni Seçin", list(pdf_listesi.keys()))

if secim:
    url = pdf_listesi[secim]
    st.markdown(f"### 📄 {secim} ({bugun})")
    
    # PDF'i sayfa içinde gösterme (iframe)
    pdf_display = f'<iframe src="{url}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    
    # İndirme butonu
    st.markdown(f'[📥 Bilgisayara İndir (TJK Sunucusu)]({url})')
