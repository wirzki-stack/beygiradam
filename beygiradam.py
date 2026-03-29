import streamlit as st
import requests, json, time, re
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


def claude_call(api_key, messages, max_tokens=4000, tools=None):
    """Claude API çağrısı yap."""
    body = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if tools:
        body["tools"] = tools
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json=body, timeout=60
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("error", {}).get("message", f"HTTP {r.status_code}")
    except Exception as e:
        return None, str(e)


def veri_ve_analiz_cek(api_key, tarih_str):
    """
    Claude'a web search + at yarışı analizi yaptır.
    Tek API çağrısında hem veriyi çektirir hem analiz ettirir.
    """
    gun = datetime.strptime(tarih_str, "%Y-%m-%d").strftime("%d.%m.%Y")

    # Web search aracını tanımla
    tools = [
        {
            "type": "web_search_20250305",
            "name": "web_search"
        }
    ]

    sistem = """Sen Türkiye TJK at yarışları analiz uzmanısın.
Görevin: İstenen tarihin TJK yarış programını web'den bulup, her koşu için detaylı analiz yapmak.

ÇIKTI FORMATI: Kesinlikle aşağıdaki JSON formatında yanıt ver, başka hiçbir şey yazma:
{
  "tarih": "GG.AA.YYYY",
  "kosular": [
    {
      "no": 1,
      "sehir": "İzmir",
      "saat": "14:30",
      "mesafe": "1600",
      "pist": "Kum",
      "tur": "Handikap",
      "atlar": [
        {"no": 1, "isim": "AT İSMİ", "jokey": "Jokey Adı", "hp": 85, "form": "1-2-3"},
        ...
      ],
      "analiz": {
        "banko": "AT İSMİ (No:X) — gerekçe",
        "plase": ["AT İSMİ", "AT İSMİ"],
        "tahmin": "HARD AND FAST: %45, CAN EFE: %25, CASH IS KING: %15, diğerleri: %15",
        "yorum": "2-3 cümle koşu yorumu"
      }
    }
  ]
}

Eğer veri bulamazsan: {"hata": "açıklama"}"""

    mesaj = f"""{gun} tarihli TJK at yarışı programını ara ve bul.

Şu kaynaklara bakabilirsin:
- sporx.com/at-yarisi
- tjk.org günlük program
- fanatik.com.tr hipodrom

Bugün hangi hipodromlarda (Türkiye'deki) yarış var, kaç koşu var, katılımcı atlar kimler?
Her koşu için: koşu no, saat, mesafe, pist, at isimleri, jokey, HP puanı ve son 6 yarış formunu bul.
Sonra her koşu için banko önerisi, plase adayları ve kazanma tahmini yap.

Tüm bilgileri JSON formatında döndür."""

    resp, err = claude_call(api_key, [{"role": "user", "content": mesaj}],
                           max_tokens=8000, tools=tools)
    if err:
        return None, err

    # Tool use döngüsü
    messages = [{"role": "user", "content": mesaj}]
    max_iter = 5
    for _ in range(max_iter):
        if not resp:
            break
        content = resp.get("content", [])
        stop = resp.get("stop_reason", "")

        if stop == "end_turn":
            # Son yanıtı bul
            for block in content:
                if block.get("type") == "text":
                    text = block["text"].strip()
                    # JSON çıkar
                    try:
                        m = re.search(r'\{.*\}', text, re.DOTALL)
                        if m:
                            return json.loads(m.group()), None
                    except:
                        pass
                    return None, "JSON parse hatası: " + text[:200]
            return None, "Yanıt boş"

        if stop == "tool_use":
            # Tool çağrısını işle
            messages.append({"role": "assistant", "content": content})
            tool_results = []
            for block in content:
                if block.get("type") == "tool_use":
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": "Arama yapıldı."
                    })
            messages.append({"role": "user", "content": tool_results})
            resp, err = claude_call(api_key, messages, max_tokens=8000, tools=tools)
            if err:
                return None, err
        else:
            break

    return None, "Yanıt alınamadı"


