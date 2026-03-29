import streamlit as st
import requests, re, time
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
.at-form{font-family:'DM Mono',monospace;font-size:0.75rem;color:var(--muted);min-width:60px;text-align:right;}
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

# ── Sporx'tan veri çekme ──────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Referer": "https://www.sporx.com/",
}

# Sporx'taki hipodrom kodları
SPORX_HIPODROMLAR = [
    ("IZMIR",     "İzmir"),
    ("ADANA",     "Adana"),
    ("ANKARA",    "Ankara"),
    ("ISTANBUL",  "İstanbul"),
    ("BURSA",     "Bursa"),
    ("ANTALYA",   "Antalya"),
    ("KOCAELI",   "Kocaeli"),
    ("DIYARBAKIR","Diyarbakır"),
    ("ELAZIG",    "Elazığ"),
    ("SANLIURFA", "Şanlıurfa"),
]

def sporx_ana_sayfa():
    """Sporx'tan bugünkü aktif hipodromları çek."""
    try:
        r = requests.get("https://www.sporx.com/at-yarisi", headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return None

def aktif_hipodromlar_bul(html):
    """Sporx ana sayfasından bugün yarışı olan Türk hipodromlarını bul."""
    # Sporx: <a href="/at-yarisi?hipodrom=IZMIR">İzmir</a>
    pattern = re.compile(r'at-yarisi\?hipodrom=([A-Z]+)[^"]*"[^>]*>([^<]+)<', re.IGNORECASE)
    bulunan = []
    goruldu = set()
    for m in pattern.finditer(html):
        kod = m.group(1).upper()
        isim = m.group(2).strip()
        if kod not in goruldu and any(kod == h[0] for h in SPORX_HIPODROMLAR):
            goruldu.add(kod)
            # Türkçe ismi bizim listeden al
            for hkod, hadi in SPORX_HIPODROMLAR:
                if hkod == kod:
                    bulunan.append((kod, hadi))
                    break
    return bulunan

def sporx_hipodrom_cek(kod):
    """Bir hipodromun koşu listesini çek."""
    url = f"https://www.sporx.com/at-yarisi?hipodrom={kod}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return None

def sporx_parse(html, sehir_adi):
    """Sporx HTML'inden koşu ve at verilerini çıkar."""
    kosular = {}
    temiz = re.compile(r'<[^>]+>')

    # Sporx tablo yapısı: NO, AT/YAŞ/BİLGİLER, KİLO, JOKEY, ORİJİN, SAHİP/ANTRENÖR, HP, SON6, KGS, EİD, GANYAN, AGF
    # Her koşu başlığı: "X. Koşu" veya koşu saati
    
    # Önce koşu bloklarını bul
    kosu_re = re.compile(r'(\d+)\.\s*Ko[sş]u', re.IGNORECASE)
    saat_re = re.compile(r'(\d{2}:\d{2})')
    mesafe_re = re.compile(r'(\d{3,4})\s*(Kum|Çim|Sentetik|ÇİM|KUM)', re.IGNORECASE)
    
    # Tablo satırlarını çek — her <tr> potansiyel at satırı
    satir_re = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
    td_re    = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)
    
    # Sporx'ta at bilgisi sütunları: NO | AT İSMİ (yaş) | KİLO | JOKEY | ... | HP | SON6 | ...
    # at ismi bold: <strong>AT İSMİ</strong> veya düz metin
    
    mevcut_kosu = 1
    mevcut_saat = "?"
    mevcut_mesafe = "?"
    mevcut_pist = "?"
    
    # HTML'yi satır satır işle
    for satir_html in satir_re.findall(html):
        tdler = td_re.findall(satir_html)
        if not tdler:
            continue
        
        temizler = [re.sub(r'\s+', ' ', temiz.sub('', td)).strip() for td in tdler]
        
        # Koşu başlığı satırı — "X. Koşu" içeriyor
        satir_metin = temiz.sub('', satir_html)
        km = kosu_re.search(satir_metin)
        if km:
            mevcut_kosu = int(km.group(1))
            sm = saat_re.search(satir_metin)
            if sm:
                mevcut_saat = sm.group(1)
            mm = mesafe_re.search(satir_metin)
            if mm:
                mevcut_mesafe = mm.group(1)
                mevcut_pist = mm.group(2).capitalize()
            continue
        
        # At satırı: ilk sütun rakam (at no), 2. sütunda at ismi
        if len(temizler) >= 7:
            # İlk kolon at numarası olmalı
            try:
                at_no = int(temizler[0])
            except:
                # ST: prefix ile olabilir
                m = re.match(r'ST:\s*\d+', temizler[0], re.IGNORECASE)
                if not m:
                    continue
                try:
                    at_no = int(re.search(r'\d+', temizler[0]).group())
                except:
                    continue
            
            # 2. sütun: AT İSMİ (yaş bilgisi de olabilir)
            at_raw = temizler[1] if len(temizler) > 1 else ""
            # İsmi ayır: büyük harfler isim, küçük/yaş bilgisi ayrı
            at_isim = re.split(r'\s+\d+[yY]', at_raw)[0].strip()
            if len(at_isim) < 2:
                continue
            
            # Jokey — genellikle 3. veya 4. sütun
            jokey = temizler[3] if len(temizler) > 3 else "-"
            if not jokey or len(jokey) < 2:
                jokey = temizler[2] if len(temizler) > 2 else "-"
            
            # HP — 7. sütun (index 6)
            hp = 0
            for i in range(5, min(9, len(temizler))):
                try:
                    v = int(temizler[i])
                    if 10 <= v <= 150:
                        hp = v
                        break
                except:
                    pass
            
            # Son 6 yarış — 8. sütun
            form = "-"
            for i in range(6, min(10, len(temizler))):
                if re.match(r'^[\d\-]+$', temizler[i]) and len(temizler[i]) >= 3:
                    form = temizler[i]
                    break
            
            if mevcut_kosu not in kosular:
                kosular[mevcut_kosu] = {
                    "no": mevcut_kosu, "sehir": sehir_adi,
                    "saat": mevcut_saat, "mesafe": mevcut_mesafe,
                    "pist": mevcut_pist, "tur": "Düz", "atlar": []
                }
            
            kosular[mevcut_kosu]["atlar"].append({
                "no": at_no, "isim": at_isim,
                "jokey": jokey, "hp": hp, "form": form
            })
    
    return [v for v in kosular.values() if v["atlar"]]

