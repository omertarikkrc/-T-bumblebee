"""
İTÜ Kontenjan Tarayıcı + Ders Alıcı Bot
========================================
Belirli saat aralıklarında dersin kontenjanını sürekli tarar.
Yer açıldığı an Kepler API'sine istek atarak dersi alır.

Kurulum : pip install requests
Çalıştır: python kontenjan_tarayici.py
"""

import requests
import time
import re
from datetime import datetime, time as dtime

# ─────────────────────────────────────────
#  AYARLAR — doldur
# ─────────────────────────────────────────

# Token: Chrome → Kepler → F12 → Network → KayitZamaniKontrolu → Headers → authorization
TOKEN = "Bearer eyJ..."

# Takip edilecek dersler
# CRN: ders numarası, BRANS_KODU_ID: ders programı API'sindeki ID
#   ATA  → 43
#   ING  → 188   (kontrol et)
#   TUR  → ...   (kontrol et)
# Branş kodu ID'sini bulmak için:
#   https://obs.itu.edu.tr/public/DersProgram → F12 → Network → ders branşı seç
#   → DersProgramSearch isteğinin URL'sinde dersBransKoduId=XX görünecek
HEDEFLER = [
    {"crn": "30287", "brans_kodu_id": 43, "ad": "ATA 122"},
    # {"crn": "30312", "brans_kodu_id": 43, "ad": "ATA 122 alt grup"},
    # Buraya istediğin kadar ders ekleyebilirsin
]

# Tarama saat aralığı (24 saat formatı)
TARAMA_BASLANGIC = dtime(9, 0)    # 09:00
TARAMA_BITIS     = dtime(23, 0)   # 23:00

# Tarama sıklığı (saniye)
# Site verileri 5 dk'da bir günceller, ama biz yine de daha sık bakabiliriz
TARAMA_ARALIGI = 30   # her 30 saniyede bir tara

# ─────────────────────────────────────────
#  SABİTLER
# ─────────────────────────────────────────

DERS_PROGRAM_URL_TEMPLATE = (
    "https://obs.itu.edu.tr/public/DersProgram/DersProgramSearch"
    "?programSeviyeTipiAnahtari=LS&dersBransKoduId={brans_kodu_id}"
)
COURSE_SELECTION_URL = "https://obs.itu.edu.tr/api/ders-kayit/v21/"

RETURN_VALUES = {
    "successResult"          : "✓ İşlem başarılı.",
    "Ekleme İşlemi Başarılı" : "✓ Ders eklendi.",
    "errorResult"            : "✗ Operasyon tamamlanamadı.",
    "VAL01" : "✗ Genel hata.",
    "VAL02" : "↻ Kayıt zaman engeli.",
    "VAL03" : "✗ Bu dönem zaten alınmış.",
    "VAL04" : "✗ Ders planında yok.",
    "VAL05" : "✗ Maksimum kredi aşıldı.",
    "VAL06" : "✗ Kontenjan dolu.",
    "VAL09" : "✗ Ders çakışması.",
    "VAL11" : "✗ Önşart eksik.",
    "VAL15" : "✗ Maksimum 12 CRN.",
    "VAL16" : "↻ Aktif işlem var.",
    "VAL21" : "⊗ İstek limiti aşıldı!",
    "VAL22" : "✗ CC+ notu verilmiş.",
    "Kontenjan Dolu" : "✗ Kontenjan dolu.",
}

SUCCESS_CODES = {"successResult", "Ekleme İşlemi Başarılı"}

# ─────────────────────────────────────────
#  YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────

def log(msg, seviye=""):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = f"[{seviye}] " if seviye else ""
    print(f"[{ts}] {prefix}{msg}")

def tarama_zamani_mi():
    """Şu an tarama saat aralığında mı?"""
    su_an = datetime.now().time()
    if TARAMA_BASLANGIC <= TARAMA_BITIS:
        return TARAMA_BASLANGIC <= su_an <= TARAMA_BITIS
    else:  # gece yarısını geçen aralık (ör: 22:00-06:00)
        return su_an >= TARAMA_BASLANGIC or su_an <= TARAMA_BITIS

def ders_programi_cek(brans_kodu_id):
    """Ders programı HTML'ini indir."""
    url = DERS_PROGRAM_URL_TEMPLATE.format(brans_kodu_id=brans_kodu_id)
    try:
        r = requests.get(url, timeout=10)
        return r.text
    except Exception as e:
        log(f"Ders programı çekilemedi: {e}", "HATA")
        return None

