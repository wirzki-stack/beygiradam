import streamlit as st
import json, requests, csv, io, re, time
from datetime import datetime, timedelta

st.set_page_config(page_title="🏇 BeygiRadam", page_icon="🏇", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
:root{--gold:#D4A843;--gold-dim:#8B6914;--bg:#0A0B0D;--bg2:#111318;--bg3:#1A1D25;--border:#252830;--text:#E8E9EC;--muted:#5A5E6B;--blue:#3B82F6;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background-color:var(--bg)!important;color:var(--text)!important;}
.stApp{background-color:var(--bg)!important;}
.hero{background:linear-gradient(135deg,#0A0B0D,#151820,#0A0B0D);border:1px solid var(--border);border-top:3px solid var(--gold);border-radius:12px;padding:2rem 2.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden;}
.hero::before{content:'🏇';position:absolute;right:2rem;top:50%;transform:translateY(-50%);font-size:5rem;opacity:0.07;}
.hero h1{font-family:'Bebas Neue',sans-serif;font-size:3rem;letter-spacing:4px;color:var(--gold);margin:0;line-height:1;}
.hero p{color:var(--muted);margin:0.4rem 0 0;font-size:0.9rem;}
.stat-box{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:1rem;text-align:center;}
.stat-val{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:var(--gold);line-height:1;}
.stat-lbl{font-size:0.75rem;color:var(--muted);margin-top:0.2rem;}
.at-row{display:flex;align-items:center;padding:0.45rem 0;border-bottom:1px solid var(--border);gap:0.8rem;}
.at-no{font-family:'DM Mono',monospace;color:var(--muted);font-size:0.82rem;width:26px;text-align:center;}
.at-name{font-weight:500;flex:1;font-size:0.88rem;}
.at-jokey{font-size:0.75rem;color:var(--muted);min-width:90px;}
.at-hp{font-family:'DM Mono',monospace;font-size:0.82rem;}
.at-form{font-family:'DM Mono',monospace;font-size:0.75rem;color:var(--muted);min-width:70px;}
.ai-box{background:linear-gradient(135deg,#0D1117,#111827);border:1px solid #1E3A5F;border-left:3px solid var(--blue);border-radius:8px;padding:1rem 1.2rem;font-size:0.87rem;line-height:1.75;color:#CBD5E1;white-space:pre-wrap;}
.info-strip{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:0.8rem 1rem;font-size:0.82rem;color:var(--muted);margin-bottom:1rem;}
.date-chip{display:inline-block;background:var(--bg3);border:1px solid var(--border);border-radius:20px;padding:0.2rem 0.8rem;font-family:'DM Mono',monospace;font-size:0.78rem;color:var(--gold);margin-bottom:1rem;}
section[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
.stButton>button{background:linear-gradient(135deg,var(--gold-dim),var(--gold))!important;color:#000!important;font-family:'Bebas Neue',sans-serif!important;font-size:1.1rem!important;letter-spacing:2px!important;border:none!important;border-radius:8px!important;padding:0.6rem 2rem!important;width:100%!important;}
.stTextInput>div>div>input{background:var(--bg3)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text)!important;font-family:'DM Mono',monospace!important;}
div[data-testid="stExpander"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:10px!important;}
hr{border-color:var(--border)!important;}
</style>
""", unsafe_allow_html=True)

# ── Sabitler ─────────────────────────────────────────────────
SEHIRLER = [
    "Istanbul", "Ankara", "Izmir", "Bursa", "Adana",
    "Antalya", "Kocaeli", "Diyarbakir", "Elazig", "Sanliurfa",
    "İstanbul", "İzmir", "Diyarbakır", "Elazığ", "Şanlıurfa",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.tjk.org/",
}

# ── Veri Çekme ────────────────────────────────────────────────
def csv_dene(tarih_ymd, sehir_adi):
    obj = datetime.strptime(tarih_ymd, "%Y-%m-%d")
    yil = obj.strftime("%Y")
    klasor = obj.strftime("%Y-%m-%d")
    dosya = obj.strftime("%d.%m.%Y")
    url = (f"https://medya-cdn.tjk.org/raporftp/TJKPDF/{yil}/{klasor}/CSV/"
           f"GunlukYarisProgrami/{dosya}-{sehir_adi}-GunlukYarisProgrami-TR.csv")
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code == 200 and len(r.content) > 200:
            return r.content, url
    except:
        pass
    return None, url

def csv_parse(raw, sehir_adi):
    kosular = {}
    try:
        for enc in ["windows-1254", "utf-8", "latin-1"]:
            try:
                metin = raw.decode(enc, errors="strict")
                break
            except:
                metin = raw.decode("windows-1254", errors="replace")

        reader = csv.DictReader(io.StringIO(metin), delimiter=";")
        cols = [c.strip() for c in (reader.fieldnames or [])]

        def bul(*isimler):
            for n in isimler:
                for c in cols:
                    if c.lower() == n.lower():
                        return c
            return isimler[0]

        c_kno  = bul("KosuNo","KOSU_NO","Kosu No","Koşu No")
        c_at   = bul("AtAdi","AT_ADI","At Adi","At Adı")
        c_yno  = bul("YarisNo","YARIS_NO","No","Yaris No")
        c_jok  = bul("JokeyAdi","JOKEY","Jokey","Jokey Adi")
        c_hp   = bul("HP","Hp","hp")
        c_mes  = bul("Mesafe","MESAFE","mesafe")
        c_pist = bul("PistAdi","PIST","Pist","Pist Adi")
        c_tur  = bul("KosuTipi","KOSU_TIPI","Kosu Tipi","Tür")
        c_saat = bul("KosuSaati","Saat","Kosu Saati")
        c_form = bul("SonAltiYarisFormu","Form","Son 6 Yaris")
        c_kilo = bul("Siklet","Sıklet","Kilo")

        for row in reader:
            try:
                kno_raw = row.get(c_kno, "").strip()
                if not kno_raw: continue
                kno = int(kno_raw)
                at  = row.get(c_at, "").strip()
                if not at: continue
                try: yno = int(row.get(c_yno,"0").strip())
                except: yno = 0
                jok  = row.get(c_jok, "-").strip() or "-"
                mes  = row.get(c_mes, "?").strip() or "?"
                pist = row.get(c_pist,"?").strip() or "?"
                tur  = row.get(c_tur, "?").strip() or "?"
                saat = row.get(c_saat,"?").strip() or "?"
                form = row.get(c_form,"-").strip() or "-"
                kilo = row.get(c_kilo,"-").strip() or "-"
                try: hp = int(float(row.get(c_hp,"0").strip()))
                except: hp = 0

                if kno not in kosular:
                    kosular[kno] = {"no":kno,"sehir":sehir_adi,"saat":saat,
                                    "mesafe":mes,"pist":pist,"tur":tur,"atlar":[]}
                kosular[kno]["atlar"].append(
                    {"no":yno,"isim":at,"jokey":jok,"hp":hp,"form":form,"kilo":kilo})
            except: continue
    except Exception as e:
        pass
    return list(kosular.values())

def tjk_veri_cek(tarih_ymd):
    tum = []
    denenen = []
    # Farklı şehir ismi varyantlarını dene
    sehir_varyantlar = {
        "İstanbul": ["İstanbul","Istanbul","istanbul"],
        "Ankara":   ["Ankara","ankara"],
        "İzmir":    ["İzmir","Izmir","izmir"],
        "Bursa":    ["Bursa","bursa"],
        "Adana":    ["Adana","adana"],
        "Antalya":  ["Antalya","antalya"],
        "Kocaeli":  ["Kocaeli","kocaeli"],
        "Diyarbakır":["Diyarbakır","Diyarbakir","diyarbakir"],
        "Elazığ":   ["Elazığ","Elazig","elazig"],
        "Şanlıurfa":["Şanlıurfa","Sanliurfa","sanliurfa"],
    }
    for sehir, varyantlar in sehir_varyantlar.items():
        for v in varyantlar:
            raw, url = csv_dene(tarih_ymd, v)
            denenen.append(url)
            if raw:
                kosular = csv_parse(raw, sehir)
                if kosular:
                    tum.extend(kosular)
                break
    if not tum:
        return None, f"Bugün hiçbir hipodromda program bulunamadı.\nDenenen örnek URL:\n{denenen[0]}"
    return {"tarih": tarih_ymd, "kosular": tum, "kaynak":"tjk-cdn"}, None

# ── Claude Analiz ─────────────────────────────────────────────
def claude_analiz(api_key, kosu):
    at_listesi = "\n".join([
        f"  {a['no']}. {a['isim']} | Jokey: {a['jokey']} | HP: {a['hp']} | Form: {a['form']} | Kilo: {a['kilo']}"
        for a in kosu["atlar"]
    ])
    prompt = (
        f"Sen TJK Türkiye at yarışları uzmanısın.\n\n"
        f"KOŞU: {kosu['no']}. Ayak | {kosu['sehir']} | {kosu['mesafe']}m {kosu['pist']} | {kosu['tur']} | Saat: {kosu['saat']}\n\n"
        f"KATILIMCILAR:\n{at_listesi}\n\n"
        f"Analiz:\n"
        f"1. BANKO: En guçlu 1 at (isim + no + kisa gerekce)\n"
        f"2. PLASE: 2-3 alternatif at\n"
        f"3. KAZANMA TAHMINI: One cikan 4-5 at icin tahmini yuzde olasilik\n"
        f"4. KISA YORUM: 2-3 cumle\n\n"
        f"Turkce yaz, kisa ve net ol. Son satira 'Bu tahmin amaclidir.' ekle."
    )
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key,
                     "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514",
                  "max_tokens": 700,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=35
        )
        if r.status_code == 200:
            return r.json()["content"][0]["text"], None
        err = r.json().get("error", {}).get("message", f"HTTP {r.status_code}")
        return None, err
    except Exception as e:
        return None, str(e)

# ── API Key al ────────────────────────────────────────────────
# Önce Secrets dene, yoksa form
api_key = ""
try:
    k = st.secrets.get("ANTHROPIC_API_KEY", "")
    if k and str(k).startswith("sk-"):
        api_key = str(k)
except:
    pass

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Bebas Neue,sans-serif;font-size:1.6rem;letter-spacing:3px;color:#D4A843;margin-bottom:1rem;">⚙ AYARLAR</div>', unsafe_allow_html=True)

    if api_key:
        st.markdown('<div style="font-size:0.8rem;color:#22C55E;padding:0.5rem;background:#071407;border:1px solid #166534;border-radius:6px;margin-bottom:0.8rem;">✅ API Key aktif (Secrets)</div>', unsafe_allow_html=True)
    else:
        inp = st.text_input("Anthropic API Key", type="password",
                            placeholder="sk-ant-api03-...",
                            key="ak")
        if inp:
            api_key = inp

    st.markdown("---")
    tarih_sec = st.date_input("Analiz Tarihi", value=datetime.now().date())
    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#5A5E6B;line-height:1.9;">🔒 Key sunucuda saklanmaz.<br>📡 Veri: tjk.org CDN (CSV)<br>🤖 Analiz: Claude Sonnet<br>⚠️ Yalnızca bilgi amaçlıdır.</div>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown('<div class="hero"><h1>BEYGİR ADAM</h1><p>Türkiye At Yarışları · Otomatik AI Analiz Sistemi · TJK Verisi</p></div>', unsafe_allow_html=True)
tarih_ymd = tarih_sec.strftime("%Y-%m-%d")
st.markdown(f'<div class="date-chip">📅 {tarih_sec.strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

# API key uyarısı
if not api_key:
    st.markdown('<div class="info-strip">🔑 Sidebar\'dan <b>Anthropic API Key</b> girin. <a href="https://console.anthropic.com" target="_blank" style="color:#D4A843;">console.anthropic.com</a> adresinden alabilirsiniz.</div>', unsafe_allow_html=True)

# Buton — api_key widget'ı ile aynı form içinde değil, ayrı
calistir = st.button("📡 VERİ ÇEK & ANALİZ ET", disabled=(not api_key))

# ── Ana Mantık ────────────────────────────────────────────────
if calistir and api_key:
    with st.spinner("📡 TJK CSV dosyaları indiriliyor..."):
        veri, hata = tjk_veri_cek(tarih_ymd)

    if hata or not veri:
        st.error("❌ " + (hata or "Veri alınamadı"))
        st.info("💡 Yarış programı henüz yayınlanmamış olabilir. Yarış günü sabah 09:00'dan sonra deneyin.")
        st.stop()

    kosular = veri["kosular"]
    st.markdown("---")

    # Özet istatistik
    c1, c2, c3 = st.columns(3)
    sehirler_list = list(set(k["sehir"] for k in kosular))
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(kosular)}</div><div class="stat-lbl">TOPLAM KOŞU</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{sum(len(k["atlar"]) for k in kosular)}</div><div class="stat-lbl">TOPLAM AT</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(sehirler_list)}</div><div class="stat-lbl">HİPODROM</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    # Her koşu
    for kosu in sorted(kosular, key=lambda x: (x["sehir"], x["no"])):
        atlar = sorted(kosu["atlar"], key=lambda a: a.get("hp", 0), reverse=True)
        baslik = f"🏁 {kosu['no']}. AYAK  ·  {kosu['sehir']}  ·  {kosu['mesafe']}m {kosu['pist']}  ·  {kosu.get('saat','')}"

        with st.expander(baslik, expanded=False):
            col_at, col_ai = st.columns([1, 1])

            with col_at:
                st.markdown("**📋 Katılımcılar** *(HP sırasıyla)*")
                for i, at in enumerate(atlar):
                    renk = "#D4A843" if i == 0 else "#9CA3AF" if i == 1 else "#5A5E6B"
                    st.markdown(
                        f'<div class="at-row">'
                        f'<div class="at-no">{at["no"]}</div>'
                        f'<div class="at-name">{at["isim"]}</div>'
                        f'<div class="at-jokey">{at["jokey"]}</div>'
                        f'<div class="at-form">{at["form"]}</div>'
                        f'<div class="at-hp" style="color:{renk};">{at["hp"]} HP</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            with col_ai:
                st.markdown("**🤖 Claude AI Analiz**")
                key = f"a_{tarih_ymd}_{kosu['sehir']}_{kosu['no']}"
                if key not in st.session_state:
                    with st.spinner("Analiz ediliyor..."):
                        sonuc, hata_ai = claude_analiz(api_key, kosu)
                        st.session_state[key] = sonuc if sonuc else ("❌ " + str(hata_ai))
                    time.sleep(0.2)
                txt = st.session_state.get(key, "")
                if txt:
                    st.markdown(f'<div class="ai-box">{txt}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="info-strip" style="text-align:center;">⚠️ Bu uygulama yalnızca bilgi amaçlıdır. Kesin tahmin değildir. Sorumlu oynayın.</div>', unsafe_allow_html=True)

elif not calistir:
    # Başlangıç ekranı
    st.markdown("""
    <div style="text-align:center;padding:3rem 0;color:#5A5E6B;">
        <div style="font-size:3rem;margin-bottom:1rem;">🏇</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:3px;color:#8B6914;margin-bottom:0.5rem;">HAZIR</div>
        <div style="font-size:0.9rem;">API key girin, ardından<br>
        <b style="color:#D4A843;">VERİ ÇEK & ANALİZ ET</b> butonuna basın.</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    boxes = [
        ("📡", "Otomatik Veri", "TJK CDN'den CSV indirir. JavaScript gerektirmez, her ortamda çalışır."),
        ("🤖", "AI Analiz", "Claude Sonnet her koşu için banko, plase ve kazanma tahmini üretir."),
        ("🔒", "Güvenli", "API key Streamlit Secrets ile korunur, sunucuda düz metin saklanmaz."),
    ]
    for col, (ico, baslik, acik) in zip([c1, c2, c3], boxes):
        with col:
            st.markdown(f'<div class="stat-box" style="text-align:left;"><div style="font-size:1.5rem;margin-bottom:0.5rem;">{ico}</div><div style="font-weight:500;margin-bottom:0.3rem;">{baslik}</div><div style="font-size:0.8rem;color:#5A5E6B;">{acik}</div></div>', unsafe_allow_html=True)
