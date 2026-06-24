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

Kurulumu doğrulamak için terminali aç ve şunu yaz:
```
python --version
```

### 2. Botu İndir

**Git kuruluysa:**
```bash
git clone https://github.com/KULLANICI_ADIN/itu-ders-secici.git
cd itu-ders-secici
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

Token, Kepler'in sana verdiği geçici kimlik kartı. Yaklaşık 1-2 saat geçerli.

1. Chrome'da şu sayfaya git ve giriş yap:
   `https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayit`

2. `F12` tuşuna bas → **Network** sekmesine tıkla

3. Üstteki filtreden **Fetch/XHR**'ı seç

4. Sayfayı `F5` ile yenile

5. Listede **`KayitZamaniKontrolu`** isteğine tıkla

6. **Headers** sekmesinde `authorization` satırını bul → **`Bearer eyJ...`** ile başlayan değeri kopyala

> ⚠️ Ders seçiminden en fazla 1-2 saat önce al, süresi doluyor.

---

### Adım 2 — `itu_bot.py` Dosyasını Düzenle

`itu_bot.py` dosyasını Not Defteri veya VS Code ile aç. En üstteki **AYARLAR** bölümünü doldur:

```python
TOKEN = "Bearer eyJ..."              # kopyaladığın token

CRN_LIST = ["30280", "30287"]        # almak istediğin dersler

SCRN_LIST = []                       # bırakmak istediğin dersler (yoksa boş bırak)

START_TIME = datetime(2026, 9, 15, 17, 0)   # ders seçim tarihi ve saati
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

## Hata Kodları

| Kod | Anlam | Bot ne yapıyor |
|-----|-------|----------------|
| `Ekleme İşlemi Başarılı` | Ders alındı ✓ | Durur |
| `VAL02` | Henüz zaman açılmadı | Tekrar dener |
| `VAL06` / `Kontenjan Dolu` | Kontenjan dolu | Yedek CRN varsa onu dener |
| `VAL09` | Ders çakışması | Vazgeçer |
| `VAL16` | Aktif işlem var | Tekrar dener |
| `VAL21` | İstek limiti aşıldı | Durur |

---

## Sık Sorulan Sorular

**Token nedir?**
Kepler'e giriş yaptığında site sana geçici bir kimlik kartı veriyor. Bot bu kartı göstererek senin adına işlem yapıyor.

**Token ne kadar süre geçerli?**
Yaklaşık 1-2 saat. Ders seçiminden kısa süre önce al.

**Bot neden tarayıcı açmıyor?**
Tarayıcıyı sen açıp token alıyorsun, bot sadece o token'ı kullanarak HTTP isteği atıyor. Daha hızlı ve daha az hata çıkarıyor.

**Ders seçildi mi nasıl anlarım?**
Terminaldeki log'da `✓ Ders eklendi.` yazar. Ayrıca Kepler'de kontrol edebilirsin:
`https://obs.itu.edu.tr/ogrenci/DersKayitIslemleri/DersKayitIslemGecmisi`

---

## Lisans

MIT — istediğin gibi kullanabilirsin.
