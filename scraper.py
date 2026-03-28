"""
scraper.py — TJK CDN'den CSV indirir.
Şehir adı varyantlarını sırayla dener (Türkçe, Latin, URL-encoded).
"""
import requests, json, csv, io, sys
from datetime import datetime, timedelta
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.tjk.org/",
}

# Her şehir için deneme sırası: TJK'nın dosya adında kullandığı isim
SEHIR_VARYANTLAR = {
    "İstanbul": ["İstanbul", "Istanbul", "istanbul"],
    "Ankara":   ["Ankara", "ankara"],
    "İzmir":    ["İzmir", "Izmir", "izmir"],
    "Bursa":    ["Bursa", "bursa"],
    "Adana":    ["Adana", "adana"],
    "Antalya":  ["Antalya", "antalya"],
    "Kocaeli":  ["Kocaeli", "kocaeli"],
    "Diyarbakır": ["Diyarbakır", "Diyarbakir"],
    "Elazığ":   ["Elazığ", "Elazig"],
    "Şanlıurfa":["Şanlıurfa", "Sanliurfa"],
}

def bugun():
    return (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d")

def csv_url(tarih_ymd, sehir_adi):
    obj = datetime.strptime(tarih_ymd, "%Y-%m-%d")
    yil     = obj.strftime("%Y")
    klasor  = obj.strftime("%Y-%m-%d")
    dosya   = obj.strftime("%d.%m.%Y")
    # Türkçe karakterleri URL-encode et
    sehir_encoded = quote(sehir_adi, safe="")
    return (
        f"https://medya-cdn.tjk.org/raporftp/TJKPDF/{yil}/{klasor}/CSV/"
        f"GunlukYarisProgrami/{dosya}-{sehir_encoded}-GunlukYarisProgrami-TR.csv"
    )

def csv_indir(tarih_ymd, sehir_adi):
    url = csv_url(tarih_ymd, sehir_adi)
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and len(r.content) > 200:
            print(f"    ✅ Bulundu: {url}")
            return r.content
    except Exception as e:
        print(f"    ❌ Hata ({sehir_adi}): {e}")
    return None

def csv_parse(icerik_bytes, sehir_adi):
    kosular = {}
    for enc in ["windows-1254", "utf-8-sig", "utf-8", "latin-1"]:
        try:
            metin = icerik_bytes.decode(enc)
            break
        except:
            continue
    else:
        metin = icerik_bytes.decode("windows-1254", errors="replace")

    reader = csv.DictReader(io.StringIO(metin), delimiter=";")
    cols = [c.strip() for c in (reader.fieldnames or [])]
    print(f"    Kolonlar: {cols[:8]}")

    def bul(*names):
        for n in names:
            for c in cols:
                if c.strip().lower() == n.lower():
                    return c
        return names[0]

    c_kno  = bul("KosuNo","KOSU_NO","Kosu No","kosu_no","KoşuNo")
    c_at   = bul("AtAdi","AT_ADI","At Adi","At Adı","at_adi")
    c_yno  = bul("YarisNo","YARIS_NO","No","Yarış No","yaris_no")
    c_jok  = bul("JokeyAdi","JOKEY","Jokey","Jokey Adı","jokey_adi")
    c_hp   = bul("HP","Hp","hp")
    c_mes  = bul("Mesafe","MESAFE","mesafe")
    c_pist = bul("PistAdi","PIST","Pist","pist_adi")
    c_tur  = bul("KosuTipi","KOSU_TIPI","Koşu Tipi","Tur","tur")
    c_saat = bul("KosuSaati","Saat","saat","kosu_saati")
    c_form = bul("SonAltiYarisFormu","Form","Son 6 Yarış","son6")
    c_kilo = bul("Siklet","Sıklet","Kilo","siklet")

    for row in reader:
        try:
            kno_raw = row.get(c_kno,"").strip()
            if not kno_raw: continue
            kno = int(kno_raw)
            at  = row.get(c_at,"").strip()
            if not at: continue
            try: yno = int(row.get(c_yno,"0").strip())
            except: yno = 0
            jok  = row.get(c_jok,"-").strip() or "-"
            mes  = row.get(c_mes,"?").strip() or "?"
            pist = row.get(c_pist,"?").strip() or "?"
            tur  = row.get(c_tur,"?").strip() or "?"
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

    return list(kosular.values())

def veri_cek(tarih_ymd=None):
    if not tarih_ymd:
        tarih_ymd = bugun()
    print(f"📅 {tarih_ymd}")
    tum = []
    for sehir, varyantlar in SEHIR_VARYANTLAR.items():
        print(f"  🔍 {sehir}...")
        for v in varyantlar:
            raw = csv_indir(tarih_ymd, v)
            if raw:
                kosular = csv_parse(raw, sehir)
                print(f"  → {len(kosular)} koşu")
                tum.extend(kosular)
                break
        else:
            print(f"  ⏭  {sehir}: yok")
    return {"tarih": tarih_ymd, "kosular": tum, "kaynak": "tjk-cdn-csv"}

def main():
    tarih = sys.argv[1] if len(sys.argv) > 1 else None
    data = veri_cek(tarih)
    with open("veriler.json","w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    n = len(data["kosular"])
    print(f"{'✅' if n else '⚠️'} {n} koşu → veriler.json")

if __name__ == "__main__":
    main()
