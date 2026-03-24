import requests
import json
import os

def verileri_cek():
    # TJK'nın bugün (24 Mart) için veriyi sunduğu resmi API adresi
    url = "https://api.tjk.org/v1/race/program/20260324"
    
    # TJK'yı "ben gerçek bir insanım" diye ikna eden en güçlü başlıklar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.tjk.org",
        "Referer": "https://www.tjk.org/TR/YarisSever/Info/Page/GunlukYarisProgrami",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }

    try:
        print("🔗 TJK Sunucusuna güvenli bağlantı kuruluyor...")
        # Bir oturum (session) başlatıyoruz ki TJK bizi gerçek bir kullanıcı sansın
        session = requests.Session()
        # Önce ana sayfaya gidip bir 'ziyaretçi çerezi' (cookie) alalım
        session.get("https://www.tjk.org", headers={"User-Agent": headers["User-Agent"]}, timeout=15)
        
        # Şimdi çerezlerle beraber asıl bülteni istiyoruz
        response = session.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            # Veriyi kontrol et ve içeriğe göre ayıkla
            actual_data = []
            if isinstance(data, list):
                actual_data = data
            elif isinstance(data, dict):
                actual_data = data.get('data', [])

            if actual_data and len(actual_data) > 0:
                with open("veriler.json", "w", encoding="utf-8") as f:
                    json.dump(actual_data, f, ensure_all_ascii=False, indent=4)
                print(f"✅ BAŞARILI: {len(actual_data)} adet yarış verisi kaydedildi!")
            else:
                print("⚠️ TJK'dan veri geldi ama liste boş. Program henüz yayınlanmamış olabilir.")
                # Boş olsa bile dosyayı oluştur ki hata vermesin
                with open("veriler.json", "w") as f: json.dump([], f)
        else:
            print(f"❌ TJK Engeli: Hata Kodu {response.status_code}")
            raise Exception(f"TJK API hatası: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")
        # Hata durumunda boş dosya oluşturarak robotun çökmesini engelle
        if not os.path.exists("veriler.json"):
            with open("veriler.json", "w") as f: json.dump([], f)

if __name__ == "__main__":
    verileri_cek()
