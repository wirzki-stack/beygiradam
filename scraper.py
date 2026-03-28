"""
scraper.py — TJK CDN'den CSV indirir, şehir listesi sabittir.
JavaScript bağımlılığı yoktur, Streamlit Cloud'da çalışır.
"""
import requests, json, csv, io, sys
from datetime import datetime, timedelta

SEHIRLER = [
    {"id": "1",  "adi": "İstanbul"},
    {"id": "3",  "adi": "Ankara"},
    {"id": "2",  "adi": "İzmir"},
    {"id": "5",  "adi": "Bursa"},
    {"id": "4",  "adi": "Adana"},
    {"id": "10", "adi": "Antalya"},
    {"id": "9",  "adi": "Kocaeli"},
    {"id": "6",  "adi": "Diyarbakır"},
    {"id": "7",  "adi": "Elazığ"},
    {"id": "8",  "adi": "Şanlıurfa"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.tjk.org/",
    "Accept": "*/*",
}

def bugun():
    return (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d")

def csv_url(tarih_ymd, sehir_adi):
    obj = datetime.strptime(tarih_ymd, "%Y-%m-%d")
    dosya_tarih = obj.strftime("%d.%m.%Y")   # 28.03.2026
    klasor_tarih = obj.strftime("%Y-%m-%d")  # 2026-03-28
    yil = obj.strftime("%Y")
    return (
        f"https://medya-cdn.tjk.org/raporftp/TJKPDF/{yil}/{klasor_tarih}/CSV/"
        f"GunlukYarisProgrami/{dosya_tarih}-{sehir_adi}-GunlukYarisProgrami-TR.csv"
    )

def csv_indir(tarih_ymd, sehir_adi):
    url = csv_url(tarih_ymd, sehir_adi)
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and len(r.content) > 100:
            return r.content
    except:
        pass
    return None

def csv_parse(icerik_bytes, sehir_adi):
    """CSV'yi parse edip koşu listesi döndürür."""
    kosular = {}
    try:
        metin = icerik_bytes.decode("windows-1254", errors="replace")
        reader = csv.DictReader(io.StringIO(metin), delimiter=";")
        for satir in reader:
            try:
                k_no = satir.get("KosuNo", satir.get("KOSU_NO", "")).strip()
                if not k_no:
                    continue
                k_no = int(k_no)

                at_isim = satir.get("AtAdi", satir.get("AT_ADI", satir.get("At Adı", ""))).strip()
                yaris_no = satir.get("YarisNo", satir.get("YARIS_NO", satir.get("No", ""))).strip()
                jokey = satir.get("JokeyAdi", satir.get("JOKEY", satir.get("Jokey", "-"))).strip()
                hp = satir.get("HP", satir.get("Hp", "0")).strip()
                mesafe = satir.get("Mesafe", satir.get("MESAFE", "?")).strip()
                pist = satir.get("PistAdi", satir.get("PIST", satir.get("Pist", "?"))).strip()
                tur = satir.get("KosuTipi", satir.get("KOSU_TIPI", satir.get("Tür", "?"))).strip()
                saat = satir.get("KosuSaati", satir.get("Saat", "?")).strip()
                form = satir.get("SonAltiYarisFormu", satir.get("Form", "-")).strip()

                if k_no not in kosular:
                    kosular[k_no] = {
                        "no": k_no, "sehir": sehir_adi,
                        "saat": saat, "mesafe": mesafe,
                        "pist": pist, "tur": tur, "atlar": []
                    }

                if at_isim:
                    try: hp_int = int(float(hp))
                    except: hp_int = 0
                    try: no_int = int(yaris_no)
                    except: no_int = 0
                    kosular[k_no]["atlar"].append({
                        "no": no_int, "isim": at_isim,
                        "jokey": jokey, "hp": hp_int, "form": form
                    })
            except:
                continue
    except Exception as e:
        print(f"  CSV parse hatası: {e}")
    return list(kosular.values())

def veri_cek(tarih_ymd=None):
    if not tarih_ymd:
        tarih_ymd = bugun()
    print(f"📅 Tarih: {tarih_ymd}")
    tum_kosular = []
    for s in SEHIRLER:
        print(f"  🔍 {s['adi']} deneniyor...")
        icerik = csv_indir(tarih_ymd, s["adi"])
        if icerik:
            kosular = csv_parse(icerik, s["adi"])
            print(f"  ✅ {s['adi']}: {len(kosular)} koşu")
            tum_kosular.extend(kosular)
        else:
            print(f"  ⏭  {s['adi']}: bugün yok")
    return {"tarih": tarih_ymd, "kosular": tum_kosular, "kaynak": "tjk-cdn-csv"}

def main():
    tarih = sys.argv[1] if len(sys.argv) > 1 else None
    data = veri_cek(tarih)
    with open("veriler.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    n = len(data["kosular"])
    print(f"{'✅' if n else '⚠️'} {n} koşu kaydedildi → veriler.json")

if __name__ == "__main__":
    main()
