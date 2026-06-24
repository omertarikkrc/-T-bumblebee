# İTÜ Kepler Ders Botları 🎓

Kepler ders seçim sistemi için iki Python botu:

| Bot | Ne işe yarar? |
|-----|---------------|
| **`itu_bot.py`** | Ders seçim saati geldiğinde otomatik istek atar, dersleri alır |
| **`kontenjan_tarayici.py`** | Kontenjanı dolu olan dersi sürekli tarar, yer açıldığı an alır |

**Selenium yok, tarayıcı açmıyor.** Sadece `requests` kütüphanesi kullanıyor.

---

## Kurulum

### 1. Python Kur

Python kurulu değilse → https://www.python.org/downloads

Kurulumda **"Add Python to PATH"** kutucuğunu mutlaka işaretle.

Kurulumu doğrulamak için terminali aç:
```
python --version
```

### 2. Botu İndir

Sağ üstteki yeşil **Code** butonuna tıkla → **Download ZIP** → ZIP'i aç.

### 3. Gerekli Paketi Kur

```bash
pip install requests
```

---

## Token Alma (her iki bot için aynı)

Token, Kepler'in sana verdiği geçici kimlik kartı. Bot bunu kullanarak senin adına işlem yapıyor. Yaklaşık 1-2 saat geçerli — **kullanımdan kısa süre önce al.**

**1.** Chrome'da şu sayfaya git ve giriş yap:
```
https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayit
```

**2.** `F12` tuşuna bas → üstten **Network** sekmesine tıkla → **Fetch/XHR** filtresini seç

**3.** `F5` ile sayfayı yenile

**4.** Sol listede **`KayitZamaniKontrolu`** isteğine tıkla

**5.** **Headers** sekmesinde aşağı in, **`Authorization`** satırını bul

**6.** `Bearer eyJ...` ile başlayan uzun metni **tamamını** kopyala

