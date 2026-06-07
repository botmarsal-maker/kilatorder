import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_IDS, DB_PATH
from database import Database
import os

bot = telebot.TeleBot(BOT_TOKEN)
db = Database(DB_PATH)

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        KeyboardButton('🏷️ List Produk'),
        KeyboardButton('🛍️ Voucher'),
        KeyboardButton('📁 Laporan Stok')
    )
    
    # Ambil produk untuk membuat tombol angka
    try:
        products = db.get_products()
        if products:
            product_buttons = [KeyboardButton(str(p['id'])) for p in products[:3]] # Batasi 3 untuk tampilan rapi
            if product_buttons:
                markup.add(*product_buttons)
    except:
        pass

    markup.add(
        KeyboardButton('💰 Deposit'),
        KeyboardButton('❓ Cara Order'),
        KeyboardButton('⚠️ Information')
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = db.get_user(message.chat.id)
    text = f"Halo selamat datang di Bot Store Digital! 👋\n"
    text += f"ID Kamu: {message.chat.id}\n"
    text += f"Saldo saat ini: Rp {user['balance']:,}\n\n"
    text += "Silakan pilih menu di bawah ini untuk memulai layanan."
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '🏷️ List Produk')
def list_produk(message):
    products = db.get_products()
    if not products:
        bot.send_message(message.chat.id, "Belum ada produk yang tersedia saat ini.")
        return

    text = "Daftar Produk Digital Kami:\n\n"
    for p in products:
        text += f"[{p['id']}] {p['nama_produk']}\n"
        text += f"Harga: Rp {p['harga']:,} | Stok: {p['stok']}\n\n"
    
    text += "Kirim teks atau tekan tombol angka 1, 2, atau 3 untuk langsung membeli."
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton('➡️ Selanjutnya', callback_data='next_page'),
        InlineKeyboardButton('🔥 PRODUK POPULER', callback_data='popular_products')
    )
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['next_page', 'popular_products'])
def handle_dummy_callbacks(call):
    bot.answer_callback_query(call.id, "Menu ini sedang dalam pengembangan.")


@bot.message_handler(func=lambda message: message.text == 'Kembali')
def back_to_main(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text.isdigit())
def buy_product(message):
    product_id = int(message.text)
    product = db.get_product(product_id)
    if not product:
        return
        
    if product['stok'] <= 0:
        bot.send_message(message.chat.id, "Maaf, stok produk ini sedang kosong. ❌")
        return
        
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Ya, Beli", callback_data=f"buy_{product_id}"))
    markup.add(InlineKeyboardButton(text="❌ Batal", callback_data="cancel_buy"))
    
    user = db.get_user(message.chat.id)
    text = f"Konfirmasi Pembelian:\n\n"
    text += f"Produk: {product['nama_produk']}\n"
    text += f"Harga: Rp {product['harga']:,}\n"
    text += f"Sisa Saldo Anda: Rp {user['balance']:,}\n\n"
    text += "Apakah Anda yakin ingin membeli?"
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def process_buy(call):
    product_id = int(call.data.split('_')[1])
    user_id = call.message.chat.id
    
    product = db.get_product(product_id)
    user = db.get_user(user_id)
    
    if not product or product['stok'] <= 0:
        bot.answer_callback_query(call.id, "Produk tidak tersedia atau stok habis. ❌", show_alert=True)
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except: pass
        return
        
    if user['balance'] < product['harga']:
        bot.answer_callback_query(call.id, "Saldo tidak mencukupi. ❌ Silakan deposit.", show_alert=True)
        return

    # Proses Pembelian
    db.update_balance(user_id, -product['harga'])
    db.update_stock(product_id, -1)
    db.add_transaction(user_id, product_id, product['harga'])
    
    bot.answer_callback_query(call.id, "Pembelian Berhasil! ✅")
    bot.edit_message_text(f"Pembelian {product['nama_produk']} Berhasil!\nSaldo Anda telah dipotong Rp {product['harga']:,}.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    # Kirim Produk
    bot.send_message(user_id, f"🎉 Terima kasih! Berikut adalah produk digital Anda:\n\n>> DATA/KODE UNTUK {product['nama_produk'].upper()} <<\n\nSimpan baik-baik data di atas.", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_buy')
def cancel_buy(call):
    bot.answer_callback_query(call.id, "Pembelian Dibatalkan.")
    try:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    except: pass

@bot.message_handler(func=lambda message: message.text == '💰 Deposit')
def request_deposit(message):
    text = "Silakan masukkan nominal deposit (Misal: 50000):"
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, process_deposit_amount)

def process_deposit_amount(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Nominal harus berupa angka yang valid.", reply_markup=main_menu())
        return
        
    amount = int(message.text)
    if amount < 10000:
        bot.send_message(message.chat.id, "Minimal deposit adalah Rp 10,000.", reply_markup=main_menu())
        return
        
    deposit_id = db.add_deposit(message.chat.id, amount)
    
    text = f"Tiket Deposit #{deposit_id} Dibuat!\n"
    text += f"Nominal: Rp {amount:,}\n\n"
    text += "Silakan transfer ke rekening berikut:\n"
    text += "BCA: 1234567890 a.n Admin Store\n"
    text += "OVO: 081234567890\n\n"
    text += "Setelah transfer, kirimkan BUKTI TRANSFER berupa foto/screenshot di sini."
    
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, process_deposit_proof, deposit_id, amount)

def process_deposit_proof(message, deposit_id, amount):
    if not message.photo:
        bot.send_message(message.chat.id, "Anda harus mengirimkan foto. Silakan ulangi tiket deposit.", reply_markup=main_menu())
        db.update_deposit_status(deposit_id, 'failed')
        return
        
    bot.send_message(message.chat.id, "Bukti transfer diterima. Menunggu persetujuan Admin. ⏳", reply_markup=main_menu())
    
    # Kirim ke Admin
    for admin in ADMIN_IDS:
        try:
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("✅ Approve", callback_data=f"dep_approve_{deposit_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"dep_reject_{deposit_id}")
            )
            bot.send_photo(admin, message.photo[-1].file_id, caption=f"🎫 Deposit Masuk!\nUser ID: {message.chat.id}\nAmount: Rp {amount:,}\nTicket: #{deposit_id}", reply_markup=markup)
        except: pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('dep_'))
