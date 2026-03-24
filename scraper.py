import requests
import json
import os

def verileri_cek():
    # TJK'nın bugün (24 Mart) için veriyi sunduğu resmi API adresi
    url = "https://api.tjk.org/v1/race/program/20260324"
    
    # TJK bot olduğumuzu anlamasın diye "insan gibi" davranan başlıklar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.tjk.org",
        "Referer": "https://www.tjk.org/"
    }

    try:
        print("🔗 TJK verileri çekilmeye başlanıyor...")
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            # Veri boş mu kontrol et (Gelen verinin tipine göre)
            if data:
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_all_ascii=False, indent=4)
                print("✅ İşlem Başarılı: veriler.json güncellendi!")
            else:
                print("⚠️ TJK'dan veri geldi ama içi boş.")
        else:
            print(f"❌ TJK API Hatası: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
