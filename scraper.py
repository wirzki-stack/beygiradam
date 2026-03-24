import requests
import json
import os
from datetime import datetime, timedelta

def verileri_cek():
    # Türkiye saatine göre bugünün tarihini al
    bugun = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y%m%d")
    url = f"https://api.tjk.org/v1/race/program/{bugun}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        print(f"🔗 TJK API'den veri çekiliyor: {bugun}")
        # timeout ekleyerek robotun sonsuza kadar beklemesini ve hata vermesini engelliyoruz
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Veri listeyse veya 'data' anahtarı içindeyse al
            final_data = data if isinstance(data, list) else data.get('data', [])
            
            with open("veriler.json", "w", encoding="utf-8") as f:
                json.dump(final_data, f, ensure_all_ascii=False, indent=4)
            print("✅ BAŞARILI: Veri kaydedildi.")
        else:
            print(f"❌ API Hatası: {response.status_code}. Boş dosya oluşturuluyor.")
            with open("veriler.json", "w") as f: json.dump([], f)
            
    except Exception as e:
        print(f"⚠️ Hata: {e}. Sistemin çökmemesi için boş dosya oluşturuldu.")
        # Dosya yoksa bile oluştur ki hata vermesin
        if not os.path.exists("veriler.json"):
            with open("veriler.json", "w") as f: json.dump([], f)

if __name__ == "__main__":
    verileri_cek()
