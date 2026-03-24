import json
import os

def verileri_cek():
    # Eğer TJK kapalıysa veya hata veriyorsa, sistemin çökmemesi için 
    # en azından bir taslak dosya oluşturur.
    taslak_veri = [
        {
            "raceCityName": "ADANA",
            "raceNumber": 1,
            "raceTime": "14:30",
            "raceEntries": [
                {"No": "1", "At Adı": "VERİ BEKLENİYOR", "Jokey": "-", "Kilo": "-", "HP": "0"}
            ]
        }
    ]
    
    try:
        # Burada dosya yoksa oluşturuyoruz, varsa dokunmuyoruz
        if not os.path.exists("veriler.json"):
            with open("veriler.json", "w", encoding="utf-8") as f:
                json.dump(taslak_veri, f, ensure_all_ascii=False, indent=4)
        print("✅ Sistem hazır, veriler.json kontrol edildi.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
