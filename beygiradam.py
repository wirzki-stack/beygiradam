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
.at-jokey{font-size:0.75rem;color:var(--muted);min-width:80px;}
.at-hp{font-family:'DM Mono',monospace;font-size:0.82rem;}
.at-form{font-family:'DM Mono',monospace;font-size:0.75rem;color:var(--muted);}
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
    {"id":"1","adi":"İstanbul"}, {"id":"3","adi":"Ankara"},
    {"id":"2","adi":"İzmir"},   {"id":"5","adi":"Bursa"},
    {"id":"4","adi":"Adana"},   {"id":"10","adi":"Antalya"},
    {"id":"9","adi":"Kocaeli"}, {"id":"6","adi":"Diyarbakır"},
    {"id":"7","adi":"Elazığ"},  {"id":"8","adi":"Şanlıurfa"},
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.tjk.org/",
}

# ── Veri Çekme ────────────────────────────────────────────────
def csv_url(tarih_ymd, sehir_adi):
    obj = datetime.strptime(tarih_ymd, "%Y-%m-%d")
    return (
        f"https://medya-cdn.tjk.org/raporftp/TJKPDF/{obj.strftime('%Y')}/"
        f"{obj.strftime('%Y-%m-%d')}/CSV/GunlukYarisProgrami/"
        f"{obj.strftime('%d.%m.%Y')}-{sehir_adi}-GunlukYarisProgrami-TR.csv"
    )

def csv_indir(tarih_ymd, sehir_adi):
    try:
        r = requests.get(csv_url(tarih_ymd, sehir_adi), headers=HEADERS, timeout=12)
        if r.status_code == 200 and len(r.content) > 200:
            return r.content
    except:
        pass
    return None

def csv_parse(raw, sehir_adi):
    kosular = {}
    try:
        metin = raw.decode("windows-1254", errors="replace")
        reader = csv.DictReader(io.StringIO(metin), delimiter=";")
        cols = reader.fieldnames or []

        def col(*names):
            for n in names:
                for c in cols:
                    if c.strip().lower() == n.lower():
                        return c
            return names[0]

        c_kno   = col("KosuNo","KOSU_NO","Koşu No")
        c_at    = col("AtAdi","AT_ADI","At Adı","At Adi")
        c_yno   = col("YarisNo","YARIS_NO","No","Yarış No")
        c_jok   = col("JokeyAdi","JOKEY","Jokey","Jokey Adı")
        c_hp    = col("HP","Hp","hp")
        c_mes   = col("Mesafe","MESAFE")
        c_pist  = col("PistAdi","PIST","Pist")
        c_tur   = col("KosuTipi","KOSU_TIPI","Koşu Tipi","Tür")
        c_saat  = col("KosuSaati","Saat","Koşu Saati")
        c_form  = col("SonAltiYarisFormu","Form","Son 6 Yarış")
        c_kilo  = col("Siklet","Sıklet","Kilo","siklet")

        for row in reader:
            try:
                kno_raw = row.get(c_kno,"").strip()
                if not kno_raw: continue
                kno = int(kno_raw)
                at  = row.get(c_at,"").strip()
                yno = row.get(c_yno,"").strip()
                jok = row.get(c_jok,"-").strip()
                hp_s= row.get(c_hp,"0").strip()
                mes = row.get(c_mes,"?").strip()
                pist= row.get(c_pist,"?").strip()
                tur = row.get(c_tur,"?").strip()
                saat= row.get(c_saat,"?").strip()
                form= row.get(c_form,"-").strip()
                kilo= row.get(c_kilo,"-").strip()
                try: hp_int = int(float(hp_s))
                except: hp_int = 0
                try: yno_int = int(yno)
                except: yno_int = 0
                if kno not in kosular:
                    kosular[kno] = {"no":kno,"sehir":sehir_adi,"saat":saat,
                                    "mesafe":mes,"pist":pist,"tur":tur,"atlar":[]}
                if at:
                    kosular[kno]["atlar"].append(
                        {"no":yno_int,"isim":at,"jokey":jok,"hp":hp_int,"form":form,"kilo":kilo})
            except: continue
    except Exception as e:
        pass
    return list(kosular.values())

def tjk_veri_cek(tarih_ymd):
    bulunan = []
    hatalar = []
    for s in SEHIRLER:
        raw = csv_indir(tarih_ymd, s["adi"])
        if raw:
            kosular = csv_parse(raw, s["adi"])
            bulunan.extend(kosular)
    if not bulunan:
        return None, "Bugün hiçbir hipodromda program bulunamadı"
    return {"tarih": tarih_ymd, "kosular": bulunan, "kaynak":"tjk-cdn"}, None

