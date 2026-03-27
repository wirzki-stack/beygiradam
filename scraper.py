import requests
import json
import os
import sys
from datetime import datetime, timedelta


def bugunun_tarihini_al():
    """Türkiye saatine göre (UTC+3) bugünün tarihini YYYYMMDD formatında döndür."""
    return (datetime.utcnow() + timedelta(hours=3)).strftime("%Y%m%d")


def tjk_programini_cek(tarih=None):
    """TJK API'den koşu programını çek."""
    if tarih is None:
        tarih = bugunun_tarihini_al()

    url = f"https://api.tjk.org/v1/race/program/{tarih}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Referer": "https://www.tjk.org/",
    }

    print(f"📅 Tarih: {tarih}")
    print(f"🔗 URL: {url}")

    try:
        r = requests.get(url, headers=headers, timeout=20)
        print(f"📶 HTTP Status: {r.status_code}")

        if r.status_code == 200:
            return r.json()
        else:
            print(f"⚠️ Sunucu hatası: {r.status_code}")
            return None
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return None


def kaydet(data, dosya="veriler.json"):
    """Veriyi JSON dosyasına kaydet."""
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Kaydedildi: {dosya}")


def main():
    tarih = sys.argv[1] if len(sys.argv) > 1 else None
    data = tjk_programini_cek(tarih)

    if data:
        kaydet(data)
        print("✅ Veri başarıyla çekildi ve kaydedildi.")
    else:
        print("⚠️ Veri çekilemedi. Boş dosya oluşturuluyor.")
        if not os.path.exists("veriler.json"):
            kaydet([])


if __name__ == "__main__":
    main()