def veri_cek(tarih_ymd):
    """Sporx'tan bugünkü tüm koşuları çek."""
    # Ana sayfadan aktif hipodromları bul
    ana_html = sporx_ana_sayfa()
    if not ana_html:
        return None, "Sporx'a bağlanılamadı"
    
    aktif = aktif_hipodromlar_bul(ana_html)
    if not aktif:
        # Fallback: tüm hipodromları dene
        aktif = SPORX_HIPODROMLAR[:5]
    
    tum_kosular = []
    for kod, adi in aktif:
        html = sporx_hipodrom_cek(kod)
        if not html:
            continue
        kosular = sporx_parse(html, adi)
        tum_kosular.extend(kosular)
    
    if not tum_kosular:
        return None, "Bugün aktif hipodromda koşu bulunamadı"
    
    return {"tarih": tarih_ymd, "kosular": tum_kosular}, None

def claude_analiz(api_key, kosu):
    atlar = kosu["atlar"]
    at_listesi = "\n".join([
        f"  {a['no']}. {a['isim']} | Jokey: {a['jokey']} | HP: {a['hp']} | Form: {a['form']}"
        for a in atlar
    ])
    prompt = (
        f"Sen TJK Türkiye at yarışları uzmanısın.\n\n"
        f"KOŞU: {kosu['no']}. Ayak | {kosu['sehir']} | {kosu['mesafe']}m {kosu['pist']} | Saat: {kosu['saat']}\n\n"
        f"KATILIMCILAR:\n{at_listesi}\n\n"
        f"Analiz et:\n"
        f"1. BANKO: En guçlu 1 at (isim + no + kisa gerekce)\n"
        f"2. PLASE: 2-3 alternatif\n"
        f"3. KAZANMA TAHMINI: One cikan 4-5 at icin % olasilik\n"
        f"4. KISA YORUM: 2-3 cumle\n\n"
        f"Turkce, kisa, net. Son satira uyari ekle."
    )
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 700,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=35
        )
        if r.status_code == 200:
            return r.json()["content"][0]["text"], None
        return None, r.json().get("error", {}).get("message", f"HTTP {r.status_code}")
    except Exception as e:
        return None, str(e)

