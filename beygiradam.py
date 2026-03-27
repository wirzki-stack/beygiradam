import streamlit as st
import json
import requests
import re
import time
from datetime import datetime, timedelta
from urllib.parse import unquote, quote

st.set_page_config(
    page_title="🏇 BeygiRadam | Otomatik Analiz",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
:root {
    --gold: #D4A843; --gold-dim: #8B6914; --bg: #0A0B0D; --bg2: #111318;
    --bg3: #1A1D25; --border: #252830; --text: #E8E9EC; --muted: #5A5E6B;
    --green: #22C55E; --blue: #3B82F6;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: var(--bg) !important; color: var(--text) !important; }
.stApp { background-color: var(--bg) !important; }
.hero { background: linear-gradient(135deg,#0A0B0D,#151820,#0A0B0D); border:1px solid var(--border); border-top:3px solid var(--gold); border-radius:12px; padding:2rem 2.5rem; margin-bottom:1.5rem; position:relative; overflow:hidden; }
.hero::before { content:'🏇'; position:absolute; right:2rem; top:50%; transform:translateY(-50%); font-size:5rem; opacity:0.07; }
.hero h1 { font-family:'Bebas Neue',sans-serif; font-size:3rem; letter-spacing:4px; color:var(--gold); margin:0; line-height:1; }
.hero p { color:var(--muted); margin:0.4rem 0 0; font-size:0.9rem; }
.stat-box { background:var(--bg3); border:1px solid var(--border); border-radius:8px; padding:1rem; text-align:center; }
.stat-val { font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--gold); line-height:1; }
.stat-lbl { font-size:0.75rem; color:var(--muted); margin-top:0.2rem; }
.at-row { display:flex; align-items:center; padding:0.5rem 0; border-bottom:1px solid var(--border); gap:1rem; }
.at-no { font-family:'DM Mono',monospace; color:var(--muted); font-size:0.85rem; width:28px; text-align:center; }
.at-name { font-weight:500; flex:1; font-size:0.9rem; }
.at-score { font-family:'DM Mono',monospace; font-size:0.85rem; color:var(--gold); }
.ai-box { background:linear-gradient(135deg,#0D1117,#111827); border:1px solid #1E3A5F; border-left:3px solid var(--blue); border-radius:8px; padding:1rem 1.2rem; font-size:0.88rem; line-height:1.7; color:#CBD5E1; }
.info-strip { background:var(--bg3); border:1px solid var(--border); border-radius:8px; padding:0.8rem 1rem; font-size:0.82rem; color:var(--muted); margin-bottom:1rem; }
.date-chip { display:inline-block; background:var(--bg3); border:1px solid var(--border); border-radius:20px; padding:0.2rem 0.8rem; font-family:'DM Mono',monospace; font-size:0.78rem; color:var(--gold); margin-bottom:1rem; }
section[data-testid="stSidebar"] { background:var(--bg2) !important; border-right:1px solid var(--border) !important; }
.stButton > button { background:linear-gradient(135deg,var(--gold-dim),var(--gold)) !important; color:#000 !important; font-family:'Bebas Neue',sans-serif !important; font-size:1.1rem !important; letter-spacing:2px !important; border:none !important; border-radius:8px !important; padding:0.6rem 2rem !important; width:100% !important; }
.stTextInput > div > div > input { background:var(--bg3) !important; border:1px solid var(--border) !important; border-radius:8px !important; color:var(--text) !important; font-family:'DM Mono',monospace !important; }
div[data-testid="stExpander"] { background:var(--bg2) !important; border:1px solid var(--border) !important; border-radius:10px !important; }
hr { border-color:var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Veri Çekme ─────────────────────────────────────────────

def tarih_formatla_tr(tarih_ymd):
    d = datetime.strptime(tarih_ymd, "%Y-%m-%d")
    return d.strftime("%d/%m/%Y")

def sehirleri_cek(tarih_tr):
    url = f"https://www.tjk.org/TR/yarissever/Info/Page/GunlukYarisProgrami?QueryParameter_Tarih={tarih_tr}&Era=today"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
               "Accept": "text/html", "Accept-Language": "tr-TR,tr;q=0.9", "Referer": "https://www.tjk.org/"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        pattern = r'SehirId=(\d+)&QueryParameter_Tarih=[^&"]+&SehirAdi=([^&"]+)&Era=today'
        eslesimler = re.findall(pattern, r.text)
        sehirler = []
        goruldu = set()
        for sid, sadi in eslesimler:
            sadi_temiz = unquote(sadi).replace("+", " ")
            if sid not in goruldu:
                goruldu.add(sid)
                sehirler.append({"id": sid, "adi": sadi_temiz})
        return sehirler
    except:
        return []

def sehir_html_cek(tarih_tr, sehir_id, sehir_adi):
    tarih_enc = tarih_tr.replace("/", "%2F")
    url = (f"https://www.tjk.org/TR/yarissever/Info/Sehir/GunlukYarisProgrami"
           f"?SehirId={sehir_id}&QueryParameter_Tarih={tarih_enc}"
           f"&SehirAdi={quote(sehir_adi)}&Era=today")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
               "Accept": "text/html", "Accept-Language": "tr-TR,tr;q=0.9", "Referer": "https://www.tjk.org/"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        return r.text if r.status_code == 200 else None
    except:
        return None

def parse_atlar(satir_html):
    atlar = []
    satir_re = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
    td_re = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)
    temiz_re = re.compile(r'<[^>]+>')
    at_re = re.compile(r'QueryParameter_AtId=\d+[^"]*"[^>]*>\s*([A-ZÇĞİÖŞÜa-zçğışöü\s\'\-\.]+?)\s*\((\d+)\)', re.DOTALL)
    jokey_re = re.compile(r'JokeyIstatistikleri[^>]+title="([^"]+)"')
    for satir in satir_re.findall(satir_html):
        at_m = at_re.search(satir)
        if not at_m:
            continue
        at_isim = re.sub(r'\s+', ' ', at_m.group(1).strip())
        yaris_no = at_m.group(2)
        jokey_m = jokey_re.search(satir)
        jokey = jokey_m.group(1).strip() if jokey_m else "-"
        hucreler = td_re.findall(satir)
        temizler = [temiz_re.sub('', h).strip() for h in hucreler]
        hp = 0
        form = "-"
        for c in temizler:
            if re.match(r'^\d{2,3}$', c) and hp == 0:
                hp = int(c)
            if re.match(r'^[\d\-]+$', c) and len(c) >= 5 and '-' in c and form == "-":
                form = c
        atlar.append({"no": int(yaris_no), "isim": at_isim, "jokey": jokey, "hp": hp, "form": form})
    return atlar

def parse_kosular(html, sehir_adi):
    kosular = []
    pist_m = re.search(r'(Kum|Çim|Sentetik):\s*(\w+)', html)
    pist_genel = pist_m.group(1) if pist_m else "?"
    kosu_re = re.compile(r'(\d+)\.\s*Koşu[:\s]*([\d.]+)', re.IGNORECASE)
    mesafe_re = re.compile(r'(\d{3,4})\s+(Kum|Çim|Sentetik)', re.IGNORECASE)
    tur_re = re.compile(r'(Handikap\s*[\d/]*|ŞARTLI\s*[\d/]*|Maiden|Grup\s*\d*|DÜZLÜK)', re.IGNORECASE)
    pozlar = [(m.start(), m.group(1), m.group(2)) for m in kosu_re.finditer(html)]
    for idx, (pos, k_no, saat) in enumerate(pozlar):
        bitis = pozlar[idx+1][0] if idx+1 < len(pozlar) else len(html)
        blok = html[pos:bitis]
        m_m = mesafe_re.search(blok)
        mesafe = m_m.group(1) if m_m else "?"
        pist = m_m.group(2) if m_m else pist_genel
        tur_m = tur_re.search(blok)
        tur = tur_m.group(1).strip() if tur_m else "Düz Koşu"
        atlar = parse_atlar(blok)
        if atlar:
            kosular.append({"no": int(k_no), "sehir": sehir_adi, "saat": saat.strip(),
                            "mesafe": mesafe, "pist": pist, "tur": tur, "atlar": atlar})
    return kosular

YURT_DISI = ["ABD", "İngiltere", "Fransa", "Avustralya", "Afrika", "Japonya",
              "Almanya", "İtalya", "İrlanda", "BAE", "Kanada", "Guney",
              "Launceston", "Gulfstream", "Santa Anita", "Greyville", "Fairview"]

def tjk_veri_cek(tarih_ymd):
    tarih_tr = tarih_formatla_tr(tarih_ymd)
    sehirler = sehirleri_cek(tarih_tr)
    if not sehirler:
        return None, "Şehir listesi alınamadı"
    tum_kosular = []
    for s in sehirler:
        if any(k.lower() in s["adi"].lower() for k in YURT_DISI):
            continue
        html = sehir_html_cek(tarih_tr, s["id"], s["adi"])
        if html:
            kosular = parse_kosular(html, s["adi"])
            tum_kosular.extend(kosular)
    return {"tarih": tarih_ymd, "tarih_tr": tarih_tr, "kosular": tum_kosular, "kaynak": "tjk.org"}, None

def claude_analiz(api_key, kosu_no, kosu_bilgi, atlar):
    at_listesi = "\n".join([
        f"  At No {a['no']}: {a['isim']} | Jokey: {a['jokey']} | HP: {a['hp']} | Form: {a['form']}"
        for a in atlar
    ])
    prompt = f"""Sen TJK at yarışları uzmanısın.

KOŞU: {kosu_no}. Ayak | {kosu_bilgi.get('sehir','?')} | {kosu_bilgi.get('mesafe','?')}m {kosu_bilgi.get('pist','?')} | {kosu_bilgi.get('tur','?')} | Saat:{kosu_bilgi.get('saat','?')}

ATLAR:
{at_listesi}

Analiz et:
1. 🏆 BANKO: En güçlü 1 at (isim + kısa sebep)
2. 🥈 PLASE: 2-3 alternatif at
3. 📊 KAZANMA TAHMİNİ: Öne çıkan 4-5 at için % olasılık
4. 💡 KISA YORUM: 2-3 cümle

Türkçe, kısa ve net yaz. Bunun bir tahmin olduğunu belirt."""
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 600,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        if r.status_code == 200:
            return r.json()["content"][0]["text"], None
        return None, r.json().get("error", {}).get("message", f"HTTP {r.status_code}")
    except Exception as e:
        return None, str(e)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Bebas Neue,sans-serif;font-size:1.6rem;letter-spacing:3px;color:#D4A843;margin-bottom:1rem;">⚙ AYARLAR</div>', unsafe_allow_html=True)
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-api03-...",
                             help="console.anthropic.com adresinden ücretsiz alabilirsiniz.")
    st.markdown("---")
    tarih_sec = st.date_input("Analiz Tarihi", value=datetime.now().date())
    st.markdown("---")
    demo_mod = st.checkbox("📋 Demo Mod", value=not bool(api_key),
                            help="Örnek veriyle çalış (API key gerekmez)")
    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#5A5E6B;line-height:1.8;">🔒 API key sadece bu oturumda tutulur.<br>📡 Veri: tjk.org<br>🤖 Analiz: Claude Sonnet<br>⚠️ Yalnızca bilgi amaçlıdır.</div>', unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────
st.markdown('<div class="hero"><h1>BEYGİR ADAM</h1><p>Türkiye At Yarışları · Otomatik AI Analiz Sistemi · tjk.org</p></div>', unsafe_allow_html=True)
tarih_ymd = tarih_sec.strftime("%Y-%m-%d")
st.markdown(f'<div class="date-chip">📅 {tarih_sec.strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    calistir = st.button("📡 VERİ ÇEK & ANALİZ ET")
with col_btn2:
    if not api_key and not demo_mod:
        st.markdown('<div class="info-strip">💡 API key girin veya Demo Mod\'u açın</div>', unsafe_allow_html=True)

# ── Demo Veri ────────────────────────────────────────────────
def demo_veri():
    return {"tarih": tarih_ymd, "tarih_tr": tarih_sec.strftime("%d/%m/%Y"), "kosular": [
        {"no":1,"sehir":"İzmir (Şirinyer)","saat":"17.45","mesafe":"1600","pist":"Kum","tur":"Handikap",
         "atlar":[{"no":1,"isim":"WOLF DED","jokey":"Y.GÖKÇE","hp":86,"form":"51-261"},
                  {"no":2,"isim":"DEVIL STORM","jokey":"M.KEÇECİ","hp":82,"form":"112-475"},
                  {"no":3,"isim":"EL CACİQUE","jokey":"M.BİLGİN","hp":72,"form":"51-1131"},
                  {"no":4,"isim":"EAST SONATA","jokey":"G.GÖKÇE","hp":66,"form":"15-0011"},
                  {"no":5,"isim":"BOCCE","jokey":"N.AVCİ","hp":68,"form":"4-26631"}]},
        {"no":2,"sehir":"İzmir (Şirinyer)","saat":"18.30","mesafe":"1900","pist":"Kum","tur":"Şartlı",
         "atlar":[{"no":1,"isim":"CIX LIFE","jokey":"N.AVCİ","hp":91,"form":"243-350"},
                  {"no":2,"isim":"RED STORM","jokey":"M.ÇİÇEK","hp":84,"form":"113-522"},
                  {"no":3,"isim":"CANENCAN","jokey":"A.ALTIN","hp":80,"form":"3-35222"},
                  {"no":4,"isim":"GROUND SPEED","jokey":"G.GÖKÇE","hp":72,"form":"633346"},
                  {"no":5,"isim":"BOARDING PASS","jokey":"B.BÜLBÜL","hp":65,"form":"0-72155"}]},
        {"no":3,"sehir":"Antalya","saat":"19.00","mesafe":"1200","pist":"Kum","tur":"Maiden",
         "atlar":[{"no":1,"isim":"KAYAFATİH","jokey":"Ö.ÖZEN","hp":99,"form":"231373"},
                  {"no":2,"isim":"AKSU HAN","jokey":"A.KÜRÜNDÜK","hp":96,"form":"515-822"},
                  {"no":3,"isim":"ŞEKER HALHAL","jokey":"M.BİLGİN","hp":86,"form":"12400-7"},
                  {"no":4,"isim":"CANOĞLUCAN","jokey":"M.ÇİÇEK","hp":89,"form":"4-44921"},
                  {"no":5,"isim":"CANIM ÇITIR","jokey":"N.AVCİ","hp":82,"form":"541-532"}]},
    ]}

# ── Ana Mantık ────────────────────────────────────────────────
if calistir:
    if demo_mod:
        veri = demo_veri()
        st.markdown('<div class="info-strip">📋 <b>Demo Mod:</b> Örnek İzmir + Antalya verisi. Gerçek veri için API key girin.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("📡 tjk.org'dan program çekiliyor..."):
            veri, hata = tjk_veri_cek(tarih_ymd)

        if hata or not veri or not veri.get("kosular"):
            st.error(f"❌ Veri çekilemedi: {hata or 'Koşu bulunamadı'}")
            st.info("💡 Bugün yarış olmayabilir. Demo Mod'u açarak test edebilirsiniz.")
            st.stop()

    kosular = veri.get("kosular", [])

    if kosular:
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-val">{len(kosular)}</div><div class="stat-lbl">TOPLAM KOŞU</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-val">{sum(len(k["atlar"]) for k in kosular)}</div><div class="stat-lbl">TOPLAM AT</div></div>', unsafe_allow_html=True)
        with c3:
            sehirler = list(set(k["sehir"] for k in kosular))
            st.markdown(f'<div class="stat-box"><div class="stat-val">{len(sehirler)}</div><div class="stat-lbl">HİPODROM</div></div>', unsafe_allow_html=True)
        st.markdown("---")

        for kosu in kosular:
            atlar = kosu["atlar"]
            with st.expander(
                f"🏁 {kosu['no']}. AYAK  ·  {kosu['sehir']}  ·  {kosu['mesafe']}m {kosu['pist']}  ·  {kosu.get('saat','')}",
                expanded=(kosu["no"] <= 2)
            ):
                col_at, col_ai = st.columns([1, 1])

                with col_at:
                    st.markdown("**📋 Katılımcılar**")
                    sirali = sorted(atlar, key=lambda x: x.get("hp", 0), reverse=True)
                    for i, at in enumerate(sirali):
                        renk = "#D4A843" if i == 0 else "#9CA3AF" if i == 1 else "#5A5E6B"
                        hp_val = at.get("hp", 0)
                        st.markdown(f'''<div class="at-row">
                            <div class="at-no">{at["no"]}</div>
                            <div class="at-name">{at["isim"]}</div>
                            <div style="font-size:0.78rem;color:#5A5E6B;">{at["jokey"]}</div>
                            <div class="at-score" style="color:{renk};">{hp_val} HP</div>
                        </div>''', unsafe_allow_html=True)

                with col_ai:
                    st.markdown("**🤖 AI Analiz**")
                    key = f"analiz_{tarih_ymd}_{kosu['no']}_{kosu['sehir']}"

                    if key not in st.session_state:
                        if demo_mod or not api_key:
                            # Kural tabanlı demo analiz
                            sirali_at = sorted(atlar, key=lambda x: x.get("hp",0), reverse=True)
                            banko = sirali_at[0]
                            plaseler = sirali_at[1:3]
                            toplam_hp = sum(a.get("hp",50) for a in sirali_at) or 1
                            satirlar = [f"- {a['isim']}: %{max(5,int(a.get('hp',50)/toplam_hp*100))}" for a in sirali_at[:5]]
                            plase_str = ", ".join([p["isim"] + " (No:" + str(p["no"]) + ")" for p in plaseler])
                            analiz = (
                                "🏆 **BANKO:** " + banko["isim"] + " (No:" + str(banko["no"]) + ") — HP puanı en yüksek.\n\n"
                                "🥈 **PLASE:** " + plase_str + "\n\n"
                                "📊 **KAZANMA TAHMİNİ:**\n" + "\n".join(satirlar) + "\n\n"
                                "💡 **YORUM:** HP sıralamasına göre " + banko["isim"] + " bu koşunun favorisi. "
                                "Pist durumu ve jokey performansı sonucu etkileyebilir.\n\n"
                                "⚠️ *Demo mod — gerçek AI analizi için API key girin.*"
                            )
                            st.session_state[key] = analiz
                        else:
                            with st.spinner(f"{kosu['no']}. ayak analiz ediliyor..."):
                                sonuc, hata = claude_analiz(api_key, kosu["no"], kosu, atlar)
                                st.session_state[key] = sonuc if sonuc else f"❌ {hata}"
                            time.sleep(0.3)

                    analiz_txt = st.session_state.get(key, "")
                    if analiz_txt:
                        st.markdown(f'<div class="ai-box">{analiz_txt}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="info-strip" style="text-align:center;">⚠️ Yalnızca bilgi amaçlıdır. Kesin tahmin değildir. Sorumlu oynayın.</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:3rem 0;color:#5A5E6B;">
        <div style="font-size:3rem;margin-bottom:1rem;">🏇</div>
        <div style="font-family:Bebas Neue,sans-serif;font-size:1.5rem;letter-spacing:3px;color:#8B6914;margin-bottom:0.5rem;">HAZIR</div>
        <div style="font-size:0.9rem;">Sidebar'dan ayarlarınızı yapın, ardından<br>
        <b style="color:#D4A843;">VERİ ÇEK & ANALİZ ET</b> butonuna basın.</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="stat-box" style="text-align:left;"><div style="font-size:1.5rem;margin-bottom:0.5rem;">📡</div><div style="font-weight:500;margin-bottom:0.3rem;">Otomatik Veri</div><div style="font-size:0.8rem;color:#5A5E6B;">tjk.org sitesinden HTML parse ile çeker. 403 hatası yoktur.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-box" style="text-align:left;"><div style="font-size:1.5rem;margin-bottom:0.5rem;">🤖</div><div style="font-weight:500;margin-bottom:0.3rem;">AI Analiz</div><div style="font-size:0.8rem;color:#5A5E6B;">Claude AI her koşu için banko, plase ve kazanma tahmini üretir.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="stat-box" style="text-align:left;"><div style="font-size:1.5rem;margin-bottom:0.5rem;">🔒</div><div style="font-weight:500;margin-bottom:0.3rem;">Güvenli</div><div style="font-size:0.8rem;color:#5A5E6B;">API key sadece tarayıcı oturumunda tutulur, sunucuda saklanmaz.</div></div>', unsafe_allow_html=True)
