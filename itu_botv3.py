"""
İTÜ Kepler Ders Seçici — Selenium'suz, sadece requests
=======================================================
Kurulum : pip install requests
Çalıştır: python itu_bot.py
"""

import requests
import time
from datetime import datetime

# ─────────────────────────────────────────
#  AYARLAR — sadece bu bölümü doldur
# ─────────────────────────────────────────

# Kepler'den kopyaladığın Bearer token
# Nasıl alınır: Chrome → Kepler ders seçim sayfası → F12 → Network →
#               Fetch/XHR → F5 → KayitZamaniKontrolu → Headers → authorization
TOKEN = "Bearer eyJ..."

# Almak istediğin CRN'ler
# Yedek CRN için "30280:30281" formatı: 30280 dolarsa 30281 dener
CRN_LIST = ["30280", "30287", "30312"]

# Bırakmak istediğin CRN'ler (yoksa boş bırak)
SCRN_LIST = []

# Ders seçim zamanı — sadece bunu değiştir
START_TIME = datetime(2026, 6, 24, 14, 0)

# ─────────────────────────────────────────
#  SABİTLER (değiştirme)
# ─────────────────────────────────────────

COURSE_SELECTION_URL = "https://obs.itu.edu.tr/api/ders-kayit/v21/"
TIME_CHECK_URL       = "https://obs.itu.edu.tr/api/ogrenci/Takvim/KayitZamaniKontrolu"

# Saldırı penceresi:
# START_TIME - 1sn'den başlar, START_TIME + 30sn'ye kadar devam eder
# Her istek arasında 0.2sn bekler
# Kepler yoğunsa zaman aşımı olabilir — her deneme max 15sn bekler
ATTACK_START   = -1.0   # START_TIME'dan kaç saniye önce başla
ATTACK_END     = 30.0   # START_TIME'dan kaç saniye sonra dur
ATTACK_DELAY   =  0.2   # istekler arası bekleme (saniye)
REQUEST_TIMEOUT = 15    # tek istek için max bekleme (saniye)

RETURN_VALUES = {
    "successResult"                             : "✓ İşlem başarılı.",
    "Ekleme İşlemi Başarılı"                    : "✓ Ders eklendi.",
    "Silme İşlemi Başarılı"                     : "✓ Ders bırakıldı.",
    "errorResult"                               : "✗ Operasyon tamamlanamadı.",
    "VAL01"                                     : "✗ Genel hata.",
    "VAL02"                                     : "↻ Kayıt zaman engeli.",
    "VAL03"                                     : "✗ Bu dönem zaten alınmış.",
    "VAL04"                                     : "✗ Ders planında yok.",
    "VAL05"                                     : "✗ Maksimum kredi aşıldı.",
    "VAL06"                                     : "✗ Kontenjan dolu.",
    "VAL07"                                     : "✗ AA notu ile verilmiş.",
    "VAL08"                                     : "✗ Program şartı yok.",
    "VAL09"                                     : "✗ Ders çakışması.",
    "VAL10"                                     : "✗ Derse kayıtlı değilsin.",
    "VAL11"                                     : "✗ Önşart eksik.",
    "VAL12"                                     : "✗ Bu dönem açılmıyor.",
    "VAL13"                                     : "↻ Geçici engel.",
    "VAL14"                                     : "↻ Sistem yanıt vermiyor.",
    "VAL15"                                     : "✗ Maksimum 12 CRN sınırı.",
    "VAL16"                                     : "↻ Aktif işlem var.",
    "VAL18"                                     : "✗ CRN engellendi.",
    "VAL19"                                     : "✗ Önlisans dersi.",
    "VAL20"                                     : "✗ Dönem başına 1 ders bırakılabilir.",
    "VAL21"                                     : "⊗ İstek limiti aşıldı!",
    "VAL22"                                     : "✗ CC+ notu verilmiş.",
    "Kontenjan Dolu"                            : "✗ Kontenjan dolu.",
    "ERRLoad"                                   : "↻ Sistem yanıt vermiyor.",
    "NULLParam-CheckOgrenciKayitZamaniKontrolu" : "↻ Zaman engeli.",
    "CRNListEmpty"                              : "✗ CRN listesi boş.",
    "CRNNotFound"                               : "✗ CRN bulunamadı.",
}

SUCCESS_CODES = {"successResult", "Ekleme İşlemi Başarılı", "Silme İşlemi Başarılı"}
RETRY_CODES   = {"VAL01","VAL02","VAL13","VAL14","VAL16",
                 "ERRLoad","NULLParam-CheckOgrenciKayitZamaniKontrolu"}
TIMEOUT_CODES = {"VAL21"}

# ─────────────────────────────────────────
#  YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")

def get_headers():
    return {
        "Authorization": TOKEN,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/125.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
    }

def parse_crn_list(raw_list):
    crns, backup = [], {}
    for entry in raw_list:
        entry = str(entry)
        if ":" in entry:
            primary, spare = entry.split(":", 1)
            crns.append(primary)
            backup[primary] = spare
            log(f"  Yedek CRN: {primary} → {spare}")
        else:
            crns.append(entry)
    return crns, backup

def check_selection_time():
    try:
        r = requests.get(TIME_CHECK_URL, headers=get_headers(), timeout=5)
        data = r.json()
        result = data["kayitZamanKontrolResult"]
        return result["ogrenciSinifaKayitOlabilir"] or result["ogrenciSiniftanAyrilabilir"]
    except Exception:
        return False

