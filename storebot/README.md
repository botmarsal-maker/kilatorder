# Telegram Store Digital Bot

Bot Telegram otomatis ini dibangun dengan `Python` dan `pyTelegramBotAPI`. Lengkap dengan panel administrasi, sistem saldo auto-cut, dan manajemen produk/voucher SQLite3.

## Fitur Utama
1. **User Dashboard**: Tampilan UI dengan tombol emoji yang bersih dan modern.
2. **Auto-Stock & Balance**: Validasi transaksi sekunder, pengiriman saldo dan produk tanpa jeda.
3. **Manual Deposit Panel**: Integrasi sistem bukti transfer ke menu admin untuk persetujuan (Approve/Reject).
4. **Broadcast & Voucher**: Diskon promosi atau direct-message ke semua pengguna.

## Struktur Project

```text
/storebot
├── bot.py           # Entry point utama, menangani semua handler.
├── config.py        # Pengaturan token BOT dan list ADMIN_IDS
├── database.py      # Lapisan ORM/SQLite custom
├── handlers/        # Disiapkan untuk modular scaling jika file bot semakin besar
├── data/            # Direktori state/database. (Otomatis dibuat)
└── requirements.txt # Daftar packages
```

---

## 🚀 Panduan Instalasi Lengkap (Ubuntu VPS dengan Git Clone)

**1. Update Server & Install Dependensi Dasar**
Buka terminal/SSH VPS Anda, lalu jalankan:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nodejs npm -y
sudo npm install -g pm2
```

**2. Clone Repository**
Ganti URL di bawah dengan link repository GitHub Anda (jika kode sudah di-push), atau gunakan format ini:
```bash
cd ~
git clone https://github.com/USERNAME/NAMA-REPO-ANDA.git Kilatorder
cd Kilatorder/storebot
```
*(Catatan: pastikan Anda menyesuaikan link github dan masuk ke dalam folder tempat `bot.py` berada)*

**3. Buat Virtual Environment Python**
Langkah ini penting agar package Python tidak bentrok.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Konfigurasi Environment (.env)**
Buat file konfigurasi rahasia:
```bash
nano .env
```
Isi dengan data token Anda (jangan lupa sesuaikan!):
```env
BOT_TOKEN=1234567890:AAH_TokenDariBotFather
ADMIN_IDS=123456789,987654321
DB_PATH=data/store.db
```
Simpan: Tekan `Ctrl+X`, ketik `y`, lalu tekan `Enter`.

**5. Jalankan Bot dengan PM2**
Jalankan file `bot.py` menggunakan interpreter dari dalam virtual environment agar requirements dan `.env` terdeteksi:
```bash
pm2 start bot.py --name bot-toko --interpreter ./venv/bin/python
```

**6. Buat Auto-Restart (PM2 Startup)**
Agar bot selalu menyala meski VPS di-reboot:
```bash
pm2 save
pm2 startup
```

---

Selesai! 🎉 Bot Anda sekarang siap beroperasi.

**Perintah PM2 Penting:**
- `pm2 logs bot-toko` (Melihat status jalannya bot / mencari pesan error)
- `pm2 restart bot-toko` (Meresart bot)
- `pm2 stop bot-toko` (Menghentikan bot)
- `pm2 flush` (Menghapus riwayat log yang penuh)