def claude_analiz_tek(api_key, kosu):
    """Tek koşu analizi (veri zaten elimizde ama analiz yoksa)."""
    at_listesi = "\n".join([
        f"  {a['no']}. {a['isim']} | Jokey: {a['jokey']} | HP: {a['hp']} | Form: {a['form']}"
        for a in kosu["atlar"]
    ])
    prompt = (
        f"TJK yarış analizi:\n"
        f"KOŞU: {kosu['no']}. Ayak | {kosu['sehir']} | {kosu['mesafe']}m {kosu['pist']} | Saat:{kosu['saat']}\n\n"
        f"KATILIMCILAR:\n{at_listesi}\n\n"
        f"1. BANKO: En guçlu 1 at\n2. PLASE: 2-3 alternatif\n"
        f"3. KAZANMA TAHMINI: % olasilik\n4. KISA YORUM\n\nTurkce, kisa."
    )
    resp, err = claude_call(api_key, [{"role": "user", "content": prompt}], max_tokens=600)
    if err:
        return None, err
    for block in resp.get("content", []):
        if block.get("type") == "text":
            return block["text"], None
    return None, "Yanıt boş"


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
    st.markdown('<div style="font-size:0.75rem;color:#5A5E6B;line-height:1.9;">🔒 Key sunucuda saklanmaz.<br>🌐 Veri: Claude web search<br>🤖 Analiz: Claude Sonnet<br>⚠️ Yalnızca bilgi amaçlıdır.</div>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown('<div class="hero"><h1>BEYGİR ADAM</h1><p>Türkiye At Yarışları · AI Destekli Otomatik Analiz · TJK Verisi</p></div>', unsafe_allow_html=True)
tarih_ymd = tarih_sec.strftime("%Y-%m-%d")
st.markdown(f'<div class="date-chip">📅 {tarih_sec.strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="info-strip">🔑 Sidebar\'dan <b>Anthropic API Key</b> girin. <a href="https://console.anthropic.com" target="_blank" style="color:#D4A843;">console.anthropic.com</a></div>', unsafe_allow_html=True)

calistir = st.button("🔍 VERİ ÇEK & ANALİZ ET", disabled=(not api_key))

# ── Ana Mantık ────────────────────────────────────────────────
if calistir and api_key:
    cache_key = f"veri_{tarih_ymd}"

    if cache_key not in st.session_state:
        with st.spinner("🌐 Claude web'den program arıyor ve analiz yapıyor... (30-60 sn)"):
            sonuc, hata = veri_ve_analiz_cek(api_key, tarih_ymd)
            if sonuc and "kosular" in sonuc:
                st.session_state[cache_key] = sonuc
            else:
                st.error("❌ " + (hata or sonuc.get("hata", "Veri alınamadı") if sonuc else "Veri alınamadı"))
                st.info("💡 Tarih seçimini kontrol edin veya tekrar deneyin.")
                st.stop()

    veri = st.session_state[cache_key]
    kosular = veri.get("kosular", [])

    if not kosular:
        st.warning("Koşu verisi boş geldi. Tekrar deneyin.")
        st.stop()

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    sehirler_list = list(set(k["sehir"] for k in kosular))
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(kosular)}</div><div class="stat-lbl">TOPLAM KOŞU</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{sum(len(k.get("atlar",[])) for k in kosular)}</div><div class="stat-lbl">TOPLAM AT</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(sehirler_list)}</div><div class="stat-lbl">HİPODROM</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    for kosu in sorted(kosular, key=lambda x: (x.get("sehir",""), x.get("no", 0))):
        atlar = sorted(kosu.get("atlar", []), key=lambda a: a.get("hp", 0), reverse=True)
        analiz = kosu.get("analiz", {})

        with st.expander(
            f"🏁 {kosu.get('no','?')}. AYAK  ·  {kosu.get('sehir','?')}  ·  {kosu.get('mesafe','?')}m {kosu.get('pist','?')}  ·  {kosu.get('saat','')}",
            expanded=False
        ):
            col_at, col_ai = st.columns([1, 1])
            with col_at:
                st.markdown("**📋 Katılımcılar** *(HP sırasıyla)*")
                for i, at in enumerate(atlar):
                    renk = "#D4A843" if i==0 else "#9CA3AF" if i==1 else "#5A5E6B"
                    st.markdown(
                        f'<div class="at-row">'
                        f'<div class="at-no">{at.get("no","?")}</div>'
                        f'<div class="at-name">{at.get("isim","?")}</div>'
                        f'<div class="at-jokey">{at.get("jokey","-")}</div>'
                        f'<div class="at-form">{at.get("form","-")}</div>'
                        f'<div class="at-hp" style="color:{renk};">{at.get("hp",0)} HP</div>'
                        f'</div>', unsafe_allow_html=True)

            with col_ai:
                st.markdown("**🤖 Claude AI Analiz**")
                if analiz:
                    txt = (
                        f"🏆 **BANKO:** {analiz.get('banko', '-')}\n\n"
                        f"🥈 **PLASE:** {', '.join(analiz.get('plase', []))}\n\n"
                        f"📊 **KAZANMA TAHMİNİ:**\n{analiz.get('tahmin', '-')}\n\n"
                        f"💡 **YORUM:** {analiz.get('yorum', '-')}\n\n"
                        f"⚠️ Bu tahmin amaçlıdır."
                    )
                    st.markdown(f'<div class="ai-box">{txt}</div>', unsafe_allow_html=True)
                else:
                    # Analiz yoksa ayrıca çek
                    akey = f"a_{tarih_ymd}_{kosu.get('sehir')}_{kosu.get('no')}"
                    if akey not in st.session_state:
                        with st.spinner("Analiz ediliyor..."):
                            sonuc, err = claude_analiz_tek(api_key, kosu)
                            st.session_state[akey] = sonuc if sonuc else ("❌ " + str(err))
                        time.sleep(0.3)
                    txt = st.session_state.get(akey, "")
                    if txt:
                        st.markdown(f'<div class="ai-box">{txt}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="info-strip" style="text-align:center;">⚠️ Yalnızca bilgi amaçlıdır. Kesin tahmin değildir. Sorumlu oynayın.</div>', unsafe_allow_html=True)

