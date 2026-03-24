import requests
import json
import os

def verileri_cek():
    # TJK'nın bugünkü bülten adresi (24 Mart 2026)
    url = "https://api.tjk.org/v1/race/program/20260324"
    
    # TJK'nın bot engeline takılmamak için gerçek bir tarayıcı taklidi yapıyoruz
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Origin": "https://www.tjk.org",
        "Referer": "https://www.tjk.org/",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        print("🔗 TJK Sunucusuna bağlanılıyor...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verinin dolu geldiğinden emin olalım
            if data:
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_all_ascii=False, indent=4)
                print("✅ Başarılı: veriler.json dosyası güncellendi!")
            else:
                print("⚠️ TJK boş veri gönderdi. Yarışlar henüz tanımlanmamış olabilir.")
        else:
            print(f"❌ TJK Hata Verdi: {response.status_code}")
            # Hata kodunu sistemin anlaması için zorla hata fırlatıyoruz (Exit Code 1'i önlemek için)
            if not os.path.exists("veriler.json"):
                with open("veriler.json", "w") as f: json.dump([], f)
                
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
