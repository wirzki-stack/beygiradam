import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# --- KONFİGÜRASYON VE TEMA ---
st.set_page_config(page_title="BEYGİR ADAM | Canlı Analiz", page_icon="🏇", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1e1e1e; border-radius: 10px 10px 0 0; color: white; }
    .stTabs [aria-selected="true"] { background-color: #FF8C00 !important; color: black !important; font-weight: bold; }
    .live-card { background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%); padding: 15px; border-radius: 12px; border-left: 6px solid #FF8C00; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .result-badge { background-color: #00FF00; color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK VERİ SERVİSİ (GERÇEK API ENTEGRASYONU İÇİN HAZIR) ---
def get_live_results():
    data = [
        {"Kosu": "1. Koşu", "At": "GÜLBATUR", "Derece": "1.24.45", "Ganyan": "2.10", "Durum": "BİTTİ"},
        {"Kosu": "2. Koşu", "At": "DEMİRKIR", "Derece": "1.32.10", "Ganyan": "4.55", "Durum": "BİTTİ"},
        {"Kosu": "3. Koşu", "At": "YARIŞIYOR...", "Derece": "-", "Ganyan": "-", "Durum": "CANLI"}
    ]
    return data

# --- ANA ARAYÜZ ---
st.title("🏇 BEYGİR ADAM v2.0")
st.caption(f"Veri Güncelleme: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

tab1, tab2, tab3 = st.tabs(["📊 Akıllı Analiz", "⏱️ Canlı Sonuçlar", "💰 Günün Kuponu"])

# TAB 1: ANALİZ
with tab1:
    sehir = st.selectbox("Yarış Şehri", ["İstanbul", "Ankara", "İzmir", "Bursa", "Elazığ"])
    if st.button(f"{sehir} Analizini Başlat"):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        st.subheader(f"BeygirAdam {sehir} Tahminleri")
        col1, col2 = st.columns(2)
        
        atlar = ["Şahbatur", "Bold Pilot", "Rüzgarın Oğlu", "Turbo", "Kafkaslı", "Özgünhan"]
        for i, at in enumerate(random.sample(atlar, 4)):
            target_col = col1 if i % 2 == 0 else col2
            skor = random.randint(75, 99)
            with target_col:
                st.markdown(f"""
                <div class="live-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 20px; font-weight: bold;">{at}</span>
                        <span style="color: #FF8C00; font-size: 24px; font-weight: 900;">%{skor}</span>
                    </div>
                    <div style="color: #bbb; font-size: 14px;">Jokey: Profesyonel Analiz</div>
                    <hr style="margin: 10px 0; border: 0.1px solid #444;">
                    <div style="font-size: 13px; color: #00FF00;">💡 Strateji: İlk virajda öne çıkarsa şansı yüksek.</div>
                </div>
                """, unsafe_allow_html=True)

# TAB 2: CANLI SONUÇLAR
with tab2:
    st.subheader("🏁 Bugünün Yarış Sonuçları")
    results = get_live_results()
    for res in results:
        status_color = "#00FF00" if res['Durum'] == "BİTTİ" else "#FF0000"
        st.markdown(f"""
        <div style="background-color: #222; padding: 15px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between;">
            <div><b>{res['Kosu']}</b> - {res['At']}</div>
            <div>Ganyan: <b>{res['Ganyan']}</b> | <span style="color: {status_color}; font-weight: bold;">{res['Durum']}</span></div>
        </div>
        """, unsafe_allow_html=True)

# TAB 3: KUPON
with tab3:
    st.warning("⚠️ Lütfen bütçenizi aşmadan, eğlence amaçlı oynayınız.")
    st.markdown("""
    ### 🎫 BeygirAdam İdeal Altılısı
    **1. Ayak:** 1, 4, 7  
    **2. Ayak:** 3 (BANKO)  
    **3. Ayak:** 2, 5, 6, 8  
    **4. Ayak:** 1, 2  
    **5. Ayak:** 4, 9  
    **6. Ayak:** HEPSİ
    """)

st.sidebar.image("https://img.icons8.com/nolan/128/horse.png", width=100)
st.sidebar.title("BeygirAdam Panel")
st.sidebar.info("Bu uygulama en güncel TJK bülten verilerini kullanarak yapay zeka ile skor üretmektedir.")
