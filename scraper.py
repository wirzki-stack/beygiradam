import requests
import json
import os

def verileri_cek():
    # TJK'nın bugün için resmi bülten API adresi
    url = "https://api.tjk.org/v1/race/program/20260324"
    
    # TJK'yı "ben bir insanım" diye ikna eden gelişmiş başlıklar
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.tjk.org",
        "Referer": "https://www.tjk.org/",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        print("🔗 TJK'dan veri çekiliyor...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verinin gerçekten dolu olup olmadığını kontrol et
            if data and (isinstance(data, list) or (isinstance(data, dict) and data.get('data'))):
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_all_ascii=False, indent=4)
                print("✅ Başarılı: veriler.json güncellendi!")
            else:
                print("⚠️ TJK'dan boş liste döndü. Yarışlar henüz yayınlanmamış olabilir.")
        else:
            print(f"❌ TJK Hata Kodu: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
