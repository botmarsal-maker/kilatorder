import os
from dotenv import load_dotenv

# Load file .env jika ada
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Mengambil ADMIN_IDS dari env berupa string (contoh: "123456,78910") menjadi list of intergers
admin_ids_str = os.getenv("ADMIN_IDS", "")
try:
    ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
except ValueError:
    ADMIN_IDS = []

DB_PATH = os.getenv("DB_PATH", "data/store.db")

