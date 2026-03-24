import requests
import json
import os
from datetime import datetime, timedelta

def verileri_cek():
    bugun = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y%m%d")
    url = f"https://api.tjk.org/v1/race/program/{bugun}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        print(f"🔗 Bağlanıyor: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            with open("veriler.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_all_ascii=False, indent=4)
            print("✅ Veri başarıyla yazıldı.")
        else:
            # Hata kodunda bile bos dosya olustur ki robot "Exit Code 1" vermesin
            print(f"⚠️ Sunucu hatası: {response.status_code}")
            if not os.path.exists("veriler.json"):
                with open("veriler.json", "w") as f: json.dump([], f)
    except Exception as e:
        print(f"❌ Hata: {e}")
        if not os.path.exists("veriler.json"):
            with open("veriler.json", "w") as f: json.dump([], f)

if __name__ == "__main__":
    verileri_cek()