def admin_process_deposit(call):
    data = call.data.split('_')
    action, deposit_id = data[1], int(data[2])
    
    deposit = db.get_deposit(deposit_id)
    if not deposit or deposit['status'] != 'pending':
        bot.answer_callback_query(call.id, "Deposit sudah diproses.")
        return
        
    if action == 'approve':
        db.update_deposit_status(deposit_id, 'approved')
        db.update_balance(deposit['user_id'], deposit['amount'])
        bot.edit_message_caption(f"✅ DISETUJUI.\n{call.message.caption}", chat_id=call.message.chat.id, message_id=call.message.message_id)
        try: bot.send_message(deposit['user_id'], f"🎉 Deposit Rp {deposit['amount']:,} DISETUJUI. Saldo ditambahkan.")
        except: pass
    elif action == 'reject':
        db.update_deposit_status(deposit_id, 'rejected')
        bot.edit_message_caption(f"❌ DITOLAK.\n{call.message.caption}", chat_id=call.message.chat.id, message_id=call.message.message_id)
        try: bot.send_message(deposit['user_id'], f"❌ Deposit Rp {deposit['amount']:,} DITOLAK oleh Admin.")
        except: pass

@bot.message_handler(func=lambda message: message.text == '📁 Laporan Stok')
def stok_report(message):
    products = db.get_products()
    text = "📁 Laporan Stok Produk:\n\n"
    for p in products:
        text += f"- {p['nama_produk']}: {p['stok']} item\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == '❓ Cara Order')
def cara_order(message):
    text = "❓ Cara Order:\n1. Lakukan deposit.\n2. Buka List Produk.\n3. Tekan atau ketik nomor produk.\n4. Konfirmasi pembelian.\n5. Detail produk akan dikirim oleh bot."
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == '⚠️ Information')
def info_bot(message):
    bot.send_message(message.chat.id, "⚠️ Bot Store Digital beroperasi otomatis 24 Jam. Hubungi Admin jika ada kendala.")

@bot.message_handler(func=lambda message: message.text == '🛍️ Voucher')
def request_voucher(message):
    msg = bot.send_message(message.chat.id, "Kirim kode Voucher Anda:")
    bot.register_next_step_handler(msg, process_voucher)

def process_voucher(message):
    kode = message.text.upper()
    voucher = db.check_voucher(kode)
    
    if not voucher:
        bot.send_message(message.chat.id, "Voucher tidak ditemukan. ❌", reply_markup=main_menu())
        return
        
    if voucher['terpakai'] >= voucher['batas_penggunaan']:
        bot.send_message(message.chat.id, "Limit penggunaan voucher ini telah habis. ❌", reply_markup=main_menu())
        return
        
    db.use_voucher(kode)
    db.update_balance(message.chat.id, voucher['nominal'])
    bot.send_message(message.chat.id, f"Selamat! 🎉 Anda klaim voucher senilai Rp {voucher['nominal']:,}. Saldo bertambah.", reply_markup=main_menu())