def crn_bos_mu(html, crn):
    """
    HTML içinde CRN'i bul, kontenjan/kayıtlı sayılarına bak.
    Site şu formatta tablo döndürür:
      CRN | Ders Kodu | Ders Adı | ... | Kontenjan | Kayıtlı | ...

    Tabloda her satır <tr>...<td>30287</td>...<td>80</td><td>80</td>... şeklinde.
    """
    if not html:
        return None, None

    # CRN'i içeren satırı bul
    # <tr> ... <td>CRN</td> ... </tr>
    pattern = (
        r'<tr[^>]*>\s*<td[^>]*>\s*' + re.escape(str(crn)) +
        r'\s*</td>(.*?)</tr>'
    )
    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    if not match:
        return None, None

    satir = match.group(1)
    # Satırdaki tüm <td>...</td> içeriklerini al
    td_pattern = r'<td[^>]*>(.*?)</td>'
    tdler = re.findall(td_pattern, satir, re.DOTALL)
    # HTML tag'lerini temizle
    tdler_temiz = [re.sub(r'<[^>]+>', '', t).strip() for t in tdler]

    # Sondan başlayarak ilk iki sayıyı bul: bunlar kontenjan ve kayıtlı sayısıdır
    # (genelde son 3-4 sütun: Kontenjan | Kayıtlı | RezervKontenjan | RezervKayıtlı | Açıklama)
    sayilar = []
    for t in reversed(tdler_temiz):
        if t.isdigit():
            sayilar.append(int(t))
            if len(sayilar) >= 4:
                break

    if len(sayilar) < 2:
        return None, None

    # Sayılar listesi tersten geldi, düzelt
    sayilar.reverse()
    # Son iki kullanılabilir sayı: ana kontenjan ve kayıtlı
    # Genellikle: [..., kontenjan, kayitli] veya [..., rezerv_kont, rezerv_kayit, kontenjan, kayitli]
    # Basit yaklaşım: en büyük iki ardışık sayı çiftini al
    kontenjan = sayilar[-2] if len(sayilar) >= 2 else sayilar[0]
    kayitli   = sayilar[-1]

    return kontenjan, kayitli

def ders_al(crn):
    """Kepler API'sine ders alma isteği at."""
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    try:
        r = requests.post(
            COURSE_SELECTION_URL,
            headers=headers,
            json={"ECRN": [str(crn)], "SCRN": []},
            timeout=15,
        )
        return r.json()
    except Exception as e:
        log(f"Ders alma hatası: {e}", "HATA")
        return None

# ─────────────────────────────────────────
#  ANA AKIŞ
# ─────────────────────────────────────────

def main():
    print("=" * 60)
    print("  İTÜ Kontenjan Tarayıcı + Ders Alıcı")
    print("=" * 60)

    if TOKEN.startswith("Bearer eyJ..."):
        print("\n⚠  TOKEN ayarlanmamış!")
        input("Enter ile çık...")
        return

    if not HEDEFLER:
        log("HEDEFLER listesi boş.", "HATA")
        return

    log(f"Takip edilen dersler: {[h['ad'] for h in HEDEFLER]}")
    log(f"Tarama aralığı: {TARAMA_BASLANGIC.strftime('%H:%M')} - {TARAMA_BITIS.strftime('%H:%M')}")
    log(f"Tarama sıklığı: {TARAMA_ARALIGI} saniye")
    print()

    alinmis = set()  # alınan CRN'ler (artık taranmaz)
    tarama_no = 0

    while True:
        # Tarama saat aralığında mıyız?
        if not tarama_zamani_mi():
            log(f"Tarama saatleri dışında ({TARAMA_BASLANGIC} - {TARAMA_BITIS}), bekleniyor...")
            time.sleep(60)  # 1 dakikada bir kontrol et
            continue

        # Tüm dersler alındı mı?
        kalan = [h for h in HEDEFLER if h["crn"] not in alinmis]
        if not kalan:
            log("Tüm hedef dersler alındı! 🎉")
            break

        tarama_no += 1
        log(f"── Tarama #{tarama_no} ──")

        # Aynı branş kodu için tek istek atarak optimize et
        cekilen_html = {}
        for hedef in kalan:
            bid = hedef["brans_kodu_id"]
            if bid not in cekilen_html:
                cekilen_html[bid] = ders_programi_cek(bid)

        # Her hedefi kontrol et
        for hedef in kalan:
            crn = hedef["crn"]
            html = cekilen_html.get(hedef["brans_kodu_id"])
            kontenjan, kayitli = crn_bos_mu(html, crn)

            if kontenjan is None:
                log(f"  {hedef['ad']} (CRN {crn}): bulunamadı", "UYARI")
                continue

            bos_yer = kontenjan - kayitli
            durum = "BOŞ" if bos_yer > 0 else "DOLU"
            log(f"  {hedef['ad']} (CRN {crn}): {kayitli}/{kontenjan} → {durum}")

            if bos_yer > 0:
                log(f"  ⚡ BOŞ YER VAR! Ders alma deneniyor...", "FIRSAT")

                # Hızlıca art arda 5 deneme yap
                for deneme in range(1, 6):
                    sonuc = ders_al(crn)
                    if sonuc is None:
                        time.sleep(0.3)
                        continue

                    for item in sonuc.get("ecrnResultList", []):
                        kod = item.get("resultCode", "")
                        mesaj = RETURN_VALUES.get(kod, kod)
                        log(f"    Deneme #{deneme} → {mesaj}")

                        if kod in SUCCESS_CODES:
                            log(f"  🎉 {hedef['ad']} ALINDI!", "BAŞARI")
                            alinmis.add(crn)
                            break

                    if crn in alinmis:
                        break

                    # Kontenjan dolduysa veya zaman engeli varsa daha hızlı tekrar dene
                    time.sleep(0.3)

                if crn not in alinmis:
                    log(f"  Bu turda alınamadı, sonraki taramada tekrar denenecek.", "BİLGİ")

        # Tüm taramalar bitti, biraz bekle
        if any(h["crn"] not in alinmis for h in HEDEFLER):
            print()
            time.sleep(TARAMA_ARALIGI)

    print()
    log("Program sonlandı.")
    input("Enter ile çık...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        log("Kullanıcı durdurdu (Ctrl+C).")
