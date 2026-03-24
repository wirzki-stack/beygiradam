import requests
import json
from datetime import datetime

def fetch_and_save():
    # TJK'nın en güncel servis ucu
    today = datetime.now().strftime("%d-%m-%Y")
    url = f"https://online.tjk.org/tjkproxy/api/race-program/daily-races/{today}"
    
    # Gerçek bir mobil uygulama gibi görünmek için "Hacker" kimliği
    headers = {
        "User-Agent": "TJK Mobil/3.2.1 (iPhone; iOS 16.5)",
        "X-Requested-With": "com.tjk.tjk_mobil",
        "Accept": "application/json"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data:
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("✅ SIZMA BAŞARILI: Veriler JSON dosyasına işlendi.")
            else:
                print("⚠️ UYARI: Bağlantı kuruldu ama bülten boş döndü.")
        else:
            print(f"❌ HATA: TJK Erişimi Reddedildi (Kod: {r.status_code})")
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}")

if __name__ == "__main__":
    fetch_and_save()