# ── Claude Analiz ─────────────────────────────────────────────
def claude_analiz(api_key, kosu):
    atlar = kosu["atlar"]
    at_listesi = "\n".join([
        f"  {a['no']}. {a['isim']} | Jokey: {a['jokey']} | HP: {a['hp']} | Form: {a['form']} | Kilo: {a['kilo']}"
        for a in atlar
    ])
    prompt = (
        f"Sen TJK Türkiye at yarışları uzmanısın.\n\n"
        f"KOŞU: {kosu['no']}. Ayak | {kosu['sehir']} | {kosu['mesafe']}m {kosu['pist']} | {kosu['tur']} | Saat: {kosu['saat']}\n\n"
        f"KATILIMCILAR:\n{at_listesi}\n\n"
        f"Lütfen şunları yaz:\n"
        f"1. 🏆 BANKO: En güçlü 1 at (isim + no + kısa gerekçe)\n"
        f"2. 🥈 PLASE: 2-3 alternatif at (isim ve no)\n"
        f"3. 📊 KAZANMA TAHMİNİ: Öne çıkan 4-5 at için tahmini % olasılık\n"
        f"4. 💡 KISA YORUM: 2-3 cümle (pist, form, mesafe değerlendirmesi)\n\n"
        f"Türkçe yaz, kısa ve net ol. Son satıra '⚠️ Bu tahmin amaçlıdır.' ekle."
    )
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key":api_key,"anthropic-version":"2023-06-01","content-type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":700,
                  "messages":[{"role":"user","content":prompt}]},
            timeout=35
        )
        if r.status_code == 200:
            return r.json()["content"][0]["text"], None
        err = r.json().get("error",{}).get("message", f"HTTP {r.status_code}")
        return None, err
    except Exception as e:
        return None, str(e)

# ── Sidebar ───────────────────────────────────────────────────
# API key: önce Streamlit Secrets, sonra form input
def get_api_key():
    # 1. Streamlit Cloud Secrets (kalıcı, önerilen)
    try:
        k = st.secrets["ANTHROPIC_API_KEY"]
        if k and k.startswith("sk-"):
            return k, "secrets"
    except:
        pass
    # 2. Kullanıcı formu (oturum bazlı)
    return st.session_state.get("_ak", ""), "input"

with st.sidebar:
    st.markdown('<div style="font-family:Bebas Neue,sans-serif;font-size:1.6rem;letter-spacing:3px;color:#D4A843;margin-bottom:1rem;">⚙ AYARLAR</div>', unsafe_allow_html=True)

    api_key, ak_kaynak = get_api_key()

    if ak_kaynak == "secrets":
        st.markdown('<div style="font-size:0.8rem;color:#22C55E;padding:0.5rem;background:#0D1F0D;border-radius:6px;margin-bottom:0.5rem;">✅ API Key yüklendi (Secrets)</div>', unsafe_allow_html=True)
    else:
        _inp = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-api03-...",
            help="console.anthropic.com adresinden alın. Kalıcı kullanım için App Settings → Secrets bölümüne ekleyin."
        )
        if _inp.strip():
            st.session_state["_ak"] = _inp.strip()
            api_key = _inp.strip()
        if api_key:
            st.markdown('<div style="font-size:0.78rem;color:#22C55E;">✅ API Key girildi</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.75rem;color:#8B6914;padding:0.4rem;background:#1A1200;border-radius:4px;">💡 Key girip hemen butona basin</div>', unsafe_allow_html=True)

    st.markdown("---")
    tarih_sec = st.date_input("Analiz Tarihi", value=datetime.now().date())
    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#5A5E6B;line-height:1.9;">🔒 API key sunucuda saklanmaz.<br>📡 Veri: tjk.org CDN (CSV)<br>🤖 Analiz: Claude Sonnet<br>⚠️ Yalnızca bilgi amaçlıdır.</div>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown('<div class="hero"><h1>BEYGİR ADAM</h1><p>Türkiye At Yarışları · Otomatik AI Analiz Sistemi · TJK Verisi</p></div>', unsafe_allow_html=True)
