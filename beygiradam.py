import streamlit as st
import json
import requests
from datetime import datetime, timedelta
import time

# ── Sayfa Ayarları ──────────────────────────────────────────
st.set_page_config(
    page_title="🏇 BeygiRadam | Otomatik Analiz",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Tasarımı ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --gold: #D4A843;
    --gold-dim: #8B6914;
    --bg: #0A0B0D;
    --bg2: #111318;
    --bg3: #1A1D25;
    --border: #252830;
    --text: #E8E9EC;
    --muted: #5A5E6B;
    --green: #22C55E;
    --red: #EF4444;
    --blue: #3B82F6;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--bg) !important; }

/* Header */
.hero {
    background: linear-gradient(135deg, #0A0B0D 0%, #151820 50%, #0A0B0D 100%);
    border: 1px solid var(--border);
    border-top: 3px solid var(--gold);
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '🏇';
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: 0.07;
}
.hero h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    letter-spacing: 4px;
    color: var(--gold);
    margin: 0;
    line-height: 1;
}
.hero p { color: var(--muted); margin: 0.4rem 0 0; font-size: 0.9rem; }

/* Koşu Kartı */
.kosu-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.kosu-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.4rem;
    letter-spacing: 2px;
    color: var(--gold);
    margin-bottom: 0.8rem;
}

/* Banko Badge */
.banko-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--gold-dim), var(--gold));
    color: #000;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1rem;
    letter-spacing: 2px;
    padding: 0.3rem 1rem;
    border-radius: 20px;
    margin-right: 0.5rem;
}
.plase-badge {
    display: inline-block;
    background: var(--bg3);
    border: 1px solid var(--border);
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    margin-right: 0.4rem;
}

/* At satırı */
.at-row {
    display: flex;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
    gap: 1rem;
}
.at-no {
    font-family: 'DM Mono', monospace;
    color: var(--muted);
    font-size: 0.85rem;
    width: 28px;
    text-align: center;
}
.at-name { font-weight: 500; flex: 1; font-size: 0.9rem; }
.at-score {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: var(--gold);
}

/* Stat kutuları */
.stat-box {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
.stat-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: var(--gold);
    line-height: 1;
}
.stat-lbl { font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem; }

