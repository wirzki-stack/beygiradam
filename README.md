# 🏇 BeygiRadam | Otomatik At Yarışı Analiz Sistemi

Türkiye'deki TJK yarış programını her gün otomatik çeken ve **Claude AI** ile analiz eden Streamlit uygulaması.

---

## ✨ Özellikler

- 📡 **Otomatik Veri Çekimi** — TJK API'sinden her gün sabah 09:00'da otomatik program alır
- 🤖 **AI Analiz** — Claude Sonnet ile her ayak için banko + plase + kazanma tahmini
- 📋 **Demo Mod** — API key olmadan örnek veriyle test edebilirsiniz
- 🔒 **Güvenli** — API key'iniz tarayıcı oturumunda kalır, hiçbir yerde saklanmaz
- 📅 **Geçmiş** — İstediğiniz tarihin programını seçerek analiz edebilirsiniz

---

## 🚀 Kurulum (Streamlit Cloud)

### 1. Repo'yu Fork Et
GitHub'da bu repoyu fork edin.

### 2. Streamlit Cloud'a Bağla
1. [share.streamlit.io](https://share.streamlit.io) adresine gidin
2. "New app" → GitHub reponuzu seçin
3. Main file: `beygiradam.py`
4. **Deploy** butonuna basın ✅

### 3. GitHub Actions Aktifleştir
Repo'nuzda **Actions** sekmesine gidin ve workflow'u etkinleştirin.  
Her gün sabah 09:00'da otomatik çalışacak.

### 4. Kullanım
- [console.anthropic.com](https://console.anthropic.com) adresinden **ücretsiz API key** alın
- Uygulamada sidebar'a yapıştırın
- **VERİ ÇEK & ANALİZ ET** butonuna basın

---

## 🛠 Yerel Çalıştırma

```bash
pip install -r requirements.txt
streamlit run beygiradam.py
```

Sadece scraper'ı çalıştırmak için:
```bash
python scraper.py           # bugün
python scraper.py 20260327  # belirli tarih
```

---

## 📁 Dosya Yapısı

```
beygiradam/
├── beygiradam.py              # Ana Streamlit uygulaması
├── scraper.py                 # TJK API veri çekici
├── veriler.json               # Son çekilen veri (otomatik güncellenir)
├── requirements.txt           # Python bağımlılıkları
└── .github/
    └── workflows/
        └── daily_scraper.yml  # GitHub Actions (günlük cron)
```

---

## ⚠️ Yasal Uyarı

Bu uygulama **yalnızca bilgi ve eğlence amaçlıdır**. Kesin tahmin değildir.  
At yarışı sonuçları her zaman belirsizlik içerir. Sorumlu oynayın.

---

*BeygiRadam v2 | 2026 | Powered by Claude AI + TJK*