# --- DAFTAR PERINTAH ADMIN ---
def is_admin(user_id): return user_id in ADMIN_IDS

@bot.message_handler(commands=['addsaldo', 'minsaldo'])
def admin_manage_saldo(message):
    if not is_admin(message.chat.id): return
    try:
        cmd, target_id, amount = message.text.split()
        target_id, amount = int(target_id), int(amount)
        if cmd == '/addsaldo':
            db.update_balance(target_id, amount)
            bot.send_message(message.chat.id, f"Ditambahkan Rp {amount} ke {target_id}.")
        elif cmd == '/minsaldo':
            db.update_balance(target_id, -amount)
            bot.send_message(message.chat.id, f"Dikurangi Rp {amount} dari {target_id}.")
    except:
        bot.send_message(message.chat.id, "Gunakan: /addsaldo <id> <jumlah>")

@bot.message_handler(commands=['addproduk'])
def admin_add_produk(message):
    if not is_admin(message.chat.id): return
    msg = bot.send_message(message.chat.id, "Format Produk:\nNama\nHarga\nStok\nKategori\nDeskripsi")
    bot.register_next_step_handler(msg, process_add_produk)

def process_add_produk(message):
    try:
        lines = message.text.split('\n')
        db.add_product(lines[0], int(lines[1]), int(lines[2]), lines[3], '\n'.join(lines[4:]))
        bot.send_message(message.chat.id, "Produk ditambahkan!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['hapusproduk', 'editproduk'])
def admin_edit_delete(message):
    if not is_admin(message.chat.id): return
    try:
        cmd = message.text.split()[0]
        if cmd == '/hapusproduk':
            pid = int(message.text.split()[1])
            db.delete_product(pid)
            bot.send_message(message.chat.id, f"Produk {pid} dihapus.")
        elif cmd == '/editproduk':
            msg = bot.send_message(message.chat.id, "Kirim ID dan Data:\nID\nNama\nHarga\nStok\nKategori\nDeskripsi")
            bot.register_next_step_handler(msg, process_edit_produk)
    except: bot.send_message(message.chat.id, "Format salah.")

def process_edit_produk(message):
    try:
        lines = message.text.split('\n')
        db.edit_product(int(lines[0]), lines[1], int(lines[2]), int(lines[3]), lines[4], '\n'.join(lines[5:]))
        bot.send_message(message.chat.id, "Produk diedit!")
    except Exception as e: bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['addvoucher'])
def admin_add_voucher(message):
    if not is_admin(message.chat.id): return
    msg = bot.send_message(message.chat.id, "Format Voucher:\nKODE NOMINAL LIMIT")
    bot.register_next_step_handler(msg, process_add_voucher)

def process_add_voucher(message):
    try:
        kode, nom, limit = message.text.split()
        with db.conn:
            db.conn.execute("INSERT INTO vouchers (kode, nominal, batas_penggunaan, tanggal_kadaluarsa) VALUES (?, ?, ?, ?)", (kode.upper(), int(nom), int(limit), "2099-12-31"))
        bot.send_message(message.chat.id, f"Voucher {kode} siap digunakan!")
    except: bot.send_message(message.chat.id, "Error format voucher.")

@bot.message_handler(commands=['listuser', 'listtransaksi'])
def admin_reports(message):
    if not is_admin(message.chat.id): return
    cmd = message.text.split()[0]
    if cmd == '/listuser':
        u = db.get_all_users()
        bot.send_message(message.chat.id, f"Total User: {len(u)}\n" + "\n".join([f"{x['id']} (Sal: {x['balance']})" for x in u[:20]]))
    elif cmd == '/listtransaksi':
        t = db.get_all_transactions()
        bot.send_message(message.chat.id, f"Transaksi Terbaru:\n" + "\n".join([f"#{x['id']} | Prod: {x['product_id']} | Oleh: {x['user_id']}" for x in t]))

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if not is_admin(message.chat.id): return
    msg = bot.send_message(message.chat.id, "Pesan broadcast:")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    users = db.get_all_users()
    s = 0
    for u in users:
        try:
            bot.send_message(u['id'], message.text)
            s += 1
        except: pass
    bot.send_message(message.chat.id, f"Terkirim ke {s} user.")

if __name__ == '__main__':
    print("Bot Store Digital berjalan...")
    bot.infinity_polling()