def send_request(crn_list, scrn_list):
    try:
        r = requests.post(
            COURSE_SELECTION_URL,
            headers=get_headers(),
            json={"ECRN": crn_list, "SCRN": scrn_list},
            timeout=REQUEST_TIMEOUT,
        )
        return r.json()
    except requests.exceptions.Timeout:
        log("  Zaman aşımı — Kepler yoğun, tekrar denenecek.")
        return None
    except Exception as e:
        log(f"  İstek hatası: {e}")
        return None

def process_results(result_json, crn_list, scrn_list, backup_map, original_backup_map):
    timed_out = False

    for item in result_json.get("ecrnResultList", []):
        crn  = item["crn"]
        code = item.get("resultCode", "")
        msg  = RETURN_VALUES.get(code, f"Bilinmeyen kod: {code}")
        log(f"  CRN {crn}: {msg}")

        is_backup = crn in original_backup_map.values()

        if code in TIMEOUT_CODES:
            timed_out = True
            break
        elif code in SUCCESS_CODES:
            crn_list.remove(crn)
        elif code in {"VAL06", "Kontenjan Dolu"} and crn in backup_map:
            spare = backup_map.pop(crn)
            log(f"  → Yedek CRN deneniyor: {spare}")
            crn_list.remove(crn)
            crn_list.append(spare)
            backup_map[spare] = crn
        elif code in RETRY_CODES:
            pass
        else:
            if is_backup:
                original = next((k for k, v in original_backup_map.items() if v == crn), None)
                if original:
                    log(f"  → Yedek başarısız, orijinale dönülüyor: {original}")
                    crn_list.remove(crn)
                    crn_list.append(original)
                    backup_map.pop(crn, None)
                    return crn_list, scrn_list, timed_out
            elif crn in backup_map:
                spare = backup_map.pop(crn)
                log(f"  → Yedek deneniyor: {spare}")
                crn_list.remove(crn)
                crn_list.append(spare)
            else:
                crn_list.remove(crn)

    for item in result_json.get("scrnResultList", []):
        crn  = item["crn"]
        code = item.get("resultCode", "")
        msg  = RETURN_VALUES.get(code, f"Bilinmeyen kod: {code}")
        log(f"  SCRN {crn}: {msg}")
        if code in SUCCESS_CODES:
            scrn_list.remove(crn)
        elif code not in RETRY_CODES:
            scrn_list.remove(crn)

    return crn_list, scrn_list, timed_out

# ─────────────────────────────────────────
#  ANA AKIŞ
# ─────────────────────────────────────────

def main():
    print("=" * 55)
    print("  İTÜ Kepler Ders Seçici")
    print("=" * 55)

    if TOKEN.startswith("Bearer eyJ..."):
        print("\n⚠  TOKEN ayarlanmamış!")
        print("   Chrome → Kepler ders seçim sayfası → F12 → Network")
        print("   → Fetch/XHR → F5 → KayitZamaniKontrolu → Headers")
        print("   → 'authorization' satırını kopyala")
        input("\nEnter'a basarak çık...")
        return

    crn_list, backup_map = parse_crn_list(CRN_LIST)
    scrn_list = [str(s) for s in SCRN_LIST]
    original_backup_map = dict(backup_map)

    if not crn_list and not scrn_list:
        log("CRN ve SCRN listeleri boş, çıkılıyor.")
        return

    log(f"CRN listesi : {crn_list}")
    log(f"SCRN listesi: {scrn_list}")
    log(f"Hedef zaman : {START_TIME}")
    log(f"Pencere     : {START_TIME.strftime('%H:%M:%S')} -1sn → +{int(ATTACK_END)}sn, {ATTACK_DELAY}sn arayla")

    # ── Bekleme ────────────────────────────────────────
    delta = (START_TIME - datetime.now()).total_seconds()
    if delta > 300:
        wait = delta - 300
        log(f"5 dk kalana kadar bekleniyor ({wait:.0f} sn)...")
        time.sleep(wait)

    delta = (START_TIME - datetime.now()).total_seconds()
    if delta > 60:
        wait = delta - 60
        log(f"1 dk kalana kadar bekleniyor ({wait:.0f} sn)...")
        time.sleep(wait)

    # ── 1 dk kala: zaman kontrolü ──────────────────────
    log("Zaman kontrolü başladı...")
    while True:
        delta = (START_TIME - datetime.now()).total_seconds()
        if check_selection_time():
            log("✓ Kepler: ders seçimi açıldı!")
            break
        if delta <= 1.0:
            log("Hedefe 1 saniye kaldı — istek atılıyor!")
            break
        time.sleep(0.05)

    # ── Saldırı Penceresi ──────────────────────────────
    log("=" * 40)
    log("DERS SEÇİMİ BAŞLIYOR")
    log("=" * 40)

    attack_deadline = START_TIME.timestamp() + ATTACK_END
    attempt = 0

    while time.time() < attack_deadline:
        attempt += 1
        elapsed = datetime.now().timestamp() - START_TIME.timestamp()
        log(f"── Deneme #{attempt}  [{elapsed:+.2f}s] ──")

        result = send_request(crn_list, scrn_list)

        if result is not None:
            crn_list, scrn_list, timed_out = process_results(
                result, crn_list, scrn_list, backup_map, original_backup_map
            )

            if timed_out:
                log("⊗ İstek limiti aşıldı! Duruyorum.")
                break

            if not crn_list and not scrn_list:
                log("🎉 Tüm dersler alındı!")
                break

        # Pencere hâlâ açıksa bekle ve tekrar dene
        if time.time() < attack_deadline:
            time.sleep(ATTACK_DELAY)

    print()
    if crn_list or scrn_list:
        log(f"Pencere kapandı. Alınamayan CRN → {crn_list}")
    log("Program sonlandı.")
    input("Çıkmak için Enter'a bas...")

if __name__ == "__main__":
    main()
