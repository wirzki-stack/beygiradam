import requests
import json
import datetime
import os

def verileri_cek():
    # Repodaki formata göre bugünün tarihi
    bugun = datetime.datetime.now().strftime("%Y%m%d")
    url = f"https://api.tjk.org/v1/race/program/{bugun}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.tjk.org/"
    }

    try:
        print(f"🔗 TJK API Bağlantısı kuruluyor: {bugun}")
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            raw_data = response.json()
            
            # API'den gelen ham veri genellikle bir sözlük içindeki 'data' listesindedir
            # Repodaki yapıya göre veriyi kontrol edip temizleyelim
            final_data = []
            if isinstance(raw_data, list):
                final_data = raw_data
            elif isinstance(raw_data, dict):
                # TJK API'nin farklı dönme ihtimallerine karşı:
                final_data = raw_data.get('data', raw_data.get('QueryResult', []))

            if final_data:
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(final_data, f, ensure_all_ascii=False, indent=4)
                print(f"✅ Başarılı: {len(final_data)} yarış verisi kaydedildi.")
            else:
                print("⚠️ API yanıtı boş geldi (Yarışlar henüz başlamamış olabilir).")
        else:
            print(f"❌ API Hatası: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