elif not calistir:
    st.markdown("""<div style="text-align:center;padding:3rem 0;color:#5A5E6B;">
        <div style="font-size:3rem;margin-bottom:1rem;">🏇</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:3px;color:#8B6914;margin-bottom:0.5rem;">HAZIR</div>
        <div style="font-size:0.9rem;">API key girin, ardından<br>
        <b style="color:#D4A843;">VERİ ÇEK & ANALİZ ET</b> butonuna basın.<br>
        <span style="font-size:0.8rem;color:#5A5E6B;">Claude web'den veriyi bulup analiz eder (~30-60 sn)</span></div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    for col, (ico, bas, ac) in zip([c1,c2,c3],[
        ("🌐","Web Search","Claude web'i arar, TJK programını bulur. Hiçbir site engeli yok."),
        ("🤖","AI Analiz","Veri çekme + analiz tek seferde. Banko, plase, tahmin."),
        ("🔒","Güvenli","Sunucudan dış istek atılmaz. Tüm işlem Claude API üzerinden."),
    ]):
        with col:
            st.markdown(f'<div class="stat-box" style="text-align:left;"><div style="font-size:1.5rem;margin-bottom:0.5rem;">{ico}</div><div style="font-weight:500;margin-bottom:0.3rem;">{bas}</div><div style="font-size:0.8rem;color:#5A5E6B;">{ac}</div></div>', unsafe_allow_html=True)
