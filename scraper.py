"""
scraper.py — TJK web sitesinden günlük at yarışı programını çeker.
HTML parse yöntemi kullanır (api.tjk.org yerine), 403 sorunu yoktur.
Çıktı: veriler.json
"""
import requests
import json
import re
import sys
from datetime import datetime, timedelta
from urllib.parse import unquote, quote


def bugunun_tarihini_al():
    return (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d")


def tarih_formatla_tr(tarih_ymd):
    d = datetime.strptime(tarih_ymd, "%Y-%m-%d")
    return d.strftime("%d/%m/%Y")


def sehirleri_cek(tarih_tr):
    url = f"https://www.tjk.org/TR/yarissever/Info/Page/GunlukYarisProgrami?QueryParameter_Tarih={tarih_tr}&Era=today"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.tjk.org/",
    }
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
        print(f"📍 {len(sehirler)} hipodrom: {[s['adi'] for s in sehirler]}")
        return sehirler
    except Exception as e:
        print(f"❌ Şehir listesi hatası: {e}")
        return []


def sehir_html_cek(tarih_tr, sehir_id, sehir_adi):
    tarih_encoded = tarih_tr.replace("/", "%2F")
    sehir_encoded = quote(sehir_adi)
    url = (f"https://www.tjk.org/TR/yarissever/Info/Sehir/GunlukYarisProgrami"
           f"?SehirId={sehir_id}&QueryParameter_Tarih={tarih_encoded}"
           f"&SehirAdi={sehir_encoded}&Era=today")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.tjk.org/",
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            return r.text
        print(f"  ⚠️ {sehir_adi}: HTTP {r.status_code}")
        return None
    except Exception as e:
        print(f"  ❌ {sehir_adi}: {e}")
        return None


def parse_kosular(html, sehir_adi):
    kosular = []

    # Pist/hava bilgisi
    pist_m = re.search(r'(Kum|Çim|Sentetik):\s*(\w+)', html)
    pist_genel = pist_m.group(1) if pist_m else "?"
    pist_durum = pist_m.group(2) if pist_m else "?"

    # Koşu bloklarını ayır — "### X. Koşu" ya da "<h3>X. Koşu"
    # TJK HTML'de anchor ID'leri var: <h3...id="XXXXXX">
    # Daha güvenilir: tablo içeriğini regex ile çek

    # Her koşu için "X. Koşu:HH.MM" başlığını bul
    kosu_re = re.compile(r'(\d+)\.\s*Koşu[:\s]*([\d.]+)', re.IGNORECASE)
    mesafe_re = re.compile(r'(\d{3,4})\s+(Kum|Çim|Sentetik)', re.IGNORECASE)
    tur_re = re.compile(r'(Handikap\s*[\d/]*|ŞARTLI\s*[\d/]*|Maiden|Grup\s*\d*|DÜZLÜK)', re.IGNORECASE)

    # HTML'yi koşu bloklarına böl
    pozisyonlar = [(m.start(), m.group(1), m.group(2)) for m in kosu_re.finditer(html)]

    for idx, (pos, k_no, saat) in enumerate(pozisyonlar):
        bitis = pozisyonlar[idx + 1][0] if idx + 1 < len(pozisyonlar) else len(html)
        blok = html[pos:bitis]

        mesafe_m = mesafe_re.search(blok)
        mesafe = mesafe_m.group(1) if mesafe_m else "?"
        pist = mesafe_m.group(2) if mesafe_m else pist_genel

        tur_m = tur_re.search(blok)
        tur = tur_m.group(1).strip() if tur_m else "Düz Koşu"

        atlar = parse_atlar(blok)
        if not atlar:
            continue

        kosular.append({
            "no": int(k_no),
            "sehir": sehir_adi,
            "saat": saat.strip(),
            "mesafe": mesafe,
            "pist": pist,
            "pist_durum": pist_durum,
            "tur": tur,
            "atlar": atlar
        })

    return kosular