tarih_ymd = tarih_sec.strftime("%Y-%m-%d")
st.markdown(f'<div class="date-chip">📅 {tarih_sec.strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="info-strip">🔑 Sidebar\'dan <b>Anthropic API Key</b> girin, ardından butona basın. <a href="https://console.anthropic.com" target="_blank" style="color:#D4A843;">console.anthropic.com</a> adresinden ücretsiz alabilirsiniz.</div>', unsafe_allow_html=True)

calistir = st.button("📡 VERİ ÇEK & ANALİZ ET")

# ── Ana Mantık ────────────────────────────────────────────────
if calistir:
    # api_key'i tekrar oku (buton tıklamasında session_state güvenilir)
    _fresh, _ = get_api_key()
    if _fresh:
        api_key = _fresh
    if not api_key or not api_key.strip().startswith("sk-"):
        st.warning("⚠️ Geçerli bir Anthropic API Key giriniz (sk-ant-... ile başlamalı).")
        st.stop()
    api_key = api_key.strip()

    with st.spinner("📡 TJK CSV dosyaları indiriliyor..."):
        veri, hata = tjk_veri_cek(tarih_ymd)

    if hata or not veri:
        st.error("❌ " + (hata or "Veri alınamadı"))
        st.info("💡 Bugün yarış olmayabilir veya program henüz yayınlanmamış olabilir.")
        st.stop()

    kosular = veri["kosular"]
    st.markdown("---")

    # Özet
    c1, c2, c3 = st.columns(3)
    sehirler_list = list(set(k["sehir"] for k in kosular))
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(kosular)}</div><div class="stat-lbl">TOPLAM KOŞU</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{sum(len(k["atlar"]) for k in kosular)}</div><div class="stat-lbl">TOPLAM AT</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(sehirler_list)}</div><div class="stat-lbl">HİPODROM</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    # Koşuları göster
    for kosu in sorted(kosular, key=lambda x: (x["sehir"], x["no"])):
        atlar = sorted(kosu["atlar"], key=lambda a: a.get("hp",0), reverse=True)
        baslik = f"🏁 {kosu['no']}. AYAK  ·  {kosu['sehir']}  ·  {kosu['mesafe']}m {kosu['pist']}  ·  {kosu.get('saat','')}"
        with st.expander(baslik, expanded=False):
            col_at, col_ai = st.columns([1, 1])

            with col_at:
                st.markdown("**📋 Katılımcılar** *(HP'ye göre sıralı)*")
                for i, at in enumerate(atlar):
                    renk = "#D4A843" if i==0 else "#9CA3AF" if i==1 else "#5A5E6B"
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
                    with st.spinner("Analiz yapılıyor..."):
                        sonuc, hata_ai = claude_analiz(api_key, kosu)
                        st.session_state[key] = sonuc if sonuc else ("❌ " + str(hata_ai))
                    time.sleep(0.2)
                txt = st.session_state.get(key,"")
                if txt:
                    st.markdown(f'<div class="ai-box">{txt}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="info-strip" style="text-align:center;">⚠️ Bu uygulama yalnızca bilgi amaçlıdır. Kesin tahmin değildir. Sorumlu oynayın.</div>', unsafe_allow_html=True)

else:
    # Başlangıç ekranı
    st.markdown("""
    <div style="text-align:center;padding:3rem 0;color:#5A5E6B;">
        <div style="font-size:3rem;margin-bottom:1rem;">🏇</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:3px;color:#8B6914;margin-bottom:0.5rem;">HAZIR</div>
        <div style="font-size:0.9rem;">Sidebar'a API key girin, ardından<br>
        <b style="color:#D4A843;">VERİ ÇEK & ANALİZ ET</b> butonuna basın.</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    boxes = [
        ("📡","Otomatik Veri","TJK CDN'den CSV indirir. JavaScript yok, 403 yok — her ortamda çalışır."),
        ("🤖","AI Analiz","Claude Sonnet her koşu için banko, plase ve kazanma tahmini üretir."),
        ("🔒","Güvenli","API key sadece tarayıcı oturumunda tutulur, hiçbir sunucuda saklanmaz."),
    ]
    for col, (ico, baslik, acik) in zip([c1,c2,c3], boxes):
        with col:
            st.markdown(f'<div class="stat-box" style="text-align:left;"><div style="font-size:1.5rem;margin-bottom:0.5rem;">{ico}</div><div style="font-weight:500;margin-bottom:0.3rem;">{baslik}</div><div style="font-size:0.8rem;color:#5A5E6B;">{acik}</div></div>', unsafe_allow_html=True)