![Token nasıl alınır](https://private-user-images.githubusercontent.com/102172007/612411780-837c5b78-9343-46a7-ab40-dd1c3fad85c6.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODIyOTk4MDEsIm5iZiI6MTc4MjI5OTUwMSwicGF0aCI6Ii8xMDIxNzIwMDcvNjEyNDExNzgwLTgzN2M1Yjc4LTkzNDMtNDZhNy1hYjQwLWRkMWMzZmFkODVjNi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNjI0JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyNFQxMTExNDFaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03MWMxMDU0NmIwZjJjMjIwOWQ4OTkxMDhmNWY3NDg4NTZkZWFmZGFmODdmODUwNWFlZDgwMzc5OWE1Mjc5YWQyJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.IqpokWRlaW0-RBtkP76RN_YqomKdhxP__v_xHnskq0U)

> ⚠️ Token'ı kimseyle paylaşma — Kepler hesabına erişim sağlar.

---

## 1. `itu_bot.py` — Ders Seçim Saati Botu

Ders seçimin başladığı anda otomatik olarak istek atıp dersleri alır.

### Nasıl Çalışır?

1. Ders seçim saatinden **1 dakika önce** Kepler'e "açıldı mı?" diye sormaya başlar
2. Saate **1 saniye kala** ders isteği atmaya başlar
3. Sonraki **30 saniye** boyunca **0.2 saniyede bir** istek atar
4. Tüm dersler alındıysa durur

### Ayarlar

`itu_bot.py` dosyasını Not Defteri veya VS Code ile aç. En üstteki **AYARLAR** bölümünü doldur:

```python
TOKEN = "Bearer eyJ..."              # kopyaladığın token

CRN_LIST = ["30280", "30287"]        # almak istediğin dersler

SCRN_LIST = []                       # bırakmak istediğin dersler (yoksa boş bırak)

START_TIME = datetime(2026, 9, 15, 17, 0)   # ders seçim tarihi ve saati
#                     yıl   ay  gün  saat dakika
```

**Yedek CRN kullanımı** — bir dersin kontenjanı dolarsa otomatik yedek dener:
```python
CRN_LIST = ["30280", "30287:30288"]  # 30287 dolarsa 30288 dener
```

### Çalıştır

```bash
python itu_bot.py
```

### Örnek Çıktı

```
[16:59:00.000] CRN listesi : ['30280', '30287', '30312']
[16:59:00.000] Hedef zaman : 2026-09-15 17:00:00
[16:59:00.001] Zaman kontrolü başladı...
[16:59:59.001] Hedefe 1 saniye kaldı — istek atılıyor!
[16:59:59.010] ── Deneme #1  [-0.99s] ──
[16:59:59.010]   CRN 30280: ↻ Kayıt zaman engeli.
[17:00:00.210] ── Deneme #2  [+0.21s] ──
[17:00:00.210]   CRN 30280: ✓ Ders eklendi.
[17:00:00.410]   CRN 30287: ✓ Ders eklendi.
[17:00:00.610] 🎉 Tüm dersler alındı!
```

---

## 2. `kontenjan_tarayici.py` — Boş Yer Avcısı

Ders dolu olduğunda, biri dersi bırakıp yer açıldığı anda otomatik almak için kullanılır.

### Nasıl Çalışır?

1. Belirli saat aralığında çalışır (örn: 09:00-23:00)
2. Her 30 saniyede bir [Ders Programı](https://obs.itu.edu.tr/public/DersProgram) sayfasını tarar
3. Belirttiğin CRN'in kayıtlı sayısını kontenjana karşı kontrol eder
4. Boş yer varsa hemen 5 kez art arda ders alma isteği atar
5. Alındıysa o CRN'i takip listesinden çıkarır

### Ayarlar

```python
TOKEN = "Bearer eyJ..."

HEDEFLER = [
    {"crn": "30287", "brans_kodu_id": 43, "ad": "ATA 122"},
    # İstediğin kadar ders ekleyebilirsin
]

TARAMA_BASLANGIC = dtime(9, 0)    # 09:00
TARAMA_BITIS     = dtime(23, 0)   # 23:00

TARAMA_ARALIGI = 30   # her 30 saniyede bir tara
```

### `brans_kodu_id` Nasıl Bulunur?

Her ders branşının (ATA, ING, MAT vs.) kendi numarası var:

1. https://obs.itu.edu.tr/public/DersProgram sayfasına git
2. `F12` → **Network** sekmesi → **Fetch/XHR** filtresi
3. **Lisans** seç, sonra istediğin **Ders Branş Kodu**'nu seç → **Göster**
4. Listede **`DersProgramSearch?programSe...`** isteğine tıkla
5. **Headers** sekmesinde URL'de `dersBransKoduId=XX` görünecek — o sayı senin branş kodun

Bilinen branş kodları:
- **ATA** → 43

### Çalıştır

```bash
python kontenjan_tarayici.py
```

### Örnek Çıktı

```
[15:43:58] Takip edilen dersler: ['ATA 122']
[15:43:58] Tarama aralığı: 09:00 - 23:00
[15:43:58] Tarama sıklığı: 30 saniye

[15:43:58] ── Tarama #1 ──
[15:43:59]   ATA 122 (CRN 30287): 80/80 → DOLU

[15:44:29] ── Tarama #2 ──
[15:44:29]   ATA 122 (CRN 30287): 79/80 → BOŞ
[15:44:29]   ⚡ BOŞ YER VAR! Ders alma deneniyor...
[15:44:30]     Deneme #1 → ✓ Ders eklendi.
[15:44:30]   🎉 ATA 122 ALINDI!
```

---

## Bilgisayarın Uyumamasını Sağla

Bot çalışırken bilgisayarın uyku moduna geçmemesi lazım, yoksa Python süreci donar.

**Windows:**
1. `Win + R` → `powercfg.cpl` → Enter
2. Sol menüden "Bilgisayarın ne zaman uyuyacağını seçin"
3. **Ekranı kapat:** istediğin süre olabilir
4. **Bilgisayarı uyut:** **Hiçbir zaman**
5. **Değişiklikleri kaydet**

Dizüstüyse: Güç ayarları → "Kapağı kapatmanın etkisi" → **Hiçbir şey yapma**

---

## Hata Kodları

| Kod | Anlam |
|-----|-------|
| `Ekleme İşlemi Başarılı` | Ders alındı ✓ |
| `VAL02` | Henüz zaman açılmadı (bot tekrar dener) |
| `VAL03` | Bu ders zaten alınmış |
| `VAL06` / `Kontenjan Dolu` | Kontenjan dolu |
| `VAL09` | Başka derse çakışıyor |
| `VAL21` | İstek limiti aşıldı (1 saat ceza) |

---

## Sık Sorulan Sorular

**Token nedir?**
Kepler'e giriş yaptığında site sana geçici bir kimlik kartı veriyor. Bot bu kartı göstererek senin adına işlem yapıyor.

**Token ne kadar süre geçerli?**
Yaklaşık 1-2 saat. Süresi dolarsa yenisini al ve dosyaya yapıştır.

**Bot çalışırken Chrome'u kapatabilir miyim?**
Evet. Token'ı bir kere kopyaladıktan sonra Chrome'a gerek yok.

**Ders seçildi mi nasıl anlarım?**
Terminaldeki log'da `✓ Ders eklendi.` yazar. Kepler'den de kontrol edebilirsin:
`https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayitIslemGecmisi`

---

## Lisans

MIT — istediğin gibi kullanabilirsin.
