import cloudscraper
import schedule
import time
import requests
from bs4 import BeautifulSoup
import re

# === [ KONFIGURASI ] ===
EMAIL = "masukkan email kamu"
PASSWORD = "masukkan password kamu"
SERVER_ID = "masukkan server kamu" # misal server 2 masukkan angka 2
TELEGRAM_TOKEN = "masukkan telegram bot token kamu"
TELEGRAM_CHAT_ID = "masukkan uid telegram kamu"

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def send_telegram(message):
    if not TELEGRAM_TOKEN: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except:
        pass

def job_claim():
    ts = time.strftime('%H:%M:%S')
    print(f"\n[{ts}] MEMULAI PROSES AUTO-CLAIM...")
    
    
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    url_base = "https://kageherostudio.com/event/index_.php"
    url_page = "https://kageherostudio.com/event/?event=daily"
    headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': url_page}

    try:
        # --- LANGKAH 1 ---
        print(f"[{ts}]  Mengakses dashboard harian...")
        page = scraper.get(url_page)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        print(f"[{ts}]  Mencari target hadiah hari ini...")
        active_reward = soup.find('div', class_='reward-star')
        
        if not active_reward:
            print(f"[{ts}]  Hadiah tidak ditemukan! (Cek manual atau sudah klaim)")
            send_telegram("NHNE: Hadiah tidak ditemukan.")
            return

        item_name = active_reward.get('data-name')
        item_id = active_reward.get('data-id')
        period_id = active_reward.get('data-period')
        print(f"[{ts}]  Target ditemukan: {item_name} (ID: {item_id})")

        # --- LANGKAH 2 ---
        print(f"[{ts}]  Mencoba login akun: {EMAIL}...")
        login = scraper.post(f"{url_base}?act=login", data={'txtuserid': EMAIL, 'txtpassword': PASSWORD}, headers=headers)
        
        # Simulasi delay agar terlihat seperti manusia (optional, buat estetika)
        time.sleep(1)

        if login.json().get('message') == 'success':
            print(f"[{ts}]  Login Berhasil! Sesi disimpan.")
            
            # --- LANGKAH 3 ---
            print(f"[{ts}]  Mengirim paket klaim ke Server ID: {SERVER_ID}...")
            claim = scraper.post(f"{url_base}?act=daily", data={
                'itemId': item_id, 'periodId': period_id, 'selserver': SERVER_ID
            }, headers=headers)
            
            raw_res = claim.json().get('data', 'No Response')
            res_msg = clean_html(raw_res)
            
            # --- LANGKAH 4 ---
            print(f"[{ts}]  Status Respon: {res_msg}")
            
            report = (
                f"--- NHNE AUTO-CLAIM SUCCESS ---\n\n"
                f"Item: {item_name}\n"
                f"Account: {EMAIL}\n"
                f"Status: {res_msg}\n\n"
                f"-------------------------------"
            )
            print(f"[{ts}]  Mengirim laporan ke Telegram...")
            send_telegram(report)
            print(f"[{ts}]  PROSES SELESAI...Tunggu hari selanjutnya!")
        else:
            print(f"[{ts}]  Login Ditolak! Cek kembali email/password.")
            send_telegram(f"NHNE: Login Gagal untuk {EMAIL}")
            
    except Exception as e:
        print(f"[{ts}]  CRITICAL ERROR: {str(e)}")
        send_telegram(f"NHNE Error: {str(e)}")

# --- RUNNER ---
print("="*35)
print("          NHNE AUTO-CLAIM")
print("="*35)

job_claim()

print(f"\n[*] Bot masuk ke mode Standby. Menunggu jam 1 malam...")
schedule.every().day.at("01:00").do(job_claim)

while True:
    schedule.run_pending()
    time.sleep(60)