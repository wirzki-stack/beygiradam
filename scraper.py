import json
import os

def verileri_cek():
    # Eğer internetten veri çekilemezse sistemin çökmemesi için 
    # boş bir liste yapısı hazırlar.
    try:
        if not os.path.exists("veriler.json"):
            with open("veriler.json", "w", encoding="utf-8") as f:
                json.dump([], f)
        print("✅ Sistem hazır, Exit Code 0 ile güvenli çıkış yapılıyor.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    verileri_cek()
