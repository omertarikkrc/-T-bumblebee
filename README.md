# İTÜ Kepler Ders Seçici 🎓

Ders seçim saatinde otomatik olarak HTTP isteği atarak Kepler üzerinden ders seçen Python botu.

**Selenium yok, tarayıcı açmıyor.** Sadece `requests` kütüphanesi kullanıyor.

---

## Nasıl Çalışır?

1. Ders seçim saatinden **1 dakika önce** Kepler'e "açıldı mı?" diye sormaya başlar
2. Saate **1 saniye kala** ders isteği atmaya başlar
3. Açılıştan sonraki **2 saniye** boyunca **0.2 saniyede bir** istek atar (~15 istek)
4. Ders alındıysa durur

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

**Git kuruluysa:**
```bash
git clone https://github.com/omertarikkrc/-T-bumblebee.git
cd -T-bumblebee
```

**Git yoksa:**
Sağ üstteki yeşil **Code** butonuna tıkla → **Download ZIP** → ZIP'i aç.

### 3. Gerekli Paketi Kur
```bash
pip install requests
```

---

## Kullanım

### Adım 1 — Token Al

Token, Kepler'in sana verdiği geçici kimlik kartı. Bot bunu kullanarak senin adına ders seçiyor. Yaklaşık 1-2 saat geçerli, **ders seçiminden kısa süre önce al.**

**1.** Chrome'da şu sayfaya git ve giriş yap:
`https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayit`

**2.** `F12` tuşuna bas → üstten **Network** sekmesine tıkla → **Fetch/XHR** filtresini seç

**3.** `F5` ile sayfayı yenile

**4.** Sol listede **`K...`** ile başlayan **`KayitZamaniKontrolu`** isteğine tıkla

**5.** **Headers** sekmesinde aşağı in, **`Authorization`** satırını bul

**6.** `Bearer eyJ...` ile başlayan uzun metni **tamamını** kopyala

![Token nasıl alınır](images/token-nasil-alinir.png)

> ⚠️ Token'ı kimseyle paylaşma — Kepler hesabına erişim sağlar.

---

### Adım 2 — `itu_bot.py` Dosyasını Düzenle

`itu_bot.py` dosyasını Not Defteri veya VS Code ile aç. En üstteki **AYARLAR** bölümünü doldur:

```python
TOKEN = "Bearer eyJ..."              # kopyaladığın token

CRN_LIST = ["30280", "30287"]        # almak istediğin dersler

SCRN_LIST = []                       # bırakmak istediğin dersler (yoksa boş bırak)

START_TIME = datetime(2026, 9, 15, 17, 0)   # ders seçim tarihi ve saati
#                     yıl   ay  gün  saat dakika
```

**Yedek CRN kullanımı:**
Bir dersin kontenjanı dolarsa otomatik olarak yedek CRN denenmesini istiyorsan:
```python
CRN_LIST = ["30280", "30287:30288"]  # 30287 dolarsa 30288 dener
```

---

### Adım 3 — Botu Başlat

Terminali aç, `itu_bot.py` dosyasının bulunduğu klasöre git ve çalıştır:

```bash
python itu_bot.py
```

Bot ders seçim saatine kadar bekler, saatinde otomatik ateşler.

> ⚠️ Bot çalışırken bilgisayarın uyku moduna geçmediğinden emin ol.
> Windows: `Win + R` → `powercfg.cpl` → "Bilgisayarı uyut" → "Hiçbir zaman"

---

## Örnek Çıktı

```
[13:59:00.000] CRN listesi : ['30280', '30287', '30312']
[13:59:00.000] Hedef zaman : 2026-06-24 14:00:00
[13:59:00.001] Zaman kontrolü başladı...
[13:59:59.001] Hedefe 1 saniye kaldı — istek atılıyor!
[13:59:59.001] ════ DERS SEÇİMİ BAŞLIYOR ════
[13:59:59.010] ── Deneme #1  [-0.99s] ──
[13:59:59.010]   CRN 30280: ↻ Kayıt zaman engeli.
[14:00:00.210] ── Deneme #2  [+0.21s] ──
[14:00:00.210]   CRN 30280: ✓ Ders eklendi.
[14:00:00.410]   CRN 30287: ✓ Ders eklendi.
[14:00:00.610]   CRN 30312: ✓ Ders eklendi.
[14:00:00.610] 🎉 Tüm dersler alındı!
```

---

## Test Etme

Gerçek ders seçim zamanı olmasa bile test edebilirsin:

```bash
python itu_bot.py
```

`START_TIME`'ı birkaç dakika sonrasına ayarla, botu çalıştır. Bot isteği attıktan sonra şu sayfada sonucu gör:
`https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayitIslemGecmisi`

"Kayıt Zamanı Engeli" hatası görüyorsan test başarılı — bot Kepler'e ulaştı.

---

## Hata Kodları

| Kod | Anlam | Bot ne yapıyor |
|-----|-------|----------------|
| `Ekleme İşlemi Başarılı` | Ders alındı ✓ | Durur |
| `VAL02` | Henüz zaman açılmadı | Tekrar dener |
| `VAL06` / `Kontenjan Dolu` | Kontenjan dolu | Yedek CRN varsa dener |
| `VAL09` | Ders çakışması | Vazgeçer |
| `VAL16` | Aktif işlem var | Tekrar dener |
| `VAL21` | İstek limiti aşıldı | Durur |

---

## Sık Sorulan Sorular

**Token nedir?**
Kepler'e giriş yaptığında site sana geçici bir kimlik kartı veriyor. Bot bu kartı göstererek senin adına işlem yapıyor.

**Token ne kadar süre geçerli?**
Yaklaşık 1-2 saat. Ders seçiminden kısa süre önce al.

**Ders seçildi mi nasıl anlarım?**
Terminaldeki log'da `✓ Ders eklendi.` yazar. Kepler'den de kontrol edebilirsin:
`https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayitIslemGecmisi`

---

## Lisans

MIT — istediğin gibi kullanabilirsin.