def parse_atlar(blok):
    """HTML bloğundan at listesi çıkar."""
    atlar = []

    # At ismi + koşu no: "AT İSMİ (kosu_no)"
    at_re = re.compile(
        r'QueryParameter_AtId=\d+[^"]*"[^>]*>\s*'
        r'([A-ZÇĞİÖŞÜa-zçğışöü\s\'\-\.]+?)\s*'
        r'\((\d+)\)',
        re.DOTALL
    )

    # HP: tablo hücresinde 2-3 haneli sayı
    # Jokey ismi
    jokey_re = re.compile(
        r'JokeyIstatistikleri[^>]+title="([^"]+)"',
        re.DOTALL
    )

    # Form (Son 6 Y.)
    # HP sütunu — tablo <td> içinde
    # Daha güvenilir: satır bazlı parse

    # Tablo satırlarını çek
    satir_re = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
    td_re = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)
    temiz_re = re.compile(r'<[^>]+>')

    satirlar = satir_re.findall(blok)
    for satir in satirlar:
        hucreler = td_re.findall(satir)
        if len(hucreler) < 5:
            continue

        temiz = [temiz_re.sub('', h).strip() for h in hucreler]

        # At ismi hücresinde "AtKosuBilgileri" linki var mı?
        at_m = at_re.search(satir)
        if not at_m:
            continue

        at_isim = re.sub(r'\s+', ' ', at_m.group(1).strip())
        yaris_no = at_m.group(2)

        # Jokey
        jokey_m = jokey_re.search(satir)
        jokey = jokey_m.group(1).strip() if jokey_m else "-"

        # HP, Sıklet, Form — sütun sırası sabit
        # Kolon: Forma|N|At İsmi|Yaş|Orijin|Sıklet|Jokey|Sahip|Antrenör|St|HP|Son 6 Y|KGS|s20|En İyi D.|Gny|AGF
        hp = 0
        form = "-"
        siklet = "-"
        try:
            # Temiz metinlerin içinden HP ve form çek
            sayilar = [c for c in temiz if re.match(r'^\d{2,3}$', c)]
            if sayilar:
                hp = int(sayilar[0])

            # "St" (start no) — genellikle 1 hane
            # Form — rakam ve tire kombinasyonu
            for c in temiz:
                if re.match(r'^[\d\-]+$', c) and len(c) >= 3 and '-' in c:
                    form = c
                    break
        except:
            pass

        atlar.append({
            "no": int(yaris_no),
            "isim": at_isim,
            "jokey": jokey,
            "hp": hp,
            "form": form,
            "kilo": siklet
        })

    return atlar


def veri_cek(tarih_ymd=None):
    if tarih_ymd is None:
        tarih_ymd = bugunun_tarihini_al()

    tarih_tr = tarih_formatla_tr(tarih_ymd)
    print(f"📅 Tarih: {tarih_tr}")

    sehirler = sehirleri_cek(tarih_tr)
    if not sehirler:
        return {"tarih": tarih_ymd, "kosular": [], "kaynak": "tjk.org"}

    yurt_disi_keywords = ["ABD", "İngiltere", "Fransa", "Avustralya", "Afrika",
                          "Japonya", "Almanya", "İtalya", "İrlanda", "BAE",
                          "Kanada", "Park", "Guney", "Launceston", "Gulfstream",
                          "Santa Anita", "Greyville", "Fairview", "Meydan"]

    tum_kosular = []
    for sehir in sehirler:
        if any(k.lower() in sehir["adi"].lower() for k in yurt_disi_keywords):
            print(f"⏭️  Yurt dışı atlaniyor: {sehir['adi']}")
            continue

        print(f"🏇 Çekiliyor: {sehir['adi']}")
        html = sehir_html_cek(tarih_tr, sehir["id"], sehir["adi"])
        if html:
            kosular = parse_kosular(html, sehir["adi"])
            print(f"   → {len(kosular)} koşu")
            tum_kosular.extend(kosular)

    return {
        "tarih": tarih_ymd,
        "tarih_tr": tarih_tr,
        "kosular": tum_kosular,
        "kaynak": "tjk.org",
        "guncelleme": datetime.utcnow().isoformat() + "Z"
    }


def main():
    tarih = sys.argv[1] if len(sys.argv) > 1 else None
    data = veri_cek(tarih)

    with open("veriler.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    n = len(data.get("kosular", []))
    if n > 0:
        print(f"✅ Toplam {n} koşu kaydedildi → veriler.json")
    else:
        print("⚠️ Koşu bulunamadı.")


if __name__ == "__main__":
    main()

