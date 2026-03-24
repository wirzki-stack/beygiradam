import requests
import json
import os

def verileri_cek():
    # Bugünün bülten adresi
    url = "https://api.tjk.org/v1/race/program/20260324"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Origin": "https://www.tjk.org",
        "Referer": "https://www.tjk.org/TR/YarisSever/Info/Page/GunlukYarisProgrami",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        print("🔗 TJK Güvenlik Duvarı Aşılıyor...")
        session = requests.Session()
        # İlk hamle: Ana sayfaya gidip çerez (cookie) topla
        session.get("https://www.tjk.org", headers={"User-Agent": headers["User-Agent"]}, timeout=10)
        
        # İkinci hamle: Toplanan çerezlerle veriyi iste
        response = session.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            # Veri yapısını ayıkla
            actual_data = []
            if isinstance(data, list):
                actual_data = data
            elif isinstance(data, dict):
                actual_data = data.get('data', [])

            if actual_data and len(actual_data) > 0:
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(actual_data, f, ensure_all_ascii=False, indent=4)
                print(f"✅ BAŞARILI: {len(actual_data)} Yarış Kaydedildi!")
            else:
                print("⚠️ TJK boş döndü. Program henüz yayınlanmamış olabilir.")
        else:
            print(f"❌ TJK Engeli: Kod {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
