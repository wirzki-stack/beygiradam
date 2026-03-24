import requests
import json
import datetime
import os

def verileri_cek():
    # Repodaki formata göre bugünün tarihini al (Örn: 20260324)
    bugun = datetime.datetime.now().strftime("%Y%m%d")
    url = f"https://api.tjk.org/v1/race/program/{bugun}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.tjk.org/"
    }

    try:
        print(f"🔗 {bugun} verisi TJK API'den çekiliyor...")
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            # Veri boş değilse kaydet
            if data:
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_all_ascii=False, indent=4)
                print("✅ Başarılı: veriler.json güncellendi.")
            else:
                print("⚠️ API yanıt verdi ama veri boş.")
        else:
            print(f"❌ Hata Kodu: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
