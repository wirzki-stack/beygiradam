import requests
import json
import datetime

def verileri_cek():
    # Bugünün tarihini al (Format: 20260324)
    bugun = datetime.datetime.now().strftime("%Y%m%d")
    print(f"📅 {bugun} tarihi için veriler çekiliyor...")

    # TJK API URL (Günlük bülten verisi)
    url = f"https://api.tjk.org/v1/race/program/{bugun}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            # Veriyi dosyaya kaydet
            with open("veriler.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_all_ascii=False, indent=4)
            
            print("✅ Veriler başarıyla 'veriler.json' dosyasına kaydedildi!")
            return True
        else:
            print(f"❌ TJK API Hatası: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️ Bir hata oluştu: {e}")
        # Hata durumunda boş bir liste oluştur ki Streamlit çökmesin
        with open("veriler.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        return False

if __name__ == "__main__":
    verileri_cek()
