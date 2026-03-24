import requests
import json
import os

def verileri_cek():
    # TJK'nın günlük bülten sayfası (Doğrudan web sitesi linki)
    # API yerine direkt bülten sayfasından çekmeyi deniyoruz
    url = "https://api.tjk.org/v1/race/program/20260324"
    
    # Gerçek bir Windows bilgisayar ve Google Chrome tarayıcısı taklidi
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.tjk.org/TR/YarisSever/Info/Page/GunlukYarisProgrami",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }

    try:
        print("🔗 TJK ana sunucusuna sızılıyor...")
        session = requests.Session()
        # Önce ana sayfaya gidip çerez (cookie) alalım
        session.get("https://www.tjk.org", headers={"User-Agent": headers["User-Agent"]}, timeout=10)
        
        # Şimdi asıl veriyi çekelim
        response = session.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            # Veri kontrolü
            if data and (isinstance(data, list) and len(data) > 0):
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_all_ascii=False, indent=4)
                print(f"✅ BAŞARILI: {len(data)} yarış verisi kaydedildi!")
            else:
                # Eğer liste değilse içindeki data kısmına bak
                actual_data = data.get('data', []) if isinstance(data, dict) else []
                if actual_data:
                    with open("veriler.json", "w", encoding="utf-8") as f:
                        json.dump(actual_data, f, ensure_all_ascii=False, indent=4)
                    print("✅ BAŞARILI: Veri sözlükten ayıklandı ve kaydedildi!")
                else:
                    print("⚠️ TJK bugün için henüz program yayınlamamış veya erişim kısıtlı.")
        else:
            print(f"❌ TJK Engeli: Hata Kodu {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
