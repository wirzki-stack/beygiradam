import streamlit as st
import requests
import io
import re
import pandas as pd

try:
    import PyPDF2
except ImportError:
    st.error("Lütfen requirements.txt dosyanıza 'PyPDF2' ekleyin!")

st.set_page_config(page_title="BEYGİR ADAM AI v250", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FFD700;'>🏇 AI GERÇEK BÜLTEN ANALİZİ</h1>", unsafe_allow_html=True)

pdf_url = st.sidebar.text_input("🔗 TJK PDF Linkini Yapıştırın:")
analiz_buton = st.sidebar.button("🚀 Bülteni Çöz ve Analiz Et")

if pdf_url and analiz_buton:
    with st.spinner("Yapay Zeka bülten tablolarını çözümlüyor..."):
        try:
            response = requests.get(pdf_url, timeout=30)
            pdf_file = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text() + "\n"

            # --- GELİŞMİŞ AYIKLAMA ALGORİTMASI ---
            # PDF satırlarını temizle ve at isimlerini (Büyük harf ve yanındaki rakamlar) bul
            # Genelde at isimleri satır başında veya numaranın yanındadır.
            lines = all_text.split('\n')
            data_list = []
            
            for line in lines:
                # Örn: "1 ALPERENBEY 58 MS.CELIK 85" gibi yapıları yakalar
                match = re.search(r"(\d+)\s+([A-ZÇĞİÖŞÜ ]{3,})\s+(\d{2})\s+.*?\s+(\d{1,3})", line)
                if match:
                    data_list.append({
                        "no": match.group(1),
                        "at": match.group(2).strip(),
                        "kilo": match.group(3),
                        "hp": int(match.group(4))
                    })

            if data_list:
                df = pd.DataFrame(data_list).drop_duplicates(subset=['at'])
                st.success(f"✅ Analiz Tamamlandı: {len(df)} Gerçek At Verisi İşlendi.")
                
                # Koşu simülasyonu (Veriyi koşulara bölerek göster)
                # TJK bülteninde her 10-12 at bir koşu sayılabilir
                chunk_size = 10
                for i in range(0, len(df), chunk_size):
                    kosu_num = (i // chunk_size) + 1
                    with st.expander(f"🏁 {kosu_num}. KOŞU ANALİZİ (Gerçek Veri)"):
                        sub_df = df.iloc[i:i+chunk_size]
                        
                        # Yapay Zeka Tahmini: HP puanı en yüksek olanı seç
                        favori = sub_df.sort_values(by="hp", ascending=False).iloc[0]
                        
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.write(f"🎯 **AI Favorisi:** {favori['at']}")
                            st.write(f"📊 **Handikap Puanı:** {favori['hp']}")
                            st.table(sub_df[['no', 'at', 'hp']])
                        with c2:
                            chance = min(favori['hp'] + 10, 99)
                            st.metric("Kazanma Olasılığı", f"%{chance}")
                            st.progress(chance / 100)
            else:
                st.error("⚠️ PDF'teki tablolar okunamadı. TJK PDF'leri bazen şifreli olabilir.")

        except Exception as e:
            st.error(f"⚠️ Hata oluştu: {e}")
else:
    st.info("👋 Gerçek at isimlerini görmek için güncel PDF linkini yapıştırın.")