/* AI Analiz kutusu */
.ai-box {
    background: linear-gradient(135deg, #0D1117, #111827);
    border: 1px solid #1E3A5F;
    border-left: 3px solid var(--blue);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #CBD5E1;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}

/* Butonlar */
.stButton > button {
    background: linear-gradient(135deg, var(--gold-dim), var(--gold)) !important;
    color: #000 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 2px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Input */
.stTextInput > div > div > input {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* Info kutusu */
.info-strip {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 1rem;
}

/* Tarih göstergesi */
.date-chip {
    display: inline-block;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--gold);
    margin-bottom: 1rem;
}

div[data-testid="stExpander"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

.element-container { margin-bottom: 0.5rem !important; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Yardımcı Fonksiyonlar ─────────────────────────────────────

def tjk_veri_cek(tarih_str=None):
    """TJK API'den günlük koşu programını çek."""
    if tarih_str is None:
        tarih_str = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y%m%d")

    url = f"https://api.tjk.org/v1/race/program/{tarih_str}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "tr-TR,tr;q=0.9"
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            return r.json(), None
        else:
            return None, f"TJK API yanıt vermedi (HTTP {r.status_code})"
    except Exception as e:
        return None, str(e)


def veri_isle(raw_data):
    """Ham TJK verisini temiz koşu listesine dönüştür."""
    kosular = []
    try:
        # TJK API yapısına göre parse et
        program = raw_data
        if isinstance(program, dict):
            program = program.get("data", program.get("races", program.get("program", [])))
        if not isinstance(program, list):
            return []

        for kosu in program:
            try:
                atlar = []
                runners = kosu.get("runners", kosu.get("horses", kosu.get("starters", [])))
                for at in runners:
                    atlar.append({
                        "no": at.get("runnerNo", at.get("no", at.get("number", "?"))),
                        "isim": at.get("horseName", at.get("name", at.get("horse", "Bilinmiyor"))),
                        "jokey": at.get("jockeyName", at.get("jockey", "-")),
                        "kilo": at.get("weight", at.get("kilo", "-")),
                        "hp": at.get("hp", at.get("score", at.get("rating", 0))),
                        "yas": at.get("age", "-"),
                        "form": at.get("form", at.get("lastRaces", "-")),
                    })

                kosular.append({
                    "no": kosu.get("raceNo", kosu.get("no", len(kosular)+1)),
                    "sehir": kosu.get("hippodromeName", kosu.get("city", kosu.get("track", "?"))),
                    "mesafe": kosu.get("distance", "-"),
                    "pist": kosu.get("trackCondition", kosu.get("ground", "-")),
                    "tur": kosu.get("raceType", kosu.get("type", "-")),
                    "atlar": atlar
                })
            except:
                continue
    except Exception as e:
        pass
    return kosular


def claude_analiz(api_key, kosu_no, kosu_bilgi, atlar):
    """Claude API ile bir koşuyu analiz et."""
    at_listesi = "\n".join([
        f"  At No {a['no']}: {a['isim']} | Jokey: {a['jokey']} | HP: {a['hp']} | Form: {a['form']}"
        for a in atlar
    ])

    prompt = f"""Sen Türkiye'deki TJK (Türkiye Jokey Kulübü) at yarışlarında uzman bir analistsin.

KOŞU BİLGİSİ:
- Koşu: {kosu_no}. Ayak
- Şehir/Hipodrom: {kosu_bilgi.get('sehir', '?')}
- Mesafe: {kosu_bilgi.get('mesafe', '?')} metre
- Pist: {kosu_bilgi.get('pist', '?')}
- Tür: {kosu_bilgi.get('tur', '?')}

YARIŞACAK ATLAR:
{at_listesi}

Lütfen bu koşuyu analiz et ve şunu ver:
1. 🏆 BANKO: En güçlü 1 at (isim ve neden)
2. 🥈 PLASE: 2-3 güçlü alternatif at (isim listesi)
3. 📊 KAZANMA TAHMİNLERİ: Her at için kısa % tahmini (sadece öne çıkan 4-5 at)
4. 💡 KISA ANALİZ: 2-3 cümle koşu yorumu

Yanıtı kısa, net ve Türkçe ver. Kesin yargılardan kaçın, tahmin olduğunu belirt."""

    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 600,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        if r.status_code == 200:
            return r.json()["content"][0]["text"], None
        else:
            err = r.json().get("error", {}).get("message", f"HTTP {r.status_code}")
            return None, err
    except Exception as e:
        return None, str(e)


def demo_veri_olustur():
    """API çalışmadığında gösterim için örnek veri."""
    return [
        {
            "no": 1,
            "sehir": "İstanbul (Veliefendi)",
            "mesafe": "1400",
            "pist": "Çim",
            "tur": "Düz Koşu",
            "atlar": [
                {"no": 1, "isim": "RÜZGAR GELİNİ", "jokey": "A. Çelik", "kilo": "57", "hp": 98, "form": "1-2-1"},
                {"no": 2, "isim": "KARADENİZ", "jokey": "M. Kaya", "kilo": "55", "hp": 87, "form": "2-3-2"},
                {"no": 3, "isim": "ALTINOK", "jokey": "S. Demir", "kilo": "56", "hp": 82, "form": "1-4-3"},
                {"no": 4, "isim": "EGE FIRTINASI", "jokey": "E. Yılmaz", "kilo": "54", "hp": 75, "form": "3-2-5"},
                {"no": 5, "isim": "BOZKIR", "jokey": "T. Arslan", "kilo": "58", "hp": 71, "form": "5-1-4"},
            ]
        },
        {
            "no": 2,
            "sehir": "Ankara (75. Yıl)",
            "mesafe": "1200",
            "pist": "Kum",
            "tur": "Handikap",
            "atlar": [
                {"no": 1, "isim": "ŞAHIN", "jokey": "K. Polat", "kilo": "60", "hp": 94, "form": "1-1-2"},
                {"no": 2, "isim": "FIRAT", "jokey": "H. Öztürk", "kilo": "57", "hp": 88, "form": "2-1-3"},
                {"no": 3, "isim": "ÇINAR", "jokey": "R. Güneş", "kilo": "55", "hp": 79, "form": "4-2-1"},
                {"no": 4, "isim": "MARMARA", "jokey": "B. Koç", "kilo": "56", "hp": 68, "form": "3-5-2"},
            ]
        },
        {
            "no": 3,
            "sehir": "İzmir (Şirinyer)",
            "mesafe": "1600",
            "pist": "Çim",
            "tur": "Maiden",
            "atlar": [
                {"no": 1, "isim": "AKDENIZ RÜZGARI", "jokey": "C. Şahin", "kilo": "54", "hp": 91, "form": "1-3-1"},
                {"no": 2, "isim": "TOROS", "jokey": "N. Aydın", "kilo": "56", "hp": 85, "form": "2-2-4"},
                {"no": 3, "isim": "GEZGİN", "jokey": "F. Kurt", "kilo": "55", "hp": 80, "form": "3-1-2"},
                {"no": 4, "isim": "YILDIRIM", "jokey": "U. Doğan", "kilo": "57", "hp": 72, "form": "4-4-3"},
                {"no": 5, "isim": "SÜRMELI", "jokey": "I. Taş", "kilo": "53", "hp": 65, "form": "5-3-5"},
            ]
        }
    ]


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family: Bebas Neue, sans-serif; font-size: 1.6rem; 
                letter-spacing: 3px; color: #D4A843; margin-bottom: 1rem;'>
        ⚙ AYARLAR
    </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        help="console.anthropic.com adresinden alabilirsiniz."
    )

    st.markdown("---")

    tarih_sec = st.date_input(
        "Analiz Tarihi",
        value=datetime.now().date(),
        help="Hangi günün programı analiz edilsin?"
    )

    st.markdown("---")

    demo_mod = st.checkbox(
        "📋 Demo Mod",
        value=not bool(api_key),
        help="TJK API yerine örnek veriyle çalış"
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.75rem; color: #5A5E6B; line-height: 1.6;'>
    🔒 API key'iniz sadece bu oturumda kullanılır, hiçbir yerde saklanmaz.<br><br>
    📡 Veri kaynağı: api.tjk.org<br><br>
    🤖 Analiz: Claude Sonnet<br><br>
    ⚠️ Bu uygulama yalnızca bilgi amaçlıdır.
    </div>
    """, unsafe_allow_html=True)


# ── Ana Sayfa ─────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>BEYGİR ADAM</h1>
    <p>Türkiye At Yarışları · Otomatik AI Analiz Sistemi · TJK Verisi</p>
</div>
""", unsafe_allow_html=True)

tarih_str = tarih_sec.strftime("%Y%m%d")
tarih_goster = tarih_sec.strftime("%d %B %Y")

st.markdown(f'<div class="date-chip">📅 {tarih_goster}</div>', unsafe_allow_html=True)

# ── Veri Çekme Butonu ─────────────────────────────────────────
col_btn1, col_btn2 = st.columns([1, 1])

with col_btn1:
    veri_cek_btn = st.button("📡 VERİ ÇEK & ANALİZ ET")

with col_btn2:
    if not api_key and not demo_mod:
        st.markdown("""
        <div class="info-strip">
        💡 API key girin veya Demo Mod'u açın
        </div>
        """, unsafe_allow_html=True)


# ── Ana Mantık ────────────────────────────────────────────────
if veri_cek_btn:
    # Veriyi al
    if demo_mod:
        kosular = demo_veri_olustur()
        st.markdown("""
        <div class="info-strip">
        📋 <b>Demo Mod:</b> Gerçek TJK verisi yerine örnek veri kullanılıyor.
        Gerçek analiz için API key girin ve Demo Mod'u kapatın.
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner(f"📡 TJK API'den {tarih_goster} programı çekiliyor..."):
            raw, hata = tjk_veri_cek(tarih_str)

        if hata or not raw:
            st.error(f"❌ Veri çekilemedi: {hata or 'Boş yanıt'}")
            st.info("💡 Demo Mod'u açarak örnek verilerle analizi deneyebilirsiniz.")
            kosular = []
        else:
            kosular = veri_isle(raw)
            if not kosular:
                st.warning("⚠️ Veri çekildi ancak koşu bulunamadı. Bugün program olmayabilir veya API yapısı değişmiş olabilir.")
                st.info("Demo Mod ile test edebilirsiniz.")
                kosular = []

    if kosular:
        # Özet istatistikler
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-val">{len(kosular)}</div>
                <div class="stat-lbl">TOPLAM KOŞU</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            toplam_at = sum(len(k["atlar"]) for k in kosular)
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-val">{toplam_at}</div>
                <div class="stat-lbl">TOPLAM AT</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            sehirler = list(set(k["sehir"] for k in kosular))
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-val">{len(sehirler)}</div>
                <div class="stat-lbl">HİPODROM</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Her koşuyu göster ve analiz et
        for kosu in kosular:
            kosu_no = kosu["no"]
            atlar = kosu["atlar"]

            with st.expander(
                f"🏁  {kosu_no}. AYAK  ·  {kosu['sehir']}  ·  {kosu['mesafe']}m  ·  {kosu['pist']}",
                expanded=(kosu_no <= 3)
            ):
                col_at, col_ai = st.columns([1, 1])

                # Sol: At listesi
                with col_at:
                    st.markdown("**📋 Katılımcılar**")
                    if atlar:
                        atlar_sirali = sorted(atlar, key=lambda x: (x.get("hp") or 0), reverse=True)
                        for i, at in enumerate(atlar_sirali):
                            hp_val = at.get("hp") or 0
                            renk = "#D4A843" if i == 0 else ("#9CA3AF" if i == 1 else "#5A5E6B")
                            st.markdown(f"""
                            <div class="at-row">
                                <div class="at-no">{at['no']}</div>
                                <div class="at-name">{at['isim']}</div>
                                <div style="font-size:0.78rem; color:#5A5E6B;">{at['jokey']}</div>
                                <div class="at-score" style="color:{renk};">{hp_val} HP</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("At bilgisi bulunamadı.")

                # Sağ: AI Analiz
                with col_ai:
                    st.markdown("**🤖 AI Analiz**")

                    if not api_key and not demo_mod:
                        st.markdown("""
                        <div class="ai-box">
                        🔑 AI analizi için sidebar'dan API key girin.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        analiz_key = f"analiz_{tarih_str}_{kosu_no}"

                        if analiz_key not in st.session_state:
                            if demo_mod:
                                # Demo için basit kural tabanlı analiz
                                if atlar:
                                    sirali = sorted(atlar, key=lambda x: x.get("hp") or 0, reverse=True)
                                    banko = sirali[0]
                                    plaseler = sirali[1:3]
                                    analiz = f"""🏆 **BANKO:** {banko['isim']} (No:{banko['no']}) — HP puanı en yüksek at, formu da güçlü.

🥈 **PLASE:** {', '.join([f"{p['isim']} (No:{p['no']})" for p in plaseler])}

📊 **KAZANMA TAHMİNLERİ:**
{chr(10).join([f"- {a['isim']}: %{max(5, int((a.get('hp') or 50) / sum(x.get('hp') or 50 for x in atlar) * 100))} tahmini olasılık" for a in sirali[:4]])}

💡 **KISA ANALİZ:** Bu koşuda HP puanına göre {banko['isim']} öne çıkıyor. Kum/çim farkı ve form durumu değerlendirmeyi etkileyebilir. Yatırım kararlarınızda kendi araştırmanızı da göz önünde bulundurun.

⚠️ *Bu demo modda kural tabanlı tahmindir, gerçek AI analizi değildir.*"""
                                    st.session_state[analiz_key] = analiz
                                else:
                                    st.session_state[analiz_key] = "At verisi yok."
                            else:
                                with st.spinner(f"{kosu_no}. ayak analiz ediliyor..."):
                                    sonuc, hata = claude_analiz(api_key, kosu_no, kosu, atlar)
                                    if hata:
                                        st.session_state[analiz_key] = f"❌ Hata: {hata}"
                                    else:
                                        st.session_state[analiz_key] = sonuc
                                    time.sleep(0.5)  # rate limit

                        analiz_metni = st.session_state.get(analiz_key, "")
                        if analiz_metni:
                            st.markdown(f'<div class="ai-box">{analiz_metni}</div>', unsafe_allow_html=True)

        # Alt uyarı
        st.markdown("---")
        st.markdown("""
        <div class="info-strip" style="text-align:center;">
        ⚠️ Bu uygulama yalnızca bilgi ve eğlence amaçlıdır. Kesin tahmin değildir. 
        Yarış sonuçları her zaman belirsizlik içerir. Sorumlu oynayın.
        </div>
        """, unsafe_allow_html=True)

else:
    # Başlangıç ekranı
    st.markdown("""
    <div style='text-align:center; padding: 3rem 0; color: #5A5E6B;'>
        <div style='font-size: 3rem; margin-bottom: 1rem;'>🏇</div>
        <div style='font-family: Bebas Neue, sans-serif; font-size: 1.5rem; 
                    letter-spacing: 3px; color: #8B6914; margin-bottom: 0.5rem;'>
            HAZIR
        </div>
        <div style='font-size: 0.9rem;'>
            Sidebar'dan ayarlarınızı yapın, ardından<br>
            <b style='color: #D4A843;'>VERİ ÇEK & ANALİZ ET</b> butonuna basın.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nasıl çalışır
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stat-box" style="text-align:left;">
            <div style='font-size:1.5rem; margin-bottom:0.5rem;'>📡</div>
            <div style='font-weight:500; margin-bottom:0.3rem;'>Otomatik Veri</div>
            <div style='font-size:0.8rem; color:#5A5E6B;'>
            TJK resmi API'sinden günlük yarış programını otomatik çeker. Koşu, at, jokey bilgisi.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-box" style="text-align:left;">
            <div style='font-size:1.5rem; margin-bottom:0.5rem;'>🤖</div>
            <div style='font-weight:500; margin-bottom:0.3rem;'>AI Analiz</div>
            <div style='font-size:0.8rem; color:#5A5E6B;'>
            Claude AI her koşu için banko önerisi, plase adayları ve kazanma tahminleri üretir.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-box" style="text-align:left;">
            <div style='font-size:1.5rem; margin-bottom:0.5rem;'>🔒</div>
            <div style='font-weight:500; margin-bottom:0.3rem;'>Güvenli</div>
            <div style='font-size:0.8rem; color:#5A5E6B;'>
            API key'iniz sadece tarayıcı oturumunda tutulur, hiçbir sunucuda saklanmaz.
            </div>
        </div>
        """, unsafe_allow_html=True)
