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
.hero{background:linear-gradient(135deg,#0A0B0D,#151820,#0A0B0D);border:1px solid var(--border);border-top:3px solid var(--gold);border-radius:12px;padding:2rem 2.5rem;margin-bottom:1.5rem;}
.hero h1{font-family:'Bebas Neue',sans-serif;font-size:3rem;letter-spacing:4px;color:var(--gold);margin:0;}
.hero p{color:var(--muted);margin:0.4rem 0 0;font-size:0.9rem;}
.stat-box{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:1rem;text-align:center;}
.stat-val{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:var(--gold);line-height:1;}
.stat-lbl{font-size:0.75rem;color:var(--muted);margin-top:0.2rem;}
.at-row{display:flex;align-items:center;padding:0.45rem 0;border-bottom:1px solid var(--border);gap:0.8rem;}
.at-no{font-family:'DM Mono',monospace;color:var(--muted);font-size:0.82rem;width:26px;}
.at-name{font-weight:500;flex:1;font-size:0.88rem;}
.at-jokey{font-size:0.75rem;color:var(--muted);min-width:90px;}
.at-hp{font-family:'DM Mono',monospace;font-size:0.82rem;}
.at-form{font-family:'DM Mono',monospace;font-size:0.75rem;color:var(--muted);min-width:60px;text-align:right;}
.ai-box{background:linear-gradient(135deg,#0D1117,#111827);border:1px solid #1E3A5F;border-left:3px solid var(--blue);border-radius:8px;padding:1rem 1.2rem;font-size:0.87rem;line-height:1.75;color:#CBD5E1;white-space:pre-wrap;}
.info-strip{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:0.8rem 1rem;font-size:0.82rem;color:var(--muted);margin-bottom:1rem;}
.date-chip{display:inline-block;background:var(--bg3);border:1px solid var(--border);border-radius:20px;padding:0.2rem 0.8rem;font-family:'DM Mono',monospace;font-size:0.78rem;color:var(--gold);margin-bottom:1rem;}
section[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
.stButton>button{background:linear-gradient(135deg,var(--gold-dim),var(--gold))!important;color:#000!important;font-family:'Bebas Neue',sans-serif!important;font-size:1.1rem!important;letter-spacing:2px!important;border:none!important;border-radius:8px!important;padding:0.6rem 2rem!important;width:100%!important;}
.stTextInput>div>div>input{background:var(--bg3)!important;border:1px solid var(--border)!important;color:var(--text)!important;font-family:'DM Mono',monospace!important;}
div[data-testid="stExpander"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:10px!important;}
hr{border-color:var(--border)!important;}
</style>
""", unsafe_allow_html=True)


def claude_api(api_key, messages, tools=None, max_tokens=8000):
    body = {"model": "claude-sonnet-4-20250514", "max_tokens": max_tokens, "messages": messages}
    if tools:
        body["tools"] = tools
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json=body, timeout=120
    )
    return r.status_code, r.json()


def veri_cek_web_search(api_key, gun_tr):
    """
    Claude web_search aracını kullanarak TJK programını çeker.
    Tool-use döngüsünü tam uygular.
    """
    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    system_prompt = """Sen TJK at yarışları uzmanısın. Web araması yaparak istenen günün yarış programını bul.
    
MUTLAKA aşağıdaki JSON formatında yanıt ver (başka bir şey yazma, sadece JSON):
{
  "kosular": [
    {
      "no": 1,
      "sehir": "İzmir",
      "saat": "14:30",
      "mesafe": "1600",
      "pist": "Kum",
      "tur": "Handikap",
      "atlar": [
        {"no": 1, "isim": "AT ADI", "jokey": "JOKEY ADI", "hp": 85, "form": "1-2-3"}
      ],
      "banko": "AT ADI (No:1)",
      "plase": "AT ADI, AT ADI",
      "tahmin": "AT1: %40, AT2: %25, AT3: %15",
      "yorum": "Koşu yorumu"
    }
  ]
}"""

    user_msg = f"""{gun_tr} tarihli TJK at yarışı programını bul.
    
sporx.com/at-yarisi veya tjk.org adreslerinde ara.
Türkiye'deki hipodromlarda (İzmir, Adana, Ankara, İstanbul, Bursa vb.) bugün hangi koşular var?
Her koşudaki atları, jokeyleri, HP puanlarını ve formu bul.
Sonra her koşu için banko, plase ve kazanma tahmini yap.
Tüm yanıtı SADECE JSON olarak ver."""

    messages = [{"role": "user", "content": user_msg}]
    debug_log = []

    for iterasyon in range(6):
        debug_log.append(f"İterasyon {iterasyon+1}: Claude'a istek gönderiliyor...")
        status, resp = claude_api(api_key, messages, tools=tools)
        debug_log.append(f"HTTP {status}, stop_reason: {resp.get('stop_reason', '?')}")

        if status != 200:
            err = resp.get("error", {}).get("message", f"HTTP {status}")
            debug_log.append(f"HATA: {err}")
            return None, "\n".join(debug_log) + f"\n\nAPI Hatası: {err}"

        content = resp.get("content", [])
        stop_reason = resp.get("stop_reason", "")

        if stop_reason == "end_turn":
            for block in content:
                if block.get("type") == "text":
                    text = block["text"].strip()
                    debug_log.append(f"Metin alındı ({len(text)} karakter)")
                    # JSON çıkar
                    try:
                        # Doğrudan JSON
                        data = json.loads(text)
                        if "kosular" in data:
                            debug_log.append(f"✅ {len(data['kosular'])} koşu bulundu!")
                            return data, None
                    except:
                        pass
                    try:
                        # JSON bloğu içinde
                        m = re.search(r'\{[\s\S]*"kosular"[\s\S]*\}', text)
                        if m:
                            data = json.loads(m.group())
                            if "kosular" in data:
                                debug_log.append(f"✅ {len(data['kosular'])} koşu bulundu!")
                                return data, None
                    except:
                        pass
                    # JSON yok, ham metni döndür
                    debug_log.append("JSON parse başarısız, ham metin:")
                    debug_log.append(text[:500])
                    return {"_ham_metin": text, "kosular": []}, "\n".join(debug_log)
            return None, "\n".join(debug_log) + "\n\nİçerik boş"

        elif stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": content})
            tool_results = []
            for block in content:
                if block.get("type") == "tool_use":
                    debug_log.append(f"Tool: {block.get('name')} — input: {str(block.get('input',''))[:100]}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": "Arama tamamlandı."
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            debug_log.append(f"Beklenmeyen stop_reason: {stop_reason}")
            break

    return None, "\n".join(debug_log) + "\n\nMaks iterasyona ulaşıldı"


def claude_analiz(api_key, kosu):
    at_listesi = "\n".join([
        f"  {a['no']}. {a['isim']} | Jokey: {a['jokey']} | HP: {a['hp']} | Form: {a['form']}"
        for a in kosu.get("atlar", [])
    ])
    prompt = (
        f"TJK koşu analizi:\n"
        f"KOŞU: {kosu['no']}. Ayak | {kosu['sehir']} | {kosu['mesafe']}m {kosu['pist']} | {kosu['saat']}\n\n"
        f"ATLAR:\n{at_listesi}\n\n"
        f"1. BANKO: En iyi 1 at (kısa gerekçe)\n"
        f"2. PLASE: 2-3 alternatif\n"
        f"3. KAZANMA TAHMİNİ: % olasılık\n"
        f"4. KISA YORUM\n\nTürkçe, kısa."
    )
    _, resp = claude_api(api_key, [{"role": "user", "content": prompt}], max_tokens=600)
    for block in resp.get("content", []):
        if block.get("type") == "text":
            return block["text"]
    return "Analiz alınamadı."


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
        st.markdown('<div style="font-size:0.8rem;color:#22C55E;padding:0.5rem;background:#071407;border:1px solid #166534;border-radius:6px;margin-bottom:0.8rem;">✅ API Key aktif</div>', unsafe_allow_html=True)
    else:
        inp = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-api03-...", key="ak")
        if inp:
            api_key = inp
    st.markdown("---")
    tarih_sec = st.date_input("Analiz Tarihi", value=datetime.now().date())
    st.markdown("---")
    debug_mod = st.checkbox("🔧 Debug Modu", value=False, help="Hata detaylarını göster")
    st.markdown("---")
    st.markdown('<div style="font-size:0.75rem;color:#5A5E6B;line-height:1.9;">🌐 Veri: Claude web search<br>🤖 Analiz: Claude Sonnet<br>⚠️ Yalnızca bilgi amaçlıdır.</div>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown('<div class="hero"><h1>BEYGİR ADAM</h1><p>Türkiye At Yarışları · AI Destekli Analiz · TJK Verisi</p></div>', unsafe_allow_html=True)
tarih_ymd = tarih_sec.strftime("%Y-%m-%d")
gun_tr = tarih_sec.strftime("%d.%m.%Y")
st.markdown(f'<div class="date-chip">📅 {tarih_sec.strftime("%d %B %Y")}</div>', unsafe_allow_html=True)

if not api_key:
    st.markdown('<div class="info-strip">🔑 Sidebar\'dan <b>Anthropic API Key</b> girin.</div>', unsafe_allow_html=True)

calistir = st.button("🔍 VERİ ÇEK & ANALİZ ET", disabled=(not api_key))

# ── Ana Mantık ────────────────────────────────────────────────
if calistir and api_key:
    cache_key = f"veri_{tarih_ymd}"
    debug_key = f"debug_{tarih_ymd}"

    if cache_key not in st.session_state:
        with st.spinner(f"🌐 Claude {gun_tr} programını web'den arıyor... (30-90 sn sürebilir)"):
            veri, debug_bilgi = veri_cek_web_search(api_key, gun_tr)
            st.session_state[debug_key] = debug_bilgi or ""
            if veri and veri.get("kosular"):
                st.session_state[cache_key] = veri
            else:
                st.session_state[cache_key] = None

    if debug_mod and st.session_state.get(debug_key):
        with st.expander("🔧 Debug Log", expanded=True):
            st.code(st.session_state[debug_key])

    veri = st.session_state.get(cache_key)

    if not veri or not veri.get("kosular"):
        # Ham metin varsa göster
        if veri and veri.get("_ham_metin"):
            st.warning("⚠️ JSON parse başarısız. Claude'un ham yanıtı:")
            st.text_area("Ham yanıt", veri["_ham_metin"], height=300)
        else:
            st.error("❌ Veri alınamadı. Debug modunu açın ve tekrar deneyin.")
        if st.button("🔄 Temizle ve Tekrar Dene"):
            for k in list(st.session_state.keys()):
                if k.startswith("veri_") or k.startswith("debug_"):
                    del st.session_state[k]
            st.rerun()
        st.stop()

    kosular = veri["kosular"]
    st.success(f"✅ {len(kosular)} koşu bulundu!")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    sehirler_list = list(set(k.get("sehir","?") for k in kosular))
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(kosular)}</div><div class="stat-lbl">TOPLAM KOŞU</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{sum(len(k.get("atlar",[])) for k in kosular)}</div><div class="stat-lbl">TOPLAM AT</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{len(sehirler_list)}</div><div class="stat-lbl">HİPODROM</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    for kosu in sorted(kosular, key=lambda x: (x.get("sehir",""), x.get("no",0))):
        atlar = sorted(kosu.get("atlar",[]), key=lambda a: a.get("hp",0), reverse=True)
        with st.expander(
            f"🏁 {kosu.get('no','?')}. AYAK  ·  {kosu.get('sehir','?')}  ·  {kosu.get('mesafe','?')}m {kosu.get('pist','?')}  ·  {kosu.get('saat','')}",
            expanded=False
        ):
            col_at, col_ai = st.columns([1, 1])
            with col_at:
                st.markdown("**📋 Katılımcılar**")
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
                # Önce koşu içindeki analizi kullan
                banko = kosu.get("banko","")
                plase = kosu.get("plase","")
                tahmin = kosu.get("tahmin","")
                yorum = kosu.get("yorum","")

                if banko:
                    txt = f"🏆 BANKO: {banko}\n\n🥈 PLASE: {plase}\n\n📊 TAHMİN: {tahmin}\n\n💡 YORUM: {yorum}\n\n⚠️ Tahmin amaçlıdır."
                    st.markdown(f'<div class="ai-box">{txt}</div>', unsafe_allow_html=True)
                elif atlar:
                    akey = f"a_{tarih_ymd}_{kosu.get('sehir')}_{kosu.get('no')}"
                    if akey not in st.session_state:
                        with st.spinner("Analiz ediliyor..."):
                            st.session_state[akey] = claude_analiz(api_key, kosu)
                        time.sleep(0.3)
                    txt = st.session_state.get(akey, "")
                    if txt:
                        st.markdown(f'<div class="ai-box">{txt}</div>', unsafe_allow_html=True)
                else:
                    st.info("At verisi yok.")

    st.markdown("---")
    st.markdown('<div class="info-strip" style="text-align:center;">⚠️ Yalnızca bilgi amaçlıdır. Kesin tahmin değildir.</div>', unsafe_allow_html=True)

elif not calistir:
    st.markdown("""<div style="text-align:center;padding:2rem 0;color:#5A5E6B;">
        <div style="font-size:3rem;margin-bottom:1rem;">🏇</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:3px;color:#8B6914;margin-bottom:0.5rem;">HAZIR</div>
        <div style="font-size:0.9rem;">API key girin → Butona bas<br>
        <span style="font-size:0.8rem;color:#5A5E6B;">Claude web'den veriyi arar (~30-90 sn)</span></div>
    </div>""", unsafe_allow_html=True)
