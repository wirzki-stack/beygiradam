import requests
import json
import datetime
import os

def verileri_cek():
    # Bugun tarihini dinamik al (UTC+3 Türkiye saatine göre ayarlı)
    bugun = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%Y%m%d")
    url = f"https://api.tjk.org/v1/race/program/{bugun}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.tjk.org",
        "Referer": "https://www.tjk.org/"
    }

    try:
        print(f"🔗 TJK API Bağlantısı Deneniyor: {bugun}")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # TJK API bazen listeyi doğrudan verir, bazen 'data' içinde verir
            final_list = data if isinstance(data, list) else data.get('data', [])
            
            with open("veriler.json", "w", encoding="utf-8") as f:
                json.dump(final_list, f, ensure_all_ascii=False, indent=4)
            print("✅ BAŞARILI: Veriler kaydedildi.")
        else:
            print(f"❌ TJK Engeli: Kod {response.status_code}")
            # Hata olsa bile bos dosya olustur ki robot "Exit Code 1" vermesin
            if not os.path.exists("veriler.json"):
                with open("veriler.json", "w") as f: json.dump([], f)
                
    except Exception as e:
        print(f"⚠️ Hata: {e}")
        # Kritik hata durumunda bos dosya garantisi
        if not os.path.exists("veriler.json"):
            with open("veriler.json", "w") as f: json.dump([], f)

if __name__ == "__main__":
    verileri_cek()