# ── API Key ───────────────────────────────────────────────────
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
        inp = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-api03-...", key="ak")
        if inp:
            api_key = inp
    st.markdown("---")
    tarih_sec = st.date_input("Analiz Tarihi", value=datetime.now().date())
    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#5A5E6B;line-height:1.9;">🔒 Key sunucuda saklanmaz.<br>📡 Veri: sporx.com<br>🤖 Analiz: Claude Sonnet<br>⚠️ Yalnızca bilgi amaçlıdır.</div>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown('<div class="hero"><h1>BEYGİR ADAM</h1><p>Türkiye At Yarışları · Otomatik AI Analiz Sistemi · sporx.com verisi</p></div>', unsafe_allow_html=True)
tarih_ymd = tarih_sec.strftime("%Y-%m-%d")
st.markdown(f'<div class="date-chip">📅 {tarih_sec.strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="info-strip">🔑 Sidebar\'dan <b>Anthropic API Key</b> girin. <a href="https://console.anthropic.com" target="_blank" style="color:#D4A843;">console.anthropic.com</a></div>', unsafe_allow_html=True)

calistir = st.button("📡 VERİ ÇEK & ANALİZ ET", disabled=(not api_key))

# ── Ana Mantık ────────────────────────────────────────────────
if calistir and api_key:
    with st.spinner("📡 sporx.com'dan program çekiliyor..."):
        veri, hata = veri_cek(tarih_ymd)

    if hata or not veri:
        st.error("❌ " + (hata or "Veri alınamadı"))
        st.info("💡 Yarış programı henüz yayınlanmamış veya bugün yarış yoktur.")
        st.stop()

    kosular = veri["kosular"]
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    sehirler_list = list(set(k["sehir"] for k in kosular))
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(kosular)}</div><div class="stat-lbl">TOPLAM KOŞU</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{sum(len(k["atlar"]) for k in kosular)}</div><div class="stat-lbl">TOPLAM AT</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(sehirler_list)}</div><div class="stat-lbl">HİPODROM</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    for kosu in sorted(kosular, key=lambda x: (x["sehir"], x["no"])):
        atlar = sorted(kosu["atlar"], key=lambda a: a.get("hp", 0), reverse=True)
        with st.expander(
            f"🏁 {kosu['no']}. AYAK  ·  {kosu['sehir']}  ·  {kosu['mesafe']}m {kosu['pist']}  ·  {kosu.get('saat','')}",
            expanded=False
        ):
            col_at, col_ai = st.columns([1, 1])
            with col_at:
                st.markdown("**📋 Katılımcılar** *(HP sırasıyla)*")
                for i, at in enumerate(atlar):
                    renk = "#D4A843" if i==0 else "#9CA3AF" if i==1 else "#5A5E6B"
                    st.markdown(
                        f'<div class="at-row">'
                        f'<div class="at-no">{at["no"]}</div>'
                        f'<div class="at-name">{at["isim"]}</div>'
                        f'<div class="at-jokey">{at["jokey"]}</div>'
                        f'<div class="at-form">{at["form"]}</div>'
                        f'<div class="at-hp" style="color:{renk};">{at["hp"]} HP</div>'
                        f'</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="info-strip" style="text-align:center;">⚠️ Yalnızca bilgi amaçlıdır. Kesin tahmin değildir. Sorumlu oynayın.</div>', unsafe_allow_html=True)

elif not calistir:
    st.markdown("""<div style="text-align:center;padding:3rem 0;color:#5A5E6B;">
        <div style="font-size:3rem;margin-bottom:1rem;">🏇</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:3px;color:#8B6914;margin-bottom:0.5rem;">HAZIR</div>
        <div style="font-size:0.9rem;">API key girin, ardından<br>
        <b style="color:#D4A843;">VERİ ÇEK & ANALİZ ET</b> butonuna basın.</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    for col, (ico, bas, ac) in zip([c1,c2,c3],[
        ("📡","Otomatik Veri","sporx.com'dan günlük programı çeker. TJK engelini aşar."),
        ("🤖","AI Analiz","Claude Sonnet banko, plase ve kazanma tahmini üretir."),
        ("🔒","Güvenli","API key Secrets ile korunur, sunucuda saklanmaz."),
    ]):
        with col:
            st.markdown(f'<div class="stat-box" style="text-align:left;"><div style="font-size:1.5rem;margin-bottom:0.5rem;">{ico}</div><div style="font-weight:500;margin-bottom:0.3rem;">{bas}</div><div style="font-size:0.8rem;color:#5A5E6B;">{ac}</div></div>', unsafe_allow_html=True)
