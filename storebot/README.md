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

## 🚀 Panduan Instalasi (Ubuntu VPS / Linux Server)

**1. Update Server Repository & Install Dependensi Dasar**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

**2. Siapkan Direktori & Salin File**
```bash
mkdir -p /root/storebot
cd /root/storebot
```
*(Unggah atau salin semua source code / direktori ini ke folder `/root/storebot`.)*

**3. Buat Virtual Environment Python**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Konfigurasi Token BOT**
Edit `config.py` sesuai kebutuhan:
```bash
nano config.py
# Pastikan BOT_TOKEN diisi token dari @BotFather
# Pastikan ADMIN_IDS diisi dengan Chat ID admin
```

**5. Deploy menggunakan Systemd (Background Service)**
Buat file service backend agar bot menyala 24/7 dan auto-restart jika server di-reboot.

```bash
sudo nano /etc/systemd/system/storebot.service
```
Isi konfigurasi berikut ini ke editor nano (tekan `Ctrl+X` - `Y` - `Enter` untuk menyimpan):
```ini
[Unit]
Description=Telegram Store Digital Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/storebot
ExecStart=/root/storebot/venv/bin/python /root/storebot/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**6. Aktifkan Daemon Bot**
```bash
sudo systemctl daemon-reload
sudo systemctl enable storebot
sudo systemctl start storebot
```

Cek status BOT Anda:
```bash
sudo systemctl status storebot
```
Atau lihat log live-nya:
```bash
sudo journalctl -u storebot.service -f
```

Selesai! 🎉 Bot Anda sekarang siap beroperasi.
