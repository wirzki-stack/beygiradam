import requests
import json
import os

def verileri_cek():
    url = "https://api.tjk.org/v1/race/program/20260324" # Bugünün verisi
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Dosyayı tam burada oluşturuyoruz
            with open("veriler.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_all_ascii=False)
            print("✅ veriler.json başarıyla oluşturuldu!")
        else:
            # TJK cevap vermezse boş dosya oluştur ki hata vermesin
            with open("veriler.json", "w", encoding="utf-8") as f:
                json.dump([], f)
            print(f"⚠️ TJK Hata verdi: {response.status_code}")
    except Exception as e:
        with open("veriler.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
