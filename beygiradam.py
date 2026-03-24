import streamlit as st
import pandas as pd
import json
from fpdf import FPDF
import io

st.set_page_config(page_title="BEYGİR ADAM PDF v100", layout="wide")
st.title("🏇 BEYGİR ADAM | PDF BÜLTEN")

# Manuel Veri Girişi
manuel_json = st.sidebar.text_area("JSON Verisini Buraya Yapıştırın:", height=200)

if manuel_json:
    try:
        data = json.loads(manuel_json)
        if isinstance(data, dict): data = data.get('data', [])
        
        # Şehir Seçimi
        cities = sorted(list(set([r.get('raceCityName') for r in data if r.get('raceCityName')])))
        selected_city = st.selectbox("📍 Şehir Seçin", cities)
        
        city_races = [r for r in data if r.get('raceCityName') == selected_city]

        # PDF OLUŞTURMA FONKSİYONU
        def create_pdf(city_name, races):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, f"{city_name} YARIS BULTENI", ln=True, align="C")
            pdf.ln(10)

            for r in races:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, f"{r['raceNumber']}. Kosu - Saat: {r['raceTime']}", ln=True)
                pdf.set_font("Arial", "", 10)
                
                # Tablo Başlıkları
                pdf.cell(10, 8, "No", 1)
                pdf.cell(60, 8, "At Adi", 1)
                pdf.cell(60, 8, "Jokey", 1)
                pdf.cell(20, 8, "Kilo", 1)
                pdf.cell(20, 8, "HP", 1)
                pdf.ln()

                for entry in r.get('raceEntries', []):
                    pdf.cell(10, 8, str(entry.get('programNumber','')), 1)
                    pdf.cell(60, 8, str(entry.get('horseName',''))[:25], 1)
                    pdf.cell(60, 8, str(entry.get('jockeyName',''))[:25], 1)
                    pdf.cell(20, 8, str(entry.get('weight','')), 1)
                    pdf.cell(20, 8, str(entry.get('handicapScore','')), 1)
                    pdf.ln()
                pdf.ln(5)
            
            return pdf.output(dest='S').encode('latin-1')

        # PDF İndirme Butonu
        if st.button(f"📥 {selected_city} Bültenini PDF Yap"):
            pdf_bytes = create_pdf(selected_city, city_races)
            st.download_button(
                label="📄 PDF Dosyasını İndir",
                data=pdf_bytes,
                file_name=f"{selected_city}_Bulten.pdf",
                mime="application/pdf"
            )

        # Ekranda Gösterim
        for r in city_races:
            with st.expander(f"🏁 {r['raceNumber']}. Koşu - {r['raceTime']}"):
                df = pd.DataFrame(r['raceEntries'])
                st.table(df[['programNumber', 'horseName', 'jockeyName', 'weight', 'handicapScore']])
                
    except Exception as e:
        st.error(f"Hata: {e}")
else:
    st.info("Bülteni PDF'e çevirmek için JSON verisini sola yapıştırın.")
